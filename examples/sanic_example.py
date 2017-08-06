from sanic import Sanic
from sanic.response import json, text
from throttle import RedisThrottle


app = Sanic()

@app.route("/")
@RedisThrottle("5/m", "request.remote_addr",
                    callback=lambda *args, **kwargs:
                        text('tirgger the throttle', status=503))
async def test(request):
    return json({"hello": "world"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
