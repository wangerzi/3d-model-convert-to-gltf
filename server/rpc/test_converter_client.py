import grpc
import converter_pb2_grpc
import converter_pb2
import os


def get_stub(target):
    channel = grpc.insecure_channel(target, (
        ('grpc.max_receive_message_length', -1),
        ('grpc.max_send_message_length', -1),
    ))
    stub = converter_pb2_grpc.ConverterStub(channel)
    return stub


def convert_file_and_save(target, t, source, dist, is_bin=False):
    stub = get_stub(target)
    with open(source, 'rb') as f:
        response = stub.convertToGltf(
            converter_pb2.convertReq(type=t, isBin=is_bin, file=f.read())
        )

        with open(dist, 'wb') as d:
            d.write(response.file)

    return True


def run():
    if convert_file_and_save("127.0.0.1:8999", 'stl', '../../assets/test.stl', 'test.glb.zip', True):
        print("convert success")
    else:
        print("convert failed")


if __name__ == '__main__':
    run()
