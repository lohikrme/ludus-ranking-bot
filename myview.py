# myview.py 
# Made by Chinese Parrot 29th july 2024

import discord

class MyView(discord.ui.View):
    def __init__(self, custom_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_id = custom_id

    def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        self.clear_items()