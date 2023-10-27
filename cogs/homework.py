import discord
from database import Database, read, insert, delete
from discord import app_commands
from discord.ext import commands
from buttons import Confirmation, Page
from math import ceil

def page(page_number = 1, min = 0, max = 5):
    page = {
        'page': page_number,
        'min': min,
        'max': max
    }
    
    return page

class Homework(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="homework", description="Show current list of homeworks")
    @app_commands.describe()
    @app_commands.guild_only()
    async def homework(self, ctx: discord.Interaction):
        await ctx.response.defer()

        data = Database.get_data(read['homeworks_from_guild'], (ctx.guild.id,))

        number_of_homeworks = len(data)

        if number_of_homeworks == 0:
            await ctx.followup.send(content="There are no homeworks to pass! Horray!", ephemeral=True)
            return

        await self.view_homework_list(ctx, data, number_of_homeworks, "Homework", "Please take note of the deadline!")


    @app_commands.command(name="addhomework", description="Add a homework")
    @app_commands.describe(code="The subject's ID",
                           description="The homework's description",
                           deadline="The homework's deadline (MM/DD/YYYY HH:MM)")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def addhomework(self, ctx: discord.Interaction, code: str,
                                                          description: str,
                                                          deadline: str = None):
        await ctx.response.defer(ephemeral=True)

        data = Database.get_data(read['enrolled_subject_from_code'], (code, ctx.guild.id))

        if deadline == None:
            deadline = "No deadline"
        if len(data) == 0:
            await ctx.followup.send(f"Subject code `{code}` does not exist. Please type `/subjects` to see available subject codes.", ephemeral=True)
            return
        
        confirmation = Confirmation(ctx.user)
        embed_var = discord.Embed(title="Confirmation", description="Create a new homework.", color=0x00FF00)
        embed_var.add_field(name=f"{data[0][1]}", value=f"{description}\n" +
                                                        f"*{deadline}*")
        
        await ctx.followup.send(embed=embed_var, view=confirmation)
        await confirmation.wait()

        if confirmation.value == 0:
            await ctx.edit_original_response(content="Adding a new homework has been cancelled.", embed=None, view=None)
            return
        elif confirmation.value == None:
            await ctx.edit_original_response(content="Response timeout.", embed=None, view=None)
            return
        
        Database.execute_command(insert['homework'], (ctx.guild.id, code, description, deadline))
        await ctx.edit_original_response(content=f"Homework has been added.", embed=None, view=None)

    @app_commands.command(name="deletehomework", description="Delete a homework")
    @app_commands.describe(id="The homework's ID")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def deletehomework(self, ctx: discord.Interaction, id: int):
        await ctx.response.defer(ephemeral=True)

        data = Database.get_data(read['homework_from_id'], (ctx.guild.id, id))

        if len(data) == 0:
            await ctx.followup.send(f"Homework #{id} does not exists. Check `/homework` for available homeworks.", ephemeral=True)
            return
        
        confirmation = Confirmation(ctx.user)
        embed_var = discord.Embed(title="Confirmation", description="This will delete the homework specified.", color=0xFF0000)
        embed_var.add_field(name=f"{data[0][0]}", value=f"{data[0][1]}\n" +
                                                        f"*{data[0][2]}*")
        
        await ctx.followup.send(embed=embed_var, view=confirmation)
        await confirmation.wait()

        if confirmation.value == 0:
            await ctx.edit_original_response(content="Deleting a homework has been cancelled.", embed=None, view=None)
            return
        elif confirmation.value == None:
            await ctx.edit_original_response(content="Response timeout.", embed=None, view=None)
            return
        
        Database.execute_command(delete['homework'], (id,))
        await ctx.edit_original_response(content=f"Homework has been deleted.", embed=None, view=None)

    async def view_homework_list(self, ctx: discord.Interaction, data, number_of_homeworks, title, description):
        total_pages = ceil(number_of_homeworks/5)

        pages = page(1, 0, 5)

        while True:
            embed_var = discord.Embed(title=f"{title} ({pages['page']}/{total_pages})", 
                                      description=f"{description}",
                                      color=0xFF0000)
            page_view = Page(ctx.user)

            if pages['max'] > number_of_homeworks:
                pages['max'] = number_of_homeworks

            for homeworks in data[pages['min']:pages["max"]]:
                embed_var.add_field(name=homeworks[1], value=f"ID #{homeworks[0]}: {homeworks[2]}\n*{homeworks[3]}*", inline=False)

            await ctx.edit_original_response(content="", embed=embed_var, view=page_view)

            await page_view.wait()

            embed_var.clear_fields()

            if page_view.value == 'previous':
                if pages['page'] - 1 <= 0:
                    continue
                pages = page(pages['page'] - 1, (pages['page'] - 1) * 5 - 5, pages['min'])

            if page_view.value == 'next':
                if pages["page"] + 1 > total_pages:
                    continue
                pages = page(pages["page"] + 1, pages["max"], (pages["page"] + 1) * 5)

            if page_view.value == None:
                break
            
        await ctx.edit_original_response(view=None)


async def setup(bot):
    await bot.add_cog(Homework(bot))