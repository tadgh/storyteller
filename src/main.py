import asyncio

from sanic import Sanic
from sanic.response import json
# from bot import StoryTeller
from bot import StoryTeller

app = Sanic(name="zoop")
bot = StoryTeller()


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

webserver = app.create_server(host='0.0.0.0', port=8000, debug=True, return_asyncio_server=True)
asyncio.ensure_future(webserver)

loop = asyncio.get_event_loop()
loop.create_task(bot.boot_up())
loop.run_forever()


