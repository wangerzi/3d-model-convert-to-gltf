# python -m grpc_tools.protoc -I../../rpc/protos --python_out=. --grpc_python_out=. ../../rpc/protos/converter.proto
import sys
import grpc
import os
import time

sys.path.append(os.path.dirname(__file__))
import converter_pb2_grpc
import converter_pb2


def get_stub(target):
    channel = grpc.insecure_channel(target, (
        ('grpc.max_receive_message_length', -1),
        ('grpc.max_send_message_length', -1),
    ))
    stub = converter_pb2_grpc.ConverterStub(channel)
    return stub


def convert_file_and_save(target, t, source, dist, is_bin=False, need_draco=True, no_zip=False):
    stub = get_stub(target)
    with open(source, 'rb') as f:
        response = stub.convertToGltf(
            converter_pb2.convertReq(type=t, isBin=is_bin, file=f.read(), needDraco=need_draco, noZip=no_zip)
        )
        if response.file == b'':
            return False

        with open(dist, 'wb') as d:
            d.write(response.file)

    return True


def run():
    try:
        start_time = time.time()
        if convert_file_and_save("127.0.0.1:8999", 'stl', '../../../assets/test.stl', 'test.glb.zip', False, True, True):
            end_time = time.time()
            print("convert success", str(end_time - start_time), 's')
        else:
            print("convert failed")
    except Exception as err:
        print("convert exception:", err)


if __name__ == '__main__':
    run()
