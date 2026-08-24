# Arquitectura del Agente Investigador Serverless

Este proyecto implementa una arquitectura **Serverless-First en AWS** guiada por los principios de **Arquitectura Hexagonal (Ports & Adapters)**, **Domain-Driven Design (DDD)**, **Segregación de Comandos y Consultas (CQRS)** y orquestación de casos de uso mediante **Cadena de Responsabilidad (Chain of Responsibility)**.

---

## 1. Diagrama General de la Solución

```mermaid
flowchart TB
    subgraph ClientLayer [Clientes / Consumidores]
        User([Usuario / Frontend / CI-CD])
    end

    subgraph AWSCloud [AWS Serverless Infrastructure]
        APIGW[Amazon API Gateway REST API]

        subgraph LambdaLayer [Funciones AWS Lambda]
            StartFn["StartResearchFunction<br/>(POST /research)"]
            StatusFn["GetResearchStatusFunction<br/>(GET /research/{job_id})"]
            WorkerFn["ExecuteResearchWorkerFunction<br/>(Background AI Agent)"]
        end

        subgraph ExternalServices [Servicios Gestionados e IA]
            Bedrock[Amazon Bedrock<br/>Claude Sonnet 4.5]
            Tavily[Tavily Search API<br/>Búsqueda Web]
            S3Bucket[(Amazon S3 Bucket<br/>Reportes Markdown)]
        end
    end

    User -->|1. POST /research| APIGW
    APIGW -->|Enruta POST| StartFn
    StartFn -->|2. Invocación Asíncrona (Event)| WorkerFn
    StartFn -->>|3. 202 Accepted {job_id}| User

    WorkerFn -->|4. Razonamiento ReAct| Bedrock
    Bedrock <-->|5. Tool Web Search| Tavily
    WorkerFn -->|6. Guarda reports/{job_id}.md| S3Bucket

    User -->|7. GET /research/{job_id}| APIGW
    APIGW -->|Enruta GET| StatusFn
    StatusFn -->|8. Valida reporte / Genera URL| S3Bucket
    StatusFn -->>|9. 200 OK {s3_report_url}| User
```

---

## 2. Macro-Separación de Capas (`arch-core`)

El código fuente está dividido en dos capas fundamentales con reglas de dependencia unidireccionales:

```mermaid
graph TD
    subgraph AppLayer ["Capa 1: Presentación y Entrega (src/app/)"]
        Handlers["Delivery Handlers (app/aws/handlers/)<br/>- start_research_handler<br/>- get_research_status_handler<br/>- execute_research_worker_handler"]
        Controllers["Controllers (app/controllers/)<br/>- StartResearchController<br/>- GetResearchStatusController<br/>- ExecuteResearchWorkerController"]
        Decorators["Observability Decorators<br/>- LoggingDecorator<br/>- MetricsDecorator"]
    end

    subgraph ContextLayer ["Capa 2: Bounded Context & Core DDD (src/context/)"]
        subgraph KitModule ["Kit Reutilizable (src/context/kit/)"]
            Chain["Chain of Responsibility (ChainBuilder, Step)"]
            CQRS["CQRS Abstractions (Command, Query)"]
            DTOs["DTOs (Result, Optional, Either, Metadata)"]
            Errors["Domain Errors (DomainError, ValidationError, NotFoundError)"]
            VOs["Value Objects (Uuid, Date, String, Number, Boolean)"]
        end

        subgraph ResearchContext ["Bounded Context: Research (src/context/research/)"]
            UseCases["Application: Use Cases & Pipelines<br/>- StartResearchUseCase<br/>- GetResearchStatusUseCase<br/>- ExecuteResearchWorkerUseCase"]
            DomainPorts["Domain: Ports & Contracts<br/>- IReportStoragePort<br/>- IAsyncWorkerInvokerPort<br/>- IResearchAgentPort"]
            InfraFactory["Infrastructure: Factory & Adapters<br/>- InfrastructureFactory<br/>- S3StorageAdapter<br/>- LambdaInvokerAdapter<br/>- BedrockAgentAdapter<br/>- PowertoolsAdapters"]
        end
    end

    Handlers --> Controllers
    Controllers --> Decorators
    Controllers --> InfraFactory
    Controllers --> CQRS
    Decorators --> CQRS
    UseCases --> Chain
    UseCases --> DTOs
    UseCases --> Errors
    UseCases --> DomainPorts
    InfraFactory --> DomainPorts
```

