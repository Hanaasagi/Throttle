# Throttle

Python Throttle implementation based on slide window algorithm.

### How to use

This package offers a decorator for limiting the number of calls in a period of time. This plugin often called Throttle.
First, you should choose a identify to distinguish every call. For example, if you decorate a api, maybe client ip will be the identify.Of course, the identify can be same, it will be a global throttle.
The identify can be a attribute which will be passed to decorated function or method, supporting nested. Besides, it can be a function, or a variable in other context(construct a closure).

There are two throttle for different situation, sync or async.Now offer local storage for sync, redis for async.

Read the example below to learn more.

### Examples

With Flask
```
from flask import Flask
from flask import request
from flask import abort
from throttle import SyncThrottle
from throttle.storage import LocalStorage


app = Flask(__name__)


@app.route("/")
@SyncThrottle("5/m", lambda: request.remote_addr,
              callback=lambda *args, **kwargs: abort(503),
              storage=LocalStorage(max_len=100))
def hello():
    return "Hello World!"


if __name__ == '__main__':
    app.run(port=8000)
```

With Sanic
```
from sanic import Sanic
from sanic.response import json, text
from throttle import AsyncThrottle
from throttle.storage import RedisStorage


app = Sanic()


@app.route("/")
@AsyncThrottle("5/m", "request.remote_addr",
               callback=lambda *args, **kwargs:
                   text('tirgger the throttle', status=503),
               storage=RedisStorage('localhost',
                                    port=6379, password=''))
async def test(request):
    return json({"hello": "world"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

```

### license
MIT
