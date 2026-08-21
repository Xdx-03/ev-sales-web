"""Per-execution identifier used to correlate reports and test evidence."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4


def create_run_id() -> str:
    configured = os.getenv("EV_TEST_RUN_ID", "").strip()
    if configured:
        return configured
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"web-{timestamp}-{uuid4().hex[:8]}"
