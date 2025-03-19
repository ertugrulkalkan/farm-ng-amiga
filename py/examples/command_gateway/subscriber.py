import asyncio

from farm_ng.core.event_service_pb2 import EventServiceConfig
from farm_ng.core.event_service_pb2 import SubscribeRequest
from farm_ng.core.event_client import EventClient

from data_provider import DataProvider


class Subscriber:
    def __init__(self, config: EventServiceConfig, data_provider: DataProvider) -> None:
        self.dp: DataProvider = data_provider
        self.config: EventServiceConfig = config
        self.client: EventClient = EventClient(config)
        self.subscriptions: list[SubscribeRequest] = list(config.subscriptions)
        self.tasks: list[asyncio.Task] = []

    async def _subscribe(self, subscription: SubscribeRequest) -> None:
        async for event, msg in self.client.subscribe(subscription):
            self.dp.on_event(event, msg)

    def run(self) -> list[asyncio.Task]:
        for subscription in self.subscriptions:
            self.tasks.append(asyncio.create_task(self._subscribe(subscription)))
        return self.tasks
