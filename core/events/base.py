"""Event bus abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any


class AbstractEventBus(ABC):
    @abstractmethod
    async def publish(self, channel: str, payload: dict[str, Any]) -> None:
        """Publish an event to the given channel."""

    @abstractmethod
    async def subscribe(
        self,
        channel: str,
        handler: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> None:
        """Subscribe a handler to events on the given channel."""
