# mybutton.py
# Made by Chinese Parrot 29th july 2024

import discord

class MyButton(discord.ui.Button):
    def __init__(self, custom_id, label, style, callback_function):
        super().__init__(custom_id=custom_id, label=label, style=style)
        self.callback_function = callback_function

    async def callback(self, interaction):
        await self.callback_function(interaction)
        self.disabled = True