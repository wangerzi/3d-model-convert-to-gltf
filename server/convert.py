import service.Convert
import sys, shutil

def main():
    if len(sys.argv) < 3:
        print("Params not found, format: python convert.py [type] [file path] [out file path]")
        return False
    out_convert_gltf_path = service.Convert.convert_by_type(sys.argv[1], sys.argv[2])

    if len(sys.argv) > 3:
        out_file_path = sys.argv[3]
        if out_file_path != out_convert_gltf_path:
            shutil.move(out_convert_gltf_path, out_file_path)
    else:
        out_file_path = out_convert_gltf_path

    print(out_file_path)

if __name__ == '__main__':
    main()
