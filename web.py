from gevent.wsgi import WSGIServer
from app import CreateApp

app = CreateApp()

if __name__ == '__main__':
    #app.run(host = '0.0.0.0',port = 8000,debug=True)
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()