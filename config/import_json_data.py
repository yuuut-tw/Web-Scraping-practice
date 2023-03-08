import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir)))

import json
import config.import_config as cf


def get_member_name():
    
    file_path = rf"{cf.config['project_path']}/data/group_member.json"
    
    with open(file_path, 'r') as f:
        data = json.loads(f.read())

    return data