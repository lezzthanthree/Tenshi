import asyncio
from cogs import listeners, subjects, moderation, schedules, time, homework
from discord import Intents, app_commands, Client
from discord.ext import commands
from discord.ext.commands import Bot
from discord.errors import HTTPException, LoginFailure
from setup import settings
from rich import print as p

class MyClient(Bot):
    def __init__(self, intents, command_prefix):
        super().__init__(intents=intents, command_prefix=command_prefix)

        asyncio.run(listeners.setup(self))
        asyncio.run(moderation.setup(self))
        asyncio.run(subjects.setup(self))
        asyncio.run(homework.setup(self))
        asyncio.run(schedules.setup(self))
        asyncio.run(time.setup(self))
        
intents = Intents.default()
intents.members = True
intents.message_content = True

client = MyClient(intents, settings['prefix'])

try:
    client.run(settings['token'])
except LoginFailure:
    p("[b red]Token error! Please set up your token in setup.py.")
