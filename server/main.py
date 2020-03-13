from aiohttp import web
from routes import setup_routes
from setting import config
import db.redis as redis
from background import setup_background
import service.Convert

max_size = config['upload']['maxsize']
app = web.Application(client_max_size=1024**2*max_size)
app['config'] = config
app['redis'] = redis.connect(config['redis'])

setup_routes(app)
setup_background(app)

if __name__ == '__main__':
    web.run_app(app)
