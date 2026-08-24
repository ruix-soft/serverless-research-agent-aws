import pytest
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from context.kit.vo import (
    Boolean,
    NewBoolean,
    new_boolean,
    Number,
    NewNumber,
    new_number,
    String,
    NewString,
    new_string,
    Uuid,
    NewUuid,
    new_uuid,
    RandomUuid,
    random_uuid,
    Date,
    NewDate,
    new_date,
    NewDateNow,
    new_date_now,
    DateFromStandardString,
    date_from_standard_string,
)


def test_boolean_vo():
    b_true = NewBoolean(True)
    b_false = new_boolean(False)

    assert b_true.value() is True
    assert b_true.Value() is True
    assert b_true.is_true() is True
    assert b_true.IsTrue() is True
    assert b_true.is_false() is False
    assert b_true.IsFalse() is False
    assert bool(b_true) is True
    assert str(b_true) == "true"
    assert str(b_false) == "false"

    assert b_true.equals(NewBoolean(True))
    assert not b_true.equals(b_false)

    b_mut = NewBoolean(True)
    b_mut.negate()
    assert b_mut.is_false() is True
    b_mut.Negate()
    assert b_mut.is_true() is True


def test_number_vo():
    n1 = NewNumber(10.5555)
    assert n1.value() == 10.5555
    assert n1.Value() == 10.5555

    n2 = new_number(5.2)
    assert n1.is_bigger_than(n2) is True
    assert n1.IsBiggerThan(n2) is True
    assert n2.is_bigger_than(n1) is False

    n_dec = NewNumber(10.12345678)
    n_dec.format_to_two_decimal()
    assert n_dec.value() == 10.12

    n_dec2 = NewNumber(10.12345678)
    n_dec2.FormatToFourDecimal()
    assert n_dec2.value() == 10.1235

    n_dec3 = NewNumber(10.12345678)
    n_dec3.FormatToSixDecimal()
    assert n_dec3.value() == 10.123457

    assert str(NewNumber(5.0)) == "5"
    assert str(NewNumber(5.25)) == "5.25"


def test_string_vo():
    s = NewString("  Hello World  ")
    assert s.value() == "  Hello World  "
    assert s.Value() == "  Hello World  "

    s.clean()
    assert s.value() == "Hello World"

    s_sub = NewString("Rocket 🚀 Science")
    assert s_sub.get_first_characters(6) == "Rocket"
    assert s_sub.GetFirstCharacters(8) == "Rocket 🚀"

    s_sub.set_first_characters(6)
    assert s_sub.value() == "Rocket"


def test_uuid_vo():
    valid_uuid_str = "123e4567-e89b-12d3-a456-426614174000"
    u = NewUuid(valid_uuid_str)
    assert u.value() == valid_uuid_str
    assert u.Value() == valid_uuid_str
    assert str(u) == valid_uuid_str

    with pytest.raises(ValueError, match="<Uuid> does not allow the value"):
        NewUuid("invalid-uuid-string")

    u_rand = RandomUuid()
    assert u_rand.value() is not None
    assert len(u_rand.value()) == 36


def test_date_vo():
    dt = datetime(2026, 8, 24, 12, 30, 45, tzinfo=timezone.utc)
    d = NewDate(dt)

    assert d.value() == dt
    assert d.to_ymd_string() == "2026-08-24"
    assert d.ToYmdString() == "2026-08-24"
    assert d.to_ymd_his_string() == "2026-08-24 12:30:45"
    assert d.ToYmdHisString() == "2026-08-24 12:30:45"
    assert d.to_ymd_no_hyphens_string() == "20260824"
    assert d.ToYmdNoHyphensString() == "20260824"

    d_added = d.add_days(5)
    assert d_added.to_ymd_string() == "2026-08-29"
    # Inmutabilidad
    assert d.to_ymd_string() == "2026-08-24"

    # Parsing from standard string
    parsed = DateFromStandardString("2026-08-24 15:30:00.123")
    assert parsed.to_ymd_string() == "2026-08-24"
    assert parsed.to_ymd_his_string() == "2026-08-24 15:30:00"

    parsed_iso = date_from_standard_string("2026-08-24T18:45:10")
    assert parsed_iso.to_ymd_his_string() == "2026-08-24 18:45:10"

