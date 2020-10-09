import controller.Convert as Convert
from exception.BaseException import BaseException
from aiohttp import web


def handle(func):
    # wrapper exception handler
    async def run(request):
        try:
            res = await func(request)
        except BaseException as err:
            return web.json_response({'code': 999, "message": str(err), "data": {}})
        return res

    return run


def setup_routes(app):
    app.router.add_post('/convert/stp', handle(Convert.stp))
    app.router.add_post('/convert/stl', handle(Convert.stl))
    app.router.add_post('/convert/iges', handle(Convert.iges))
