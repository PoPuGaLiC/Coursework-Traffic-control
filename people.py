import cv2
from shapely.geometry import Point


class People:
    def __init__(self, obj_id: int, track: tuple, network):
        self.id = obj_id
        self.network = network
        self.obj_class = "person"
        self.bbox = self.get_bbox(track)
        self.death_count = 0
        self.direction_id = None
        self.in_queue_id = None
        self.time = [None, None]
    
    def update(self, track: tuple):
        self.bbox = self.get_bbox(track)
    
    def get_bbox(self, track):
        return track[:4]
    
    def get_centroid(self):
        bbox = [int(x) for x in self.bbox]
        w = bbox[2]-bbox[0]
        h = bbox[3]-bbox[1]
        return (bbox[0]+w//2, bbox[1]+h//2)
    
    def get_point(self):
        return Point(self.get_centroid())
    
    def draw(self, frame):
        if self.is_death():
            return frame
        bbox = [int(x) for x in self.bbox]
        cv2.putText(frame, str(self.id), (bbox[0], bbox[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
        cv2.putText(frame, self.network.classes[self.obj_class], (bbox[0]+20, bbox[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 1)
        cv2.circle(frame, self.get_centroid(), 1, (0, 255, 0), 2)
        return frame
    
    def death(self):
        if not self.is_death():
            self.death_count+=1
    
    def is_death(self):
        if self.death_count > 25:
            return True
        return False
    
    def set_enter_time(self, seconds):
        if self.time[0] is None:
            self.time[0] = seconds
    
    def set_exit_time(self, seconds):
        if self.time[1] is None:
            self.time[1] = seconds
    
    def way_time(self):
        if None not in self.time:
            return self.time[1] - self.time[0]
        return
    
    def __str__(self):
        return f"PeopleID: {self.id} | WayTime: {self.way_time()}"
