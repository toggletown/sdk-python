# ToggleTown Python SDK

Official Python SDK for [ToggleTown](https://toggletown.com) feature flags.

## Installation

```bash
pip install toggletown
```

## Quick Start

```python
from toggletown import ToggleTownClient

client = ToggleTownClient("tt_live_your_api_key")
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
with ToggleTownClient("tt_live_xxx") as client:
    enabled = client.get_boolean_flag("feature", False, {"user_id": "123"})
```

## Documentation

Full documentation with configuration, targeting rules, framework integration (Flask, Django), and best practices:

**[Python SDK Guide](https://docs.toggletown.com/sdks/python)**

## License

MIT
