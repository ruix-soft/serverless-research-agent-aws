import os
from strands import Agent
from tools import web_search

SYSTEM_PROMPT = """Eres un Agente Investigador Senior especializado en análisis tecnológico y cloud computing.
Tu objetivo es realizar investigaciones profundas, objetivas y bien estructuradas sobre el tema solicitado.
Instrucciones:
1. Utiliza la herramienta `web_search` para obtener datos actualizados e hipervínculos relevantes.
2. Analiza críticamente los resultados y sintetiza la información.
3. Estructura la respuesta final en formato Markdown limpio, incluyendo secciones claras, conclusiones y referencias a las fuentes.
"""

class ResearchAgent:
    def __init__(self, model_id: str = None):
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.agent = Agent(
            tools=[web_search],
            system_prompt=SYSTEM_PROMPT,
            model=self.model_id
        )

    def run(self, topic: str) -> str:
        prompt = f"Realiza una investigación completa sobre el siguiente tema: {topic}"
        result = self.agent(prompt)
        return str(result)