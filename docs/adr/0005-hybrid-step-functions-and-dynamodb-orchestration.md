# 5. Solución Híbrida: Orquestación Resiliente con AWS Step Functions y Persistencia en DynamoDB

* **Estatus:** Aceptado
* **Fecha:** 2026-08-24

## Contexto

En versiones anteriores, el inicio de una investigación asíncrona utilizaba una invocación directa de Lambda a Lambda (`lambda:InvokeFunction` con `InvocationType: Event`) y determinaba el estado de finalización infiriendo la presencia del archivo Markdown en Amazon S3 (`report_exists`).

Este enfoque presentaba limitaciones críticas en producción:
1. **Estados Zombi (*Limbo*):** Si la Lambda worker fallaba por timeout de LLM, error en Tavily o límite de memoria, el archivo en S3 nunca se creaba y el cliente consultando `GET /research/{id}` recibía `IN_PROGRESS` indefinidamente.
2. **Falta de Trazabilidad y Reintentos Inteligentes:** Las fallas transitorias de cuotas en Bedrock (*ThrottlingException*) provocaban la pérdida inmediata del trabajo o reintentos ciegos a nivel de invocación asíncrona de Lambda.
3. **Imposibilidad de Distinguir 404 de Trabajos Nuevos:** Un trabajo inexistente devolvía la misma respuesta que un trabajo recién encolado.

## Opciones Evaluadas

1. **Gestión de Estado Exclusiva en Código (DynamoDB `JobsTable` + Lambda Worker):**
   - *Ventajas:* Modelo de persistencia simple.
   - *Desventajas:* Si la Lambda sufre un crash fatal (OOM, timeout duro de 300s), el bloque `except` no se ejecuta y el estado queda en `IN_PROGRESS`.
2. **Orquestación Pura con AWS Step Functions (sin DynamoDB):**
   - *Ventajas:* Máquina de estados visual y reintentos nativos.
   - *Desventajas:* Consultar el estado de ejecución en Step Functions mediante `DescribeExecution` tiene límites de cuota estrictos en la API de AWS y no permite consultas de baja latencia tipo CQRS.
3. **Solución Híbrida Enterprise: Step Functions (Orquestador) + DynamoDB (Modelo de Lectura CQRS) [ELEGIDA]:**
   - *Ventajas:*
     - **Direct SDK Integration:** Step Functions escribe directamente en DynamoDB (`JobsTable`) sin requerir Lambdas intermedias (*Lambda Glue*).
     - **Resiliencia Total:** Reintentos automáticos con retroceso exponencial (*Exponential Backoff*) ante `ThrottlingException` y captura universal de fallos (`Catch: States.ALL`) para garantizar la transición a `FAILED`.
     - **Lectura CQRS de Alto Rendimiento:** `GET /research/{id}` lee directamente de DynamoDB con latencias menores a 5 ms y retorna estados `IN_PROGRESS`, `COMPLETED` o `FAILED`.

## Decisión

Adoptar la **Solución Híbrida** integrando AWS Step Functions, Amazon DynamoDB y la metodología de arquitectura limpia de **Luis Ruiz** (`arch-core` con `context.kit`):

1. **Entidad de Dominio `ResearchJob` (DDD Aggregate Root):**
   - Modela el ciclo de vida del trabajo con estados `IN_PROGRESS`, `COMPLETED` y `FAILED`, encapsulando invariantes de negocio mediante Value Objects (`Uuid`, `StringVO`, `DateVO`).
2. **Máquina de Estados `ResearchStateMachine` (`AWS::Serverless::StateMachine`):**
   - **Paso 1:** `DynamoDB:PutItem` $\rightarrow$ Registra el trabajo como `IN_PROGRESS` con TTL de 7 días.
   - **Paso 2:** `Lambda:Invoke` $\rightarrow$ Ejecuta `ExecuteResearchWorkerFunction` con 3 reintentos ante excepciones transitorias y bloque `Catch` para redirigir a fallo.
   - **Paso 3A (Éxito):** `DynamoDB:UpdateItem` $\rightarrow$ Actualiza a `COMPLETED` y guarda la ruta `s3_key`.
   - **Paso 3B (Fallo):** `DynamoDB:UpdateItem` $\rightarrow$ Actualiza a `FAILED` y almacena el motivo del error.
3. **Lectura CQRS:**
   - `GetResearchStatusUseCase` consulta `IResearchJobRepository` (DynamoDB). Si el trabajo está completado genera la URL presignada de S3; si falló, entrega el mensaje de error de forma inmediata.

## Consecuencias

* **Positivas:**
  * **Eliminación Total de Estados Zombi:** Todo fallo de cómputo, timeout o error de API externa queda registrado de forma confiable en DynamoDB.
  * **Alineación con el AWS Well-Architected Framework (Pilar de Fiabilidad):** Manejo de errores y reintentos desacoplado del código de la función Lambda.
  * **Rendimiento de Consulta Óptimo:** Consultas instantáneas indexadas por clave de partición `JOB#{id}`.
  * **Cero Costo en Reposo:** Step Functions Standard + DynamoDB Pay-Per-Request mantienen la naturaleza 100% serverless.
* **Negativas:**
  * Se requiere la definición del flujo de estados en el template de SAM / CloudFormation.

