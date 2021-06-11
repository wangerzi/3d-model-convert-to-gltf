## Python demo

At first, you should generate grpc code by grpc tools. Reference for official [Basics tutorial](https://grpc.io/docs/languages/python/basics/)

If you only want to run the example code ,you can skip to **Connect to server** directly.

> **Important notice**: the `grpc.max_receive_message_length` and `grpc.max_send_message_length` suggest set `-1`, because sometimes we want to convert a heavy model.

### Install `grpcio-tools`

```shell script
python -m pip install grpcio-tools
```

### Generate code

If you have

```shell script
python -m grpc_tools.protoc -I../../rpc/protos --python_out=. --grpc_python_out=. ../../rpc/protos/converter.proto
```

### Connect to server

I guess you are already run `rpc_server.py` at `127.0.0.1:8999`, if you have another port or another ip, you can change the code under there

If you want to convert another model, change the third param to change (support zip / source type file).

```python
def run():
    if convert_file_and_save("127.0.0.1:8999", 'stl', '../../../assets/test.stl', 'test.glb.zip', True):
        print("convert success")
    else:
        print("convert failed")
```