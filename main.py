# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random
from threading import Thread
from time import sleep

import discord

# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

NIGHT_CATEGORY = "NIGHT PHASE"
TOWN_SQUARE = "Town Square"

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
guild = None

@client.event
async def on_ready():
    global guild
    print(f'{client.user} has connected to Discord in guild {client.guilds}')
    guild = discord.utils.get(client.guilds, name=GUILD)

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f"Hi {member.name}, welcome to Blood on the Clocktower! Here is the link to join the session https://bra1n.github.io/townsquare/#play/max"
    )

async def wake_up():
    await send_all_to_town_square()

async def send_to_random_night_channels(members):
    channels = get_night_phase_channels()
    random.shuffle(channels)
    for member in members:
        await member.move_to(channels.pop())


def extract_non_bots_from_night_channels(night_channels):
    night_members = []
    for channel in night_channels:
        for member_id, _ in channel.voice_states.items():
            member = guild.get_member(member_id)
            if not member.bot:
                night_members.append(member)
    return night_members


async def send_all_to_town_square():
    night_channels = get_night_phase_channels()
    night_members = extract_non_bots_from_night_channels(night_channels)
    town_square = get_town_square()
    for member in night_members:
        await member.move_to(town_square)

async def go_to_sleep():
    channel = get_town_square()
    voice_states = channel.voice_states
    members = [guild.get_member(member_id) for member_id, _ in voice_states.items()]
    await send_to_random_night_channels(members)


def get_town_square():
    channel = discord.utils.get(guild.voice_channels, name="Town Square", bitrate=64000)
    return channel

def get_night_phase_channels():
    category = discord.utils.find(lambda m: m.name == "Night Phase", guild.categories)
    return category.channels


currentDayAndNight = 1
async def notify_day_count():
    global currentDayAndNight
    update_channel = discord.utils.get(guild.channels, name='game-chat')
    await update_channel.send(f"Last night was Night {currentDayAndNight}\nToday is Day {currentDayAndNight}")
    currentDayAndNight += 1


def reset_count():
    global currentDayAndNight
    currentDayAndNight = 1


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.name == "moveeradmin":
        if "go to sleep" in message.content.lower():
            await go_to_sleep()
        elif "wake up" in message.content.lower():
            await wake_up()
            await notify_day_count()
        elif "game over" in message.content.lower():
            reset_count()

client.run(TOKEN)


