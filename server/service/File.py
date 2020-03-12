import time
import os

def save_file(file_obj, filename, upload_path):
    save_path = upload_path + str(time.time()) + '/'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    save_file_path = save_path + filename
    with open(save_file_path, 'wb') as f:
        f.write(file_obj.read())
        f.close()
    return save_file_path
