# Description: DataProvider class for the CommandGateway example
from numpy import double

from farm_ng.gps.gps_pb2 import GpsFrame
from farm_ng.filter.filter_pb2 import FilterState
from farm_ng.track.track_pb2 import TrackFollowerState
from farm_ng.canbus.tool_control_pb2 import ToolStatuses
from farm_ng_core_pybind import Pose3F64


class DataProvider:
    def __init__(self):
        self.latitude: double = 0.0
        self.longitude: double = 0.0
        self.altitude: double = 0.0
        self.speed: double = 0.0
        self.heading: double = 0.0
        self.isPositionValid = False
        self.lastPose: Pose3F64 = None

    def on_event(self, event, msg):
        if isinstance(event, GpsFrame):
            self.latitude = event.latitudes
            self.longitude = event.longitude
            self.altitude = event.altitude
            self.speed = event.ground_speed

        if isinstance(event, FilterState):
            self.heading = event.heading
            self.isPositionValid = True if event.has_converged else False
            self.lastPose = event.pose
            
        if isinstance(event, TrackFollowerState):
            self.track_follower_state = event.status.track_status
            print("track follower state: ", self.track_follower_state)
            
        if isinstance(event, ToolStatuses):
            pass

    def print_data(self):
        print(f"Latitude: {self.latitude}")
        print(f"Longitude: {self.longitude}")
        print(f"Altitude: {self.altitude}")
        print(f"Speed: {self.speed}")
        print(f"Heading: {self.heading}")
        print(f"Position Valid: {self.isPositionValid}")
        print(f"Last Pose: {self.lastPose}")
