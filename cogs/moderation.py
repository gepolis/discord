import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from disnake.ext.commands import Param


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def clear(self, interaction: disnake.CommandInteraction, amount: int):
        await interaction.response.defer()
        await interaction.channel.purge(limit=amount)
        embed = disnake.Embed(
            title="Канал очищен",
            description=f"Администратор: {interaction.author.mention}",
            color=disnake.Colour.green()
        )
        await interaction.send(embed=embed)

    @commands.slash_command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, interaction: disnake.CommandInteraction, member: disnake.Member, reason=None):
        error = None

        if reason is None:
            error = "Укажите причину"

        member_top_role = member.top_role.position
        moderator_top_role = interaction.author.top_role.position
        if member_top_role < moderator_top_role:
            error = "Недостаточно прав!"

        if error is not None:
            embed = disnake.Embed(
                title="Ошибка",
                description=error,
                color=disnake.Colour.red()
            )
            await interaction.send(embed=embed, ephemeral=True)
        else:
            await member.kick(reason=reason)
            embed = disnake.Embed(
                title="Пользователь был выгнан",
                description=f"Причина: {reason}\nВыгнал: {interaction.author.mention}\nПользователь: {member.mention}",
                color=disnake.Colour.green()
            )
            await interaction.send(embed=embed)

    @commands.slash_command()
    @commands.cooldown(5, 60*10) # 10 minutes
    @commands.has_permissions(ban_members=True)
    async def ban(self, interaction: disnake.CommandInteraction, member: disnake.Member, reason=None):
        error = None

        if reason is None:
            error = "Укажите причину"

        member_top_role = member.top_role.position
        moderator_top_role = interaction.author.top_role.position
        if member_top_role < moderator_top_role:
            error = "Недостаточно прав!"

        if error is not None:
            embed = disnake.Embed(
                title="Ошибка",
                description=error,
                color=disnake.Colour.red()
            )
            await interaction.send(embed=embed, ephemeral=True)
        else:
            await member.kick(reason=reason)
            embed = disnake.Embed(
                title="Пользователь был заблокирован",
                description=f"Причина: {reason}\nЗаблокирован: {interaction.author.mention}\nПользователь: {member.mention}",
                color=disnake.Colour.green()
            )
            await interaction.send(embed=embed)


    @commands.slash_command()
    @commands.has_permissions(ban_members=True)
    async def request_unban(self, interaction: disnake.CommandInteraction, member: disnake.User, reason=None):
        channel = interaction.guild.get_channel(1167749846350975026)
        embed = disnake.Embed(
            title="Запрос на разблокировку",
            description=f"Причина: {reason}\nЗапросил: {interaction.author.mention}\nПользователь: {member.mention}",
        )
        await channel.send(embed=embed)

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def bans(self, interaction: disnake.CommandInteraction):

        embed = disnake.Embed(
            title="Список заблокированных пользователей",
            description=f"Список: {interaction.guild.bans}",
            color=disnake.Colour.green()
        )
        await interaction.send(embed=embed)

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def send_eer(self, interaction: disnake.CommandInteraction):
        embed = disnake.Embed(
            title="Правила персонала",
            description=f"1. Будьте вежливы и уважительны к участникам сервера.\n2. Будьте активными и готовыми помочь участникам с их вопросами и проблемами.\n3. Следите за соблюдением правил сервера и немедленно реагируйте на нарушения.\n4. Будьте терпимы к различным мнениям и культурам.\n5. Умейте эффективно общаться и решать конфликты с участниками сервера.\n6. Будьте ответственными и выполняйте свои обязанности с дисциплиной и в срок.\n7. Слушайте обратную связь участников сервера и стремитесь к постоянному улучшению качества обслуживания.",
            color=disnake.Colour.magenta()
        )
        await interaction.channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Moderation(bot))