from redis import Redis
db = None

def connect(config):
    global db
    if db != None:
        return db
    conn = Redis(host=config['host'], port=config['port'], password=config['password'], db=config['db'], decode_responses=True)
    db = conn
    return db
