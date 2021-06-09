import darknet
import os
import numpy as np
import cv2
from sort_1 import Sort


class Network:
    def __init__(self, folder, objs_class):
        self.folder = folder
        self.meta = None
        self.net = None
        self.darknet_image = None
        self.width = 0
        self.height = 0                                                                                                                                                                                                        `classes = None
        self.tracker = Sort(max_age = 25)
        self.detections = None
        self.trackers = None
        self.objects = {}
        self.objs_class = objs_class

    def load_net(self):
        configs = os.listdir(self.folder)
        configs = {os.path.splitext(f)[-1].replace(".", ''):self.folder+"/"+f for f in configs}
        self.net = darknet.load_net_custom(os.path.abspath(configs['cfg']).encode("ascii"), 
                                           os.path.abspath(configs['weights']).encode("ascii"), 0, 1)
        self.meta = darknet.load_meta(os.path.abspath(configs['data']).encode("ascii"))
        self.width = darknet.network_width(self.net)
        self.height = darknet.network_height(self.net)
        ##print(help(darknet.load_net_custom()))
        # exit(0)
        self.darknet_image = darknet.make_image(self.width, self.height, 3)

        with open(configs['names'], "r") as f:
            self.classes = [s.replace('\n', '') for s in f.readlines()]
    
    def detect(self, frame):
        
        frame = self.get_frame(frame)
        darknet.copy_image_from_bytes(self.darknet_image, frame.tobytes())
        self.detections = darknet.detect_image(self.net, self.meta, self.darknet_image, thresh=0.25)
        return self.detections, frame
    
    def get_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return cv2.resize(frame_rgb, (self.width, self.height), interpolation=cv2.INTER_LINEAR)
    
    def det_to_track(self, detections):
        def convertBack(x, y, w, h):
            xmin = int(round(x - (w / 2)))
            xmax = int(round(x + (w / 2)))
            ymin = int(round(y - (h / 2)))
            ymax = int(round(y + (h / 2)))
            return xmin, ymin, xmax, ymax

        det = []
        for detection in detections:
            x, y, w, h, score = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3], \
            detection[1]
            print("DETECTION", score, self.classes.index(detection[0].decode('UTF-8')))

            xmin, ymin, xmax, ymax = convertBack(float(x), float(y), float(w), float(h))
            pt1 = (xmin, ymin)
            pt2 = (xmax, ymax)
            det.append([xmin, ymin, xmax, ymax, score, self.classes.index(detection[0].decode('UTF-8'))])

        return np.array(det)

    def update_trackers(self):
        self.trackers = self.tracker.update(self.det_to_track(self.detections))
        print("TRACKERS:", self.det_to_track(self.detections))
        return self.trackers
    
    def update_objects(self):
        for track in self.trackers:
            obj_id = track[4]
            if obj_id not in self.objects.keys():
                self.objects[obj_id] = self.objs_class(obj_id, track, self)
            self.objects[obj_id].update(track)
    
    def get_objects(self):
        return self.objects.values()
    
    def check_death(self):
        lost_objs = set(self.objects.keys())-set([id[4] for id in self.trackers])
        for l in lost_objs:
            self.objects[l].death()
            if self.objects[l].is_death():
                del self.objects[l]
    
    def update(self, frame):
        _, frame = self.detect(frame)
        self.update_trackers()
        self.update_objects()
        self.check_death()

        return frame
    
    def draw(self, frame):
        for obj in self.get_objects():
            obj.draw(frame)
