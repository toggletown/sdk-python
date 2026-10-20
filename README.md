# ToggleTown Python SDK

Official Python SDK for [ToggleTown](https://toggletown.com) feature flags.

## Installation

```bash
pip install git+https://github.com/toggletown/sdk-python.git
```

## Quick Start

```python
from toggletown import ToggleTownClient

client = ToggleTownClient("your_environment_api_key")
client.initialize()

enabled = client.get_boolean_flag("new-feature", False, {
    "user_id": "user-123",
    "plan": "pro",
})

if enabled:
    print("New feature is enabled!")

client.close()
```

## Flag Types

```python
enabled = client.get_boolean_flag("feature", False, context)
variant = client.get_string_flag("experiment", "control", context)
limit = client.get_number_flag("max-items", 10, context)
config = client.get_json_flag("config", {"enabled": False}, context)
```

## Context Manager

```python
with ToggleTownClient("prod_xxx") as client:
    enabled = client.get_boolean_flag("feature", False, {"user_id": "123"})
```

## Staleness Detection

```python
client = ToggleTownClient(
    "prod_xxx",
    on_stale=lambda last, age: print(f"Flags stale! age: {age}s"),
)

client.is_stale()            # bool
client.get_last_updated_at() # datetime or None
client.get_status()          # {"status": "fresh"|"stale", "last_updated_at": ..., "age_seconds": ...}
```

## Documentation

Full documentation with configuration, targeting rules, framework integration (Flask, Django), and best practices:

**[Python SDK Guide](https://docs.toggletown.com/sdks/python)**

## License

MIT
