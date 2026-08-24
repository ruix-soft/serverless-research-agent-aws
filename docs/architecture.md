# Arquitectura del Agente Investigador Serverless (Metodología Luis Ruiz)

Este proyecto implementa la metodología y filosofía arquitectónica diseñada y refinada por **Luis Ruiz** (estandarizada bajo la especificación **`arch-core`**), combinando una arquitectura **Serverless-First en AWS** con principios rigurosos de **Arquitectura Hexagonal (Ports & Adapters)**, **Domain-Driven Design (DDD)** táctico, **Segregación de Comandos y Consultas (CQRS)**, orquestación atómica mediante **Cadena de Responsabilidad (Chain of Responsibility)**, control de tasa distribuido (**Rate Limiting con DynamoDB**) y orquestación distribuida resiliente (**AWS Step Functions + DynamoDB JobsTable**).

---

## 1. Diagrama General de la Solución

```mermaid
flowchart TB
    subgraph ClientLayer [Clientes / Consumidores]
        User([Usuario / Frontend / CI-CD])
    end

    subgraph AWSCloud [AWS Serverless Infrastructure]
        APIGW[Amazon API Gateway REST API]

        subgraph LambdaIngress [Capa de Ingesta y Consulta]
            StartFn["StartResearchFunction<br/>(POST /research)"]
            StatusFn["GetResearchStatusFunction<br/>(GET /research/{job_id})"]
        end

        subgraph OrchestrationLayer [Orquestación Distribuida]
            SFN["AWS Step Functions<br/>(ResearchStateMachine)"]
            WorkerFn["ExecuteResearchWorkerFunction<br/>(Background AI Agent)"]
        end

        subgraph PersistenceLayer [Almacenamiento y Estado]
            RateLimitsDB[(DynamoDB: RateLimitsTable<br/>Control de Tasa con TTL)]
            JobsDB[(DynamoDB: JobsTable<br/>Ciclo de Vida de Trabajos con TTL)]
            S3Bucket[(Amazon S3 Bucket<br/>Reportes Markdown)]
        end

        subgraph ExternalServices [Servicios Gestionados e IA]
            Bedrock[Amazon Bedrock<br/>Claude Sonnet 4.5]
            Tavily[Tavily Search API<br/>Búsqueda Web]
        end
    end

    User -->|1. POST /research| APIGW
    APIGW -->|Enruta POST| StartFn
    StartFn <-->|2. Evalúa Rate Limit| RateLimitsDB
    StartFn -->|3. Inicia State Machine| SFN
    StartFn -->>|4. 202 Accepted {job_id}| User

    SFN -->|5. Direct SDK: PutItem IN_PROGRESS| JobsDB
    SFN -->|6. Invoca Worker con Retry/Catch| WorkerFn
    WorkerFn -->|7. Razonamiento ReAct| Bedrock
    Bedrock <-->|8. Tool Web Search| Tavily
    WorkerFn -->|9. Guarda reports/{job_id}.md| S3Bucket
    WorkerFn -->>|10. Retorna s3_key| SFN
    SFN -->|11A. Direct SDK Éxito: UpdateItem COMPLETED| JobsDB
    SFN -->|11B. Direct SDK Fallo: UpdateItem FAILED| JobsDB

    User -->|12. GET /research/{job_id}| APIGW
    APIGW -->|Enruta GET| StatusFn
    StatusFn <-->|13. Evalúa Rate Limit| RateLimitsDB
    StatusFn -->|14. Consulta estado (<5ms)| JobsDB
    StatusFn -->|15. Si COMPLETED: Genera Presigned URL| S3Bucket
    StatusFn -->>|16. 200 OK {status, s3_report_url/error}| User
```

---

## 2. Macro-Separación de Capas: Metodología Arquitectónica Luis Ruiz (`arch-core`)

La estructura del código fuente implementa la metodología y filosofía de diseño desarrollada por **Luis Ruiz**, la cual establece una separación estricta en dos capas fundamentales con reglas de dependencia unidireccionales:

