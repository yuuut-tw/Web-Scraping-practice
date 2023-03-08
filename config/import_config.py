import json
import pathlib

root_path = str(pathlib.Path(__file__).parent.absolute())

def initialize(conf):
    global config
    config = conf
    

with open(root_path + '/config.txt', "r") as f:
    conf = json.load(f)


initialize(conf)
