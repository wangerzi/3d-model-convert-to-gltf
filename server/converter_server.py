import logging
import sys
from concurrent import futures

import grpc

# from rpc import converter_pb2
# from rpc import converter_pb2_grpc
from service import upload

sys.path.append('./rpc')
import converter_pb2
import converter_pb2_grpc


class ConverterService(converter_pb2_grpc.ConverterServicer):
    def convertToGltf(self, request, context):
        try:
            service = upload.Upload()
            service.save(request.file)
            print("receive and handle ", request.type, service.get_save_path(), service.is_zip())
            # service.clear_source_file()
        finally:
            service.clear_save_dir()
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
