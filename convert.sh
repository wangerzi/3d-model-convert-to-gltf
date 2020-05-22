# convert.sh [stl|step|iges|obj] inputpath.stl outputpath.glb
dirPath=`pwd`
docker run -v $dirPath:$dirPath wj2015/3d-model-convert-to-gltf:v1.0 /bin/bash -c "cd $dirPath && conda run -n pythonocc python /opt/3d-model-convert-to-gltf/server/convert.py $1 $2 $3"