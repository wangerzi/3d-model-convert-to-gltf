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
        self.source_zip_path = ''
        self.zip = False

    def is_zip(self):
        return self.zip

    def get_source_zip_path(self):
        return self.source_zip_path

    def get_base_dir(self):
        return self.base_dir

    def get_save_dir(self):
        return self.save_dir

    def get_save_path(self):
        return self.save_path

    def save(self, file_bytes):
        # pre: generate save dir and save path
        self.save_dir = os.path.join(self.base_dir, str(time.time()) + '.' + str(random.randint(0, 10000)))
        os.makedirs(self.save_dir, exist_ok=True)

        # 1. save to temp file path
        self.save_path = os.path.join(self.save_dir, 'upload-' + str(random.randint(0, 10000)) + '.tmp')
        with open(self.save_path, 'wb') as f:
            f.write(file_bytes)
        self.zip = zipfile.is_zipfile(self.save_path)

        return self

    def unzip_save_file_with_clear_source(self):
        if self.is_zip():
            self.unzip_save_file()
            self.clear_source_file()
        return self

    def unzip_save_file(self):
        # unzip self.save_path to self.save_dir
        if self.is_zip():
            with zipfile.ZipFile(self.save_path) as z:
                z.extractall(self.save_dir)
        pass

    def clear_source_file(self):
        self.clear_file(self.save_path)
        return self

    def clear_file(self, file_path):
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
        return self

    def clear_save_dir(self):
        if os.path.exists(self.save_path):
            shutil.rmtree(self.save_dir)
        return self

    def zip_source_dir(self):
        if os.path.isdir(self.save_dir):
            files = self._save_dir_file_list()
            zip_path = os.path.join(self.save_dir, 'zip-temp-' + str(random.randint(0, 10000)) + '.zip')

            with zipfile.ZipFile(zip_path, 'w') as z:
                for i in range(0, len(files)):
                    z.write(files[i])
            self.source_zip_path = zip_path
        return self

    def scan_first_ext_file(self, ext=""):
        if len(ext) <= 0:
            return ""
        ext = ext.lower()
        files = self._save_dir_file_list()
        for i in range(0, len(files)):
            if files[i].lower().endswith("." + ext):
                return files[i]
        return ""

    def _save_dir_file_list(self):
        files = []
        for f in os.listdir(self.save_dir):
            print('file scan', f)
            if not f in ['', '.', '..']:
                files.append(os.path.join(self.save_dir, f))
        return files
