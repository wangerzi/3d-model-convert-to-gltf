import service.Convert
from exception.ConvertException import ConvertException
import threading

def setup_background(app):
    create_threads(app)

threads = []
def create_threads(app):
    process_num = int(app['config']['app']['background_process_num'])
    if process_num <= 0:
        process_num = 1
    for i in range(0, process_num):
        thread = threading.Thread(target=handle_background(app, convert_background))
        thread.start()
        threads.append(thread)

    return threads

# pass variable for multi threading
def handle_background(app, callback):
    def func():
        callback(app)
    return func

def convert_background(app):
    while True:
        # get information
        try:
            req_id, json_dict = service.Convert.get_wait_mission(app['redis'])
        except ConvertException as err:
            print('Get information error ', err)
        except Exception as err:
            print('Unexcpeted error', err)
        # read and convert
        # notice result
