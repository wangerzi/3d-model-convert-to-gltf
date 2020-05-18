from exception.ConvertException import ConvertException
import json
import hashlib
import time
from service import File
import os
from OCC.Extend.DataExchange import read_iges_file,read_step_file,read_stl_file,write_stl_file
from service.stl2gltf import stl_to_gltf

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
def convert_by_type(file_type, file_path):
    file_type = file_type.lower()
    # 1. check file_type
    if file_type not in ['stl', 'stp', 'iges', 'obj']:
        raise ConvertException('convert file type is not support, type:' + file_type)
    result = False
    # 1.1 check file_path
    if not os.path.exists(file_path):
        raise ConvertException('convert file need exists, file:' + file_path)
    # 2. file_type to handler
    if file_type == 'stl':
        result = convert_stl_handler(file_path)
    elif file_type == 'stp':
        result = convert_stp_handler(file_path)
    elif file_type == 'iges':
        result = convert_iges_handler(file_path)
    elif file_type == 'obj':
        result = convert_obj_handler(file_path)
    return result

# unified convert config
def write_stl_by_shapes(shapes, convert_stl_path):
    return write_stl_file(shapes, convert_stl_path, 'binary', 0.03, 0.5)
def check_stl_binary(path_to_stl):
    import struct
    header_bytes = 80
    unsigned_long_int_bytes = 4
    float_bytes = 4
    vec3_bytes = 4 * 3
    spacer_bytes = 2
    num_vertices_in_face = 3

    vertices = {}
    indices = []

    unpack_face = struct.Struct("<12fH").unpack
    face_bytes = float_bytes*12 + 2

    with open(path_to_stl, "rb") as f:
        f.seek(header_bytes) # skip 80 bytes headers

        num_faces_bytes = f.read(unsigned_long_int_bytes)
        number_faces = struct.unpack("<I", num_faces_bytes)[0]

        # the vec3_bytes is for normal
        stl_assume_bytes = header_bytes + unsigned_long_int_bytes + number_faces * (vec3_bytes*3 + spacer_bytes + vec3_bytes)
        return stl_assume_bytes == os.path.getsize(path_to_stl)
    return False


def convert_stl_handler(file_path):
    # 1. read stl file, if not binary, convert to binary
    convert_stl_path = file_path + '.stl'
    if not check_stl_binary(file_path):
        shapes = read_stl_file(file_path)
        write_stl_by_shapes(shapes, convert_stl_path)
    else:
        convert_stl_path = file_path
    return convert_stl_to_draco_gltf(file_path, convert_stl_path)

def convert_stp_handler(file_path):
    # 1. read stp file and convert to stl
    convert_stl_path = file_path + '.stl'
    shapes = read_step_file(file_path)
    write_stl_by_shapes(shapes, convert_stl_path)
    return convert_stl_to_draco_gltf(file_path, convert_stl_path)

def convert_iges_handler(file_path):
    # 1. read iges file and convert to stl
    convert_stl_path = file_path + '.stl'
    shapes = read_iges_file(file_path)
    write_stl_by_shapes(shapes, convert_stl_path)
    return convert_stl_to_draco_gltf(file_path, convert_stl_path)



from service.GltfPipeline import gltf_pipeline, obj2gltf
def convert_stl_to_draco_gltf(file_path, convert_stl_path):
    # 2. convert binary stl to gltf
    convert_gltf_path = file_path + '.glb'
    stl_to_gltf(convert_stl_path, convert_gltf_path, True)
    # 3. gltf-pipeline
    out_convert_gltf_path = file_path + '.zip' + '.glb'
    if not gltf_pipeline(convert_gltf_path, out_convert_gltf_path):
        raise ConvertException('gltf draco fail, file:' + convert_gltf_path)
    from setting import config
    if not config['app']['save_upload_temp_file']:
        clear_file(file_path, convert_stl_path, convert_gltf_path)
    return out_convert_gltf_path

def clear_file(*file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.unlink(file_path)
def convert_obj_handler(file_path):
    convert_gltf_path = file_path + '.glb'
    if not obj2gltf(file_path, convert_gltf_path):
        raise ConvertException('obj convert draco gltf fail, file:' + convert_gltf_path)
    return convert_gltf_path
########### model convert end
