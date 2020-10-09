from aiohttp import web
from validate import Convert
import service.Convert

success_response = {
    "code": 200,
    "message": "Joined the queue successfully!",
    "data": {
        "req_id": ''
    }
}


async def stl(request):
    app = request.app

    # get post data
    data = await request.post()
    data = dict(data)

    # validate request
    Convert.stl(request, data)

    # get queue json
    req_id, json_dict = service.Convert.make_queue_json(request, data, 'stl')

    success_response['data']['req_id'] = req_id
    return web.json_response(success_response)


async def stp(request):
    app = request.app

    # get post data
    data = await request.post()
    data = dict(data)

    # validate request
    Convert.stp(request, data)

    # get queue json
    req_id, json_dict = service.Convert.make_queue_json(request, data, 'stp')

    success_response['data']['req_id'] = req_id
    return web.json_response(success_response)


async def iges(request):
    app = request.app

    # get post data
    data = await request.post()
    data = dict(data)

    # validate request
    Convert.iges(request, data)

    # get queue json
    req_id, json_dict = service.Convert.make_queue_json(request, data, 'iges')

    success_response['data']['req_id'] = req_id
    return web.json_response(success_response)

async def obj(request):
    app = request.app
    # get post data
    data = await request.post()
    data = dict(data)

    # validate request
    Convert.obj(request, data)

    # get queue json
    req_id, json_dict = service.Convert.make_queue_json(request, data, 'obj')

    success_response['data']['req_id'] = req_id
    return web.json_response(success_response)

async def fbx(request):
    app = request.app

    # get post data
    data = await request.post()
    data = dict(data)

    # validate request
    Convert.fbx(request, data)

    # get queue json
    req_id, json_dict = service.Convert.make_queue_json(request, data, 'fbx')

    success_response['data']['req_id'] = req_id
    return web.json_response(success_response)
