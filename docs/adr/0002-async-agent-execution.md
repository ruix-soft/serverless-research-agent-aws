# 2. Patrón de Ejecución Asíncrona para Agentes de IA en AWS

* **Estatus:** Aceptado
* **Fecha:** 2026-08-24

## Contexto
El flujo ReAct del Agente de Investigación (razonamiento en Amazon Bedrock + búsquedas en Tavily API) requiere ~60 segundos para generar el reporte final en Markdown. AWS API Gateway (REST API) impone un límite duro de 29 segundos para ejecuciones sincrónicas, lo que provocaba errores `Endpoint request timed out` (HTTP 504) hacia el cliente, a pesar de que la función Lambda terminaba exitosamente en segundo plano.

## Decisión
Implementar un patrón asíncrono desencadenado por eventos (*Event-Driven Poll Pattern*):

1. **Iniciación (`POST /research`):** Valida los parámetros, genera un `job_id` (UUID), invoca la función Lambda de manera asíncrona (`InvocationType: Event`) y retorna una respuesta `202 Accepted` en <1 segundo con la URL para consultar el estado.
2. **Procesamiento de Fondo:** La Lambda Worker ejecuta el motor del agente de IA sin restricciones de timeout HTTP y guarda el reporte final en Amazon S3 bajo la ruta `reports/{job_id}.md`.
3. **Consulta de Estado (`GET /research/{job_id}`):** Valida la existencia del objeto en S3. Si el archivo existe, retorna HTTP `200 OK` con una URL presignada regional de S3 válida por 1 hora.

## Consecuencias
* **Positivas:**
  * Se elimina la restricción de timeout de 29s de API Gateway.
  * Permite escalar el agente para tareas pesadas o múltiples iteraciones de LLM.
  * Mantiene la seguridad del bucket S3 restringido mediante URLs presignadas temporales.
* **Negativas:**
  * Requiere que el cliente realice *polling* HTTP para verificar la finalización del trabajo.