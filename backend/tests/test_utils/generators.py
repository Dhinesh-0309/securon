"""Property-based test generators using Hypothesis"""

from datetime import datetime, timezone
from typing import Any, Dict
import hypothesis.strategies as st

from src.securon.interfaces.core_types import (
    CloudLog,
    NormalizedLogEntry,
    LogSource,
    Severity,
    AnomalyType,
    RuleSource,
    RuleStatus,
    TimeRange,
)
from src.securon.interfaces.iac_scanner import SecurityRule


# Basic generators
severity_strategy = st.sampled_from(Severity)
log_source_strategy = st.sampled_from(LogSource)
anomaly_type_strategy = st.sampled_from(AnomalyType)
rule_source_strategy = st.sampled_from(RuleSource)
rule_status_strategy = st.sampled_from(RuleStatus)

# IP address generator
ip_address_strategy = st.builds(
    lambda a, b, c, d: f"{a}.{b}.{c}.{d}",
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
)

# Date generator (within reasonable range)
date_strategy = st.datetimes(
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2024, 12, 31),
    timezones=st.just(timezone.utc),
)

# Time range generator
time_range_strategy = st.builds(
    lambda start, duration: TimeRange(
        start=start,
        end=datetime.fromtimestamp(start.timestamp() + duration, tz=timezone.utc)
    ),
    date_strategy,
    st.integers(min_value=1, max_value=86400),  # 1 second to 1 day
)

# Normalized log entry generator
normalized_log_entry_strategy = st.builds(
    NormalizedLogEntry,
    timestamp=date_strategy,
    source_ip=ip_address_strategy,
    destination_ip=st.one_of(st.none(), ip_address_strategy),
    port=st.one_of(st.none(), st.integers(min_value=1, max_value=65535)),
    protocol=st.one_of(st.none(), st.sampled_from(["TCP", "UDP", "ICMP"])),
    action=st.text(min_size=1, max_size=50),
    user=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    resource=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
    api_call=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
)

# Cloud log generator
cloud_log_strategy = st.builds(
    CloudLog,
    timestamp=date_strategy,
    source=log_source_strategy,
    raw_data=st.dictionaries(st.text(), st.text()),
    normalized_data=normalized_log_entry_strategy,
)

# Security rule generator
security_rule_strategy = st.builds(
    SecurityRule,
    id=st.uuids().map(str),
    name=st.text(min_size=5, max_size=100),
    description=st.text(min_size=10, max_size=500),
    severity=severity_strategy,
    pattern=st.text(min_size=5, max_size=200),
    remediation=st.text(min_size=10, max_size=500),
    source=rule_source_strategy,
    status=rule_status_strategy,
    created_at=date_strategy,
)

# Terraform file content generator (basic structure)
terraform_content_strategy = st.text(min_size=50, max_size=1000).filter(
    lambda content: "resource" in content or "provider" in content
)

# File path generator
file_path_strategy = st.text(min_size=5, max_size=100).filter(
    lambda path: "/" in path and path.endswith(".tf")
)