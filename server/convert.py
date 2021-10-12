import shutil
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))

from service import Convert


def main():
    if len(sys.argv) < 3:
        print("Params not found, format: python convert.py [type] [file path] [out file path]")
        return False

    is_bin = True
    need_draco = True
    if len(sys.argv) > 3 and sys.argv[3][-4:] == 'gltf':
        is_bin = False
    if len(sys.argv) > 4 and sys.argv[4] == 'no-draco':
        need_draco = False

    out_convert_gltf_path = Convert.convert_by_type(sys.argv[1], os.path.abspath(sys.argv[2]), is_bin, need_draco)

    if len(sys.argv) > 3:
        out_file_path = sys.argv[3]
        if out_file_path != out_convert_gltf_path:
            shutil.move(out_convert_gltf_path, out_file_path)
    else:
        out_file_path = out_convert_gltf_path

    print(out_file_path)


if __name__ == '__main__':
    main()
