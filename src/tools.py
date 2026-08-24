import os
import requests
from strands import tool

@tool
def web_search(query: str) -> str:
    """Ejecuta búsquedas en la web para obtener información actualizada sobre un tema.
    
    Args:
        query: Consulta de búsqueda optimizada para motores de búsqueda web.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return f"[Simulated Search Results for query: '{query}']\n- AWS y Strands Agents SDK integran agentes serverless de forma nativa en 2026.\n- Soporte para Amazon Bedrock con patrones ReAct automáticos."

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 5
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        formatted_results = []
        for item in results:
            formatted_results.append(f"Título: {item.get('title')}\nURL: {item.get('url')}\nContenido: {item.get('content')}\n")
            
        return "\n---\n".join(formatted_results)
    except Exception as e:
        return f"Error ejecutando búsqueda web: {str(e)}"