```mermaid
graph TD
    subgraph AppLayer ["Capa 1: Presentación y Entrega (src/app/)"]
        Handlers["Delivery Handlers (app/aws/handlers/)<br/>- start_research_handler<br/>- get_research_status_handler<br/>- execute_research_worker_handler"]
        Controllers["Controllers (app/controllers/)<br/>- StartResearchController<br/>- GetResearchStatusController<br/>- ExecuteResearchWorkerController"]
        Decorators["CQRS & Observability Decorators<br/>- CommandRateLimitDecorator<br/>- QueryRateLimitDecorator<br/>- LoggingDecorator<br/>- MetricsDecorator"]
    end

    subgraph ContextLayer ["Capa 2: Bounded Context & Core DDD (src/context/)"]
        subgraph KitModule ["Kit Reutilizable (src/context/kit/)"]
            Aggregate["AggregateRoot (Base Domain Model)"]
            Chain["Chain of Responsibility (ChainBuilder, Step)"]
            CQRS["CQRS Abstractions (Command, Query)"]
            DTOs["DTOs (Result, Optional, Either, Metadata)"]
            Errors["Domain Errors (DomainError, ValidationError, NotFoundError, RateLimitError)"]
            VOs["Value Objects (Uuid, Date, String, Number, Boolean)"]
            Services["Service Contracts (RateLimiterService, LoggerService, etc.)"]
        end

        subgraph ResearchContext ["Bounded Context: Research (src/context/research/)"]
            Entities["Domain Entities & Aggregates<br/>- ResearchJob (AggregateRoot)<br/>- ResearchJobStatus (Enum)"]
            UseCases["Application: Use Cases & Pipelines<br/>- StartResearchUseCase<br/>- GetResearchStatusUseCase<br/>- ExecuteResearchWorkerUseCase"]
            DomainPorts["Domain: Ports & Contracts<br/>- IResearchJobRepository<br/>- IStateMachineInvokerPort<br/>- IReportStoragePort<br/>- IResearchAgentPort<br/>- IInfrastructureFactory"]
            InfraFactory["Infrastructure: Factory & Adapters<br/>- InfrastructureFactory<br/>- DynamoDBJobRepositoryAdapter<br/>- StepFunctionsInvokerAdapter<br/>- DynamoDBRateLimiterAdapter<br/>- S3StorageAdapter<br/>- BedrockAgentAdapter<br/>- PowertoolsAdapters"]
        end
    end

    Handlers --> Controllers
    Controllers --> Decorators
    Controllers --> InfraFactory
    Controllers --> CQRS
    Decorators --> CQRS
    Decorators --> Services
    Entities --> Aggregate
    Entities --> VOs
    UseCases --> Chain
    UseCases --> DTOs
    UseCases --> Errors
    UseCases --> Entities
    UseCases --> DomainPorts
    InfraFactory --> DomainPorts
    InfraFactory --> Services
```

---

## 3. Flujos Detallados de los Servicios

### Flujo 1: Inicio de Investigación Asíncrona (`POST /research`)

```mermaid
sequenceDiagram
    autonumber
    actor Client as Cliente HTTP
    participant APIGW as API Gateway
    participant Handler as start_research_handler
    participant Controller as StartResearchController
    participant RateDec as CommandRateLimitDecorator
    participant DynamoRL as DynamoDBRateLimiterAdapter (RateLimitsTable)
    participant UseCase as StartResearchUseCase (Chain)
    participant Step1 as ValidateStartResearchStep
    participant Step2 as InvokeStateMachineStep
    participant Step3 as BuildStartResearchOutputStep
    participant SFNAdapter as StepFunctionsInvokerAdapter
    participant SFN as AWS Step Functions

    Client->>APIGW: POST /research {"topic": "AI in Healthcare", "depth": "detailed"}
    APIGW->>Handler: Invoca lambda_handler(event, context)
    Note over Handler: Parsea JSON, extrae IP/User-Agent en Metadata y crea StartResearchInputDTO
    Handler->>Controller: run(input_dto, ctx=metadata)
    Controller->>RateDec: execute(input_dto, ctx=metadata)

    RateDec->>DynamoRL: allow("start_research:{ip}", limit=5, window_ms=60000)
    
    alt Si se excede el Rate Limit (>5 peticiones/minuto)
        DynamoRL-->>RateDec: False
        RateDec-->>Handler: Result.err(RateLimitError)
        Handler-->>Client: HTTP 429 Too Many Requests
    else Si la petición está permitida
        DynamoRL-->>RateDec: True
        RateDec->>UseCase: execute(input_dto, ctx)
        
        rect rgb(240, 248, 255)
            Note over UseCase: Pipeline Chain of Responsibility
            UseCase->>Step1: execute(input_dto, shared_context)
            Note over Step1: Valida tópico y genera job_id (UUID)
            Step1-->>UseCase: Result.ok(None)

            UseCase->>Step2: execute(input_dto, shared_context)
            Step2->>SFNAdapter: start_execution(job_id, topic)
            SFNAdapter->>SFN: states:StartExecution (Asíncrono)
            SFNAdapter-->>Step2: Retorno inmediato
            Step2-->>UseCase: Result.ok(None)

            UseCase->>Step3: execute(input_dto, shared_context)
            Note over Step3: Construye StartResearchOutputDTO (status="IN_PROGRESS")
            Step3-->>UseCase: Result.ok(output_dto)
        end

        UseCase-->>Controller: Result.ok(output_dto)
        Controller-->>Handler: Result.ok(output_dto)
        Handler->>APIGW: HTTP 202 Accepted {"job_id": "...", "status": "IN_PROGRESS", "status_url": "/research/{id}"}
        APIGW-->>Client: Respuesta 202 Accepted
    end
```

