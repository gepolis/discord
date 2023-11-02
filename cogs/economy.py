from disnake import app_commands, ApplicationCommandInteraction, ui
from disnake.ext import commands
import disnake
from db import Users
from cogs.menus.economy import AdminMainView


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Users("db.db")

    @commands.slash_command()
    async def balance(self, interaction: disnake.CommandInteraction):
        usr = self.db.get_user(interaction.user.id)
        embed = disnake.Embed(
            title="Баланс",
            description=f"В банке: {usr[2]}$",
            color=disnake.Colour.green()
        )
        await interaction.send(embed=embed)

    @commands.slash_command()
    @commands.cooldown(1, 60*60) # 1 hour cooldown
    async def work(self, interaction: disnake.CommandInteraction):
        self.db.add_money(interaction.author.id, 200)
        user = self.db.get_user(interaction.author.id)
        embed = disnake.Embed(
            title="Работа",
            description=f"Вы получили 200$\n\nВ банке: {user[2]}$\n",
            color=disnake.Colour.green()
        )
        await interaction.send(embed=embed, ephemeral=True)

        async def callback(self, interaction: ApplicationCommandInteraction):
            user = self.db.get_user(interaction.user.id)
            embed = disnake.Embed(
                title="Ваш баланс",
                description=f"В банке: {user[2]}$",
                color=disnake.Colour.green()
            )
            await interaction.response.send_message(embed=embed)

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def economy(self, interaction: disnake.CommandInteraction):
        view = AdminMainView()
        await interaction.send("Управление экономикой",view=view,ephemeral=True)
    @commands.Cog.listener()
    async def on_slash_command_error(self,interaction: ApplicationCommandInteraction, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            embed = disnake.Embed(
                title="Команда слишком часто используется",
                description=f"Попробуйте через {error.retry_after:.1f} секунд"
            )
            await interaction.send(embed=embed, ephemeral=True)
        else:
            print(error)
def setup(bot):
    bot.add_cog(Economy(bot))

#📜