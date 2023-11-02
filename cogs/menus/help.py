import disnake

class SelectCategory(disnake.ui.Select):
    def __init__(self, show_admin=False, show_moderator=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = "Выберите категорию"
        self.options = [

        ]