### Reglas de Dependencia:
1. **`app/`** importa de **`context/`**, pero nunca contiene lógica de dominio ni reglas de negocio.
2. **`context/research/domain/`** es el núcleo puro; no depende de ninguna capa exterior ni de frameworks.
3. **`context/research/application/`** orquesta los casos de uso dependiendo únicamente del dominio y del `kit`.
4. **`context/research/infrastructure/`** implementa los puertos del dominio e interactúa con SDKs de AWS o terceros.

---

## 3. Flujos Detallados de los Servicios

### Flujo 1: Inicio de Investigación Asíncrona (`POST /research`)

Permite al cliente solicitar una investigación profunda sin bloquear la conexión HTTP.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Cliente HTTP
    participant APIGW as API Gateway
    participant Handler as start_research_handler
    participant Controller as StartResearchController
    participant Decorator as Metrics/Logging Decorator
    participant UseCase as StartResearchUseCase (Chain)
    participant Step1 as ValidateStartResearchStep
    participant Step2 as InvokeWorkerStep
    participant Step3 as BuildStartResearchOutputStep
    participant Invoker as LambdaInvokerAdapter
    participant Worker as ExecuteResearchWorker Lambda

    Client->>APIGW: POST /research {"topic": "AI in Healthcare", "depth": "detailed"}
    APIGW->>Handler: Invoca lambda_handler(event, context)
    Note over Handler: Parsea JSON, valida obligatoriedad de 'topic' y crea StartResearchInputDTO
    Handler->>Controller: run(input_dto)
    Controller->>Decorator: execute(input_dto)
    Note over Decorator: Registra Log inicial e inicia métrica de invocación/latencia
    Decorator->>UseCase: execute(input_dto)
    
    rect rgb(240, 248, 255)
        Note over UseCase: Ejecuta Pipeline de Cadena de Responsabilidad
        UseCase->>Step1: execute(input_dto, shared_context)
        Note over Step1: Valida tópico y genera job_id (UUID) en shared_context
        Step1-->>UseCase: Result.ok(None)

        UseCase->>Step2: execute(input_dto, shared_context)
        Step2->>Invoker: invoke_worker(job_id, topic)
        Invoker->>Worker: Invocación Asíncrona Event (lambda:InvokeFunction)
        Invoker-->>Step2: Retorno inmediato
        Step2-->>UseCase: Result.ok(None)

        UseCase->>Step3: execute(input_dto, shared_context)
        Note over Step3: Construye StartResearchOutputDTO (status="IN_PROGRESS")
        Step3-->>UseCase: Result.ok(output_dto)
    end

    UseCase-->>Decorator: Result.ok(output_dto)
    Note over Decorator: Registra métrica de éxito y Log de duración
    Decorator-->>Controller: Result.ok(output_dto)
    Controller-->>Handler: Result.ok(output_dto)
    Handler->>APIGW: HTTP 202 Accepted {"job_id": "...", "status": "IN_PROGRESS", "status_url": "/research/{id}"}
    APIGW-->>Client: Respuesta 202 Accepted
