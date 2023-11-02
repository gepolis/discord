import disnake
from disnake import Embed, Colour


class EmbedType:
    SUCCESS = Colour.green()
    ERROR = Colour.red()
    INFO = Colour.blue()
    MAGENTA = Colour.magenta()


class EmbedManager:
    def __init__(self, mode: EmbedType, title: str, description: str = None, fields: list = None):
        self.mode = mode
        self.title = title
        self.description = description
        self.fields = fields

    def generate(self):
        embed = Embed(title=self.title, description=self.description, colour=self.mode)
        if self.fields is not None:
            for field in self.fields:
                if len(field) != 3:
                    inline = False
                else:
                    inline = field[2]
                embed.add_field(name=field[0], value=field[1], inline=inline)
        return embed


class BanEmbed:
    def __init__(self, user: disnake.User, reason: str, given_by: disnake.User):
        self.server_embed = EmbedManager(EmbedType.ERROR, f"Успешно заблокирован",
                                         fields=[("Выдал", f'{given_by.mention}', True),
                                                 ("Пользователь", f'{user.mention}', True),
                                                 ("Причина", f'{reason}', False)]).generate()
        self.dm_embed = EmbedManager(EmbedType.ERROR, f"Вы были заблокированы",
                                     fields=[("Выдал", f'{given_by.mention}', True),
                                             ("Причина", f'{reason}', False)]).generate()


class HelpCategoryCommand:
    def __init__(self, name: str, args: str, description: str):
        self.name = name
        self.args = args
        self.description = description

    def __str__(self):
        return [f'/{self.name} {self.args}', self.description]


class HelpCategory:
    def __init__(self, name: str):
        self.name = name
        self.commands = []

    def add_command(self, command: HelpCategoryCommand):
        self.commands.append(command)

    def add_commands(self, *commands):
        for command in commands:
            self.commands.append(command)

    def generate_commands_text(self):
        text = ""
        for i in self.commands:
            text += f'`{i.name}` '
        return text

    def generate_embed(self):
        embed = disnake.Embed(title=self.name, colour=disnake.Colour.magenta())
        for i in self.commands:
            embed.add_field(name=f'/{i.name} {i.args}', value=i.description, inline=False)
        return embed


class HelpManager:
    def __init__(self):
        self.categories = {}

    def add_category(self, category: HelpCategory):
        self.categories[category.name] = category

    def get_categories(self):
        return self.categories

    def get_category(self, name):
        return self.categories[name]

    def get_dropdown(self):
        categories = []
        for i in self.categories:
            print(i)
            categories.append(disnake.SelectOption(label=i, value=i))
        return categories

    def generate_embed(self):
        embed = disnake.Embed(title="Помощь", colour=disnake.Colour.magenta())
        for i in self.categories:
            embed.add_field(name=i, value=self.categories[i].generate_commands_text())
        return embed
