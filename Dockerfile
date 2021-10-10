# docker build . -t wj2015/3d-model-convert-to-gltf:v1.6
# startup docker by: docker run -d -p 8999:8999 wj2015/3d-model-convert-to-gltf:latest
# you can debug by: docker run -it --rm -v `pwd`:/opt/3d-model-convert-to-gltf/ wj2015/3d-model-convert-to-gltf:latest /bin/bash
# you can also execute `conda activate pythonocc` to enter the environment.
FROM continuumio/miniconda3:4.10.3-alpine
LABEL maintainer=admin@wj2015.com

#RUN cd /opt && \
    # if built in china, you should config this mirror
#    /opt/conda/bin/conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ && \
#    /opt/conda/bin/conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ && \
#    /opt/conda/bin/conda config --set show_channel_urls yes && \
#    /opt/conda/bin/conda activate pythonocc
#    git clone https://github.com/wangerzi/3d-model-convert-to-gltf.git && \
RUN conda create -n pythonocc -c dlr-sc -c pythonocc pythonocc-core=7.4.0rc1 -y
# install 12.0.0 nodejs
RUN wget -q https://nodejs.org/download/release/v12.0.0/node-v12.0.0-linux-x64.tar.gz && \
    tar -zxvf node-v12.0.0-linux-x64.tar.gz && rm -rf node-v12.0.0-linux-x64.tar.gz
#    ln -s bin/node /usr/local/bin/node && ln -s bin/npm /usr/local/bin/npm && chmod -R a+x /usr/local/bin &&\
ENV PATH $PATH:/node-v12.0.0-linux-x64/bin/
RUN apk --update add linux-headers binutils-gold gnupg libstdc++ mesa-dev && rm -rf /var/cache/apk/* && \
    npm install -g gltf-pipeline obj2gltf fbx2gltf && \
    ln -s /node-v12.0.0-linux-x64/lib/node_modules/fbx2gltf/bin/Linux/FBX2glTF /node-v12.0.0-linux-x64/bin/fbx2gltf
COPY . /opt/3d-model-convert-to-gltf
# install pip requirements
RUN cd /opt/3d-model-convert-to-gltf && \
    conda run -n pythonocc pip install -r server/requirements.txt
WORKDIR /opt/3d-model-convert-to-gltf

EXPOSE 8999

CMD conda run -n pythonocc python /opt/3d-model-convert-to-gltf/server/rpc_server.py
