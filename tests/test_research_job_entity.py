import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.research.domain.entities.research_job import ResearchJob, ResearchJobStatus
from context.kit.vo.uuid import Uuid


def test_research_job_creation():
    job = ResearchJob.create(topic="Quantum Computing")
    assert job.id is not None
    assert job.topic.value() == "Quantum Computing"
    assert job.status == ResearchJobStatus.IN_PROGRESS
    assert job.is_in_progress() is True
    assert job.is_completed() is False
    assert job.is_failed() is False


def test_research_job_mark_as_completed():
    job = ResearchJob.create(topic="AI Agents")
    job.mark_as_completed("reports/job-123.md")
    assert job.status == ResearchJobStatus.COMPLETED
    assert job.is_completed() is True
    assert job.s3_key == "reports/job-123.md"
    assert job.error_message is None


def test_research_job_mark_as_failed():
    job = ResearchJob.create(topic="AI Agents")
    job.mark_as_failed("Bedrock quota exceeded")
    assert job.status == ResearchJobStatus.FAILED
    assert job.is_failed() is True
    assert job.error_message == "Bedrock quota exceeded"


def test_research_job_primitives_serialization():
    job = ResearchJob.create(topic="Serverless Architecture", id="11111111-1111-1111-1111-111111111111")
    job.mark_as_completed("reports/1111.md")
    primitives = job.to_primitives()

    assert primitives["id"] == "11111111-1111-1111-1111-111111111111"
    assert primitives["topic"] == "Serverless Architecture"
    assert primitives["status"] == "COMPLETED"
    assert primitives["s3_key"] == "reports/1111.md"

    restored_job = ResearchJob.from_primitives(primitives)
    assert restored_job.id.value() == job.id.value()
    assert restored_job.topic.value() == job.topic.value()
    assert restored_job.status == ResearchJobStatus.COMPLETED
    assert restored_job.s3_key == "reports/1111.md"