```

---

### Flujo 2: Ejecución de Fondo del Agente IA (`ExecuteResearchWorkerFunction`)

Ejecuta el ciclo de investigación profunda autónoma en segundo plano sin restricciones de timeout HTTP.

```mermaid
sequenceDiagram
    autonumber
    participant Event as Invocación Asíncrona (Event)
    participant Handler as execute_research_worker_handler
    participant Controller as ExecuteResearchWorkerController
    participant Decorator as Metrics/Logging Decorator
    participant UseCase as ExecuteResearchWorkerUseCase (Chain)
    participant Step1 as ValidateWorkerPayloadStep
    participant Step2 as RunAgentReasoningStep
    participant Step3 as PersistReportStorageStep
    participant Step4 as BuildWorkerOutputStep
    participant Agent as BedrockAgentAdapter (Strands + Claude)
    participant Tavily as Tavily Search Engine
    participant S3 as S3StorageAdapter (Amazon S3)

    Event->>Handler: Payload {job_id: "...", topic: "..."}
    Handler->>Controller: run(input_dto)
    Controller->>Decorator: execute(input_dto)
    Decorator->>UseCase: execute(input_dto)

    rect rgb(240, 248, 255)
        Note over UseCase: Ejecuta Pipeline de Cadena de Responsabilidad
        UseCase->>Step1: execute(input_dto, shared_context)
        Note over Step1: Valida job_id y topic en shared_context
        Step1-->>UseCase: Result.ok(None)

        UseCase->>Step2: execute(input_dto, shared_context)
        Step2->>Agent: execute_research(topic)
        Note over Agent: Inicializa Agente Strands con prompt de sistema
        loop Ciclo ReAct (Reasoning + Acting)
            Agent->>Agent: Razonamiento e identificación de fuentes requeridas
            Agent->>Tavily: search_web(query)
            Tavily-->>Agent: Resultados relevantes de la web
        end
        Note over Agent: Sintetiza hallazgos en formato Markdown profesional
        Agent-->>Step2: Contenido Markdown generado
        Note over Step2: Almacena report_content en shared_context
        Step2-->>UseCase: Result.ok(None)

        UseCase->>Step3: execute(input_dto, shared_context)
        Step3->>S3: upload_report(job_id, content, extension="md")
        Note over S3: PutObject en s3://reports-bucket/reports/{job_id}.md
        S3-->>Step3: "reports/{job_id}.md"
        Note over Step3: Almacena s3_key en shared_context
        Step3-->>UseCase: Result.ok(None)

        UseCase->>Step4: execute(input_dto, shared_context)
        Note over Step4: Construye ExecuteResearchWorkerOutputDTO(status="SUCCESS")
        Step4-->>UseCase: Result.ok(output_dto)
    end

    UseCase-->>Decorator: Result.ok(output_dto)
    Decorator-->>Controller: Result.ok(output_dto)
    Controller-->>Handler: Result.ok(output_dto)
    Handler-->>Event: Retorna {"job_id": "...", "status": "SUCCESS", "s3_key": "reports/..."}
```

---

### Flujo 3: Consulta de Estado y Descarga (`GET /research/{job_id}`)

Permite al cliente realizar *polling* o consultar si su reporte ya fue generado para obtener una URL de descarga segura.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Cliente HTTP
    participant APIGW as API Gateway
    participant Handler as get_research_status_handler
    participant Controller as GetResearchStatusController
    participant Decorator as Metrics/Logging Decorator
    participant UseCase as GetResearchStatusUseCase (Chain)
    participant Step1 as ValidateGetStatusStep
    participant Step2 as CheckReportStorageStep
    participant Step3 as BuildGetStatusOutputStep
    participant Storage as S3StorageAdapter (Amazon S3)

    Client->>APIGW: GET /research/{job_id}
    APIGW->>Handler: Invoca lambda_handler(pathParameters={job_id: "..."})
    Handler->>Controller: run(input_dto)
    Controller->>Decorator: execute(input_dto)
    Decorator->>UseCase: execute(input_dto)

    rect rgb(240, 248, 255)
        Note over UseCase: Ejecuta Pipeline de Cadena de Responsabilidad
        UseCase->>Step1: execute(input_dto, shared_context)
        Note over Step1: Valida parámetro job_id
        Step1-->>UseCase: Result.ok(None)

        UseCase->>Step2: execute(input_dto, shared_context)
        Step2->>Storage: report_exists(job_id)
        Storage-->>Step2: exists (True / False)

        alt Si el reporte YA existe en S3
            Step2->>Storage: generate_presigned_url("reports/{job_id}.md", expiration=3600)
            Storage-->>Step2: https://s3.amazonaws.com/... (URL válida por 1 hora)
            Note over Step2: shared_context.exists = True, shared_context.presigned_url = url
        else Si el reporte aún NO existe
            Note over Step2: shared_context.exists = False
        end
        Step2-->>UseCase: Result.ok(None)

        UseCase->>Step3: execute(input_dto, shared_context)
        alt Reporte listo
            Note over Step3: GetResearchStatusOutputDTO(status="COMPLETED", s3_report_url=url)
        else En progreso
            Note over Step3: GetResearchStatusOutputDTO(status="IN_PROGRESS", message="En generación...")
        end
        Step3-->>UseCase: Result.ok(output_dto)
    end

    UseCase-->>Decorator: Result.ok(output_dto)
    Decorator-->>Controller: Result.ok(output_dto)
    Controller-->>Handler: Result.ok(output_dto)
    Handler->>APIGW: HTTP 200 OK {"job_id": "...", "status": "COMPLETED", "s3_report_url": "https://..."}
    APIGW-->>Client: Respuesta 200 OK
```

