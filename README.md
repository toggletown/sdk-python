# ToggleTown Python SDK

Official Python SDK for [ToggleTown](https://toggletown.com) feature flags.

## Installation

```bash
pip install toggletown
```

## Quick Start

```python
from toggletown import ToggleTownClient

# Initialize the client
client = ToggleTownClient("tt_live_your_api_key")
client.initialize()

# Evaluate a boolean flag
enabled = client.get_boolean_flag("new-feature", False, {
    "user_id": "user-123",
    "plan": "pro",
})

if enabled:
    print("New feature is enabled!")

# Clean up when done
client.close()
```

## Context Manager

```python
from toggletown import ToggleTownClient

with ToggleTownClient("tt_live_xxx") as client:
    enabled = client.get_boolean_flag("feature", False, {"user_id": "123"})
```

## Configuration

```python
client = ToggleTownClient(
    api_key="tt_live_xxx",
    api_url="https://api.toggletown.com",  # Optional
    polling_interval=30,  # Seconds between flag refreshes
    on_error=lambda e: print(f"Error: {e}"),  # Error callback
)
```

## Flag Types

### Boolean Flags

```python
enabled = client.get_boolean_flag("feature-enabled", False, context)
```

### String Flags

```python
variant = client.get_string_flag("experiment-variant", "control", context)
```

### Number Flags

```python
max_items = client.get_number_flag("max-items", 10, context)
```

### JSON Flags

```python
config = client.get_json_flag("feature-config", {"enabled": False}, context)
```

## User Context

Pass user attributes for targeting rules:

```python
context = {
    "user_id": "user-123",  # Required for percentage rollouts
    "email": "user@example.com",
    "plan": "enterprise",
    "country": "US",
    "beta_user": True,
}

enabled = client.get_boolean_flag("premium-feature", False, context)
```

## Flask Integration

```python
from flask import Flask, g, request
from toggletown import ToggleTownClient

app = Flask(__name__)
client = ToggleTownClient("tt_live_xxx")
client.initialize()

@app.before_request
def setup_flags():
    g.flag_context = {
        "user_id": request.headers.get("X-User-ID"),
        "plan": request.headers.get("X-User-Plan", "free"),
    }

@app.route("/api/feature")
def feature():
    enabled = client.get_boolean_flag("new-feature", False, g.flag_context)
    return {"enabled": enabled}

@app.teardown_appcontext
def cleanup(exception):
    pass  # Client cleanup handled at app shutdown

# Cleanup on shutdown
import atexit
atexit.register(client.close)
```

## Django Integration

```python
# settings.py
from toggletown import ToggleTownClient

FEATURE_FLAGS = ToggleTownClient("tt_live_xxx")
FEATURE_FLAGS.initialize()

# views.py
from django.conf import settings

def my_view(request):
    context = {
        "user_id": str(request.user.id) if request.user.is_authenticated else None,
        "plan": getattr(request.user, "plan", "free"),
    }

    enabled = settings.FEATURE_FLAGS.get_boolean_flag("feature", False, context)
    return JsonResponse({"enabled": enabled})
```

## Thread Safety

The client is thread-safe. Flag data is protected by locks and can be safely accessed from multiple threads.

## Error Handling

```python
def handle_error(error: Exception):
    print(f"Flag fetch failed: {error}")
    # Optionally send to error tracking

client = ToggleTownClient(
    "tt_live_xxx",
    on_error=handle_error,
)

try:
    client.initialize()
except Exception as e:
    print(f"Initialization failed: {e}")
    # Use defaults if initialization fails
```

## License

MIT
