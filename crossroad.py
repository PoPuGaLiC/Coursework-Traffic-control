from shapely.geometry.polygon import Polygon
from itertools import cycle
import numpy as np
import cv2


class Crossroad:
    def __init__(self, config, camera):
        self.zones = config['zones']
        self.direction_eneters = [Polygon(x['enter']) for x in self.zones]
        self.direction_sequences = [Polygon(x['sequence']) for x in self.zones]
        self.direction_exits = [Polygon(x['exit']) for x in self.zones]
        self.queues = None
        self.reset_queues()
        self.camera = camera
        self.all_tackts = cycle(config['tackt_duration'])
        self.tackt = next(self.all_tackts)

    def update_objects(self, objects):
        for obj in objects:
            if self.set_enter_zone(obj) is not None and self.in_exit_zone(obj):
                obj.set_exit_time(self.camera.seconds())

    def get_direction_count(self):
        return len(self.zones)

    def reset_queues(self):
        self.queues = [[] for _ in range(self.get_direction_count())]

    def set_enter_zone(self, obj):
        if obj.direction_id is not None:
            return obj.direction_id
        for zone_id, zone in enumerate(self.direction_eneters):
            if zone.contains(obj.get_point()):
                obj.direction_id = zone_id
                obj.set_enter_time(self.camera.seconds())
                obj.in_queue_id = len(self.queues[zone_id])
                self.queues[zone_id].append(obj)
                return zone_id

    def in_sequence_zone(self, obj):
        if self.direction_sequences[obj.direction_id].contains(obj.get_point()):
            return True
        return False

    def in_exit_zone(self, obj):
        if self.direction_exits[obj.direction_id].contains(obj.get_point()):
            return True
        return False

    def check_tackt(self):
        if self.camera.seconds() >= self.tackt:
            print("===== CHANGE TACKT! =====")
            self.camera.frame_count = 0
            self.tackt = next(self.all_tackts)
            return True
        return False

    def draw_areas(self, frame):
        for zones in self.zones:
            for zone in zones.values():
                frame = cv2.polylines(frame, [np.array(zone)], True, (0, 255, 0), 1)
        return frame
