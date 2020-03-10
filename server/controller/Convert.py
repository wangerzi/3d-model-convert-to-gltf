from aiohttp import web

success_response = {
    "code": 200,
    "message": "Joined the queue successfully!",
    "data": {
        "req_id": 1
    }
}
async def stl(request):
    app = request.app
    redis = app['redis']

    redis.set('test', 1)
    print('test result:', redis.get('test'))
    return web.json_response(success_response)
async def stp(request):
    return web.json_response(success_response)
async def iges(request):
    return web.json_response(success_response)
async def process(request):
    return web.json_response(success_response)
