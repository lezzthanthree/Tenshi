import discord
from datetime import datetime, timezone, timedelta
from discord import app_commands
from discord.ext import commands
from database import Database, read, update
from decimal import Decimal

def get_time_and_day(utc):
    return datetime.now(timezone.utc) + timedelta(hours=utc)

class TimeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="now", description="Show the current time and date")
    @app_commands.describe()
    async def now(self, ctx: discord.Interaction):
        current_utc = Database.get_data(read['utc'], (ctx.guild.id,))[0][0]
        date = get_time_and_day(current_utc)
        format_date = {
            'day': "%A",
            'month': "%B",
            'hour': "%H",
            'minute': "%M",
            'second': "%S"
        }
        embed_var = discord.Embed(title=f"Today is {date.strftime(format_date['day'])}, {date.strftime(format_date['month'])} {date.day}, {date.year}.",
                                  description=f"Current time is {date.strftime(format_date['hour'])}:{date.strftime(format_date['minute'])}:{date.strftime(format_date['second'])}.",
                                  color=0x0000FF)
        embed_var.set_footer(text=f"Timezone: UTC{Decimal(current_utc).normalize():+}")
        await ctx.response.send_message(embed=embed_var)

    @app_commands.command(name="setutc", description="Set timezone for this server.")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(utc="UTC must be between -12 and +14. Decimal acceptable.")
    async def set_utc(self, ctx: discord.Interaction, utc: app_commands.Range[float, -12, 14]):
        Database.execute_command(update['utc'], (utc, ctx.guild_id))
        await ctx.response.send_message(f"Timezone has successfully changed to UTC{Decimal(utc).normalize():+}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TimeCommand(bot))