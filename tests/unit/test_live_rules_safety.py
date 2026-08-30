import pytest

from app.tools.live_rules import RulesFetchError, _reject_obvious_local_host


@pytest.mark.parametrize(
    "host",
    ["localhost", "127.0.0.1", "10.0.0.5", "192.168.1.4", "::1"],
)
def test_private_or_local_hosts_are_rejected(host: str) -> None:
    with pytest.raises(RulesFetchError):
        _reject_obvious_local_host(host)


@pytest.mark.parametrize(
    "host",
    ["example.com", "devpost.com", "allthingsagentichackathon.devpost.com"],
)
def test_public_hostnames_are_not_rejected_by_literal_guard(host: str) -> None:
    _reject_obvious_local_host(host)
