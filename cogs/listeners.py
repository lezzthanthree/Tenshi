import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.app_commands.errors import BotMissingPermissions
from rich import print as p
from database import Database, create, insert, delete, update

class Listeners(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        Database.execute_command(create['guild'], ())
        Database.execute_command(create['subject'], ())
        Database.execute_command(create['enrollment'], ())
        Database.execute_command(create['schedule'], ())
        
        await self.bot.tree.sync()
        for guild in self.bot.guilds:
            Database.execute_command(insert['guild'], (guild.id, guild.name))
        p(f'[b blue]Bot active as {self.bot.user}!')
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        Database.execute_command(insert['guild'], (guild.id, guild.name))
        p(f"[b green]Joined {guild} = {guild.id}. Adding to database.")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        Database.execute_command(delete['guild'], (guild.id,))
        p(f"[b red]Left {guild} = {guild.id}. Removing from database.")

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        if not before.name == after.name:
            Database.execute_command(update['guild'], (after.name, after.id))
            p(f"[b yellow]Update {before.name} from {after.name}. Updating database.")

    # @commands.Cog.listener()
    # async def on_message(self, message: discord.Message):
    #     p(f"from {message.author} in {message.guild.id}: {message.content}")
    #     await self.bot.process_commands(message)
        
# class ErrorListeners(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @commands.Cog.listener()
#     async def on_command_error(self, ctx: discord.Interaction, error):
#         if isinstance(error, BotMissingPermissions):
#             print("MissingPermissions!")
#             await ctx.response.send_message("You don't have permission to use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Listeners(bot))   
    # await bot.add_cog(ErrorListeners(bot))   