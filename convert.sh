# convert.sh [stl|stp|iges|obj|fbx] inputpath.stl outputpath.gltf
# convert.sh [stl|stp|iges|obj|fbx] inputpath.stl outputpath.glb
inputPath=$(
  cd "$(dirname "$2")"
  pwd
)
inputFile=$inputPath/`basename $2`
outPath=$(
  cd "$(dirname "$3")"
  pwd
)
outFile=$outPath/`basename $3`
docker run -v $inputPath:$inputPath -v $outPath:$outPath wj2015/3d-model-convert-to-gltf:v1.6 /bin/bash -c "cd $inputPath && conda run -n pythonocc python /opt/3d-model-convert-to-gltf/server/convert.py $1 $inputFile $outFile"
