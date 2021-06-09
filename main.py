import net
import cv2
from camera import Camera
from vehicle import Vehicle
from people import People
from crossroad import Crossroad
import json
import os


def save_data(queues: list, path: str):
    json_queues = [{} for _ in queues]
    if not os.path.exists(path):
        with open(path, "w") as write_file:
            json.dump([], write_file)

    with open(path, "r") as read_file:
        old_json = json.load(read_file)

    for qid, queue in enumerate(queues):
        json_queues[qid]['id'] = qid
        json_queues[qid]['objects'] = {}
        for obj in queue:
            json_queues[qid]['objects'][obj.in_queue_id] = {}
            json_queues[qid]['objects'][obj.in_queue_id]["id"] = obj.id
            json_queues[qid]['objects'][obj.in_queue_id]["class"] = obj.network.classes[obj.obj_class]
            json_queues[qid]['objects'][obj.in_queue_id]["time"] = obj.way_time()

    save_json = {"cycle_id": save_data.count, "queues": json_queues}
    old_json.append(save_json)
    with open(path, "w") as write_file:
        json.dump(old_json, write_file)

    save_data.count += 1
save_data.count = 0


with open("configs/pob40pob.json") as cfg:
    config = json.load(cfg)

vehicles_net = net.Network("vehicles", Vehicle)
vehicles_net.load_net()
people_net = net.Network("people", People)
people_net.load_net()
camera = Camera(vehicles_net, config["camera_cfg"])
crossroad = Crossroad(config, camera)

while True:
    frame = camera.read()
    
    vframe = vehicles_net.update(frame)
    pframe = vehicles_net.update(frame)
    vehicles_net.draw(vframe)
    people_net.draw(pframe)
    frame = crossroad.draw_areas(vframe)
    frame = crossroad.draw_areas(pframe)
    crossroad.update_objects(vehicles_net.get_objects())  
    crossroad.update_objects(people_net.get_objects())
    
    if crossroad.check_tackt():           
        print(*crossroad.queues)
        save_data(crossroad.queues, config['logfile'])
        crossroad.reset_queues()

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    camera.save(image)
    cv2.imshow('frame', image)
    cv2.waitKey(1)
    ch = 0xFF & cv2.waitKey(1)
    if ch == 27:
        break
