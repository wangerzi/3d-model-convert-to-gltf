# 3DModelConvertToGltf - An Unified Model Format Conversion Tool

## Document

English|[中文](README_ZH.md)

The main reason for this project is that I encountered a scenario where **the STEP and IGES models need to be displayed on the Web**, but the web3d  libraries on the market do not support this format, and the direct display of STL files uploaded by users will consume a lot of bandwidth or CDN Traffic, converted to compressed gltf would be more appropriate.

Demo assets model effect compare:

| model type | file path                | Convert time | Origin size | After size |
| ---------- | ------------------------ | ------------ | ----------- | ---------- |
| stl        | assets/test.stl          | 2368.890ms   | 7.6 MB      | 86 KB      |
| iges       | assets/test.iges         | 1641.226ms   | 1 M         | 111 KB     |
| stp        | assets/test.stp          | 2969.200ms   | 5.1 MB      | 217 KB     |
| fbx        | assets/Samba Dancing.fbx | <1000ms      | 3.7 MB      | 614 KB     |

**support input format：** STL/IGES/STP/OBJ/FBX

**support output format：** GLTF/GLB

I organized my thoughts into a blog: [STEP and IGES models are converted to the web-friendly glb format](https://blog.wj2015.com/2020/03/08/step%e5%92%8ciges%e6%a8%a1%e5%9e%8b%e8%bd%ac%e6%8d%a2%e4%b8%ba%e9%80%82%e7%94%a8web%e7%9a%84glb%e6%a0%bc%e5%bc%8f/)

> PS: My blog is write by Chinese, if you are non-Chinese native speaker, you should take a Google Translate tool for well.

**Project status:** stable


## Features

- [x] Basic project structure planning and interface design
- [x] Conversion and compression code implementation
- [x] Add obj format to darco gltf
- [x] ~~Related API implementation(not so useful, droped)~~
- [x] docker image packaging
- [x] write easy to use convert.sh
- [x] online convert preview
- [ ] [bug] stp convert to gltf is too large
- [x] [bug] stl convert to gltf missing node (result: stl format have no node information, [https://en.wikipedia.org/wiki/STL_(file_format)](https://en.wikipedia.org/wiki/STL_(file_format)))
- [ ] [bug] stp/iges convert to gltf missing node
- [x] grpc support
- [ ] rpc should response error detail
- [x] rpc api should support no draco
- [ ] [bug] rpc docker server logs output problems


## Using this project

- Lexcent 3D Printing
  > You can scan this following qrcode by Wechat, it's helpful for 3d printing and preview everywhere.
  ![img](./assets/using/lixian.jpg)

## Version update

##### v1.7 pre release

convert.sh support no-draco option

##### v1.6 2021-10-10 13:08

Smaller docker images, from 4.42GB to 1.87GB, fix docker can't running problems.

##### v1.5 2021-07-25 16:06

Fix some bugs, support no draco convert

##### v1.4 2021-06-11 17:20

Support GRPC, convert code refactor, fix bugs.

##### v1.3 2020-06-24 17:19

Add English document, fix bugs.

##### v1.0 2020-05-21 19:08

Basic commit, core feature complete, support shell convert.


## Why not assmip

I tried to use [assimp](https://github.com/assimp/assimp), but the result under the test of `stl/iges/obj` conversion is not good. I used [https://hub.docker.com/r/dylankenneally/assimp](https://hub.docker.com/r/dylankenneally/assimp) docker environment for testing, you can have a try on it.

## Why not implement API in this project

Model conversion is a very performance-consuming and slow-speed service. The upload and download of the model will consume bandwidth. **If it is deployed directly on your own server, it will be a very bandwidth-intensive and CPU-consuming task**. For the most common method to upload and download large files is to **introduce OSS and CDN with dynamic expansion of queues and back-end services**, but the deployment cost and implementation cost will be relatively high.

## Quick Start

Due to the trouble of environment configuration and other reasons, the command line mode **still needs to rely on docker**. **The command line mode is suitable for simple invocation on the server side.** The conversion process blocks the processes to be synchronized and cannot be deployed in a distributed manner to increase concurrency.The most recommended way is to use **grpc with docker** deployment to make rpc, which can be synchronous or asynchronous, and will be **easy to extend**.

> PS：When there are too many simultaneous conversion models in the command line mode or a single model is too large, there is a risk that the server providing the web service is stuck

### Online convert previewer

You can convert model online (<100MB) powered by [modelbox-sdk](https://github.com/wangerzi/modelbox-sdk)，preview link: [https://wangerzi.gitee.io/modelbox-sdk/examples/index.html](https://wangerzi.gitee.io/modelbox-sdk/examples/index.html)

### GRPC Mode

Based on GRPC, and it will be more convient to **build a dynamically expanded service cluster**, we support uploading zip/model source files, for the compatibility of each model, **response files are all in zip**, you need to decompress it after got it.

You should run server-side rpc service by docker, please make sure 8999 port is usable and `wj2015/3d-model-convert-to-gltf:latest` image is up to date, command:

```shell
$ docker pull wj2015/3d-model-convert-to-gltf:latest
$ docker run -d -p 8999:8999 wj2015/3d-model-convert-to-gltf:latest
```

When using grpc in this project, please copy  `server/rpc/protos/converter.proto` , and generate a code template according to the language of caller and enjoy it. Official document: [Support Language](https://grpc.io/docs/languages/)

#### Completed examples

If this project is helpful to you, you can commit another examples and PR, such as php/golang/Nodejs rpc call examples.

| name                            | code                                 | comments         |
| ------------------------------- | ------------------------------------ | ---------------- |
| Python rpc client usage example | server/examples/python/rpc_client.py | convert and save |

### Command Mode

Download the  `convert.sh`, and grant execution authority, execute the following command, the second param should choose in `stl|stp|iges|obj|fbx`, please determine according to the file type 

> The script depends on the docker environment, so you should prepare the Docker environment first. **Command mode is not support zip file convert**, beacause docker volume will auto sync picture or mtl assets to docker container.

```shell
convert.sh stl inputpath.stl outputpath.glb # convert to glb single bin file
convert.sh stl inputpath.stl outputpath.gltf # generate gltf file
```

In the `assets` directory, there are four test files` test.stl` `test.stp`` test.igs` `E 45 Aircraft_obj.obj` `Samba Dancing.fbx`, copy it to the project path, and you can see the convert result.

> If you got this error when you use php-fpm or other language executor to execute convert.sh, you can add your execute user to docker group to avoid this problem.
>
> > usermod -a -G docker nginx
>
> docker: Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Post http://%2Fvar%2Frun%2Fdocker.sock/v1.40/containers/create: dial unix /var/run/docker.sock: connect: permission denied.

By calling in other languages, you can synchronously **determine whether the output file exists** to determine whether the conversion is successful, such as:

```php
<?php
$out = 'out.glb';
$input = 'test.stl';
$type = 'stl';
// please be careful about execution attack
shell_exec('convert.sh '.$type.' '.$input.' '.$out);
if (file_exists($out)) {
    echo "convert result:" . $out;
} else {
    echo "convert failed";
}
```

### Docker Environment

Under the docker host machine installed with docker, run the following command to pull the image (about 4G)

```shell
docker pull wj2015/3d-model-convert-to-gltf
```

Inside the container  and execute `conda run -n pythonocc python convert.py [stl|step|iges|obj|fbx] input.stl out.glb` can convert model synchronous.

### Simple Load Diagram

If there is a demand for multi-machine load, you can use nginx proxy / docker container with rpc to do a simple load balancing, or use message queue with producer and consumer. The HTTP API or queue needs to implement your own logic.

![1583754967257](assets/1583754967257.png)

## Join us

### Docker development environment

At first install `docker` and `docker-compose`, refer to official documents: [Docker Desktop](https://www.docker.com/products/docker-desktop)

Then, enter to `environment/` documents, execute `docker-compose up`, the execute result is as follows to indicate success

```shell
user@MacBook-Pro environment % docker-compose up
Recreating 3d-model-convert-to-gltf-app ... done
Starting 3d-model-convert-to-gltf-redis ... done
Attaching to 3d-model-convert-to-gltf-redis, 3d-model-convert-to-gltf-app
3d-model-convert-to-gltf-redis | 1:C 09 Oct 2020 03:03:29.150 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
3d-model-convert-to-gltf-redis | 1:C 09 Oct 2020 03:03:29.150 # Redis version=6.0.1, bits=64, commit=00000000, modified=0, pid=1, just started
3d-model-convert-to-gltf-redis | 1:C 09 Oct 2020 03:03:29.150 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
3d-model-convert-to-gltf-redis | 1:M 09 Oct 2020 03:03:29.152 * Running mode=standalone, port=6379.
3d-model-convert-to-gltf-redis | 1:M 09 Oct 2020 03:03:29.152 # WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.
3d-model-convert-to-gltf-redis | 1:M 09 Oct 2020 03:03:29.152 # Server initialized
```

If there are port conflicts, initialization failures and other abnormal situations, please check  and search the information according to the error information.

Create a new terminal, execute `docker ps` for this current execute docker containers, the execution result is as follows to indicate success

```shell
user@MacBook-Pro 3d-model-convert-to-gltf % docker ps
CONTAINER ID        IMAGE                             COMMAND                  CREATED             STATUS              PORTS               NAMES
69b684ed7755        wj2015/3d-model-convert-to-gltf   "conda run -n python…"   3 seconds ago       Up 2 seconds                            3d-model-convert-to-gltf-app
```

Next, enter the container to execute the command and enter the `pythonocc` conda environment. Executing the script in this environment can facilitate code changes and debugging

```shell
wangjie@MacBook-Pro 3d-model-convert-to-gltf % docker exec -it 3d-model-convert-to-gltf-app /bin/bash
(base) root@5efd6ef96814:/opt/3d-model-convert-to-gltf# conda activate pythonocc
(pythonocc) root@69b684ed7755:/opt/3d-model-convert-to-gltf# python server/convert.py 
Params not found, format: python convert.py [type] [file path] [out file path]
```

### Non-docker development environment

Mainly for developers who cannot run docker, you can try to use this method to build a development environment.

Create conda virtual environment:
```shell script
conda create -n 3d-model-convert-to-gltf-pythonocc -c dlr-sc -c pythonocc pythonocc-core=7.4.0rc1
conda activate 3d-model-convert-to-gltf-pythonocc
pip install -r server/requirements.txt
```


Your local node version need `12.0.0`, or  got error when you run the `gltf-pipeline` command, and you should install `gltf-pipeline`  and  `obj2gltf` packages.

#### Local debug environment install guide
Install `nvm` by this script(MacOs or Linux), you can download .exe executable file from [https://github.com/coreybutler/nvm-windows](https://github.com/coreybutler/nvm-windows) 
```shell script
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash
```
Install and use node 12.0.0, with other packages.
```shell script
nvm install 12.0.0
nvm use 12.0.0
npm install -g gltf-pipeline obj2gltf
```
Then, download FBX2glTf from [https://github.com/facebookincubator/FBX2glTF](https://github.com/facebookincubator/FBX2glTF) and put it to environment dir.

> PS: you should rename FBX2Gltf to fbx2gltf for Unified invoking

Understand the code and the file structure, submit the PR after the modification. Welcome to email me admin@wj2015.com.

## License

3DModelConvertToGltf is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/GitbookIO/gitbook/blob/master/LICENSE) for the full license text.

