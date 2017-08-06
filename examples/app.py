from sanic import Sanic
from sanic.response import json
from throttle import RedisThrottle

app = Sanic()

@app.route("/")
@RedisThrottle("5/m", "request.remote_addr")
async def test(request):
    return json({"hello": "world"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