---

## 4. Matriz de Componentes, Puertos y Adaptadores

| Componente | Capa | Responsabilidad Principal | Puertos / Contratos Asociados |
| :--- | :--- | :--- | :--- |
| **`start_research_handler`** | Presentación (`app/aws/`) | Handler Lambda para `POST /research`. Parsea payloads y llama al controlador. | AWS Lambda Event Bridge |
| **`get_research_status_handler`** | Presentación (`app/aws/`) | Handler Lambda para `GET /research/{id}`. Extrae path params y llama al controlador. | AWS Lambda Event Bridge |
| **`execute_research_worker_handler`**| Presentación (`app/aws/`) | Handler Lambda para ejecución de fondo del agente. | AWS Lambda Async Event |
| **`StartResearchController`** | Presentación (`app/controllers/`) | Orquestador CQRS del comando de inicio de investigación con decoradores de observabilidad. | `ICommandHandler`, `LoggingDecorator`, `MetricsDecorator` |
| **`GetResearchStatusController`** | Presentación (`app/controllers/`) | Orquestador CQRS de la consulta de estado con decoradores de observabilidad. | `IQueryHandler`, `LoggingDecorator`, `MetricsDecorator` |
| **`ExecuteResearchWorkerController`**| Presentación (`app/controllers/`) | Orquestador CQRS del comando de ejecución del worker con decoradores. | `ICommandHandler`, `LoggingDecorator`, `MetricsDecorator` |
| **`StartResearchUseCase`** | Aplicación (`context/research/`) | Pipeline en cadena para iniciar el trabajo e invocar el worker. | `IAsyncWorkerInvokerPort` |
| **`GetResearchStatusUseCase`** | Aplicación (`context/research/`) | Pipeline en cadena para validar y consultar almacenamiento de reportes. | `IReportStoragePort` |
| **`ExecuteResearchWorkerUseCase`** | Aplicación (`context/research/`) | Pipeline en cadena para coordinar razonamiento de IA y persistencia en S3. | `IResearchAgentPort`, `IReportStoragePort` |
| **`S3StorageAdapter`** | Infraestructura (`context/research/`) | Adaptador concreto de persistencia usando Amazon S3 SDK (`boto3`). | `IReportStoragePort` |
| **`LambdaInvokerAdapter`** | Infraestructura (`context/research/`) | Adaptador concreto para invocar Lambdas asíncronas (`boto3`). | `IAsyncWorkerInvokerPort` |
| **`BedrockAgentAdapter`** | Infraestructura (`context/research/`) | Adaptador concreto del agente ReAct (Strands SDK + Bedrock + Tavily). | `IResearchAgentPort` |
| **`PowertoolsAdapters`** | Infraestructura (`context/research/`) | Adaptadores de observabilidad estructurada (Logger, Metrics). | `ILoggerPort`, `IMetricsPort`, `LoggerService`, `MetricsService` |
| **`InfrastructureFactory`** | Infraestructura (`context/research/`) | Fábrica abstracta para ensamblaje manual de adaptadores. | `IInfrastructureFactory` |