import os

def gltf_pipeline(input_path, out_path, is_binary = True):
    command = 'gltf-pipeline.cmd -i '+input_path+' -o '+out_path+' -d'
    if is_binary:
        command += ' -b'
    os.system(command)
    # exists mains success
    return os.path.exists(out_path)
