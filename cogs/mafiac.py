import disnake
from disnake.ext import commands

from database import mafia
from cogs.menus.mafia import CreateGameModal


class MafiaCom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.leading_role = 1168891411551228025

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def create_game(self, inter: disnake.CommandInteraction):
        modal = CreateGameModal()
        await inter.response.send_modal(modal)

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def delete_room(self, inter: disnake.CommandInteraction, code):
        room = mafia.MafiaRooms.get(mafia.MafiaRooms.invite == code)
        category = inter.guild.get_channel(room.control_channel).category
        for channel in category.channels:
            await channel.delete()
        room.delete_instance()
        await category.delete()
        await inter.response.send_message("Комната удалена", ephemeral=True)


def setup(bot):
    bot.add_cog(MafiaCom(bot))
