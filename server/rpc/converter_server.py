import zipfile
from concurrent import futures
import grpc
import logging

import converter_pb2
import converter_pb2_grpc


class ConverterService(converter_pb2_grpc.ConverterServicer):
    def convertToGltf(self, request, context):
        upload_file = 'upload.tmp'
        with open(upload_file, 'wb') as f:
            f.write(request.file)
        is_zip = zipfile.is_zipfile(upload_file)
        print("receive and handle ", request.type, is_zip)
        return converter_pb2.convertResp(file=request.file)


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=(
            ('grpc.max_receive_message_length', -1),
            ('grpc.max_send_message_length', -1),
        )
    )
    converter_pb2_grpc.add_ConverterServicer_to_server(ConverterService(), server)

    target = "[::]:8999"
    server.add_insecure_port(target)
    server.start()
    print("server at ", target)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
