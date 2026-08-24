import json
import uuid
import time
from agent import ResearchAgent

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

        agent = ResearchAgent()
        report_md = agent.run(topic)

        execution_time = round(time.time() - start_time, 2)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "job_id": job_id,
                "status": "COMPLETED",
                "topic": topic,
                "report_content": report_md,
                "execution_time_seconds": execution_time
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }