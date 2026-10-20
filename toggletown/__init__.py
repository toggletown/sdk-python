"""
ToggleTown Python SDK

A Python SDK for evaluating feature flags from ToggleTown.

Example:
    from toggletown import ToggleTownClient

    client = ToggleTownClient("your_environment_api_key")
    client.initialize()

    enabled = client.get_boolean_flag("new-feature", False, {"user_id": "user-123"})
"""

from .client import ToggleTownClient
from .evaluator import evaluate_flag

__version__ = "0.1.0"
__all__ = ["ToggleTownClient", "evaluate_flag"]
