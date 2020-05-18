# 3DModelConvertToGltf - An Unified Model Format Conversion Tool

The main reason for this project is that I encountered a scenario where **the STEP and IGES models need to be displayed on the Web**, but the web3d class libraries on the market do not support this format, and the direct display of STL files uploaded by users will consume a lot of bandwidth or CDN Traffic, converted to compressed gltf would be more appropriate.

**support input format：** STL/IGES/STEP/OBJ

**support output format：** GLB

I organized my thoughts into a blog: [STEP and IGES models are converted to the web-friendly glb format](https://blog.wj2015.com/2020/03/08/step%e5%92%8ciges%e6%a8%a1%e5%9e%8b%e8%bd%ac%e6%8d%a2%e4%b8%ba%e9%80%82%e7%94%a8web%e7%9a%84glb%e6%a0%bc%e5%bc%8f/)

> PS: My blog is Chinese, if you are a non-Chinese native speaker, please bring a Google Translate

**Project status:** coding

## Document

English|[中文](README_ZH.md)

## Quick Start

Due to the trouble of environment configuration and other reasons, the command line mode **still needs to rely on docker**. **The command line mode is suitable for simple invocation on the server side.** The conversion process blocks the processes to be synchronized and cannot be deployed in a distributed manner to increase concurrency.

> PS：When there are too many simultaneous conversion models in the command line mode or a single model is too large, there is a risk that the server providing the web service is stuck

### Command mode

Download the `convert.sh`, Grant execute permission, execute the following instructions

```shell
convert.sh [stl|step|iges] inputpath.stl outputpath.glb
```

In the `assets` directory, there are three test files `test.stl` `test.stp` `test.igs`, copy them to the project path, and follow the instructions above to see that the corresponding results are generated.

By calling in other languages, you can synchronously **determine whether the output file exists** to determine whether the conversion is successful, such as:

```php
<?php
$out = 'out.glb';
$input = 'test.stl';
$type = 'stl';
shell_exec('convert.sh '.$type.' '.$input.' '.$out);
if (file_exists($out)) {
    echo "convert result:" . $out;
} else {
    echo "convert failed";
}
```

### API mode

At the first, clone the code

```shell
git clone https://github.com/wangerzi/3d-model-convert-to-gltf.git
cd 3d-model-convert-to-gltf
```

It is recommended to use docker-compose to run this project, eliminating the troubles of the environment

> config/ It is **default configuration path**, which affects the operation through the docker directory mapping. If you **modify it, remember to restart the service**
>
> uploads/ It is a **directory for uploading files and file conversion results**, and it is generally run through docker directory mapping.

```shell
docker-compose up -d
```

Serve to port 8080 by default, and you can access http://IPAddress:8080/ to test if deployment is complete.

### Simple Load Diagram

If there is a demand for multi-machine load, you can use nginx's reverse proxy to do a simple load balancing

![1583754967257](assets/1583754967257.png)

For data consistency, there are two strategies for distributed deployment:

- Use a Redis instance **and mount upload on a shared disk**. The advantage is that the conversion performance of each server can be brought into play, and there will be no stacking tasks. **The disadvantage is trouble.**
- Every server uses a local Redis instance. The advantage is that the files are processed locally and the deployment is relatively simple. The disadvantage is that there **may be a stack of tasks on one machine** and other machines being idle.

### API Document

The response when all conversion interface calls are successful is as follows,`req_id` can get the current queue progress through the interface

```json
{
    "code": 200,
    "message": "Transform success",
    "data": {
        "req_id": "sha1 code length:41"
    }
}
```

When you fail, you will get this message:

```json
{
    "code": 999,
    "message": "Err information",
    "data": {}
}
```

Considering the possibility of distributed deployment, all interfaces will **not perform file conversion caching and deduplication**, so **it is best to use this as an intranet service** and request the interface provided by this project through the business server

#### Convert STL API

Convert STL files in Ascii format or binary format to GLTF uniformly

**Method：** POST

**Path：** /convert/stl

**Request params**

| Param name     | Type   | Must | Description                                                  |
| -------------- | ------ | ---- | ------------------------------------------------------------ |
| file           | File   | Yes  | Upload STL file by form                                      |
| callback       | string | Yes  | After the conversion is complete, the file link and accompanying information are passed into the Web Hook Callback |
| customize_data | JSON   | No   | Incidental information, transmitted when callback            |

#### Convert STP API

Unified model files in STEP format to GLTF

**Method：** POST

**Path：** /convert/stp

**Request Params**

| Param name     | Type   | Must | Description                                                  |
| -------------- | ------ | ---- | ------------------------------------------------------------ |
| file           | File   | Yes  | Upload STEP file by form                                     |
| callback       | string | Yes  | After the conversion is complete, the file link and accompanying information are passed into the Web Hook Callback |
| customize_data | JSON   | No   | Incidental information, transmitted when callback            |

#### Convert IGES API

Convert model files in IGES format to GLTF uniformly

**Method：** POST

**Path：** /convert/iges

**Request Params**

| Param name     | Type   | Must | Description                                                  |
| -------------- | ------ | ---- | ------------------------------------------------------------ |
| file           | File   | Yes  | Upload IGES file by form                                     |
| callback       | string | Yes  | After the conversion is complete, the file link and accompanying information are passed into the Web Hook Callback |
| customize_data | text   | No   | Incidental information, transmitted when callback            |

#### Get the current conversion progress

Get the current conversion progress according to req_id

**Method：** GET

**Path：** /convert/process

**Request Params**

| Param name | Type   | Must       | Description                          |
| ---------- | ------ | ---------- | ------------------------------------ |
| req_id     | string | convert id | response when you access convert api |

**Response format**

```json
{
    "code": 200,
    "data": {
        "current": 1,
        "total": 100,
        "status": 0
    }
}
```

> status is 0 for waiting, status is 1 for conversion, status is 2 for completed

### Conversion callback specification

The callback parameter mentioned in the interface document is used to actively call after the conversion is complete, and is used to transfer the conversion result file and accompanying information.

For convenience, the model id can be spliced on the GET parameter in the callback. For example, the following url indicates the model with the id = 1, and this id will be passed along with the callback call.

> http://xxx.com/convert/callback?id=1

**Response params**

| Param name     | Type    | Description                                               |
| -------------- | ------- | --------------------------------------------------------- |
| result         | integer | Conversion result 1 Conversion failed 0 Conversion failed |
| message        | string  | Error Description                                         |
| file           | File    | File content (as POST form)                               |
| customize_data | text    | Incidental information, transmitted when callback         |

**Response format**

If it is accepted or ignored normally, please return the JSON with the following format and make sure code is 200

```json
{
    "code": 200
}
```

If the **processing fails**, please **return empty or the code in the JSON is not 200**. The failed data will be **re-pushed at the interval of 5/15/30/60/120**. If both fail, it will be discarded and not pushed

## Redis Desgin

The pending queues in `3d-preview-model-waiting`, and the list holds the globally unique `req_id`

Processing / Unprocessed Information put in `3d-preview-model-data-${req_id}` , value is a JSON about upload file, The automatic expiration time is 2 days by default, the format is as follows:

```json
{
    "type": "stl",
    "file": "/usr/share/nginx/html/uploads/xxx.stl",
    "status": 1,
    "result": {
        "glb": "/usr/share/nginx/html/uploads/xxx.glb"
    }
}
```

The successfully processed `req_id` is placed in the `3d-preview-model-convert-success` **Hash table**, and the key stored is the globally unique `req_id`. **It will be removed from the notification after successful notification or repeated notification multiple timeouts**, and it will be deleted when it is removed Files and `3d-preview-model-data-$ {req_id}`

## Mission

- [x] Basic project structure planning and interface design
- [x] Conversion and compression code implementation
- [x] Add obj format to darco gltf
- [ ] Related interface implementation
- [ ] docker image packaging

## Join us

At first you should study [aio-http](https://aiohttp.readthedocs.io/en/stable/), this project is based on it

When you are local, I suggest you into the `server/` path, and use `aiohttp-devtools runserver` for convenience, your local node version need `12.0.0`, or  got error when you run the `gltf-pipeline` command, and you should install `gltf-pipeline`  and  `obj2gltf` packages.

Understand the code structure briefly, and submit the PR after the modification. Welcome to email admin@wj2015.com to discuss with me.

## License

3DModelConvertToGltf is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/GitbookIO/gitbook/blob/master/LICENSE) for the full license text.

