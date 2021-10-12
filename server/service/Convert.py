from exception.ConvertException import ConvertException
import hashlib
import time
from service import File
import os
from OCC.Extend.DataExchange import read_iges_file, read_step_file, read_stl_file, write_stl_file
from service.stl2gltf import stl_to_gltf
from service.GltfPipeline import gltf_pipeline, obj2gltf, fbx2gltf


# ########## model convert start

class BaseModel:
    def __init__(self):
        self.ext = []

    def get_ext(self):
        return self.ext

    @staticmethod
    def clear_file(*file_paths):
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.unlink(file_path)

    def handler(self, file_path, is_bin, need_draco):
        if not file_path:
            raise ConvertException("convert file can't be empty")
        if not (os.path.exists(file_path) and os.path.isfile(file_path)):
            raise ConvertException("convert file should be exists")


class StlModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.ext = ['stl']

    # unified convert config
    @staticmethod
    def write_by_shapes(shapes, convert_stl_path):
        return write_stl_file(shapes, convert_stl_path, 'binary', 0.03, 0.5)

    @staticmethod
    def check_binary(path_to_stl):
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

    @staticmethod
    def convert_stl_to_gltf(file_path, convert_stl_path, is_bin=False, clear_stl_source=False, clear_convert_stl=False,
                            need_draco=True):
        # todo:: remove too many flag
        # 1. convert binary stl to gltf
        if is_bin:
            convert_gltf_path = file_path + '.glb'
            # for draco
            dist_convert_gltf_path = file_path + '.draco' + '.glb'
            stl_to_gltf(convert_stl_path, convert_gltf_path, is_bin)
            convert_gltf_bin_path = ""
        else:
            output_path = os.path.dirname(file_path)
            # for draco
            stl_to_gltf(convert_stl_path, output_path, is_bin)
            dist_convert_gltf_path = file_path + '.gltf'
            convert_gltf_path = os.path.join(output_path, 'out.gltf')
            convert_gltf_bin_path = os.path.join(output_path, 'out.bin')
        # 2. gltf-pipeline
        if need_draco:
            try:
                if not gltf_pipeline(convert_gltf_path, dist_convert_gltf_path, is_bin):
                    raise ConvertException('gltf draco fail, file:' + convert_gltf_path)
            finally:
                StlModel.clear_file(convert_gltf_path)
                if convert_gltf_bin_path:
                    StlModel.clear_file(convert_gltf_bin_path)
        else:
            # no draco no out_convert_gltf_path
            dist_convert_gltf_path = convert_gltf_path

        if clear_stl_source:
            StlModel.clear_file(file_path)
        if clear_convert_stl:
            StlModel.clear_file(convert_stl_path)
        return dist_convert_gltf_path

    def handler(self, file_path, is_bin=False, need_draco=True):
        super(StlModel, self).handler(file_path, is_bin, need_draco)
        # read stl file, if not binary, convert to binary
        convert_stl_path = file_path + '.stl'
        clear_convert_stl = False
        if not self.check_binary(file_path):
            shapes = read_stl_file(file_path)
            self.write_by_shapes(shapes, convert_stl_path)
            clear_convert_stl = True
        else:
            convert_stl_path = file_path
        return self.convert_stl_to_gltf(file_path, convert_stl_path, is_bin, False, clear_convert_stl, need_draco)


class StpModel(BaseModel):
    def __init__(self):
        super(StpModel, self).__init__()
        self.ext = ['stp', 'step']

    def handler(self, file_path, is_bin, need_draco):
        super(StpModel, self).handler(file_path, is_bin, need_draco)
        # read stp file and convert to stl
        convert_stl_path = file_path + '.stl'
        try:
            shapes = read_step_file(file_path)
            StlModel.write_by_shapes(shapes, convert_stl_path)
            result = StlModel.convert_stl_to_gltf(file_path, convert_stl_path, is_bin, True, True, need_draco)
        finally:
            self.clear_file(convert_stl_path)
        return result


class IgesModel(BaseModel):
    def __init__(self):
        super(IgesModel, self).__init__()
        self.ext = ['igs', 'iges']

    def handler(self, file_path, is_bin, need_draco):
        super(IgesModel, self).handler(file_path, is_bin, need_draco)
        # read iges file and convert to stl
        convert_stl_path = file_path + '.stl'
        try:
            shapes = read_iges_file(file_path)
            StlModel.write_by_shapes(shapes, convert_stl_path)
            result = StlModel.convert_stl_to_gltf(file_path, convert_stl_path, is_bin, True, True, need_draco)
        finally:
            self.clear_file(convert_stl_path)
        return result


class ObjModel(BaseModel):
    def __init__(self):
        super(ObjModel, self).__init__()
        self.ext = ['obj']

    def handler(self, file_path, is_bin, need_draco):
        super(ObjModel, self).handler(file_path, is_bin, need_draco)
        if is_bin:
            convert_gltf_path = file_path + '.glb'
        else:
            convert_gltf_path = file_path + '.gltf'
        if not obj2gltf(file_path, convert_gltf_path, is_bin, need_draco):
            raise ConvertException('obj convert draco gltf fail, file:' + convert_gltf_path)
        return convert_gltf_path


class FbxModel(BaseModel):
    def __init__(self):
        super(FbxModel, self).__init__()
        self.ext = ['fbx']

    def handler(self, file_path, is_bin, need_draco):
        super(FbxModel, self).handler(file_path, is_bin, need_draco)
        if is_bin:
            convert_gltf_path = file_path + '.glb'
        else:
            convert_gltf_path = file_path + '.gltf'

        if not fbx2gltf(file_path, convert_gltf_path, is_bin, need_draco):
            raise ConvertException('fbx convert draco gltf fail, file:' + convert_gltf_path)
        return convert_gltf_path


class ModelFactory:
    @staticmethod
    def make_model(file_type):
        if file_type == 'stl':
            return StlModel()
        elif file_type == 'stp':
            return StpModel()
        elif file_type == 'iges':
            return IgesModel()
        elif file_type == 'obj':
            return ObjModel()
        elif file_type == 'fbx':
            return FbxModel()
        else:
            raise ConvertException(file_type + ' model is not support')


def convert_by_type(file_type, file_path, is_bin=False, need_draco=True):
    file_type = file_type.lower()
    # 1. check file_type
    if file_type not in ['stl', 'stp', 'iges', 'obj', 'fbx']:
        raise ConvertException('convert file type is not support, type:' + file_type)
    result = False
    # 1.1 check file_path
    if not os.path.exists(file_path):
        raise ConvertException('convert file need exists, file:' + file_path)
    # 2. file_type to handler
    model = ModelFactory.make_model(file_type)

    result = model.handler(file_path, is_bin, need_draco)
    return result

# ########## model convert end
