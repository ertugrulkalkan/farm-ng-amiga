from math import radians

from farm_ng.core.event_service_pb2 import EventServiceConfig
from farm_ng.core.event_client import EventClient
from farm_ng.track.track_pb2 import Track
from farm_ng.track.track_pb2 import TrackFollowRequest
from farm_ng_core_pybind import Pose3F64
from google.protobuf.empty_pb2 import Empty

from track_planner import TrackBuilder
from data_provider import DataProvider
from enumeration import EnTrackType
from subscriber import Subscriber


class TrackBuildFollow:
    def __init__(self, follower_config: EventServiceConfig, data_provider: DataProvider):
        self.track_follower_sub = Subscriber(follower_config, data_provider)
        self.follower_config = follower_config
        self.data_provider = data_provider
        self.waypoints = []
        self.track : Track = None

    def set_waypoints(self, waypoints: list[dict[str, object]]) -> None:
        self.waypoints = waypoints

    def build_track(self):
        print("Building track...")

        start: Pose3F64 = self.data_provider.lastPose

        track_builder = TrackBuilder(start=start)
        goalNumber = 0

        # just two segment type were added; however we have also arc segment and ab line segment 
        for segment in self.waypoints:
            if segment["TrackType"] == EnTrackType.None_:
                continue
            elif segment["TrackType"] == EnTrackType.Move:
                track_builder.create_straight_segment(next_frame_b=f"goal{goalNumber}",
                                                      distance=segment["Amount"], spacing=0.1)
                goalNumber += 1
            elif segment["TrackType"] == EnTrackType.Rotate:
                track_builder.create_turn_segment(next_frame_b=f"goal{goalNumber}",
                                                  angle=radians(segment["Amount"]), spacing=0.1)
                goalNumber += 1
            else:
                print("Invalid track type")

        self.track = track_builder.track

    async def execute(self):
        await EventClient(self.follower_config).request_reply("/set_track", TrackFollowRequest(track=self.track))
        await EventClient(self.follower_config).request_reply("/start", Empty())
