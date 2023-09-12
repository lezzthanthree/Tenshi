import discord

class Buttons(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=30)
        self.author = author
        self.value = None

    async def interaction_check(self, ctx: discord.Interaction):
        if not ctx.user.id == self.author.id:
            await ctx.response.send_message("This is not your button to press.", ephemeral=True)

        return ctx.user.id == self.author.id

class Confirmation(Buttons):
    def __init__(self, author):
        super().__init__(author=author)
    
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def button_yes(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.edit_message(content="Please wait...", embed=None)
        self.value = 1
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def button_no(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.edit_message(content="Please wait...", embed=None)
        self.value = 0
        self.stop()

class Page(Buttons):
    def __init__(self, author):
        super().__init__(author=author)
        self.value = None
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, emoji='⏮')
    async def button_previous(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.edit_message(content="Fetching...")
        self.value = 'previous'
        self.stop()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, emoji='⏭')
    async def button_next(self, ctx: discord.Interaction, button: discord.ui.Button):
        await ctx.response.edit_message(content="Fetching...")
        self.value = 'next'
        self.stop()
