# 1. Elección de Arquitectura Serverless-First para el Agente de Investigación de IA

* **Estatus:** Aceptado
* **Fecha:** 2026-08-24

## Contexto
Se requiere construir una solución automatizada capaz de orquestar investigaciones técnicas profundas en la web, procesar la información mediante Modelos de Lenguaje Avanzados (LLMs) y generar reportes estructurados en Markdown sin incurrir en costos de infraestructura fija ni mantenimiento de servidores dedicados.

## Decisión
Adoptar un stack 100% Serverless-First en AWS desplegado mediante **AWS SAM (Serverless Application Model)**:

1. **Cómputo:** AWS Lambda con runtime Python 3.12 para garantizar ejecución ligera, pago por uso exacto y costo cero en reposo.
2. **Motor de IA (LLM):** Amazon Bedrock invocando perfiles de inferencia de Anthropic Claude (Sonnet/Haiku) para la orquestación del ciclo ReAct (Reasoning + Acting).
3. **Framework de Agente:** Strands Agents SDK para la gestión del prompt de sistema y la abstracción de invocación de herramientas (*tools*).
4. **Búsqueda Web:** Tavily API integrada como *tool* nativa del agente para obtener datos actualizados de internet.
5. **Almacenamiento:** Amazon S3 para la persistencia de los reportes generados.
6. **API Layer:** Amazon API Gateway (REST API) como punto de entrada de las peticiones.

## Consecuencias
* **Positivas:**
  * Escalabilidad automática y arquitectura orientada a eventos.
  * Mantenimiento de infraestructura reducido al mínimo (Infrastructure as Code con SAM).
  * Optimización de costos: solo se paga por tiempo de ejecución de Lambda, tokens de Bedrock y peticiones a Tavily.
* **Negativas:**
  * Dependencia del límite de timeout de 29s de API Gateway (solucionado en el ADR 0002).
  * Variabilidad en la latencia de respuesta según el tiempo de procesamiento del LLM.