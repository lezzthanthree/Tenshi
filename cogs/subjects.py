import discord
from discord import app_commands
from discord.ext import commands
from buttons import Confirmation
from database import Database, create, insert, delete, update, read
from sqlite3 import IntegrityError

class SubjectCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addsubject", description="Adds a subject")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(subject="The name of the subject",
                           code="The subject's code")
    @app_commands.guild_only()
    async def add_subject(self, ctx: discord.Interaction, subject: str, code: str = None):
        await ctx.response.defer(ephemeral=True)
        
        if code == None:
            code = subject.replace(" ", "")[:3].upper() + "-" + str(hash(subject))[0:5]
        
        confirmation = Confirmation(ctx.user)

        embed_var = discord.Embed(title="Confirmation", description="This subject will be added to the subject list. Confirm?", color=0x00FF00)
        embed_var.add_field(name=code, value=subject)

        await ctx.followup.send(embed=embed_var, view=confirmation, ephemeral=True)
        await confirmation.wait()

        get_original = await ctx.original_response()

        if confirmation.value == 0:
            await get_original.edit(content="Adding a new subject has been cancelled.", embed=None, view=None)
            return
        elif confirmation.value == None:
            await get_original.edit(content="Response timeout.", embed=None, view=None)
            return
        
        try:
            Database.execute_command(insert['subject'], (code, subject, ctx.guild.id))
        except IntegrityError:
            await get_original.edit(content=f"Subject `{code}` has already been in the database.", embed=None, view=None)
            return

        await get_original.edit(content=f"{subject} has been added to the subject list.", embed=None, view=None)

    @app_commands.command(name="removesubject", description="Remove a subject on the list")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(code="The subject's code")
    @app_commands.guild_only()
    async def remove_subject(self, ctx: discord.Interaction, code: str):
        await ctx.response.defer(ephemeral=True)
        
        data = Database.get_data(read['subject_from_code'], (code, ctx.guild.id))

        if len(data) == 0:
            await ctx.followup.send(f"Subject code `{code}` does not exist. Please type `/subjects` to see available subject codes.", ephemeral=True)
            return
        
        confirmation = Confirmation(ctx.user)

        embed_var = discord.Embed(title="Confirmation", description="This subject will be removed to the subject list. Confirm?", color=0x00FF00)
        embed_var.add_field(name=data[0][0], value=data[0][1])

        await ctx.followup.send(embed=embed_var, view=confirmation, ephemeral=True)
        await confirmation.wait()

        get_original = await ctx.original_response()

        if confirmation.value == 0:
            await get_original.edit(content="Removing a subject has been cancelled.", embed=None, view=None)
            return
        elif confirmation.value == None:
            await get_original.edit(content="Response timeout.", embed=None, view=None)
            return
        
        Database.execute_command(delete['subject'], (code,))
        await get_original.edit(content=f"{code} has been removed to the subject list.", embed=None, view=None)

    @app_commands.command(name="subjects", description="Shows all subjects")
    @app_commands.describe()
    @app_commands.guild_only()
    async def subjects(self, ctx: discord.Interaction):
        await ctx.response.defer()

        data = Database.get_data(read['subjects_from_guild'], (ctx.guild.id,))
        number_of_subjects = len(data)

        embed_var = discord.Embed(title="Current Subjects", 
                                  description="Here is the list of subjects in this server.",
                                  color=0xFF0000)

        if number_of_subjects == 0:
            embed_var.add_field(name="There are no subjects listed.", value="Ask the School Angels to add one.")
            await ctx.followup.send(embed=embed_var)
            return

        for subjects in data:
            embed_var.add_field(name=subjects[0], value=subjects[1], inline=False)

        await ctx.followup.send(embed=embed_var)

async def setup(bot):
    await bot.add_cog(SubjectCommands(bot))