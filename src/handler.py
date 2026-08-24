import json
import uuid
import time
from agent import ResearchAgent
from storage import S3ReportStorage

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        topic = body.get("topic")

        if not topic:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "El campo 'topic' es obligatorio."})
            }

        job_id = f"req-{uuid.uuid4()}"
        start_time = time.time()

        # 1. Bucle de razonamiento con Strands Agents SDK
        agent = ResearchAgent()
        report_md = agent.run(topic)

        # 2. Guardar archivo en S3 y firmar enlace de descarga (expira en 1 hr)
        storage = S3ReportStorage()
        object_key = storage.upload_report(job_id=job_id, content=report_md, extension="md")
        presigned_url = storage.generate_presigned_url(object_key=object_key, expiration_seconds=3600)

        execution_time = round(time.time() - start_time, 2)

        # 3. Retorno estandarizado de la API
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "job_id": job_id,
                "status": "COMPLETED",
                "topic": topic,
                "s3_report_url": presigned_url,
                "execution_time_seconds": execution_time
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }