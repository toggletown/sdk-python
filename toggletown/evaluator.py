"""
Flag evaluation logic - mirrors the JavaScript SDK evaluator.
"""

import hashlib
from typing import Any, Dict, List, Optional


def hash_string(input_str: str) -> int:
    """Hash a string to a number between 0-99 for rollout bucketing.

    Uses SHA-256 for consistency with Node.js and browser SDKs.
    """
    hex_digest = hashlib.sha256(input_str.encode()).hexdigest()
    num = int(hex_digest[:8], 16)
    return num % 100


def is_in_rollout(user_id: str, flag_key: str, percentage: int) -> bool:
    """Check if a user is in the rollout percentage."""
    if percentage == 0:
        return False
    if percentage >= 100:
        return True
    bucket = hash_string(f"{user_id}:{flag_key}")
    return bucket < percentage


def matches_rule(rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Check if context matches a targeting rule."""
    attribute = rule.get("attribute", "")
    operator = rule.get("operator", "")
    rule_value = rule.get("value")

    # Get attribute value from context
    # Support both flat context and nested attributes
    if attribute in context:
        attr_value = context[attribute]
    elif "attributes" in context and attribute in context.get("attributes", {}):
        attr_value = context["attributes"][attribute]
    else:
        return False

    # Operator matching
    if operator == "equals":
        return attr_value == rule_value
    elif operator == "not_equals":
        return attr_value != rule_value
    elif operator == "contains":
        return isinstance(attr_value, str) and isinstance(rule_value, str) and rule_value in attr_value
    elif operator == "not_contains":
        return isinstance(attr_value, str) and isinstance(rule_value, str) and rule_value not in attr_value
    elif operator == "gt":
        try:
            return float(attr_value) > float(rule_value)
        except (ValueError, TypeError):
            return False
    elif operator == "lt":
        try:
            return float(attr_value) < float(rule_value)
        except (ValueError, TypeError):
            return False
    elif operator == "in":
        if isinstance(rule_value, list):
            return attr_value in rule_value
        return False
    elif operator == "not_in":
        if isinstance(rule_value, list):
            return attr_value not in rule_value
        return True
    elif operator == "always":
        return True

    return False


def get_off_value(flag_type: str) -> Any:
    """Get the 'off' value for a flag type."""
    if flag_type == "BOOLEAN":
        return False
    elif flag_type == "STRING":
        return ""
    elif flag_type == "NUMBER":
        return 0
    elif flag_type == "JSON":
        return None
    return None


def evaluate_flag(flag_config: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """
    Evaluate a flag for a given context.

    Args:
        flag_config: The flag configuration from the API
        context: User context with attributes for targeting

    Returns:
        The evaluated flag value
    """
    if not flag_config:
        return None

    flag_type = flag_config.get("type", "BOOLEAN")
    enabled = flag_config.get("enabled", False)
    default_value = flag_config.get("defaultValue")
    rules = flag_config.get("rules", [])
    rollout_percentage = flag_config.get("rolloutPercentage", 0)
    flag_key = flag_config.get("key", "")

    if not enabled:
        return default_value

    # Get user_id for rollout (support both user_id and userId)
    user_id = context.get("user_id") or context.get("userId") or ""

    # Check targeting rules in order
    for rule in rules:
        if not matches_rule(rule, context):
            continue

        rule_percentage = rule.get("percentage")
        rule_value = rule.get("rollValue")

        # If rule has a percentage rollout, check if user qualifies
        if rule_percentage is not None and rule_percentage < 100:
            if not user_id or not is_in_rollout(user_id, flag_key, rule_percentage):
                continue

        return rule_value if rule_value is not None else default_value

    # No rules matched - check global percentage rollout
    if rollout_percentage > 0 and user_id:
        if is_in_rollout(user_id, flag_key, rollout_percentage):
            return default_value
        return get_off_value(flag_type)

    return default_value
