import os
from context.research.domain.ports import IResearchAgentPort

SYSTEM_PROMPT = """Eres un Agente Investigador Senior especializado en análisis tecnológico y cloud computing.
Tu objetivo es realizar investigaciones profundas, objetivas y bien estructuradas sobre el tema solicitado.

REGLAS OBLIGATORIAS DE BÚSQUEDA:
1. Realiza como MÁXIMO 2 búsquedas web con `web_search`. No hagas búsquedas iterativas adicionales.
2. Tras la primera o segunda búsqueda, sintetiza inmediatamente los datos obtenidos.
3. Estructura la respuesta final en formato Markdown limpio, incluyendo conclusiones y referencias a las fuentes.
"""

class BedrockAgentAdapter(IResearchAgentPort):
    """Adapter wrapping Strands Agent with Amazon Bedrock and Tavily Web Search."""
    def __init__(self, model_id: str = None):
        self.model_id = model_id or os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-sonnet-4-5-20250929-v1:0")

    def execute_research(self, topic: str) -> str:
        try:
            from strands import Agent
            from context.research.infrastructure.tavily_search_tool import web_search

            agent = Agent(
                tools=[web_search],
                system_prompt=SYSTEM_PROMPT,
                model=self.model_id
            )
            prompt = f"Realiza una investigación completa sobre el siguiente tema: {topic}"
            result = agent(prompt)
            return str(result)
        except Exception as e:
            raise RuntimeError(f"Error en la ejecución del agente de investigación Strands/Bedrock: {str(e)}")

