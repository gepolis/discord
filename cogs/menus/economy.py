import disnake
from db import Users

db = Users("db.db")
class AdminModal(disnake.ui.Modal):
    def __init__(self, user_id,type):
        component = disnake.ui.TextInput(
            label="Сумма",
            placeholder="Сумма",
            min_length=1,
            max_length=255,
            custom_id="amount",
        )
        super().__init__(
            title="Админ панель",
            components=[component],
        )
        self.type = type
        self.user_id = user_id

    async def callback(self, inter: disnake.ModalInteraction):
        value = inter.text_values['amount']
        if self.type == "give":
            db.add_money(self.user_id, int(value))
        elif self.type == "take":
            db.add_money(self.user_id, int(value)*-1)
        else:
            bal = db.get_user(self.user_id)[2]
            db.add_money(inter.user.id, int(bal) * -1)
        await inter.response.send_message(f"Успешно",ephemeral=True)



class AdminSelectUser(disnake.ui.UserSelect):
    def __init__(self, type):
        super().__init__(
            placeholder="Выберите участника",
            min_values=1,
            max_values=1,
        )
        self.type_m = type

    async def callback(self, inter: disnake.MessageInteraction):
        if self.type_m == "reset":
            bal = db.get_user(self.values[0].id)[2]
            db.add_money(self.values[0].id, int(bal) * -1)
            await inter.response.send_message(f"Успешно",ephemeral=True)
        elif self.type_m == "info":
            bal = db.get_user(self.values[0].id)[2]
            embed = disnake.Embed(
                title="Информация ",
                description=f"Баланс {self.values[0].mention}: {bal}$",
            )
            await inter.response.send_message(embed=embed,ephemeral=True)
        else:
            await inter.response.send_modal(AdminModal(self.values[0].id,self.type_m))



class AdminSelectUserView(disnake.ui.View):
    def __init__(self,t):
        super().__init__()
        self.add_item(AdminSelectUser(t))

class AdminMainMenu(disnake.ui.StringSelect):
    def __init__(self):
        options = [
            disnake.SelectOption(label="Выдать", value="give",description="Выдает деньги определенному участнику"),
            disnake.SelectOption(label="Забрать", value="take",description="Забрать деньги определенного участника"),
            disnake.SelectOption(
                label="Обнулить баланс", value="reset",description="Обнулить баланс определенного участника"
            ),
            disnake.SelectOption(
                label="Сбросить экономику", value="reset_all",description="Сбросить экономику всего сервера"
            ),
            disnake.SelectOption(
                label="Информация", value="info",description="Информация о балансе участника"
            )
        ]

        super().__init__(
            placeholder="Выберите действие",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        if self.values[0] == "give":
            view = AdminSelectUserView("give")
            await inter.response.send_message("Выберите участника", view=view,ephemeral=True)
        elif self.values[0] == "take":
            view = AdminSelectUserView("take")
            await inter.response.send_message("Выберите участника", view=view,ephemeral=True)
        elif self.values[0] == "reset":
            view = AdminSelectUserView("reset")
            await inter.response.send_message("Выберите участника", view=view,ephemeral=True)
        elif self.values[0] == "reset_all":
            db.reset_money()
            await inter.response.send_message("Экономика была сброшена",ephemeral=True)
        elif self.values[0] == "info":
            view = AdminSelectUserView("info")
            await inter.response.send_message("Выберите участника", view=view, ephemeral=True)


class AdminMainView(disnake.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(AdminMainMenu())
