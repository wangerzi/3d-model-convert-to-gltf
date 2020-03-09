# 3DModelConvertToGltf 统一模型格式转换工具

此项目产生的主要原因是工作中遇到了需要在Web中展示 STEP 和 IGES 模型的场景，但是市面上的web3d类库均不支持此格式，并且用户上传的STL文件直接展示会占用大量带宽或者CDN流量，转换为压缩后的gltf会比较合适。

**支持输入格式：**STL/IGES/STEP

**支持输出格式：**GLB

为此总结博客如下，本项目即采用了博客中介绍的思路：[STEP和IGES模型转换为适用Web的glb格式](https://blog.wj2015.com/2020/03/08/step%e5%92%8ciges%e6%a8%a1%e5%9e%8b%e8%bd%ac%e6%8d%a2%e4%b8%ba%e9%80%82%e7%94%a8web%e7%9a%84glb%e6%a0%bc%e5%bc%8f/)

**项目状态：**研发中

## 快速上手

首先，下载代码

```shell
git clone https://github.com/wangerzi/3d-model-convert-to-gltf.git
cd 3d-model-convert-to-gltf
```

建议使用 docker-compose 运行此项目，省去环境的烦恼

```shell
docker-compose up -d
```

默认映射到8080端口，然后就可以通过访问 http://IPAddress:8080/ 测试是否部署完成了

如果有多机负载的需求，可借助 nginx 的反向代理做一下简单的负载均衡

### 接口文档

所有转换接口调用成功时的响应如下，`req_id` 可以通过接口获取当前队列进度

```json
{
    "code": 200,
    "message": "转换成功",
    "data": {
        "req_id": 1
    }
}
```

失败时，会有如下响应

```json
{
    "code": 999,
    "message": "错误信息",
    "data": {}
}
```

考虑到分布式部署的可能，所有的接口都不会做文件转换缓存与去重，所以最好将此作为内网服务，通过业务服务端请求本项目提供的接口

#### 转换STL接口

将Ascii格式的，或者二进制格式的STL文件，统一转换为GLTF

**方法：**POST

**路径：**/convert/stl

**请求参数**

| 参数名称       | 类型   | 必填 | 描述                                                         |
| -------------- | ------ | ---- | ------------------------------------------------------------ |
| file           | File   | 是   | 上传STL文件                                                  |
| callback       | string | 是   | 异步钩子地址，转换完毕后，会将文件链接和附带信息传递到Hook中 |
| customize_data | JSON   | 否   | 附带的信息，回调时会传输                                     |

#### 转换STP接口

将STEP格式的模型文件，统一转换为GLTF

**方法：**POST

**路径：**/convert/stp

**请求参数**

| 参数名称       | 类型   | 必填 | 描述                                                         |
| -------------- | ------ | ---- | ------------------------------------------------------------ |
| file           | File   | 是   | 上传STEP文件                                                 |
| callback       | string | 是   | 异步钩子地址，转换完毕后，会将文件链接和附带信息传递到Hook中 |
| customize_data | JSON   | 否   | 附带的信息，回调时会传输                                     |

#### 转换IGES接口

将IGES格式的模型文件，统一转换为GLTF

**方法：**POST

**路径：**/convert/iges

**请求参数**

| 参数名称       | 类型   | 必填 | 描述                                                         |
| -------------- | ------ | ---- | ------------------------------------------------------------ |
| file           | File   | 是   | 上传IGES文件                                                 |
| callback       | string | 是   | 异步钩子地址，转换完毕后，会将文件链接和附带信息传递到Hook中 |
| customize_data | text   | 否   | 附带的信息，回调时会传输（建议传JSON）                       |

#### 获取转换进度

根据 req_id 获取当前转换进度

**方法：**GET

**路径：**/convert/process

**请求参数**

| 参数名称 | 类型    | 必填   | 描述           |
| -------- | ------- | ------ | -------------- |
| req_id   | integer | 转换id | 转换时返回的id |

**响应样例**

```json
{
    "code": 200,
    "data": {
        "current": 1,
        "total": 100
    }
}
```

### 转换回调规范

接口文档中提到的 callback 参数，用于转换完毕后主动调用，用于传输转换结果文件以及附带信息。

为方便起见，可以在 callback 中的GET参数上拼接好模型 id，比如下面的 url 表示转换 id=1 的模型，这个 id 会随着回调的调用而被传递过去

> http://xxx.com/convert/callback?id=1

**提供参数**

| 参数           | 类型 | 描述             |
| -------------- | ---- | ---------------- |
| file           | File | 文件内容         |
| customize_data | text | 请求时附带的信息 |

**响应规范**

如果正常接受或者无视，请返回如下格式的JSON，并保证 code: 200

```json
{
    "code": 200
}
```

如果处理失败，请则返回空或 JSON 中的 code 不为 200，返回失败的数据则会以 15/30/60/120 的间隔重新推送，失败4次后不再推送

### 简单负载示意图

![1583754967257](assets/1583754967257.png)

## 待完成需求

- [ ] 基本项目结构规划及接口设计
- [ ] 转换及压缩代码实现
- [ ] docker镜像打包

## 参与开发

首先需要了解下 [aio-http](https://aiohttp.readthedocs.io/en/stable/)，本项目就是基于此Web框架实现的

然后看下代码，修改完毕后提交PR即可，欢迎邮箱 admin@wj2015.com 与我讨论

## 特别感谢

我自己(\*^_^\*)

## 开源协议

3DModelConvertToGltf is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/GitbookIO/gitbook/blob/master/LICENSE) for the full license text.