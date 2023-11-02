import datetime

import disnake
from disnake.ext import commands, tasks


class StaffApply(disnake.ui.Modal):
    def __init__(self):
        components = [disnake.ui.TextInput(
            label="Имя",
            placeholder="Имя",
            min_length=1,
            max_length=255,
            custom_id="name",
        ),
            disnake.ui.TextInput(
                label="Возраст",
                placeholder="Возраст",
                min_length=1,
                max_length=2,
                custom_id="age",
            ),
            disnake.ui.TextInput(
                label="Часовой пояс",
                placeholder="МСК+2",
                min_length=1,
                custom_id="timezone",
                max_length=10,
            ),
            disnake.ui.TextInput(
                label="Есть опыт в подобных должностях?",
                placeholder="Если есть то какой?",
                min_length=1,
                max_length=1000,
                custom_id="experience",
                style=disnake.TextInputStyle.paragraph,
            ),
            disnake.ui.TextInput(
                label="О себе",
                placeholder="О себе",
                custom_id="about",
                min_length=1,
                max_length=1000,
                style=disnake.TextInputStyle.paragraph,

            )
        ]
        super().__init__(
            title="Заявка на пост модератора",
            components=components,
        )

    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(
            title="Заявка",
            description="{}".format(inter.user.mention),
            colour=disnake.Colour.purple()
        )
        embed.add_field(name="Пользователь", value=f'```{inter.author}```')
        embed.add_field(name="Имя", value=f'```{inter.text_values["name"]}```')
        embed.add_field(name="Возраст", value=f'```{inter.text_values["age"]}```')
        embed.add_field(name="Часовой пояс", value=f'```{inter.text_values["timezone"]}```')
        embed.add_field(name="О себе", value=f'```{inter.text_values["about"]}```', inline=False)
        embed.add_field(name="Опыт", value=f'```{inter.text_values["experience"]}```', inline=False)
        embed.set_footer(text=f"{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        embed.set_thumbnail(url=inter.user.display_avatar.url)

        channel = inter.guild.get_channel(1168093004171591701)
        await channel.send(embed=embed)

        embed = disnake.Embed(
            title="Вы успешно отправили заявку",
            colour=disnake.Colour.green()
        )
        await inter.response.send_message(embed=embed, ephemeral=True)

class StaffView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Подать заявку",
        style=disnake.ButtonStyle.blurple,
        custom_id="staff_apply"
    )
    async def apply(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        modal = StaffApply()
        await inter.response.send_modal(modal)
class Staff(commands.Cog):
    def __init__(self, bot):
        print("Staff cog loaded")
        self.bot = bot
        self.perp = False

    @commands.slash_command()
    async def staff(self, interaction: disnake.CommandInteraction):
        modal = StaffApply()
        embed = disnake.Embed(
            title="Открыт набор в персонал",
            description="Хотите **присоединиться** к команде нашего сервера? Тогда подайте заявку!",
            colour=disnake.Colour.blurple(),
        )
        await interaction.response.send_message("Успешно", ephemeral=True)
        await interaction.channel.send(embed=embed, view=StaffView())

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.perp:
            self.perp = True

            view = StaffView()
            self.bot.add_view(view)




def setup(bot):
    bot.add_cog(Staff(bot))
