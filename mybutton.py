import discord

class MyButton(discord.ui.Button):
    def __init__(self, label, style):
        super().__init__(label=label, style=style)

    async def option_callback(self, interaction):
        if interaction:
            print("option_callback works!")