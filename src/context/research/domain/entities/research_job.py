from typing import Optional, Dict, Any, Union
from enum import Enum
from context.kit.aggregate_root import AggregateRoot
from context.kit.vo.uuid import Uuid
from context.kit.vo.string import String as StringVO
from context.kit.vo.date import Date as DateVO


class ResearchJobStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ResearchJob(AggregateRoot):
    """
    ResearchJob Aggregate Root representing the complete lifecycle of an asynchronous research task.
    """

    def __init__(
        self,
        id: Union[Uuid, str],
        topic: Union[StringVO, str],
        status: Union[ResearchJobStatus, str] = ResearchJobStatus.IN_PROGRESS,
        s3_key: Optional[str] = None,
        error_message: Optional[str] = None,
        created_at: Optional[DateVO] = None,
        updated_at: Optional[DateVO] = None,
    ) -> None:
        super().__init__()
        if isinstance(id, Uuid):
            self.id = id
        else:
            try:
                self.id = Uuid(str(id))
            except ValueError:
                # Fallback for custom formatted strings
                self.id = Uuid.random()

        self.topic = topic if isinstance(topic, StringVO) else StringVO(str(topic))
        self.status = status if isinstance(status, ResearchJobStatus) else ResearchJobStatus(status)
        self.s3_key = s3_key
        self.error_message = error_message
        self.created_at = created_at or DateVO.now()
        self.updated_at = updated_at or DateVO.now()

    @classmethod
    def create(cls, topic: str, id: Optional[str] = None) -> "ResearchJob":
        """Factory method to instantiate a new ResearchJob in IN_PROGRESS state."""
        if id:
            try:
                job_id = Uuid(id)
            except ValueError:
                job_id = Uuid.random()
        else:
            job_id = Uuid.random()

        return cls(
            id=job_id,
            topic=StringVO(topic),
            status=ResearchJobStatus.IN_PROGRESS,
        )

    def mark_as_completed(self, s3_key: str) -> None:
        """Transitions state to COMPLETED and stores report reference."""
        self.status = ResearchJobStatus.COMPLETED
        self.s3_key = s3_key
        self.error_message = None
        self.updated_at = DateVO.now()

    def mark_as_failed(self, error_message: str) -> None:
        """Transitions state to FAILED and records root cause."""
        self.status = ResearchJobStatus.FAILED
        self.error_message = error_message
        self.updated_at = DateVO.now()

    def is_completed(self) -> bool:
        return self.status == ResearchJobStatus.COMPLETED

    def is_in_progress(self) -> bool:
        return self.status == ResearchJobStatus.IN_PROGRESS

    def is_failed(self) -> bool:
        return self.status == ResearchJobStatus.FAILED

    def to_primitives(self) -> Dict[str, Any]:
        """Serializes domain entity to primitive data dictionary."""
        return {
            "id": self.id.value(),
            "topic": self.topic.value(),
            "status": self.status.value,
            "s3_key": self.s3_key,
            "error_message": self.error_message,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    @classmethod
    def from_primitives(cls, data: Dict[str, Any]) -> "ResearchJob":
        """Reconstructs domain entity from primitive dictionary."""
        return cls(
            id=data["id"],
            topic=StringVO(data["topic"]),
            status=ResearchJobStatus(data.get("status", ResearchJobStatus.IN_PROGRESS.value)),
            s3_key=data.get("s3_key"),
            error_message=data.get("error_message"),
            created_at=DateVO.from_standard_string(data["created_at"]) if "created_at" in data else DateVO.now(),
            updated_at=DateVO.from_standard_string(data["updated_at"]) if "updated_at" in data else DateVO.now(),
        )

