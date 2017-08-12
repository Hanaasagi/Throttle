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
