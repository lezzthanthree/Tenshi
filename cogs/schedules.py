import discord
from time import strptime
from datetime import datetime, timezone, timedelta
from discord import app_commands
from discord.ext import commands
from buttons import Confirmation
from database import Database, create, insert, delete, update, read
from sqlite3 import IntegrityError

def check_time(time):
    try:
        strptime(time, '%H:%M')
    except:
        return False
    else:
        return True
    
def get_day(utc):
    day = datetime.now(timezone.utc) + timedelta(hours=utc)
    return day.strftime('%A')

class ScheduleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addschedule", description="Adds a schedule for a subject")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(code="The subject's code",
                           day="The day of the subject",
                           starttime="The subject will start at? (HH:MM)",
                           endtime="The subject will end at? (HH:MM)")
    @app_commands.choices(
        day=[
                app_commands.Choice(name="Sunday",      value=0),
                app_commands.Choice(name="Monday",      value=1),
                app_commands.Choice(name="Tuesday",     value=2),
                app_commands.Choice(name="Wednesday",   value=3),
                app_commands.Choice(name="Thursday",    value=4),
                app_commands.Choice(name="Friday",      value=5),
                app_commands.Choice(name="Saturday",    value=6),
            ])
    @app_commands.guild_only()
    async def add_schedule(self, ctx: discord.Interaction, code: str, 
                                                           day: app_commands.Choice[int],
                                                           starttime: str,
                                                           endtime: str):
        await ctx.response.defer(ephemeral=True)

        data = Database.get_data(read['enrolled_subject_from_code'], (code, ctx.guild.id))

        if len(data) == 0:
            await ctx.followup.send(f"Subject code `{code}` does not exist. Please type `/subjects` to see available subject codes.", ephemeral=True)
            return
        if not check_time(starttime) or not check_time(endtime):
            await ctx.followup.send(f"`starttime` and `endtime` must be in `HH:MM` format. \n" +
                                     "Examples: `23:00`, `12:30`, `21:45`", ephemeral=True)
            return

        confirmation = Confirmation(ctx.user)

        embed_var = discord.Embed(title="Confirmation", description="This schedule will be added to the schedule list. Confirm?", color=0x00FF00)
        embed_var.add_field(name=f"{data[0][1]}", value=f"{day.name}: {starttime} - {endtime}")

        await ctx.followup.send(embed=embed_var, view=confirmation, ephemeral=True)
        await confirmation.wait()

        get_original = await ctx.original_response()

        if confirmation.value == 0:
            await get_original.edit(content="Adding a new schedule has been cancelled.", embed=None, view=None)
            return
        elif confirmation.value == None:
            await get_original.edit(content="Response timeout.", embed=None, view=None)
            return
        
        Database.execute_command(insert['schedule'], (ctx.guild_id, code, day.name, starttime, endtime))

        await get_original.edit(content=f"{data[0][1]} has been added to the schedule list.", embed=None, view=None)


    @app_commands.command(name="updateschedule", description="Update existing schedule")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(scheduleid="The schedule's ID",
                           day="The day of the subject",
                           starttime="The subject will start at? (HH:MM)",
                           endtime="The subject will end at? (HH:MM)")
    @app_commands.choices(
        day=[
                app_commands.Choice(name="Sunday",      value=0),
                app_commands.Choice(name="Monday",      value=1),
                app_commands.Choice(name="Tuesday",     value=2),
                app_commands.Choice(name="Wednesday",   value=3),
                app_commands.Choice(name="Thursday",    value=4),
                app_commands.Choice(name="Friday",      value=5),
                app_commands.Choice(name="Saturday",    value=6),
            ])
    @app_commands.guild_only()
    async def update_schedule(self, ctx: discord.Interaction, scheduleid: str, 
                                                              day: app_commands.Choice[int],
                                                              starttime: str,
                                                              endtime: str):
        await ctx.response.defer(ephemeral=True)

        data = Database.get_data(read['schedule_from_id'], (scheduleid, ctx.guild.id))

        if len(data) == 0:
            await ctx.followup.send(f"Schedule # `{scheduleid}` does not exist. Please type `/subjects` to see available subject codes.", ephemeral=True)
            return
        
        if not check_time(starttime) or not check_time(endtime):
            await ctx.followup.send(f"`starttime` and `endtime` must be in `HH:MM` format. \n" +
                                     "Examples: `23:00`, `12:30`, `21:45`", ephemeral=True)
            return

        confirmation = Confirmation(ctx.user)

        embed_var = discord.Embed(title="Confirmation", description="This schedule will change. Confirm?", color=0x00FF00)
        embed_var.add_field(name=f"{data[0][0]}", value=f"Before: {data[0][1]}: {data[0][2]} - {data[0][3]}\n" +
                                                        f"After: {day.name}: {starttime} - {endtime}")

        await ctx.followup.send(embed=embed_var, view=confirmation, ephemeral=True)
        await confirmation.wait()

        if confirmation.value == 0:
            await ctx.edit_original_response(content="Adding a new schedule has been cancelled.", embed=None, view=None)
            return
        elif confirmation.value == None:
            await ctx.edit_original_response(content="Response timeout.", embed=None, view=None)
            return
        
        Database.execute_command(update['schedule'], (day.name, starttime, endtime, scheduleid))
        await ctx.edit_original_response(content=f"Schedule #{scheduleid} has been updated", embed=None, view=None)

    @app_commands.command(name="schedule", description="Shows current schedule on day specified.")
    @app_commands.describe()
    @app_commands.choices(
        day=[
                app_commands.Choice(name="Sunday",      value=0),
                app_commands.Choice(name="Monday",      value=1),
                app_commands.Choice(name="Tuesday",     value=2),
                app_commands.Choice(name="Wednesday",   value=3),
                app_commands.Choice(name="Thursday",    value=4),
                app_commands.Choice(name="Friday",      value=5),
                app_commands.Choice(name="Saturday",    value=6),
            ])
    @app_commands.guild_only()
    async def schedule(self, ctx: discord.Interaction, day: app_commands.Choice[int]=None):
        await ctx.response.defer()

        utc = Database.get_data(read['utc'], (ctx.guild.id,))[0][0]
        day_to_check = day.name if not day == None else get_day(utc)

        data = Database.get_data(read['schedules_from_day'], (day_to_check, ctx.guild.id))
        number_of_subjects = len(data)

        embed_var = discord.Embed(title=f"{day_to_check} Subjects", 
                                  description=f"Here is the schedule for {day_to_check}.",
                                  color=0xFF0000)

        if number_of_subjects == 0:
            embed_var.add_field(name="There are no subjects listed.", value="Must be your free time!")
            await ctx.followup.send(embed=embed_var)
            return

        for subjects in data:
            embed_var.add_field(name=subjects[1], value=f"#{subjects[0]}: {subjects[2]} - {subjects[3]}", inline=False)

        await ctx.followup.send(embed=embed_var)


async def setup(bot):
    await bot.add_cog(ScheduleCommands(bot))