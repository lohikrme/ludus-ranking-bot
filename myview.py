import discord

class MyView(discord.ui.View):
    def __init__(self, custom_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_id = custom_id
        self.disable_all_items()

    def disable_all_items(self):
        for item in self.children:
            item.disabled = True