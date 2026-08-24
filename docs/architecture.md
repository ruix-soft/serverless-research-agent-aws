# Arquitectura del Agente Investigador Serverless

```mermaid
sequenceDiagram
    autonumber
    Client->>API Gateway: POST /research (Payload JSON)
    API Gateway->>AWS Lambda: Trigger Handler (Python Strands Agent)
    AWS Lambda->>Bedrock: Invocación LLM (Claude 3.5 Sonnet / ReAct Loop)
    Bedrock-->>AWS Lambda: Solicitud de herramienta (Tool Call: web_search)
    AWS Lambda->>Search API: Búsqueda Web (Tavily API / Brave)
    Search API-->>AWS Lambda: Resultados web sintetizados
    AWS Lambda->>Bedrock: Evaluación y síntesis final
    Bedrock-->>AWS Lambda: Artefacto final generado
    AWS Lambda->>Amazon S3: Almacenamiento de reporte (.md)
    AWS Lambda->>Amazon S3: Generación de Presigned URL
    AWS Lambda-->>API Gateway: 200 OK (con Presigned URL & Metadata)
    API Gateway-->>Client: Respuesta JSON final