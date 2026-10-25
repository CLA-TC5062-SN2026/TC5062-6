from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


def json_safe(value):
    if isinstance(value, dict): return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, list): return [json_safe(v) for v in value]
    # RFC 3339 (format: date-time / date del contrato); str() produciría '2026-10-24 10:00:00+00:00'.
    if isinstance(value, (datetime, date)): return value.isoformat()
    if isinstance(value, (UUID, Decimal)): return str(value)
    return value