---

### Flujo 2: Orquestación Resiliente de Fondo (`ResearchStateMachine`)

```mermaid
sequenceDiagram
    autonumber
    participant SFN as Step Functions State Machine
    participant JobsDB as DynamoDB (JobsTable)
    participant Worker as ExecuteResearchWorker Lambda
    participant Agent as BedrockAgentAdapter (Claude 4.5 + Tavily)
    participant S3 as Amazon S3

    Note over SFN: Inicio de Ejecución con payload {job_id, topic}
    SFN->>JobsDB: 1. Direct SDK PutItem {pk: "JOB#id", status: "IN_PROGRESS", ttl: 7 días}
    
    rect rgb(240, 248, 255)
        Note over SFN, Worker: 2. Invocación de Lambda con Retry (3 intentos) y Catch
        SFN->>Worker: Invoca ExecuteResearchWorkerFunction
        Worker->>Agent: execute_research(topic)
        loop Ciclo ReAct
            Agent->>Agent: Razonamiento
            Agent->>Agent: Tavily Search
        end
        Agent-->>Worker: Markdown Report
        Worker->>S3: upload_report(job_id, content) -> reports/{id}.md
        Worker-->>SFN: {"status": "SUCCESS", "s3_key": "reports/{id}.md"}
    end

    alt Si el Worker finaliza con ÉXITO
        SFN->>JobsDB: 3A. Direct SDK UpdateItem {status: "COMPLETED", s3_key: "reports/{id}.md"}
    else Si el Worker falla tras 3 reintentos (Catch: States.ALL)
        Note over SFN: Atrapa el error y desvía a MarkJobAsFailed
        SFN->>JobsDB: 3B. Direct SDK UpdateItem {status: "FAILED", error_message: "..."}
    end
```

---

### Flujo 3: Consulta de Estado y Descarga (`GET /research/{job_id}`)

```mermaid
sequenceDiagram
    autonumber
    actor Client as Cliente HTTP
    participant APIGW as API Gateway
    participant Handler as get_research_status_handler
    participant Controller as GetResearchStatusController
    participant RateDec as QueryRateLimitDecorator
    participant UseCase as GetResearchStatusUseCase (Chain)
    participant Repo as DynamoDBJobRepositoryAdapter (JobsTable)
    participant S3 as S3StorageAdapter (Amazon S3)

    Client->>APIGW: GET /research/{job_id}
    APIGW->>Handler: Invoca lambda_handler
    Handler->>Controller: run(input_dto, ctx=metadata)
    Controller->>RateDec: execute(input_dto, ctx=metadata)
    RateDec->>UseCase: execute(input_dto, ctx)

    rect rgb(240, 248, 255)
        Note over UseCase: Pipeline Chain of Responsibility
        UseCase->>Repo: find_by_id(job_id)
        Repo-->>UseCase: KitOptional[ResearchJob]
        
        alt Si el trabajo NO existe en DynamoDB
            UseCase-->>Controller: Result.err(NotFoundError)
            Controller-->>Handler: Result.err(NotFoundError)
            Handler-->>Client: HTTP 404 Not Found
        else Si el trabajo EXISTE
            alt status == "COMPLETED"
                UseCase->>S3: generate_presigned_url(s3_key, expiration=3600)
                S3-->>UseCase: https://s3.amazonaws.com/...
                UseCase-->>Handler: Result.ok(status="COMPLETED", s3_report_url=url)
                Handler-->>Client: HTTP 200 OK {"status": "COMPLETED", "s3_report_url": "..."}
            else status == "FAILED"
                UseCase-->>Handler: Result.ok(status="FAILED", error="...")
                Handler-->>Client: HTTP 200 OK {"status": "FAILED", "error": "..."}
            else status == "IN_PROGRESS"
                UseCase-->>Handler: Result.ok(status="IN_PROGRESS", message="En progreso")
                Handler-->>Client: HTTP 200 OK {"status": "IN_PROGRESS"}
            end
        end
    end
```

