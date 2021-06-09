import json
import os
import cv2
import darknet
from math import ceil


class Camera:
    def __init__(self, Network, config_path: str):
        self.network = Network
        self.config = self.load_config(config_path)
        self.output = self.get_output()
        self.frame_count = 0
        self.source = None
        self.mask = None
        self.load_source()
        self.load_mask()

    def load_config(self, config_path):
        if os.path.exists(config_path):
            with open(config_path) as cfg:
                return json.load(cfg)
        else:
            exit("Config not found")
    
    def get_output(self):
        wh = (self.network.width, self.network.height)
        return cv2.VideoWriter(self.config['camera']['output_file'], cv2.VideoWriter_fourcc(*'XVID'), 25.0, wh)
    
    def load_source(self):
        mode = self.config['camera']["mode"]
        if mode == "video":
            if not os.path.exists(self.config['camera'][mode]):
                exit("Video not found")
        self.source = cv2.VideoCapture(self.config['camera'][mode])
        self.source.set(3, 1920)
        self.source.set(4, 1080)
        while mode == "video" and self.frame_count < self.config['camera']['skip']:
                self.read()
        self.frame_count = 0
    
    def load_mask(self):
        if self.config["camera"]["use_mask"]:
            self.mask = cv2.imread(self.config["mask"], cv2.IMREAD_UNCHANGED)
    
    def read(self):
        ret, frame_read = self.source.read()
        if frame_read is None or not ret:
            self.load_source()
            return self.read()
        if self.mask is not None:
            frame_read = cv2.addWeighted(frame_read, 1, self.mask, 1, 0, 3)
        self.frame_count += 1
        return frame_read
    
    def seconds(self):
        return round(self.frame_count/25)
    
    def save(self, frame):
        if self.config["camera"]["save"]:
            self.output.write(frame)
        
