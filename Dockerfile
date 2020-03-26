from continuumio/anaconda
LABEL maintainer=admin@wj2015.com

RUN cd /opt && \
    /opt/conda/bin/conda create -n pythonocc -c dlr-sc -c pythonocc pythonocc-core=7.4.0rc1 -y --quiet && \
    activate pythonocc && \
    pip install aiohttp pyaml && \
    git clone https://github.com/wangerzi/3d-model-convert-to-gltf.git && \
    cd 3d-model-convert-to-gltf/server && \
CMD ['python', '/opt/3d-model-convert-to-gltf/server/main.py']
