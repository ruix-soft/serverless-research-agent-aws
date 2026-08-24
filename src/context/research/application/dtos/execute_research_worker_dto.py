from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class ExecuteResearchWorkerInputDTO:
    job_id: str
    topic: str

@dataclass(frozen=True)
class ExecuteResearchWorkerOutputDTO:
    job_id: str
    status: str
    s3_key: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "s3_key": self.s3_key
        }

