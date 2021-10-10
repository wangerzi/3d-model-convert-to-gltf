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
from exception.ConvertException import ConvertException


class ConverterService(converter_pb2_grpc.ConverterServicer):

    def convertToGltf(self, request, context):
        up_service = upload.Upload()

        response = converter_pb2.convertResp(file=None)
        print("receive request", request.type, request.isBin, ", need_draco: ", request.needDraco, ", no_zip: ",
              request.noZip, " size:", len(request.file) / 1024 / 1024, 'Mb')
        try:
            # save and unzip
            up_service.save(request.file).unzip_save_file_with_clear_source()

            # find source model path
            source_model_path = ''
            model = Convert.ModelFactory.make_model(request.type)
            if up_service.is_zip():
                model_ext = model.get_ext()
                find_path = up_service.scan_ext_file(model_ext, True)
                if find_path and len(find_path) > 0:
                    # find first file
                    source_model_path = find_path[0]
                else:
                    raise ConvertException("can't found match source model")

            else:
                source_model_path = up_service.get_save_path()

            # convert and clear source_model, then zip and response
            result = model.handler(source_model_path, request.isBin, request.needDraco)

            # special logic, if convert to glb, only zip glb file
            zip_source_ext = None
            if request.isBin:
                zip_source_ext = ['glb']

            if request.isBin and request.noZip:
                up_service.clear_file(source_model_path)
                find_path = up_service.scan_ext_file(['glb'], True)
                if find_path and len(find_path) > 0:
                    result_file_path = find_path[0]
                else:
                    raise ConvertException("can't found glb result file")
            else:
                result_file_path = up_service.clear_file(source_model_path).zip_source_dir(
                    zip_source_ext).get_source_zip_path()

            print("receive and handle ", request.type, up_service.get_save_path(), up_service.is_zip(),
                  'found source file', source_model_path, 'convert result', result, 'result path', result_file_path,
                  "zip size:",
                  ((os.path.getsize(result_file_path) / 1024 / 1024) if os.path.exists(result_file_path) else 'None'),
                  "Mb")

            with open(result_file_path, 'rb') as f:
                response = converter_pb2.convertResp(file=f.read())
        except Exception as err:
            print("convert error:", err)
        finally:
            up_service.clear_save_dir()
            return response


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=1),
        options=(
            ('grpc.max_receive_message_length', -1),
            ('grpc.max_send_message_length', -1),
        )
    )
    converter_pb2_grpc.add_ConverterServicer_to_server(ConverterService(), server)

    target = "0.0.0.0:8999"
    server.add_insecure_port(target)
    server.start()
    print("server at ", target)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
