import random
import shutil
import time
import os.path
import zipfile


class Upload:
    def __init__(self, base_dir="tmp"):
        self.base_dir = base_dir
        self.save_dir = ''
        self.save_path = ''
        self.zip = False

    def is_zip(self):
        return self.zip

    def get_base_dir(self):
        return self.base_dir

    def get_save_dir(self):
        return self.save_dir

    def get_save_path(self):
        return self.save_path

    def save(self, file: bytes):
        # pre: generate save dir and save path
        self.save_dir = os.path.join(self.base_dir, str(time.time()) + '.' + str(random.randint(0, 10000)))
        os.makedirs(self.save_dir, exist_ok=True)

        # 1. save to temp file path
        self.save_path = os.path.join(self.save_dir, 'upload.tmp')
        with open(self.save_path, 'wb') as f:
            f.write(file)
        self.zip = zipfile.is_zipfile(self.save_path)

        return self

    def unzip_save_file(self):
        # todo:: unzip file to self.save_dir
        pass

    def clear_source_file(self):
        if os.path.exists(self.save_path) and os.path.isfile(self.save_path):
            os.remove(self.save_path)
        return self

    def clear_save_dir(self):
        shutil.rmtree(self.save_dir)
