# 4. Control de Tasa Distribuido (Rate Limiting) con Amazon DynamoDB y Decoradores CQRS

* **Estatus:** Aceptado
* **Fecha:** 2026-08-24

## Contexto

El Agente de Investigación expone endpoints públicos en Amazon API Gateway que desencadenan operaciones de cómputo intensivo, inferencia en Modelos de Lenguaje (Amazon Bedrock / Claude Sonnet) y búsquedas web en tiempo real (Tavily API). 

Sin un mecanismo de limitación de tasa (*Rate Limiting*), el sistema quedaba vulnerable a:
1. **Ataques de Denegación de Billetera (*Denial of Wallet*):** Invocaciones masivas no autorizadas que incrementen los costos de tokens en Bedrock y cuotas de API de Tavily.
2. **Saturación de Concurrencia:** Agotamiento de la cuota de concurrencia de AWS Lambda en la cuenta.
3. **Abuso de Polling:** Consultas excesivas y repetitivas al endpoint `GET /research/{job_id}`.

## Opciones Evaluadas

1. **AWS WAF (Web Application Firewall):**
   - *Ventajas:* Protección en el borde de la red antes de llegar a Lambda.
   - *Desventajas:* Costo fijo mensual por Web ACL (~$5 USD/mes + reglas + peticiones), lo que rompe el principio de costo cero en reposo para un portafolio serverless.
2. **Amazon ElastiCache / Redis:**
   - *Ventajas:* Latencia de sub-milisegundo.
   - *Desventajas:* Requiere instancias fijas (costo continuo), gestión de VPC y configuración de red compleja para Lambdas.
3. **Amazon DynamoDB (On-Demand) con TTL + Decoradores CQRS (Elegida):**
   - *Ventajas:* 100% Serverless (modo `PAY_PER_REQUEST`, costo $0 en reposo), operaciones atómicas con `UpdateItem`, purga automática de ventanas de tiempo expiradas mediante Time-To-Live (TTL) y desacoplamiento limpio a través de decoradores CQRS.

## Decisión

Implementar un esquema de **Rate Limiting Distribuido** basado en el algoritmo de *Ventana de Tiempo Fija (Fixed Window Counter)* respaldado por **Amazon DynamoDB** y desacoplado mediante **Decoradores CQRS**:

1. **Persistencia y TTL en DynamoDB:**
   - Tabla `RateLimitsTable` con clave de partición `pk = "{key}:{window_id}"`.
   - Operación atómica `UpdateItem` con `ADD request_count :1` y `SET expires_at = if_not_exists(expires_at, :ttl)`.
   - El atributo `expires_at` permite a DynamoDB purgar automáticamente las ventanas de tiempo viejas sin consumo de unidades de escritura (WCU).
2. **Integración con la Arquitectura en Dos Capas (`arch-core`):**
   - Contrato abstracto `RateLimiterService` en `context/kit/service/`.
   - Adaptador concreto `DynamoDBRateLimiterAdapter` en `context/research/infrastructure/`.
   - Decoradores CQRS:
     - `CommandRateLimitDecorator` aplicado en `StartResearchController` (límite: 5 peticiones/minuto por IP).
     - `QueryRateLimitDecorator` aplicado en `GetResearchStatusController` (límite: 30 peticiones/minuto por IP y `job_id`).
3. **Mapeo de Errores HTTP:**
   - Cuando se excede el límite, el decorador retorna un `Result.err(RateLimitError)` que la capa de entrega (`app/aws/response.py`) traduce inmediatamente a **HTTP `429 Too Many Requests`**.

## Consecuencias

* **Positivas:**
  * **Protección Económica y de Concurrencia:** Mitiga el riesgo de facturación imprevista en Bedrock y Tavily.
  * **Cero Costo en Reposo:** Utiliza modo On-Demand y TTL de DynamoDB.
  * **Aislamiento Arquitectónico:** La lógica de negocio y los casos de uso no tienen conocimiento del control de tasa; la regla se aplica transparentemente como decorador en los controladores.
  * **Alta Testabilidad:** Permite inyectar fácilmente `MockRateLimiter` en pruebas unitarias sin depender de DynamoDB real.
* **Negativas:**
  * Cada petición válida realiza una llamada adicional `dynamodb:UpdateItem` (~5-15 ms de latencia adicional en el inicio de la petición).

