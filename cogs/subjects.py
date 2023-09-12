import discord
from discord import app_commands
from discord.ext import commands
from buttons import Confirmation, Page
from database import Database, create, insert, delete, update, read
from sqlite3 import IntegrityError
from math import ceil

def page(page_number = 1, min = 0, max = 5):
    page = {
        'page': page_number,
        'min': min,
        'max': max
    }
    
    return page

class SubjectCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="createsubject", description="Creates a subject")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(subject="The name of the subject",
                           code="The subject's code")
    @app_commands.guild_only()
    async def create_subject(self, ctx: discord.Interaction, subject: str, code: app_commands.Range[str, 5, 20] = None):
        await ctx.response.defer(ephemeral=True)

        if code == None:
            code = subject.replace(" ", "")[:3].upper() + "-" + str(hash(subject))[0:5]

        data = Database.get_data(read['search_subject_id_all'], (code,))

        if not len(data) == 0:
            await ctx.followup.send(f"`{code}` is in the database. Please rename your subject code", ephemeral=True)
            return
        
        await self.start_confirmation(ctx,
                                      "This subject will be created for enrollment. Confirm?",
                                      code,
                                      subject,
                                      f"{subject} has been created to the database.",
                                      "Creating a new subject has been cancelled.",
                                      database_command=insert['subject'],
                                      database_parameters=(code, subject, ctx.guild.id))
        
        await self.start_confirmation(ctx,
                                      "Do you also wish this server to enroll on this subject?",
                                      code,
                                      subject,
                                      f"{subject} has been enrolled to this server.",
                                      f"{subject} has been created to the database.",
                                      database_command=insert['enrollment'],
                                      database_parameters=(ctx.guild.id, code))

    @app_commands.command(name="deletesubject", description="Deletes a subject created by this server")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(code="The subject's code")
    @app_commands.guild_only()
    async def delete_subject(self, ctx: discord.Interaction, code: str):
        await ctx.response.defer(ephemeral=True)
        
        data = Database.get_data(read['subject_from_code_in_guild'], (code, ctx.guild.id))

        if len(data) == 0:
            await ctx.followup.send(f"Subject code `{code}` does not exist. Please type `/listsubjects check:owned` to see subjects created by this server.", ephemeral=True)
            return
        
        removal = await self.start_confirmation(ctx,
                                                "This subject will be deleted from the database. If this is a public subject, this will also be deleted to other servers. Confirm?",
                                                data[0][0],
                                                data[0][1],
                                                f"{code} has been deleted to the subject list.",
                                                "Deleting a subject has been cancelled.",
                                                database_command=delete['subject'],
                                                database_parameters=(ctx.guild.id, code))
        
        if removal:
            Database.execute_command(delete['enrollment_with_ids'], (code,))
        
    @app_commands.command(name="enrollsubject", description="Enrolls a subject to this server")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(code="The subject's code")
    @app_commands.guild_only()
    async def enroll_subject(self, ctx: discord.Interaction, code: str):
        await ctx.response.defer(ephemeral=True)

        data = Database.get_data(read['search_subject'], (code, code, ctx.guild.id))

        if len(data) == 0:
            await ctx.followup.send(f"Subject code `{code}` does not exist. Please type `/listsubjects` to see available subjects to enroll.", ephemeral=True)
            return

        await self.start_confirmation(ctx,
                                      "Server will be enrolling this subject. Confirm?",
                                      data[0][0],
                                      data[0][1],
                                      f"{code} has successfully been enrolled.",
                                      "Enrolling a subject has been cancelled.",
                                      database_command=insert['enrollment'],
                                      database_parameters=(ctx.guild.id, code))
        
    @app_commands.command(name="unenrollsubject", description="Unenrolls a subject from this server")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(code="The subject's code")
    @app_commands.guild_only()
    async def unenroll_subject(self, ctx: discord.Interaction, code: str):
        pass

    @app_commands.command(name="subjects", description="Shows enrolled subjects on this server")
    @app_commands.describe()
    @app_commands.guild_only()
    async def enrolled_subjects(self, ctx: discord.Interaction):
        await ctx.response.defer()

        data = Database.get_data(read['enrolled_subjects'], (ctx.guild.id,))
        number_of_subjects = len(data)

        if number_of_subjects == 0:
            await ctx.followup.send(content="There are no currently enrolled subjects. Ask the School Angels to enroll one!")
            return
                
        await self.view_subject_list(ctx, data, number_of_subjects, "Enrolled", "that are currently enrolled to this server")


    @app_commands.command(name="listsubjects", description="Check available subjects for enrollment")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe()
    @app_commands.choices(
        check=[
                app_commands.Choice(name="available", value="available_subjects"),
                app_commands.Choice(name="owned", value="owned_subjects"),
                app_commands.Choice(name="private", value="owned_private_subjects"),
              ]
    )
    @app_commands.guild_only()
    async def available_subjects(self, ctx: discord.Interaction, check: app_commands.Choice[str] = None):
        await ctx.response.defer(ephemeral=True)
        
        data_to_check = check.value if not check == None else "available_subjects"
        print(data_to_check)
        empty = "There are no subjects currently available for enrollment."
        title = "Available"
        description = "currently available for enrollment"

        data = Database.get_data(read[data_to_check], (ctx.guild.id,))
        number_of_subjects = len(data)

        if data_to_check == "owned_subjects":
            empty = "There are no subjects owned by this server."
            title = "Owned"
            description = "owned by this server"
        if data_to_check == "owned_private_subjects":
            empty = "There are no subjects privately owned by this server."
            title = "Privately Owned"
            description = "privately owned by this server"
            
        if number_of_subjects == 0:
            await ctx.followup.send(content=empty, ephemeral=True)
            return

        await self.view_subject_list(ctx, data, number_of_subjects, title, description)
    
    @app_commands.command(name="publicize", description="Make a subject available to all servers")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(code="The subject's code")
    @app_commands.guild_only()
    async def switch_to_public(self, ctx: discord.Interaction, code: str):
        await ctx.response.defer(ephemeral=True)
        
        data = Database.get_data(read['subject_from_code_in_guild'], (code, ctx.guild.id))

        if len(data) == 0:
            await ctx.followup.send(f"Subject code `{code}` does not exist. Please type `/ownedsubjects` to see available subjects on this server.", ephemeral=True)
            return
        if data[0][2] == False:
            await ctx.followup.send(f"{data[0][1]} is already public.", ephemeral=True)
            return
        
        await self.start_confirmation(ctx, 
                                      "This subject will be public. Other servers can see and enroll this subject. Confirm?",
                                      data[0][0],
                                      data[0][1],
                                      f"{data[0][1]} is now publicly available to all servers.",
                                      "Switching privacy has been cancelled.",
                                      database_command=update['private->public'],
                                      database_parameters=(code, ctx.guild.id))

    async def start_confirmation(self, ctx: discord.Interaction, message_confirmation_description = "Confirm?",
                                                                 message_field_name = "name",
                                                                 message_field_value = "value",
                                                                 message_accepted = "Confirmed.",
                                                                 message_rejected = "Rejected",
                                                                 message_timeout = "Response timeout.",
                                                                 database_command = "",
                                                                 database_parameters = ()):
        
        confirmation = Confirmation(ctx.user)

        embed_var = discord.Embed(title="Confirmation", description=message_confirmation_description, color=0x00FF00)
        embed_var.add_field(name=message_field_name, value=message_field_value)

        await ctx.edit_original_response(embed=embed_var, view=confirmation)
        await confirmation.wait()

        if confirmation.value == 0:
            await ctx.edit_original_response(content=message_rejected, embed=None, view=None)
            return False
        elif confirmation.value == None:
            await ctx.edit_original_response(content=message_timeout, embed=None, view=None)
            return False

        Database.execute_command(database_command, database_parameters)
        await ctx.edit_original_response(content=message_accepted, embed=None, view=None)
        return True

    async def view_subject_list(self, ctx: discord.Interaction, data, number_of_subjects, title, description):
        total_pages = ceil(number_of_subjects/5)

        pages = page(1, 0, 5)

        while True:
            embed_var = discord.Embed(title=f"{title} Subjects ({pages['page']}/{total_pages})", 
                                      description=f"Here are all the subjects listed {description}.",
                                      color=0xFF0000)
            page_view = Page(ctx.user)

            if pages['max'] > number_of_subjects:
                pages['max'] = number_of_subjects

            for subjects in data[pages['min']:pages["max"]]:
                embed_var.add_field(name=subjects[0], value=subjects[1], inline=False)

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
            
        await ctx.followup.send(content="Response timeout.", embed=None, view=None)

        
async def setup(bot):
    await bot.add_cog(SubjectCommands(bot))