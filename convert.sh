dirPath=`pwd`
docker run -v $dirPath:$dirPath wj2015/3d-model-convert-to-gltf:v1.0 "conda run -n pythonocc python server/convert.sh $1 $2 $3"