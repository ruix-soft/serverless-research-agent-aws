import json
import os
import uuid
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from agent import ResearchAgent

AWS_REGION = os.getenv("AWS_REGION", "mx-central-1")

# Forzar al cliente S3 a firmar usando el endpoint regional
s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    config=Config(
        signature_version='s3v4',
        s3={'addressing_style': 'virtual'}
    )
)
lambda_client = boto3.client('lambda', region_name=AWS_REGION)

BUCKET_NAME = os.getenv("REPORTS_BUCKET_NAME")
FUNCTION_NAME = os.getenv("AWS_LAMBDA_FUNCTION_NAME")

def lambda_handler(event, context):
    # Detectar si es una invocación asíncrona de fondo (Worker)
    if event.get("source") == "async_worker":
        return execute_research_worker(event)

    http_method = event.get("httpMethod")
    path_parameters = event.get("pathParameters") or {}

    # GET /research/{job_id} -> Consultar estado / URL
    if http_method == "GET" and "job_id" in path_parameters:
        return get_job_status(path_parameters["job_id"])

    # POST /research -> Iniciar tarea asíncrona
    if http_method == "POST":
        return start_async_research(event)

    return build_response(400, {"error": "Ruta o método no soportado"})

def start_async_research(event):
    body = json.loads(event.get("body", "{}"))
    topic = body.get("topic")

    if not topic:
        return build_response(400, {"error": "El campo 'topic' es obligatorio."})

    job_id = str(uuid.uuid4())
    payload = {
        "source": "async_worker",
        "job_id": job_id,
        "topic": topic
    }

    # Disparar ejecución de fondo en Lambda sin esperar respuesta
    lambda_client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )

    return build_response(202, {
        "job_id": job_id,
        "status": "IN_PROGRESS",
        "message": "Investigación iniciada. Consulta el estado en el endpoint proporcionado.",
        "status_url": f"/research/{job_id}"
    })

def execute_research_worker(event):
    job_id = event["job_id"]
    topic = event["topic"]

    agent = ResearchAgent()
    report_content = agent.run(topic)

    s3_key = f"reports/{job_id}.md"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=report_content,
        ContentType="text/markdown"
    )
    return {"status": "SUCCESS"}

def get_job_status(job_id):
    s3_key = f"reports/{job_id}.md"
    try:
        s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600
        )
        return build_response(200, {
            "job_id": job_id,
            "status": "COMPLETED",
            "s3_report_url": presigned_url
        })
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return build_response(200, {
                "job_id": job_id,
                "status": "IN_PROGRESS",
                "message": "El reporte aún se está generando."
            })
        return build_response(500, {"error": str(e)})

def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }