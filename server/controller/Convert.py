from aiohttp import web
from validate import Convert
import service.Convert

success_response = {
    "code": 200,
    "message": "Joined the queue successfully!",
    "data": {
        "req_id": 1
    }
}

async def stl(request):
    app = request.app
    db = app['redis']

    # get post data
    data = await request.post()
    data = dict(data)

    # validate request
    Convert.stl(request, data)

    # get queue json
    req_id, json_dict = service.Convert.make_queue_json(request, data, 'stl')
    # add to queue
    service.Convert.add_to_queue(db, req_id, json_dict)

    success_response['data']['req_id'] = req_id
    return web.json_response(success_response)

async def stp(request):
    app = request.app
    db = app['redis']

    # get post data
    data = await request.post()
    data = dict(data)

    # validate request
    Convert.stp(request, data)

    # get queue json
    req_id, json_dict = service.Convert.make_queue_json(request, data, 'stp')
    # add to queue
    service.Convert.add_to_queue(db, req_id, json_dict)

    success_response['data']['req_id'] = req_id
    return web.json_response(success_response)

async def iges(request):
    app = request.app
    db = app['redis']

    # get post data
    data = await request.post()
    data = dict(data)

    # validate request
    Convert.iges(request, data)

    # get queue json
    req_id, json_dict = service.Convert.make_queue_json(request, data, 'iges')
    # add to queue
    service.Convert.add_to_queue(db, req_id, json_dict)

    success_response['data']['req_id'] = req_id
    return web.json_response(success_response)

async def process(request):
    db = request.app['redis']
    data = dict(request.query)

    # validate request
    Convert.process(request, data)

    success_response['data'] = service.Convert.get_wait_mission_pos(db, data['req_id'])
    success_response['message'] = "Get process success"
    return web.json_response(success_response)
