import random
import os
import asyncio
import discord

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

NIGHT_CATEGORY = "NIGHT PHASE"
TOWN_SQUARE = "Town Square"


class StoryTeller(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.currentDayAndNight = 1
        self.clockhand = False
        self.guild = None

    def boot_up(self):
        return self.start(TOKEN)

    async def on_ready(self,):
        print(f'{self.user} has connected to Discord in guild {self.guilds}')
        self.guild = discord.utils.get(self.guilds, name=GUILD)

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f"Hi {member.name}, welcome to Blood on the Clocktower! Here is the link to join the session https://bra1n.github.io/townsquare/#play/max"
        )

    async def wake_up(self):
        await self.send_all_to_town_square()

    async def send_to_random_night_channels(self, members):
        channels = self.get_night_phase_channels()
        random.shuffle(channels)
        for member in members:
            await member.move_to(channels.pop())

    def extract_non_bots_from_night_channels(self, night_channels):
        night_members = []
        for channel in night_channels:
            for member_id, _ in channel.voice_states.items():
                member = self.guild.get_member(member_id)
                if not member.bot:
                    night_members.append(member)
        return night_members

    async def send_all_to_town_square(self, ):
        night_channels = self.get_night_phase_channels()
        night_members = self.extract_non_bots_from_night_channels(night_channels)
        town_square = self.get_town_square()
        for member in night_members:
            await member.move_to(town_square)

    async def go_to_sleep(self, ):
        channel = self.get_town_square()
        voice_states = channel.voice_states
        members = [self.guild.get_member(member_id) for member_id, _ in voice_states.items()]
        await self.send_to_random_night_channels(members)
        if clockhand:
            moveer_channel = discord.utils.get(self.guild.channels, name='game-chat')
            if currentDayAndNight == 1:
                await moveer_channel.send(f'The clockhand is on the demon')
            else:
                await moveer_channel.send(f'The clockhand has moved {currentDayAndNight - 1} times')

    def get_town_square(self):
        channel = discord.utils.get(self.guild.voice_channels, name="Town Square", bitrate=64000)
        return channel

    def get_night_phase_channels(self):
        category = discord.utils.find(lambda m: m.name == "Night Phase", self.guild.categories)
        return category.channels

    async def notify_day_count(self):
        global currentDayAndNight
        update_channel = discord.utils.get(self.guild.channels, name='game-chat')
        await update_channel.send(f"Last night was Night {currentDayAndNight}\nToday is Day {currentDayAndNight}")
        currentDayAndNight += 1

    def reset_count(self):
        global currentDayAndNight
        currentDayAndNight = 1

    async def clear_game_chat(self):
        update_channel = discord.utils.get(self.guild.channels, name='game-chat')
        messages = await update_channel.history(limit=200).flatten()
        await update_channel.delete_messages(messages)

    async def notify_whispers_end(self):
        channels = [discord.utils.get(self.guild.channels, name='general'),
                    discord.utils.get(self.guild.channels, name='game-chat')]
        for channel in channels: await channel.send(f"Whispers closing in 1 minute.")
        await asyncio.sleep(30)
        for channel in channels: await channel.send(
            f"Whispers closing in 30 seconds. Please wrap up your conversations.")
        await asyncio.sleep(30)
        for channel in channels: await channel.send(
            f"Whispers are now closed. Please return to {TOWN_SQUARE} for nominations.")

    async def send_help(self):
        help_message = (
            'The following commands are available for use:\n\n'
            f'- **go to sleep**: Send all users in {TOWN_SQUARE} to channels within the {NIGHT_CATEGORY} category\n'
            f'- **wake up**: Send all non-bot users from {NIGHT_CATEGORY} channels back to {TOWN_SQUARE}. Increments day/night count.\n'
            '- **wake up gently**: Same as "wake up", but does not increment day/night count. For use if the storyteller makes a mistake and needs to send everyone back to bed. \n'
            '- **game over**: Resets day/night count and clears the game-chat logs\n'
            '- **whisper**: Sends warnings in general and game-chat to end private conversations\n'
        )
        moveer_channel = discord.utils.get(self.guild.channels, name='moveeradmin')
        await moveer_channel.send(help_message)

    async def toggle_clockhand(self):
        global clockhand
        moveer_channel = discord.utils.get(self.guild.channels, name='moveeradmin')
        clockhand = not clockhand
        await moveer_channel.send(f'The clockhand is now {"on" if clockhand else "off"}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.channel.name == "moveeradmin":
            if "go to sleep" in message.content.lower():
                await self.go_to_sleep()
            elif "wake up gently" in message.content.lower():
                await self.wake_up()
            elif "wake up" in message.content.lower():
                await self.wake_up()
                await self.notify_day_count()
            elif "game over" in message.content.lower():
                self.reset_count()
                await self.clear_game_chat()
            elif "whisper" in message.content.lower():
                await self.notify_whispers_end()
            elif "help" in message.content.lower():
                await self.send_help()
            elif "clockhand" in message.content.lower():
                await self.toggle_clockhand()


