import os
from aws_lambda_powertools import Logger, Tracer, Metrics

# Centralized AWS Lambda Powertools configuration
SERVICE_NAME = os.getenv("POWERTOOLS_SERVICE_NAME", "serverless-research-agent")
METRICS_NAMESPACE = os.getenv("POWERTOOLS_METRICS_NAMESPACE", "ResearchAgent")

logger = Logger(service=SERVICE_NAME)
tracer = Tracer(service=SERVICE_NAME)
metrics = Metrics(namespace=METRICS_NAMESPACE, service=SERVICE_NAME)

