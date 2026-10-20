"""Tests for the flag evaluator."""

import pytest
from toggletown.evaluator import evaluate_flag, hash_string, is_in_rollout, matches_rule


class TestHashString:
    def test_deterministic(self):
        """Same input always produces same output."""
        assert hash_string("test") == hash_string("test")

    def test_range(self):
        """Hash is always between 0-99."""
        for i in range(100):
            result = hash_string(f"user-{i}")
            assert 0 <= result < 100


class TestIsInRollout:
    def test_zero_percent(self):
        """0% rollout always returns False."""
        assert is_in_rollout("user-123", "flag", 0) is False

    def test_hundred_percent(self):
        """100% rollout always returns True."""
        assert is_in_rollout("user-123", "flag", 100) is True

    def test_deterministic(self):
        """Same user/flag always gets same result."""
        result1 = is_in_rollout("user-123", "my-flag", 50)
        result2 = is_in_rollout("user-123", "my-flag", 50)
        assert result1 == result2


class TestMatchesRule:
    def test_equals(self):
        rule = {"attribute": "plan", "operator": "equals", "value": "pro"}
        assert matches_rule(rule, {"plan": "pro"}) is True
        assert matches_rule(rule, {"plan": "free"}) is False

    def test_not_equals(self):
        rule = {"attribute": "plan", "operator": "not_equals", "value": "free"}
        assert matches_rule(rule, {"plan": "pro"}) is True
        assert matches_rule(rule, {"plan": "free"}) is False

    def test_contains(self):
        rule = {"attribute": "email", "operator": "contains", "value": "@company.com"}
        assert matches_rule(rule, {"email": "user@company.com"}) is True
        assert matches_rule(rule, {"email": "user@other.com"}) is False

    def test_gt(self):
        rule = {"attribute": "age", "operator": "gt", "value": 18}
        assert matches_rule(rule, {"age": 25}) is True
        assert matches_rule(rule, {"age": 15}) is False

    def test_in_list(self):
        rule = {"attribute": "country", "operator": "in", "value": ["US", "CA", "UK"]}
        assert matches_rule(rule, {"country": "US"}) is True
        assert matches_rule(rule, {"country": "DE"}) is False

    def test_nested_attributes(self):
        rule = {"attribute": "plan", "operator": "equals", "value": "pro"}
        assert matches_rule(rule, {"attributes": {"plan": "pro"}}) is True


class TestEvaluateFlag:
    def test_disabled_flag(self):
        """Disabled flag returns the off value, not defaultValue."""
        config = {"type": "BOOLEAN", "enabled": False, "defaultValue": True}
        assert evaluate_flag(config, {}) is False

    def test_enabled_boolean(self):
        """Enabled boolean flag with 100% rollout returns default."""
        config = {
            "type": "BOOLEAN",
            "enabled": True,
            "defaultValue": True,
            "rolloutPercentage": 100,
            "rules": [],
        }
        assert evaluate_flag(config, {"user_id": "123"}) is True

    def test_targeting_rule_match(self):
        """Matching targeting rule returns rollValue or defaultValue."""
        config = {
            "type": "BOOLEAN",
            "enabled": True,
            "defaultValue": False,
            "rolloutPercentage": 0,
            "rules": [{"attribute": "plan", "operator": "equals", "value": "pro", "rollValue": True}],
        }
        assert evaluate_flag(config, {"plan": "pro"}) is True
        assert evaluate_flag(config, {"plan": "free"}) is False

    def test_string_flag(self):
        """String flag returns correct value."""
        config = {
            "type": "STRING",
            "enabled": True,
            "defaultValue": "variant-a",
            "rolloutPercentage": 100,
            "rules": [],
        }
        assert evaluate_flag(config, {"user_id": "123"}) == "variant-a"

    def test_number_flag(self):
        """Number flag returns correct value."""
        config = {
            "type": "NUMBER",
            "enabled": True,
            "defaultValue": 42,
            "rolloutPercentage": 100,
            "rules": [],
        }
        assert evaluate_flag(config, {"user_id": "123"}) == 42


class TestOffSemantics:
    def test_enabled_zero_rollout_is_off(self):
        config = {"type": "BOOLEAN", "enabled": True, "defaultValue": True, "rolloutPercentage": 0, "rules": []}
        assert evaluate_flag(config, {"user_id": "u1"}) is False

    def test_disabled_non_boolean_returns_type_off_value(self):
        assert evaluate_flag({"type": "STRING", "enabled": False, "defaultValue": "x"}, {}) == ""
        assert evaluate_flag({"type": "NUMBER", "enabled": False, "defaultValue": 5}, {}) == 0
