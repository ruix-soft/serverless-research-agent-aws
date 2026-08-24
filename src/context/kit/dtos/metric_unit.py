from enum import Enum


class MetricUnit(str, Enum):
    """
    Unidades de medida para métricas (compatibles con AWS CloudWatch / Powertools / Go kit).
    """

    SECONDS = "Seconds"
    MICROSECONDS = "Microseconds"
    MILLISECONDS = "Milliseconds"
    BYTES = "Bytes"
    KILOBYTES = "Kilobytes"
    MEGABYTES = "Megabytes"
    GIGABYTES = "Gigabytes"
    TERABYTES = "Terabytes"
    BITS = "Bits"
    KILOBITS = "Kilobits"
    MEGABITS = "Megabits"
    GIGABITS = "Gigabits"
    TERABITS = "Terabits"
    PERCENT = "Percent"
    COUNT = "Count"
    BYTES_PER_SECOND = "Bytes/Second"
    KILOBYTES_PER_SECOND = "Kilobytes/Second"
    MEGABYTES_PER_SECOND = "Megabytes/Second"
    GIGABYTES_PER_SECOND = "Gigabytes/Second"
    TERABYTES_PER_SECOND = "Terabytes/Second"
    BITS_PER_SECOND = "Bits/Second"
    KILOBITS_PER_SECOND = "Kilobits/Second"
    MEGABITS_PER_SECOND = "Megabits/Second"
    GIGABITS_PER_SECOND = "Gigabits/Second"
    TERABITS_PER_SECOND = "Terabits/Second"
    COUNT_PER_SECOND = "Count/Second"
    NONE = "None"


# Constantes para compatibilidad con Go-style
MetricUnitMilliseconds = MetricUnit.MILLISECONDS
MetricUnitCount = MetricUnit.COUNT
MetricUnitSeconds = MetricUnit.SECONDS
MetricUnitBytes = MetricUnit.BYTES
MetricUnitNone = MetricUnit.NONE

