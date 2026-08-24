from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class StartResearchInputDTO:
    topic: str
    depth: str = "detailed"
    format: str = "markdown"
    search_limit: int = 5

@dataclass(frozen=True)
class StartResearchOutputDTO:
    job_id: str
    status: str
    message: str
    status_url: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "message": self.message,
            "status_url": self.status_url
        }

