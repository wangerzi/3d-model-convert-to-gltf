from exception.ConvertException import ConvertException
import json
import hashlib
import time
from service import File

def make_queue_json(request, data, model_type="stl"):
    config = request.app['config']
    # save file to path
    save = data['file']
    file_save_path = File.save_file(save.file, save.filename, config['upload']['path'])

    # create unique req_id
    req_id = make_queue_id(file_save_path)

    return req_id, {
        'req_id': req_id,
        'type': model_type,
        'file': file_save_path,
        'customize_data': data['customize_data'],
        'status': 0,
        'result': {}
    }

def make_queue_id(file_save_path):
    return hashlib.sha1(str(file_save_path + str(time.time())).encode('utf-8')).hexdigest()

# define redis keys
waiting_list_key = '3d-preview-model-waiting'
convert_success_key = '3d-preview-model-convert-success'
info_key_prefix = '3d-preview-model-data-'

# get list all, every time get 20(default) items
def scan_list(redis, name, count=20):
    index = 0
    while True:
        data_list=redis.lrange(name,index,count+index-1)
        if not data_list:
            return
        index+=count
        for item in data_list:
            yield item

def list_item_pos(redis, name, value):
    index = 1
    for item in scan_list(redis, name):
        if value == item:
            return index
        index += 1
    return -1

def add_to_queue(redis, req_id, json_dict):
    # add convert information
    save_convert_information(redis, req_id, json_dict)
    # add to 3d-preview-model-waiting (after information)
    redis.lpush(waiting_list_key, req_id)

def save_convert_information(redis, req_id, json_dict):
    redis.setex(info_key_prefix + str(req_id), 86400 * 2, json.dumps(json_dict))

def get_convert_information(redis, req_id):
    json_str = redis.get(info_key_prefix + str(req_id))

    if json_str == None:
        raise ConvertException('convert file information is not found,req_id: ' + str(req_id))
    return json.loads(json_str)

# get waiting mission
def get_wait_mission(redis):
    _, req_id = redis.blpop(waiting_list_key)
    return req_id, get_convert_information(redis, req_id)

def get_wait_mission_len(redis):
    return int(redis.llen(waiting_list_key))

# search mission position
def get_wait_mission_pos(redis, req_id):
    result = {
            "current": -1,
            "total": 0,
            "status": 0 # 0:waiting, 1:converting, 2:success
    }
    # get total
    result['total'] = get_wait_mission_len(redis)
    # get information
    json_dict = get_convert_information(redis, req_id)
    # convert status = 0
    result['status'] = json_dict['status']
    if json_dict['status'] == 0:
        # means waiting, so need found pos at list
        pos = list_item_pos(redis, waiting_list_key, req_id)
        if pos == -1:
            result['status'] = 1
        # can't found means dealing
        result['current'] = pos > 0 and pos or 1
    else:
        result['status'] = 2
    return result

# init notice times
def notice_times_init(redis, req_id):
    # update notice hash
    return redis.hset(convert_success_key, str(req_id), 0)

# notice times ++
def notice_times_up(redis, req_id):
    return redis.hincrby(convert_success_key, str(req_id), 1)

# remove info and notice
def convert_remove(redis, req_id):
    redis.delete(info_key_prefix + str(req_id))
    return redis.hdel(redis, str(req_id))

# mark req_id convert success
def convert_success(redis, req_id, result):
    # remove other information
    convert_remove(redis, req_id)
    # update information
    json_dict = get_convert_information(redis, req_id)
    json_dict['stauts'] = 1
    json_dict['result'] = result

    return save_convert_information(redis, req_id, json_dict)

########### model convert start
########### model convert end
