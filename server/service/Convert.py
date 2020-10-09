from exception.ConvertException import ConvertException
import hashlib
import time
from service import File
import os
from OCC.Extend.DataExchange import read_iges_file, read_step_file, read_stl_file, write_stl_file
from service.stl2gltf import stl_to_gltf
from setting import config
from service.GltfPipeline import gltf_pipeline, obj2gltf, fbx2gltf


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

# ########## model convert start
def convert_by_type(file_type, file_path, is_bin=False):
    file_type = file_type.lower()
    # 1. check file_type
    if file_type not in ['stl', 'stp', 'iges', 'obj', 'fbx']:
        raise ConvertException('convert file type is not support, type:' + file_type)
    result = False
    # 1.1 check file_path
    if not os.path.exists(file_path):
        raise ConvertException('convert file need exists, file:' + file_path)
    # 2. file_type to handler
    if file_type == 'stl':
        result = convert_stl_handler(file_path, is_bin)
    elif file_type == 'stp':
        result = convert_stp_handler(file_path, is_bin)
    elif file_type == 'iges':
        result = convert_iges_handler(file_path, is_bin)
    elif file_type == 'obj':
        result = convert_obj_handler(file_path, is_bin)
    elif file_type == 'fbx':
        result = convert_fbx_handler(file_path, is_bin)
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
    face_bytes = float_bytes * 12 + 2

    with open(path_to_stl, "rb") as f:
        f.seek(header_bytes)  # skip 80 bytes headers

        num_faces_bytes = f.read(unsigned_long_int_bytes)
        number_faces = struct.unpack("<I", num_faces_bytes)[0]

        # the vec3_bytes is for normal
        stl_assume_bytes = header_bytes + unsigned_long_int_bytes + number_faces * (
                vec3_bytes * 3 + spacer_bytes + vec3_bytes)
        return stl_assume_bytes == os.path.getsize(path_to_stl)
    return False


def convert_stl_handler(file_path, is_bin=False):
    # 1. read stl file, if not binary, convert to binary
    convert_stl_path = file_path + '.stl'
    if not check_stl_binary(file_path):
        shapes = read_stl_file(file_path)
        write_stl_by_shapes(shapes, convert_stl_path)
    else:
        convert_stl_path = file_path
    return convert_stl_to_draco_gltf(file_path, convert_stl_path, is_bin)


def convert_stp_handler(file_path, is_bin=False):
    # 1. read stp file and convert to stl
    convert_stl_path = file_path + '.stl'
    shapes = read_step_file(file_path)
    write_stl_by_shapes(shapes, convert_stl_path)
    result = convert_stl_to_draco_gltf(file_path, convert_stl_path, is_bin)

    if not config['app']['save_convert_temp_file']:
        clear_file(convert_stl_path)
    return result


def convert_iges_handler(file_path, is_bin=False):
    # 1. read iges file and convert to stl
    convert_stl_path = file_path + '.stl'
    shapes = read_iges_file(file_path)
    write_stl_by_shapes(shapes, convert_stl_path)
    result = convert_stl_to_draco_gltf(file_path, convert_stl_path, is_bin)

    if not config['app']['save_convert_temp_file']:
        clear_file(convert_stl_path)
    return result


def convert_stl_to_draco_gltf(file_path, convert_stl_path, is_bin=False):
    # 2. convert binary stl to gltf
    if is_bin:
        convert_gltf_path = file_path + '.glb'
        out_convert_gltf_path = file_path + '.zip' + '.glb'
        stl_to_gltf(convert_stl_path, convert_gltf_path, is_bin)
    else:
        convert_gltf_path = file_path + '.gltf'
        output_path = os.path.dirname(convert_gltf_path)
        out_convert_gltf_path = os.path.join(output_path, 'out.gltf')
        stl_to_gltf(convert_stl_path, output_path, is_bin)
    # 3. gltf-pipeline
    if not gltf_pipeline(convert_gltf_path, out_convert_gltf_path):
        raise ConvertException('gltf draco fail, file:' + convert_gltf_path)
    if not config['app']['save_upload_temp_file']:
        clear_file(file_path, convert_stl_path)
    if not config['app']['save_convert_temp_file']:
        clear_file(convert_gltf_path)
    return out_convert_gltf_path


def clear_file(*file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.unlink(file_path)


def convert_obj_handler(file_path, is_bin=False):
    if is_bin:
        convert_gltf_path = file_path + '.glb'
    else:
        convert_gltf_path = file_path + '.gltf'
    if not obj2gltf(file_path, convert_gltf_path, is_bin):
        raise ConvertException('obj convert draco gltf fail, file:' + convert_gltf_path)
    return convert_gltf_path


def convert_fbx_handler(file_path, is_bin=False):
    if is_bin:
        convert_gltf_path = file_path + '.glb'
    else:
        convert_gltf_path = file_path + '.gltf'

    if not fbx2gltf(file_path, convert_gltf_path, is_bin):
        raise ConvertException('fbx convert draco gltf fail, file:' + convert_gltf_path)
    return convert_gltf_path
# ########## model convert end
