import discord
from discord import app_commands, permissions
from discord.ext import commands
from discord.utils import get
from discord.app_commands.errors import BotMissingPermissions
from discord.permissions import Permissions

class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="giverole", description="Gives user the School Angel role to manage messages, subjects, homeworks, and schedule")
    @app_commands.checks.bot_has_permissions(manage_roles=True, manage_messages=True)
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.describe(user="A Discord member")
    @app_commands.guild_only()
    async def give_role(self, ctx: discord.Interaction, user: discord.Member):
        await ctx.response.defer(ephemeral=True)

        role = get(ctx.guild.roles, name="School Angel")

        if not role:
            perms = discord.Permissions(manage_messages=True)
            await ctx.guild.create_role(name="School Angel", color=0xFFFFFF, permissions=perms, mentionable=True, reason="Heaven has given this member a role to moderate.")

        if get(user.roles, name="School Angel"):
            await ctx.followup.send(f"{user.mention} already has the School Angel role.", ephemeral=True)
            return

        await user.add_roles(role)
        await ctx.followup.send(f"School Angel role has been given to {user.mention}.", ephemeral=True)
    
    @app_commands.command(name="revokerole", description="Revoke the Angel role from a user")
    @app_commands.checks.bot_has_permissions(manage_roles=True, manage_messages=True)
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.describe(user="A Discord member")
    @app_commands.guild_only()
    async def revoke_role(self, ctx: discord.Interaction, user: discord.Member):
        await ctx.response.defer(ephemeral=True)
        role = get(ctx.guild.roles, name="School Angel")

        if not role:
            await ctx.followup.send(f"Server does not have the School Angel role.", ephemeral=True)
            return
        
        if not get(user.roles, name="School Angel"):
            await ctx.followup.send(f"{user.mention} does not have the School Angel role.", ephemeral=True)
            return

        await user.remove_roles(role)
        await ctx.followup.send(f"School Angel role has been revoked from {user.mention}.", ephemeral=True)

    @give_role.error
    @revoke_role.error
    async def role_error(self, ctx: discord.Interaction, error):
        if isinstance(error, BotMissingPermissions):
            await ctx.response.send_message(f"Tenshi can't create or manage roles! Please check her permissions.", ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(ModerationCommands(bot))