from aiohttp import web
from routes import setup_routes
from setting import config
import db.redis as redis

app = web.Application()
app['config'] = config
app['redis'] = redis.connect(config['redis'])
setup_routes(app)
if __name__ == '__main__':
    web.run_app(app)