---

## 4. Matriz de Componentes, Puertos y Adaptadores

| Componente | Capa | Responsabilidad Principal | Puertos / Contratos Asociados |
| :--- | :--- | :--- | :--- |
| **`ResearchJob`** | Dominio (`context/research/`) | Aggregate Root que modela el ciclo de vida del trabajo (`IN_PROGRESS`, `COMPLETED`, `FAILED`). | `AggregateRoot`, `Uuid`, `StringVO`, `DateVO` |
| **`start_research_handler`** | Presentación (`app/aws/`) | Handler Lambda para `POST /research`. Inicia el comando asíncrono. | AWS Lambda Event Bridge |
| **`get_research_status_handler`** | Presentación (`app/aws/`) | Handler Lambda para `GET /research/{id}`. Consulta estado en DynamoDB. | AWS Lambda Event Bridge |
| **`execute_research_worker_handler`**| Presentación (`app/aws/`) | Handler Lambda para ejecución de fondo del agente ReAct. | AWS Step Functions Task |
| **`StartResearchController`** | Presentación (`app/controllers/`) | Orquestador CQRS del comando con Rate Limiting (`CommandRateLimitDecorator`) y Step Functions. | `ICommandHandler`, `RateLimiterService`, `IStateMachineInvokerPort` |
| **`GetResearchStatusController`** | Presentación (`app/controllers/`) | Orquestador CQRS de la consulta con Rate Limiting (`QueryRateLimitDecorator`) y repositorio. | `IQueryHandler`, `RateLimiterService`, `IResearchJobRepository` |
| **`ExecuteResearchWorkerController`**| Presentación (`app/controllers/`) | Orquestador CQRS del comando de ejecución del worker. | `ICommandHandler`, `LoggingDecorator`, `MetricsDecorator` |
| **`StartResearchUseCase`** | Aplicación (`context/research/`) | Pipeline en cadena para iniciar el trabajo e invocar la máquina de estados. | `IStateMachineInvokerPort` |
| **`GetResearchStatusUseCase`** | Aplicación (`context/research/`) | Pipeline en cadena para consultar estado en DynamoDB y generar URL presignada. | `IResearchJobRepository`, `IReportStoragePort` |
| **`ExecuteResearchWorkerUseCase`** | Aplicación (`context/research/`) | Pipeline en cadena para coordinar razonamiento de IA y persistencia en S3. | `IResearchAgentPort`, `IReportStoragePort` |
| **`DynamoDBJobRepositoryAdapter`**| Infraestructura (`context/research/`) | Adaptador concreto para persistir y consultar `ResearchJob` en DynamoDB. | `IResearchJobRepository` |
| **`StepFunctionsInvokerAdapter`** | Infraestructura (`context/research/`) | Adaptador concreto para iniciar ejecuciones en AWS Step Functions. | `IStateMachineInvokerPort` |
| **`DynamoDBRateLimiterAdapter`**| Infraestructura (`context/research/`) | Adaptador concreto de Rate Limiting atómico con TTL en Amazon DynamoDB. | `RateLimiterService` (`context/kit/`) |
| **`S3StorageAdapter`** | Infraestructura (`context/research/`) | Adaptador concreto de persistencia usando Amazon S3 SDK (`boto3`). | `IReportStoragePort` |
| **`BedrockAgentAdapter`** | Infraestructura (`context/research/`) | Adaptador concreto del agente ReAct (Strands SDK + Bedrock + Tavily). | `IResearchAgentPort` |
| **`InfrastructureFactory`** | Infraestructura (`context/research/`) | Fábrica abstracta para ensamblaje manual de todos los adaptadores. | `IInfrastructureFactory` |