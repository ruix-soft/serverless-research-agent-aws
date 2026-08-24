from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class GetResearchStatusInputDTO:
    job_id: str


@dataclass(frozen=True)
class GetResearchStatusOutputDTO:
    job_id: str
    status: str
    s3_report_url: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    topic: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "job_id": self.job_id,
            "status": self.status
        }
        if self.topic:
            data["topic"] = self.topic
        if self.s3_report_url:
            data["s3_report_url"] = self.s3_report_url
        if self.message:
            data["message"] = self.message
        if self.error:
            data["error"] = self.error
        return data
