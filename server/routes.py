import controller.Convert as Convert

def setup_routes(app):
    app.router.add_get('/convert/stp', Convert.stp)
    app.router.add_get('/convert/stl', Convert.stl)
    app.router.add_get('/convert/iges', Convert.iges)
    app.router.add_get('/convert/process', Convert.process)
