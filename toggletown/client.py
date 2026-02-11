"""
ToggleTown Python SDK Client

Main client class for fetching and evaluating feature flags.
"""

import threading
import time
from typing import Any, Callable, Dict, Optional

import requests

from .evaluator import evaluate_flag

DEFAULT_API_URL = "https://api.toggletown.com"
DEFAULT_POLLING_INTERVAL = 30  # seconds


class ToggleTownClient:
    """
    ToggleTown feature flag client.

    Example:
        client = ToggleTownClient("tt_live_your_api_key")
        client.initialize()

        # Evaluate flags
        enabled = client.get_boolean_flag("new-feature", False, {"user_id": "123"})

        # Clean up when done
        client.close()
    """

    def __init__(
        self,
        api_key: str,
        api_url: str = DEFAULT_API_URL,
        polling_interval: int = DEFAULT_POLLING_INTERVAL,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        """
        Initialize the ToggleTown client.

        Args:
            api_key: Your environment API key (starts with tt_live_ or tt_test_)
            api_url: API base URL (optional, defaults to production)
            polling_interval: How often to refresh flags in seconds (default: 30)
            on_error: Callback for fetch errors during polling
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.polling_interval = polling_interval
        self.on_error = on_error

        self._flags: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        self._poll_thread: Optional[threading.Thread] = None
        self._stop_polling = threading.Event()
        self._lock = threading.Lock()

    def initialize(self) -> None:
        """
        Initialize the SDK and fetch flags from the server.

        Raises:
            Exception: If initial fetch fails
        """
        if self._initialized:
            return

        # Fetch flags (will raise on error)
        self._fetch_flags_initial()
        self._initialized = True

        # Start polling in background
        self._start_polling()

    def wait_for_initialization(self) -> None:
        """Wait for SDK to be initialized."""
        if not self._initialized:
            self.initialize()

    def is_initialized(self) -> bool:
        """Check if SDK has been initialized."""
        return self._initialized

    def _fetch_flags_initial(self) -> None:
        """Fetch flags from API during initialization. Raises on failure."""
        response = requests.get(
            f"{self.api_url}/api/v1/sdk/flags",
            headers={"X-API-Key": self.api_key},
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        with self._lock:
            self._flags = data.get("flags", {})

    def _fetch_flags(self) -> None:
        """Fetch flags from API (for polling). Does not raise."""
        try:
            response = requests.get(
                f"{self.api_url}/api/v1/sdk/flags",
                headers={"X-API-Key": self.api_key},
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            with self._lock:
                self._flags = data.get("flags", {})
        except Exception as e:
            if self.on_error:
                self.on_error(e)
            # Continue with cached flags

    def _start_polling(self) -> None:
        """Start background polling thread."""
        self._stop_polling.clear()
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()

    def _poll_loop(self) -> None:
        """Background polling loop."""
        while not self._stop_polling.wait(self.polling_interval):
            self._fetch_flags()

    def close(self) -> None:
        """Stop polling and clean up resources."""
        self._stop_polling.set()
        if self._poll_thread and self._poll_thread.is_alive():
            self._poll_thread.join(timeout=1)

    def _get_flag_config(self, key: str) -> Optional[Dict[str, Any]]:
        """Get flag configuration by key."""
        with self._lock:
            return self._flags.get(key)

    def get_boolean_flag(
        self,
        key: str,
        default_value: bool,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Get a boolean flag value.

        Args:
            key: The flag key
            default_value: Value to return if flag not found
            context: User context for targeting (user_id, attributes, etc.)

        Returns:
            The evaluated boolean value
        """
        flag_config = self._get_flag_config(key)
        if not flag_config:
            return default_value

        value = evaluate_flag(flag_config, context or {})
        return value if isinstance(value, bool) else default_value

    def get_string_flag(
        self,
        key: str,
        default_value: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Get a string flag value.

        Args:
            key: The flag key
            default_value: Value to return if flag not found
            context: User context for targeting

        Returns:
            The evaluated string value
        """
        flag_config = self._get_flag_config(key)
        if not flag_config:
            return default_value

        value = evaluate_flag(flag_config, context or {})
        return value if isinstance(value, str) else default_value

    def get_number_flag(
        self,
        key: str,
        default_value: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Get a number flag value.

        Args:
            key: The flag key
            default_value: Value to return if flag not found
            context: User context for targeting

        Returns:
            The evaluated number value
        """
        flag_config = self._get_flag_config(key)
        if not flag_config:
            return default_value

        value = evaluate_flag(flag_config, context or {})
        if isinstance(value, (int, float)):
            return float(value)
        return default_value

    def get_json_flag(
        self,
        key: str,
        default_value: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Get a JSON flag value.

        Args:
            key: The flag key
            default_value: Value to return if flag not found
            context: User context for targeting

        Returns:
            The evaluated JSON value (dict, list, etc.)
        """
        flag_config = self._get_flag_config(key)
        if not flag_config:
            return default_value

        value = evaluate_flag(flag_config, context or {})
        return value if value is not None else default_value

    def get_all_flags(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all flag configurations (for debugging).

        Returns:
            Dictionary of all flags
        """
        with self._lock:
            return dict(self._flags)

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
