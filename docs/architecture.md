# Arquitectura del Agente Investigador Serverless

```mermaid
sequenceDiagram
    autonumber
    Client->>API Gateway: POST /research
    API Gateway->>Lambda Router: Invoca sincrónicamente
    Lambda Router->>Lambda Worker: Invoca asíncronamente (InvocationType='Event')
    Lambda Router-->>Client: 202 Accepted {"job_id": "123", "status": "IN_PROGRESS"}
    Note over Lambda Worker: Ejecuta Bedrock + Tavily (60s)
    Lambda Worker->>Amazon S3: Guarda /reports/123.md
    Client->>API Gateway: GET /research/123
    API Gateway->>Lambda Router: Verifica existencia en S3
    Lambda Router-->>Client: 200 OK {"status": "COMPLETED", "download_url": "..."}