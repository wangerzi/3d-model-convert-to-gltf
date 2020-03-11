from aiohttp import web
from service import File
from validate import Convert

success_response = {
    "code": 200,
    "message": "Joined the queue successfully!",
    "data": {
        "req_id": 1
    }
}

async def stl(request):
    app = request.app
    config = app['config']
    redis = app['redis']

    # get post data
    data = await request.post()

    # validate request
    Convert.stl(request, data)

    # save file to path
    saveFile = data['file']
    File.saveFile(saveFile.file, saveFile.filename, config['upload']['path'])

    # add to queue
    return web.json_response(success_response)
async def stp(request):
    return web.json_response(success_response)
async def iges(request):
    return web.json_response(success_response)
async def process(request):
    return web.json_response(success_response)
