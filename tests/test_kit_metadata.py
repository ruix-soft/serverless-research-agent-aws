import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.dtos.metadata import (
    Metadata,
    NewMetadata,
    new_metadata,
)


def test_metadata_creation_and_fields():
    now = datetime.now(timezone.utc)
    meta = Metadata(
        user="usr_123",
        user_agent="Mozilla/5.0",
        ip="192.168.1.1",
        timestamp=now,
        correlation_id="corr_abc",
    )

    assert meta.user == "usr_123"
    assert meta.User == "usr_123"
    assert meta.user_agent == "Mozilla/5.0"
    assert meta.UserAgent == "Mozilla/5.0"
    assert meta.userAgent == "Mozilla/5.0"
    assert meta.ip == "192.168.1.1"
    assert meta.IP == "192.168.1.1"
    assert meta.timestamp == now
    assert meta.Timestamp == now
    assert meta.correlation_id == "corr_abc"
    assert meta.CorrelationID == "corr_abc"
    assert meta.correlationId == "corr_abc"


def test_new_metadata_helper():
    meta = NewMetadata(user="admin", correlation_id="req_999")
    assert meta.user == "admin"
    assert meta.correlation_id == "req_999"
    assert meta.timestamp is not None
    assert isinstance(meta.timestamp, datetime)

    meta2 = new_metadata(user="editor")
    assert meta2.user == "editor"
    assert meta2.correlation_id is None
    assert meta2.timestamp is not None


def test_metadata_to_dict_omitempty():
    meta = Metadata(user="alice")
    d = meta.to_dict()
    assert d == {"user": "alice"}
    assert "userAgent" not in d
    assert "ip" not in d
    assert "timestamp" not in d
    assert "correlationId" not in d

    now = datetime(2026, 8, 24, 12, 0, 0, tzinfo=timezone.utc)
    meta_full = Metadata(
        user="bob",
        user_agent="curl/8.0",
        ip="10.0.0.1",
        timestamp=now,
        correlation_id="trace_1",
    )
    d_full = meta_full.to_dict()
    assert d_full == {
        "user": "bob",
        "userAgent": "curl/8.0",
        "ip": "10.0.0.1",
        "timestamp": now.isoformat(),
        "correlationId": "trace_1",
    }
    assert meta_full.to_primitives() == d_full


def test_metadata_from_dict():
    iso_str = "2026-08-24T12:00:00+00:00"
    data = {
        "user": "charlie",
        "userAgent": "pytest",
        "ip": "127.0.0.1",
        "timestamp": iso_str,
        "correlationId": "cid_123",
    }
    meta = Metadata.from_dict(data)
    assert meta.user == "charlie"
    assert meta.user_agent == "pytest"
    assert meta.ip == "127.0.0.1"
    assert meta.timestamp == datetime.fromisoformat(iso_str)
    assert meta.correlation_id == "cid_123"

    # From primitives alias
    meta_prim = Metadata.from_primitives(data)
    assert meta_prim == meta

