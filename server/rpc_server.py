import logging
import sys
import os
from concurrent import futures

import grpc

sys.path.append(os.path.join(os.path.dirname(__file__), 'rpc'))

from rpc import converter_pb2
from rpc import converter_pb2_grpc
from service import upload
from service import Convert


class ConverterService(converter_pb2_grpc.ConverterServicer):
    def convertToGltf(self, request, context):
        up_service = upload.Upload()
        try:
            # save and unzip
            up_service.save(request.file).unzip_save_file_with_clear_source()

            # find source model path
            source_model_path = ''
            model = Convert.ModelFactory.make_model(request.type)
            if up_service.is_zip():
                model_ext = model.get_ext()
                # todo:: we can more effective
                for i in range(0, len(model_ext)):
                    find_path = up_service.scan_first_ext_file(model_ext)
                    if find_path:
                        # find first file
                        source_model_path = find_path
                        break
            else:
                source_model_path = up_service.get_save_path()

            # convert and clear source_model, then zip and response
            result = model.handler(source_model_path, request.isBin)
            zip_path = up_service.clear_file(source_model_path).zip_source_dir().get_source_zip_path()

            print("receive and handle ", request.type, up_service.get_save_path(), up_service.is_zip(), 'convert result', result, 'zip path', zip_path)

            with open(zip_path) as f:
                return converter_pb2.convertResp(file=f.read())
        finally:
            up_service.clear_save_dir()
            return converter_pb2.convertResp(file=None)


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
