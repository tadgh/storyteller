import asyncio
import os

from sanic import Sanic
from sanic.response import json, empty
from sanic_cors import CORS, cross_origin
from dotenv import load_dotenv
from bot import StoryTeller

load_dotenv()
app = Sanic(name="zoop")
cors = CORS(app, resources={r"/*": {"origins": "https://clocktower.online"}})
bot = StoryTeller()


@app.middleware('request')
async def check_key(request):
    if "token" not in request.args.keys():
        return empty(status=401)

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
    await bot.notify_day_count()
    return json({'woken': 'yes'})


@app.route('/wake_up_gently')
async def test(request):
    await bot.wake_up()
    return json({'woken': 'yes'})

@app.route('/good_wins')
async def test(request):
    await bot.clear_game_chat()
    bot.reset_count()
    return json({'victor': 'good'})

@app.route('/evil_wins')
async def test(request):
    await bot.clear_game_chat()
    bot.reset_count()
    return json({'victor': 'evil'})

@app.route('/whisper_warning')
async def test(request):
    await bot.notify_whispers_end()
    return json({'notified': 'sure'})

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


