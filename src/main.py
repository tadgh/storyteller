import asyncio
import os

from sanic import Sanic
from sanic.response import json, empty
from sanic.request import RequestParameters
from dotenv import load_dotenv
from bot import StoryTeller

load_dotenv()
app = Sanic(name="zoop")
bot = StoryTeller()


@app.middleware('request')
async def check_key(request):
    if request.args['token'][0] != os.getenv('SECRET_KEY'):
        return empty(status=401)


@app.route('/')
async def test(request):
    return json({'hello': 'world'})


@app.route('/go_to_sleep')
async def test(request):
    await bot.go_to_sleep()
    return json({'slept': 'yes'})


@app.route('/wake_up')
async def test(request):
    await bot.wake_up()
    return json({'woken': 'yes'})


@app.route('/wake_up_gently')
async def test(request):
    await bot.wake_up_gently()
    return json({'woken': 'yes'})

debug = os.getenv('SERVER_DEBUG') == 'True'
webserver = app.create_server(
    host=os.getenv('SERVER_HOST'),
    port=os.getenv('SERVER_PORT'),
    debug=debug,
    return_asyncio_server=True
)

asyncio.ensure_future(webserver)

loop = asyncio.get_event_loop()
loop.create_task(bot.boot_up())
loop.run_forever()


