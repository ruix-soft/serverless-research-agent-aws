# Serverless AI Research Agent on AWS

[![CI/CD Pipeline](https://github.com/ruix-soft/serverless-research-agent-aws/actions/workflows/pipeline.yml/badge.svg)](https://github.com/ruix-soft/serverless-research-agent-aws/actions/workflows/pipeline.yml)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![AWS SAM](https://img.shields.io/badge/AWS%20SAM-Serverless-orange.svg)](https://aws.amazon.com/serverless/sam/)
[![AWS Step Functions](https://img.shields.io/badge/AWS%20Step%20Functions-Orchestration-red.svg)](https://aws.amazon.com/step-functions/)
[![Amazon DynamoDB](https://img.shields.io/badge/Amazon%20DynamoDB-JobsTable%20%7C%20RateLimits-blueviolet.svg)](https://aws.amazon.com/dynamodb/)
[![Amazon Bedrock](https://img.shields.io/badge/Amazon%20Bedrock-Claude%20Sonnet-darkblue.svg)](https://aws.amazon.com/bedrock/)
[![OpenAPI 3.0](https://img.shields.io/badge/OpenAPI-3.0.3-brightgreen.svg)](docs/openapi.yaml)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal%20%7C%20DDD%20%7C%20CQRS-green.svg)](docs/architecture.md)
[![Tests](https://img.shields.io/badge/Tests-118%20Passing-brightgreen.svg)](tests/)

Agente autónomo de investigación profunda impulsado por Inteligencia Artificial y construido bajo una arquitectura **100% Serverless-First en AWS**. Utiliza el patrón **ReAct (Reasoning + Acting)** en **Amazon Bedrock**, el framework **Strands Agents SDK**, búsquedas web en tiempo real con **Tavily API**, orquestación distribuida resiliente con **AWS Step Functions**, persistencia de estado con **Amazon DynamoDB** y **Amazon S3**, y despliegues continuos automatizados (**CI/CD**) mediante **GitHub Actions** y **OpenID Connect (AWS OIDC)**.

El proyecto sigue rigurosamente la metodología de arquitectura de software diseñada por **Luis Ruiz** (formalizada bajo la especificación **`arch-core`**), la cual compila y refina años de experiencia en ingeniería de software y cloud computing: arquitectura estricta en **dos capas principales (`app/` y `context/`)**, Arquitectura Hexagonal (Ports & Adapters), Domain-Driven Design (DDD) táctico, Segregación de Comandos y Consultas (CQRS), **Cadena de Responsabilidad (Chain of Responsibility)** para la orquestación atómica de casos de uso, Value Objects para tipado e hidratación de primitivos, inyección manual de dependencias, observabilidad desacoplada con **AWS Lambda Powertools**, y manejo funcional de errores mediante **Railway-Oriented Programming (`Result[O, E]`)**.

---

## 🏛️ Arquitectura del Sistema

El agente resuelve las limitaciones de timeout y estados zombi mediante una **Solución Híbrida Enterprise (AWS Step Functions + DynamoDB + CQRS)**:

```mermaid
sequenceDiagram
    autonumber
    actor Client as Cliente / Frontend
    participant APIGW as Amazon API Gateway
    participant StartLambda as StartResearchFunction<br/>(POST /research)
    participant SFN as AWS Step Functions<br/>(ResearchStateMachine)
    participant JobsDB as DynamoDB (JobsTable)
    participant WorkerLambda as ExecuteResearchWorkerFunction<br/>(Background AI Agent)
    participant Bedrock as Amazon Bedrock<br/>(Claude + Strands SDK)
    participant Tavily as Tavily Web Search
    participant S3 as Amazon S3 Bucket<br/>(Reports Storage)
    participant StatusLambda as GetResearchStatusFunction<br/>(GET /research/{id})

    Note over Client, APIGW: 1. Inicio de Investigación Asíncrona (Comando CQRS)
    Client->>APIGW: POST /research {"topic": "AI in Healthcare"}
    APIGW->>StartLambda: Invoca Handler POST (Rate Limited)
    StartLambda->>SFN: Inicia State Machine (Async)
    StartLambda-->>Client: 202 Accepted {"job_id": "uuid-123", "status": "IN_PROGRESS", "status_url": "/research/uuid-123"}

    Note over SFN, S3: 2. Orquestación Resiliente de Fondo (Step Functions)
    SFN->>JobsDB: Direct SDK PutItem {pk: "JOB#uuid-123", status: "IN_PROGRESS"}
    SFN->>WorkerLambda: Invoca Worker con Retry (3 intentos) y Catch
    WorkerLambda->>Bedrock: Inicia ciclo ReAct con System Prompt
    loop Razonamiento y Búsqueda Web
        Bedrock->>Tavily: Ejecuta web_search(query)
        Tavily-->>Bedrock: Resultados y fuentes relevantes
    end
    Bedrock-->>WorkerLambda: Síntesis y Reporte en Markdown
    WorkerLambda->>S3: PutObject reports/uuid-123.md
    WorkerLambda-->>SFN: Retorna s3_key
    
    alt Éxito
        SFN->>JobsDB: Direct SDK UpdateItem {status: "COMPLETED", s3_key: "reports/uuid-123.md"}
    else Fallo / Timeout (Catch: States.ALL)
        SFN->>JobsDB: Direct SDK UpdateItem {status: "FAILED", error_message: "..."}
    end

    Note over Client, StatusLambda: 3. Consulta de Estado (Lectura CQRS <5ms)
    Client->>APIGW: GET /research/uuid-123
    APIGW->>StatusLambda: Invoca Handler GET (Rate Limited)
    StatusLambda->>JobsDB: GetItem pk="JOB#uuid-123"
    alt Si COMPLETED
        StatusLambda->>S3: Genera URL presignada regional (Válida por 1h)
        StatusLambda-->>Client: 200 OK {"status": "COMPLETED", "s3_report_url": "https://s3..."}
    else Si FAILED
        StatusLambda-->>Client: 200 OK {"status": "FAILED", "error": "Detalle del error"}
    else Si IN_PROGRESS
        StatusLambda-->>Client: 200 OK {"status": "IN_PROGRESS"}
    end
```

---

## 📂 Estructura del Proyecto (Arquitectura en Dos Capas)

La base de código está estructurada en dos capas macro con aislamiento estricto:

```
serverless-research-agent-aws/
├── .github/
│   └── workflows/
│       └── pipeline.yml                  # CI/CD Pipeline con GitHub Actions y AWS OIDC
│
├── src/
│   ├── app/                              # CAPA 1: PRESENTACIÓN Y ENTREGA
│   │   ├── aws/
│   │   │   ├── handlers/                 # Delivery Handlers delgados específicos de AWS Lambda
│   │   │   │   ├── start_research_handler.py
│   │   │   │   ├── get_research_status_handler.py
│   │   │   │   └── execute_research_worker_handler.py
│   │   │   ├── powertools.py             # Instancias singleton de Logger, Tracer y Metrics
│   │   │   └── response.py               # Mapeador de Result y DomainError a respuestas HTTP
│   │   └── controllers/                  # Controladores CQRS con decoradores
│   │       ├── base.py                   # Contratos ICommandHandler y IQueryHandler
│   │       ├── start_research_controller.py
│   │       ├── get_research_status_controller.py
│   │       ├── execute_research_worker_controller.py
│   │       └── decorators/               # Decoradores (LoggingDecorator, MetricsDecorator)
│   │
│   └── context/                          # CAPA 2: BOUNDED CONTEXTS & CORE DDD
│       ├── kit/                          # Kit de utilidades y bloques fundamentales reutilizables
│       │   ├── aggregate_root.py         # Base para Entidades y Aggregates de Dominio
│       │   ├── chain/                    # Motor de Chain of Responsibility (ChainBuilder, Step)
│       │   ├── command/                  # Abstracciones y decoradores para Comandos (CQRS)
│       │   ├── query/                    # Abstracciones y decoradores para Consultas (CQRS)
│       │   ├── criteria/                 # Patrón Criteria (Filtros, Ordenamiento, Paginación)
│       │   ├── dtos/                     # DTOs (Result, Optional, Either, Metadata)
│       │   ├── errors/                   # Jerarquía de DomainError (Validation, NotFound, RateLimit)
│       │   ├── service/                  # Contratos de servicios e interfaces abstractas
│       │   └── vo/                       # Value Objects (Uuid, Date, String, Number, Boolean)
│       │
│       └── research/                     # Bounded Context de Investigación
│           ├── domain/                   # Entidades, Puertos e interfaces del negocio
│           │   ├── entities/             # ResearchJob (AggregateRoot), ResearchJobStatus
│           │   └── ports.py              # IResearchJobRepository, IStateMachineInvokerPort, IReportStoragePort
│           ├── application/              # Casos de Uso estructurados como Pipelines de Pasos
│           │   ├── dtos/                 # DTOs inmutables de entrada y salida
│           │   └── use_cases/            # StartResearchUseCase, GetResearchStatusUseCase, ExecuteResearchWorkerUseCase
│           └── infrastructure/           # Adaptadores concretos y Ensamblaje Manual
│               ├── infrastructure_factory.py        # Fábrica abstracta de inyección de dependencias
│               ├── dynamodb_job_repository_adapter.py # Adaptador DynamoDB para ResearchJob
│               ├── step_functions_invoker_adapter.py # Adaptador de inicio en Step Functions
│               ├── dynamodb_rate_limiter_adapter.py # Adaptador de Rate Limiting atómico con TTL
│               ├── bedrock_agent_adapter.py         # Adaptador Strands + Amazon Bedrock
│               ├── s3_storage_adapter.py            # Adaptador de almacenamiento Amazon S3
│               ├── lambda_invoker_adapter.py        # Adaptador de invocación directa
│               ├── tavily_search_tool.py            # Tool de búsqueda web con Tavily API
│               └── powertools_adapters.py           # Adaptadores de observabilidad (Logger/Metrics)
│
├── infrastructure/
│   └── github-oidc-role.yaml             # CloudFormation: Proveedor OIDC e IAM Role para CI/CD
│
├── docs/                                 # DOCUMENTACIÓN TÉCNICA
│   ├── architecture.md                   # Especificación detallada de arquitectura y flujos
│   ├── openapi.yaml                      # Especificación OpenAPI 3.0 de los endpoints REST
│   └── adr/                              # Architecture Decision Records (ADRs)
│       ├── 0001-use-serverless-ai-agent-architecture.md
│       ├── 0002-async-agent-execution.md
│       ├── 0003-two-layer-clean-architecture-and-design-patterns.md
│       ├── 0004-distributed-rate-limiting-with-dynamodb.md
│       ├── 0005-hybrid-step-functions-and-dynamodb-orchestration.md
│       ├── 0006-enterprise-ci-cd-with-github-actions-and-aws-oidc.md
│       ├── 0007-end-to-end-distributed-tracing-and-observability-with-aws-xray.md
│       └── 0008-unified-finops-operational-and-ai-observability-dashboard.md
│
├── tests/                                # SUITE INTEGRAL DE PRUEBAS (118 Tests)
│   ├── test_controllers.py
│   ├── test_handlers.py
│   ├── test_decorators.py
│   ├── test_domain_result.py
│   ├── test_research_job_entity.py
│   ├── test_dynamodb_job_repository.py
│   ├── test_step_functions_invoker.py
│   ├── test_dynamodb_rate_limiter.py
│   └── test_kit_*.py                     # Tests unitarios del módulo kit
│
├── .flake8                               # Configuración de Linter PEP 8
├── template.yaml                         # Infraestructura como Código (AWS SAM Template)
└── README.md
```

---

## 🎯 Patrones de Diseño Implementados

1. **Arquitectura Hexagonal (Ports & Adapters):** Aislamiento absoluto de la lógica de negocio. Los casos de uso y el dominio no conocen los SDKs de AWS (`boto3`) ni los frameworks de presentación.
2. **Segregación de Responsabilidad de Comandos y Consultas (CQRS):** Separación limpia entre comandos que alteran estado (`CommandHandler`) y lecturas de datos ultrarrápidas (`QueryHandler`).
3. **Cadena de Responsabilidad (Chain of Responsibility):** Todos los casos de uso se ejecutan como un pipeline secuencial de pasos atómicos (`Step[I, O, C]`) que operan sobre un contexto compartido (`Context`).
4. **Trazabilidad Distribuida y Observabilidad Activa (AWS X-Ray + Powertools):** Trazabilidad de extremo a extremo propagando el `X-Amzn-Trace-Id` desde API Gateway hacia Lambdas y Step Functions, con subsegmentos automáticos para cada paso de la cadena (`StepTracingDecorator`), métricas en formato EMF (`CommandMetricsDecorator` / `QueryMetricsDecorator`) y logs estructurados (`StepLoggingDecorator`).
5. **Dashboard Unificado de FinOps & Operaciones (CloudWatch IaC):** Visualización centralizada de consumo de tokens en Amazon Bedrock, costos estimados en USD, latencias p90 y salud serverless.
6. **Patrón Saga / Orquestador Distribuido (AWS Step Functions):** Resiliencia garantizada con reintentos exponenciales automáticos y capturas de excepciones a nivel de infraestructura.
7. **Control de Tasa Distribuido (Rate Limiting Decorator):** Decoradores CQRS respaldados por DynamoDB y TTL para protección contra abusos y ataques *Denial of Wallet*.
8. **Autenticación sin Claves Estáticas (OpenID Connect - OIDC):** Despliegues seguros de CI/CD asumiendo roles temporales en AWS STS.
9. **Programación Orientada a Vías de Tren (Railway-Oriented Programming):** Todas las operaciones retornan instancias de `Result[O, DomainError]` eliminando excepciones no controladas en el flujo de negocio.

---

## 📊 Tablero Unificado de FinOps & Operaciones en Amazon CloudWatch

Desplegado automáticamente como Infraestructura como Código (`AWS::CloudWatch::Dashboard`), consolida 4 cuadrantes esenciales:

```mermaid
flowchart TD
    subgraph Dashboard ["🖥️ Amazon CloudWatch Dashboard: Serverless-Research-Agent"]
        direction TB
        
        subgraph S1 ["💰 1. SECCIÓN FINOPS & CONSUMO DE IA (Amazon Bedrock)"]
            W1["Tokens Entrada (Prompt) vs Salida (Generación)"]
            W2["Invocaciones de Claude Sonnet"]
            W3["Costo Acumulado Estimado ($ USD)"]
        end

        subgraph S2 ["📈 2. SECCIÓN CASOS DE USO Y NEGOCIO (Powertools EMF)"]
            W4["Invocaciones por Comando/Query (CQRS)"]
            W5["Latencia p90 por Caso de Uso (ms)"]
            W6["Errores de Dominio / Infraestructura"]
        end

        subgraph S3 ["⚡ 3. SECCIÓN SERVERLESS & ORQUESTACIÓN (Step Functions + Lambda + API GW)"]
            W7["Ejecuciones Exitosas vs Fallidas en Step Functions"]
            W8["Duración Promedio de Lambdas (ms)"]
            W9["Peticiones y Errores 4xx/5xx en API Gateway"]
        end

        subgraph S4 ["🛡️ 4. SECCIÓN RATE LIMITING & PERSISTENCIA (DynamoDB + S3)"]
            W10["Consumo RCU / WCU (JobsTable & RateLimitsTable)"]
            W11["Total de Reportes y Tamaño Almacenado en Amazon S3"]
        end
    end
```

---

## 🔍 Observabilidad Distribuida de Extremo a Extremo (AWS X-Ray & CloudWatch)

Toda la arquitectura cuenta con observabilidad activa integrada, permitiendo visualizar el flujo completo de ejecución desde la petición HTTP inicial hasta el razonamiento del LLM y la persistencia del reporte:

```mermaid
flowchart TD
    Client(["👤 Cliente (curl / Frontend)"]) -->|HTTP POST /research| APIGW["🌐 Amazon API Gateway\n(TracingEnabled: true)"]
    
    APIGW -->|Invocación con Trace-ID| LambdaStart["⚡ StartResearchFunction\n(Tracing: Active)"]
    
    subgraph S1 ["🔍 Subsegmentos X-Ray (StepTracingDecorator)"]
        LambdaStart --> StepV1["1️⃣ ValidateStartResearchStep"]
        StepV1 --> StepI1["2️⃣ InvokeStateMachineStep"]
        StepI1 --> StepB1["3️⃣ BuildStartResearchOutputStep"]
    end
    
    StepI1 -->|states:StartExecution| SFN["⚙️ AWS Step Functions\n(Tracing: Enabled: true)"]
    
    subgraph SFN_States ["🔄 Trazas de la Máquina de Estados"]
        SFN --> PutDDB["📥 PutJobInProgress (DynamoDB Direct SDK)"]
        PutDDB --> WorkerTask["🚀 ExecuteResearchWorkerTask"]
        WorkerTask --> CompleteDDB["💾 MarkJobAsCompleted (DynamoDB Direct SDK)"]
    end
    
    WorkerTask -->|Invocación Lambda con Trace Context| WorkerLambda["⚡ ExecuteResearchWorkerFunction\n(Tracing: Active)"]
    
    subgraph S2 ["🔍 Subsegmentos X-Ray del Worker (StepTracingDecorator)"]
        WorkerLambda --> StepWV["1️⃣ ValidateWorkerPayloadStep"]
        StepWV --> StepWR["2️⃣ RunAgentReasoningStep\n(Bedrock AI + Tavily Search)"]
        StepWR --> StepWP["3️⃣ PersistReportStorageStep\n(Amazon S3 PutObject)"]
        StepWP --> StepWB["4️⃣ BuildWorkerOutputStep"]
    end
    
    StepWR -.-> Bedrock["🧠 Amazon Bedrock (Inferencia LLM)"]
    StepWR -.-> Tavily["🌐 Tavily Web Search API"]
    StepWP -.-> S3Bucket["📦 Amazon S3 (Reports Bucket)"]
```

---

## 🔒 CI/CD & DevSecOps con AWS OIDC

El despliegue a AWS está 100% automatizado mediante **GitHub Actions** usando **OpenID Connect (OIDC)**, eliminando la necesidad de almacenar `AWS_ACCESS_KEY_ID` o secretos estáticos en GitHub.

### Aprovisionamiento Inicial del Rol OIDC en AWS

Ejecuta el siguiente comando para desplegar la plantilla CloudFormation del rol OIDC:

```bash
aws cloudformation deploy \
  --template-file infrastructure/github-oidc-role.yaml \
  --stack-name serverless-research-agent-ci-role \
  --parameter-overrides GitHubOrg=ruix-soft RepositoryName=serverless-research-agent-aws \
  --capabilities CAPABILITY_NAMED_IAM \
  --region mx-central-1
```

### Configuración en GitHub Actions

En tu repositorio de GitHub (**Settings $\rightarrow$ Secrets and variables $\rightarrow$ Actions**):
1. **`AWS_ROLE_ARN`**: `arn:aws:iam::<ACCOUNT_ID>:role/GitHubActionsServerlessResearchAgentDeployRole`
2. **`AWS_REGION`**: `mx-central-1`

---

## 🚀 Despliegue Manual en AWS (SAM CLI)

### Prerrequisitos
1. [AWS CLI](https://aws.amazon.com/cli/) y [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) instalados y configurados con credenciales de AWS.
2. [Tavily API Key](https://tavily.com/) almacenada en AWS Systems Manager Parameter Store:
   ```bash
   aws ssm put-parameter \
     --name "/serverless-research-agent/tavily-api-key" \
     --type "SecureString" \
     --value "tvly-TU_API_KEY_AQUI" \
     --region mx-central-1
   ```

### Pasos de Despliegue

```bash
# 1. Validar la plantilla SAM
sam validate --lint

# 2. Construir los artefactos
sam build

# 3. Desplegar en AWS
sam deploy --guided
```

---

## 📚 Documentación Técnica & ADRs

- 📐 [**Arquitectura Detallada y Diagramas de Secuencia**](docs/architecture.md)
- 📑 [**Especificación OpenAPI 3.0 (Contrato REST)**](docs/openapi.yaml)
- 🏛️ [**ADR 0001:** Elección de Arquitectura Serverless-First para el Agente de Investigación](docs/adr/0001-use-serverless-ai-agent-architecture.md)
- 🏛️ [**ADR 0002:** Patrón de Ejecución Asíncrona para Agentes de IA en AWS](docs/adr/0002-async-agent-execution.md)
- 🏛️ [**ADR 0003:** Arquitectura en Dos Capas e Implementación de Patrones de Diseño](docs/adr/0003-two-layer-clean-architecture-and-design-patterns.md)
- 🏛️ [**ADR 0004:** Control de Tasa Distribuido (Rate Limiting) con Amazon DynamoDB y Decoradores CQRS](docs/adr/0004-distributed-rate-limiting-with-dynamodb.md)
- 🏛️ [**ADR 0005:** Solución Híbrida: Orquestación Resiliente con AWS Step Functions y Persistencia en DynamoDB](docs/adr/0005-hybrid-step-functions-and-dynamodb-orchestration.md)
- 🏛️ [**ADR 0006:** CI/CD Enterprise con GitHub Actions y Autenticación OIDC (Zero Static Secrets)](docs/adr/0006-enterprise-ci-cd-with-github-actions-and-aws-oidc.md)
- 🏛️ [**ADR 0007:** Trazabilidad Distribuida de Extremo a Extremo con AWS X-Ray y Decoradores de Cadena](docs/adr/0007-end-to-end-distributed-tracing-and-observability-with-aws-xray.md)
- 🏛️ [**ADR 0008:** Tablero Unificado de FinOps, Operaciones y Observabilidad de IA en Amazon CloudWatch](docs/adr/0008-unified-finops-operational-and-ai-observability-dashboard.md)
