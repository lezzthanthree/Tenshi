import asyncio
from cogs import listeners, subjects, moderation, schedules, time
from discord import Intents, app_commands, Client
from discord.ext import commands
from discord.ext.commands import Bot
from setup import settings

class MyClient(Bot):
    def __init__(self, intents, command_prefix):
        super().__init__(intents=intents, command_prefix=command_prefix)

        asyncio.run(listeners.setup(self))
        asyncio.run(moderation.setup(self))
        asyncio.run(subjects.setup(self))
        asyncio.run(schedules.setup(self))
        asyncio.run(time.setup(self))
        
intents = Intents.default()
intents.members = True
intents.message_content = True

client = MyClient(intents, settings['prefix'])

client.run(settings['token'])