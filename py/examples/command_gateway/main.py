import argparse
import asyncio
import json
import socket

from math import degrees

from typing import Callable
from pathlib import Path

from farm_ng.core.events_file_reader import proto_from_json_file
from farm_ng.core.event_service_pb2 import EventServiceConfig, EventServiceConfigList

from subscriber import Subscriber
from data_provider import DataProvider
from enumeration import EnMessageType, EnTaskType
from track_build import TrackBuildFollow


class CommandGatewayConfig:
    def __init__(self, local_addr: str, local_port: int, remote_addr: str, remote_port: int) -> None:
        self.local_addr: str = local_addr
        self.local_port: int = local_port
        self.remote_addr: str = remote_addr
        self.remote_port: int = remote_port

    def to_dict(self) -> dict:
        return {
            "local": {
                "addr": self.local_addr,
                "port": self.local_port
            },
            "remote": {
                "addr": self.remote_addr,
                "port": self.remote_port
            }
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> 'CommandGatewayConfig':
        data = json.loads(json_str)
        return cls(data["local"]["addr"], data["local"]["port"], data["remote"]["addr"], data["remote"]["port"])

    @classmethod
    def from_file(cls, file: Path) -> 'CommandGatewayConfig':
        with file.open() as f:
            return cls.from_json(f.read())

    def __str__(self) -> str:
        return f"Local Address: {self.local_addr}, Local Port: {self.local_port},\
            Remote Address: {self.remote_addr}, Remote Port: {self.remote_port}"

    def __repr__(self) -> str:
        return f"CommandGatewayConfig(local_addr={self.local_addr}, local_port={self.local_port},\
            remote_addr={self.remote_addr}, remote_port={self.remote_port})"


class CommandGateway:
    def __init__(self, config: CommandGatewayConfig) -> None:
        self.config: CommandGatewayConfig = config

        # create udp socket to both send and receive messages
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((config.local_addr, config.local_port))
        self.sock.setblocking(False)

        # create udp socket to send messages
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # subscribers
        self.subscribers: list[Callable[[str], None]] = []

    def send(self, message: str) -> None:
        self.send_sock.sendto(message.encode(), (self.config.remote_addr, self.config.remote_port))

    def on_message(self, message: str) -> None:
        for subscriber in self.subscribers:
            subscriber(message)
        
    def subscribe(self, subscriber: Callable[[str], None]) -> None:
        self.subscribers.append(subscriber)

    async def run(self):
        print(f"Running Command Gateway with config: {self.config}")
        loop = asyncio.get_running_loop()
        while True:
            try:
                data, _ = await loop.sock_recvfrom(self.sock, 1024)
                message = data.decode()
                self.on_message(message)
            except Exception as e:
                print(f"Error while receiving message: {e}")


trackBuildFollow: TrackBuildFollow = None


def on_message(message: str) -> None:
    global trackBuildFollow
    
    try:
        Jmessage = json.loads(message)
    except Exception as e:
        print(f"Error while parsing message: {e}")
        return

    if Jmessage["Header"]["MessageType"] == EnMessageType.Task.value:
        task_type = Jmessage["TaskType"]
        if task_type == EnTaskType.TrackTask.value:
            waypoints = Jmessage["Waypoints"]
            if trackBuildFollow is not None:
                trackBuildFollow.set_waypoints(waypoints)
                path = trackBuildFollow.build_track()
                pass
        elif task_type == EnTaskType.Cultivation.value:
            pass
        else:
            print(f"Received Unknown Task Type: {task_type}") 

    else:
        print(f"Received Unknown Message: {Jmessage}")


async def send_live_position_each_period(gw: CommandGateway, data_provider: DataProvider, period: float = 1.0):
    while True:
        Jmessage = {
            "Header": {
                "MessageType": EnMessageType.LivePosition.value
            },
            "Position": {
                "X": data_provider.latitude,
                "Y": data_provider.longitude
            },
            "IsPositionValid": data_provider.isPositionValid,
            "Speed": data_provider.speed,
            "Heading": degrees(data_provider.heading)
        }

        message_str = json.dumps(Jmessage)

        gw.send(message_str)

        await asyncio.sleep(period)


async def main():
    global trackBuildFollow

    parser = argparse.ArgumentParser(
        prog="python main.py", description="Command and monitor tools with the canbus service."
    )
    parser.add_argument("--config", type=Path, required=True, help="The canbus service config.")
    parser.add_argument("--gateway-config", type=Path, required=True, help="The command gateway config.")
    parser.add_argument("--track-follower-config", type=Path, required=True, help="The follower config.")
    args = parser.parse_args()

    service_config = proto_from_json_file(args.config, EventServiceConfigList())
    track_follower_config = proto_from_json_file(args.track_follower_config, EventServiceConfig())

    data_provider = DataProvider()

    subscriber_tasks = []
    for config in service_config.configs:
        subscriber = Subscriber(config, data_provider)
        subscriber_tasks += subscriber.run()

    print("Subscribers: ", len(subscriber_tasks))

    gateway_config = CommandGatewayConfig.from_file(args.gateway_config)
    gateway = CommandGateway(gateway_config)

    gateway.subscribe(on_message)
    gateway_task = asyncio.create_task(gateway.run())

    periodic_sender = asyncio.create_task(send_live_position_each_period(gateway, data_provider, 0.1))

    trackBuildFollow = TrackBuildFollow(track_follower_config, data_provider)

    await asyncio.gather(*subscriber_tasks, gateway_task, periodic_sender)

if __name__ == '__main__':
    asyncio.run(main())
