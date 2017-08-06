from flask import Flask
from flask import request
from flask import abort
from throttle import Throttle


app = Flask(__name__)

@app.route("/")
@Throttle("5/m", lambda : request.remote_addr,
            callback = lambda *args, **kwargs: abort(503))
def hello():
    return "Hello World!"


if __name__ == '__main__':
    app.run(port=8000)
