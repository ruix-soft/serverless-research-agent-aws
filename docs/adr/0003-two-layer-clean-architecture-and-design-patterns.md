# 3. Arquitectura en Dos Capas (Presentación y Contexto) e Implementación de Patrones de Diseño

* **Estatus:** Aceptado
* **Fecha:** 2026-08-24

## Contexto

El Agente de Investigación Serverless requería evolucionar desde una estructura monolítica/acoplada hacia una base de código empresarial, modular, altamente testeable y preparada para escalar. Los retos principales incluían:
1. El acoplamiento entre los eventos de AWS Lambda / API Gateway y la lógica de negocio del agente de IA.
2. La contaminación del dominio y casos de uso con herramientas de observabilidad (logs, métricas, trazas).
3. El manejo inconsistente de errores y excepciones no controladas.
4. La necesidad de reutilizar componentes transversales (Value Objects, DTOs, manejo de eventos, criterios de búsqueda) en múltiples microservicios o funciones serverless.

## Decisión

Adoptar una arquitectura estricta en **Dos Capas Principales (Presentación y Contexto)** (`arch-core`) implementando patrones de diseño reconocidos:

### 1. Macro-Separación de Capas

```
src/
├── app/                  # CAPA 1: PRESENTACIÓN Y ENTREGA
│   ├── aws/
│   │   ├── handlers/     # Delivery Handlers específicos de AWS Lambda
│   │   ├── powertools.py # Instancias de AWS Lambda Powertools
│   │   └── response.py   # Mapeador de Result a respuestas API Gateway
│   └── controllers/      # Controladores y decoradores de comportamiento (CQRS)
└── context/              # CAPA 2: BOUNDED CONTEXTS & CORE DDD
    ├── kit/              # Bloques de construcción fundamentales y utilidades reutilizables
    │   ├── chain/        # Motor de Chain of Responsibility y decoradores de paso
    │   ├── command/      # Abstracciones CQRS para Comandos y decoradores
    │   ├── criteria/     # Patrón Criteria (Filtros, Ordenamiento, Paginación)
    │   ├── dtos/         # DTOs base (Result, Optional, Either, Metadata, DomainEvent)
    │   ├── errors/       # Jerarquía estándar de DomainError
    │   ├── query/        # Abstracciones CQRS para Consultas y decoradores
    │   ├── service/      # Contratos de servicios e interfaces de infraestructura
    │   └── vo/           # Value Objects base (Uuid, Date, String, Number, Boolean)
    └── research/         # Bounded Context de Investigación
        ├── application/  # DTOs y Casos de Uso (orquestados como Chain of Responsibility)
        ├── domain/       # Puertos de interfaz puros e invariantes
        └── infrastructure/# Adaptadores concretos (S3, Bedrock, Lambda, Powertools) y Factory
```

### 2. Patrones de Diseño Implementados

1. **Arquitectura Hexagonal (Ports & Adapters):**
   - El núcleo de dominio (`context/research/domain`) define contratos puros (`IReportStoragePort`, `IAsyncWorkerInvokerPort`, `IResearchAgentPort`).
   - Los adaptadores concretos (`S3StorageAdapter`, `LambdaInvokerAdapter`, `BedrockAgentAdapter`) residen en infraestructura y se conectan a los puertos sin contaminar la aplicación.

2. **Segregación de Responsabilidad de Comandos y Consultas (CQRS):**
   - Separación estricta entre operaciones que mutan estado (`CommandHandler`, p.ej. iniciar investigación o ejecutar worker) y operaciones de solo lectura (`QueryHandler`, p.ej. consultar estado).

3. **Cadena de Responsabilidad (Chain of Responsibility) para Todos los Casos de Uso:**
   - Cada caso de uso se modela como una secuencia lineal de pasos independientes (`Step[I, O, C]`) gestionados por un `ChainBuilder`.
   - La comunicación entre pasos se realiza a través de un objeto de contexto compartido (`Context`), garantizando responsabilidad única y facilidad de testing unitario por cada paso.

4. **Programación Orientada a Vías de Tren (Railway-Oriented Programming con `Result[O, E]`):**
   - Eliminación del uso de excepciones para errores de lógica de negocio. Toda operación retorna un objeto `Result.ok(value)` o `Result.err(domain_error)`.

5. **Patrón Decorador (Decorator Pattern) para Observabilidad:**
   - La observabilidad (registro estructurado de logs y publicación de métricas) se inyecta envolviendo los handlers y queries a nivel de controlador (`LoggingDecorator`, `MetricsDecorator`), manteniendo el código de aplicación completamente libre de dependencias de observabilidad.

6. **Inyección Manual de Dependencias mediante Abstract Factory (`InfrastructureFactory`):**
   - Sin frameworks IoC mágicos o contenedores pesados. Las dependencias se ensamblan de forma determinista y explícita, facilitando la sustitución de mocks en entornos de pruebas.

7. **Objetos de Valor (Value Objects):**
   - Tipado fuerte con validación intrínseca e inmutabilidad (`Uuid`, `Date`, `String`, `Number`, `Boolean`).

## Consecuencias

* **Positivas:**
  * **Testabilidad Absoluta:** 94 pruebas unitarias ejecutadas en <0.4 segundos sin dependencias externas ni servicios en la nube activos.
  * **Desacoplamiento Total:** La lógica de negocio puede migrarse a contenedores, APIs REST alternativas o CLI sin alterar el código de aplicación ni el dominio.
  * **Mantenibilidad y Extensibilidad:** Añadir validaciones o pasos a un caso de uso requiere simplemente agregar un nuevo `Step` a la cadena sin modificar los pasos existentes (Principio Abierto/Cerrado).
  * **Estandarización:** Reutilización directa del módulo `kit` en futuros contextos delimitados de la organización.
* **Negativas:**
  * Mayor cantidad de archivos y clases debido a la separación estricta de interfaces, adaptadores, controladores y decoradores.

