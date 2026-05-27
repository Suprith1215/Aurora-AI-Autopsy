import asyncio
import time
from typing import Any, Dict, List, Callable, DefaultDict
from collections import defaultdict

class EventBroker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EventBroker, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.subscribers: DefaultDict[str, List[Callable]] = defaultdict(list)
        self.history: List[Dict[str, Any]] = []
        self.queue: asyncio.Queue = asyncio.Queue()
        self._initialized = True

    async def publish(self, topic: str, data: Dict[str, Any]):
        """Publishes an event to a specific topic and appends to telemetry history."""
        event = dict(data)
        event["topic"] = topic
        event["broker_timestamp"] = time.time()
        
        self.history.append(event)
        
        # Keep history capped at 1000 items to avoid memory leaks
        if len(self.history) > 1000:
            self.history.pop(0)

        # Queue for async subscribers
        await self.queue.put(event)

        # Sync callback triggers
        for subscriber in self.subscribers[topic]:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(event)
                else:
                    subscriber(event)
            except Exception as e:
                print(f"Error executing subscriber callback for topic {topic}: {e}")

    def subscribe(self, topic: str, callback: Callable):
        """Subscribes a callback function to a topic."""
        self.subscribers[topic].append(callback)

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the chronological audit stream of all broker events."""
        return self.history[-limit:]

    def clear_history(self):
        """Clears execution logs."""
        self.history.clear()

    def clear_subscribers(self):
        """Clears all topic subscribers to prevent leak loops on hot reloads."""
        self.subscribers.clear()
