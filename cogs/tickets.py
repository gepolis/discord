import asyncio

import disnake
from disnake import ChannelType
from disnake.ext import commands

import db

tickets = db.Tickets("db.db")
assistent_logs = db.AssistentLogs("db.db")

class CloseTicket(disnake.ui.View):
    def __init__(self, channel, user):
        self.channel = channel
        self.user = user
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Закрыть", style=disnake.ButtonStyle.red, custom_id="persistent_example:close"
    )
    async def close(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.user.id == self.user:
            button.disabled = True
            tickets.close_ticket(self.channel)
            embed = disnake.Embed(
                title="Тикет",
                description=f"Тикет был закрыт",
                color=disnake.Colour.red()
            )

            channel = inter.guild.get_channel_or_thread(self.channel)
            await channel.send(embed=embed)
            id = channel.name.split("-")[1]
            await channel.edit(name=f"Closed-{id}", locked=True, reason="user requested", archived=True)

            assistents_msgs = {}
            async for i in channel.history(limit=None):
                if inter.guild.get_role(1162708530797756466) in inter.guild.get_member(i.author.id).roles:
                    assistents_msgs[i.author.id] = assistents_msgs.get(i.author.id, 0) + 1

            for k,v in assistents_msgs.items():
                assistent = k
                break
            assistent_logs.add_log(assistent, channel.id)
            if assistent_logs.check_conut(assistent,2):
                assistent = await inter.guild.fetch_member(assistent)
                await assistent.add_roles(inter.guild.get_role(1162708529669492776))
                up_channel = inter.guild.get_channel(1167932169432334366)
                embed = disnake.Embed(
                    title="Повышение",
                    description=f"{assistent.mention} был повышен до модератора.\n\nПовысил: <@1162717118622613596>",
                    color=disnake.Colour.blurple()

                )
                await up_channel.send(embed=embed)







class PersistentView(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Создать запрос", style=disnake.ButtonStyle.blurple, custom_id="persistent_example:create",emoji="📩"
    )
    async def green(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        guild = inter.guild
        count = str(int(tickets.count_tickets()) + 1)
        while len(count) != 4: count = "0" + count

        channel = guild.get_channel(1167882699248242688)
        message = await channel.send(f"{count}")
        thread = await channel.create_thread(name=f"Ticket-{count}",type=ChannelType.private_thread)
        await message.delete()
        tickets.create_ticket(inter.user.id, thread.id,)

        embed = disnake.Embed(
            title="Тикет",
            description=f"Пожалуйста, напишите свой вопрос",
            color=disnake.Colour.magenta()
        )
        embed.set_author(name=inter.user.name, icon_url=inter.user.display_avatar.url)
        await thread.send(embed=embed, view=CloseTicket(thread.id, inter.user.id))
        message = await thread.send(f"{inter.user.mention}")
        await message.delete()
        role = guild.get_role(1162708530797756466)

        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.channel == thread and m.author == inter.user,
                timeout=540
            )
        except asyncio.TimeoutError:
            warning = await thread.send(f"**{inter.user.mention}**, у вас осталась одна минута!"
                              f" Пожалуйста, напишите свой вопрос, иначе он будет удален!")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.channel == thread and m.author == inter.user,
                    timeout=60
                )
            except asyncio.TimeoutError:
                tickets.delete(thread.id)
                await thread.delete(reason="Timeout")
                return
            else:
                await warning.delete()
                msg = await thread.send(role.mention)
                await msg.delete(delay=2.0)
                return
        else:
            msg = await thread.send(role.mention)
            await msg.delete(delay=2.0)
            return


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False


    @commands.Cog.listener()
    async def on_ready(self):
        # `on_ready` can be fired multiple times during a bot's lifetime,
        # we only want to register the persistent view once.
        if not self.persistent_views_added:
            for i in tickets.all_open_tickets():
                self.bot.add_view(CloseTicket(i[1], i[0]))
            # Register the persistent view for listening here.
            # Note that this does not send the view to any message.
            # In order to do this you need to first send a message with the View, which is shown below.
            # If you have the message_id you can also pass it as a keyword argument, but for this example
            # we don't have one.
            self.bot.add_view(PersistentView(self.bot))
            self.persistent_views_added = True

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def test_ticket(self, interaction: disnake.CommandInteraction):
        view = PersistentView(self.bot)
        embed = disnake.Embed(
            title="Служба поддержки",
            description="Нажмите кнопку снизу, чтобы создать обращение в службу поддержки.",
            color=disnake.Colour.magenta()
        )
        await interaction.channel.send(embed=embed, view=view)

    @commands.slash_command()
    async def close(self, interaction: disnake.CommandInteraction):
        if tickets.exists(interaction.channel.id) and interaction.guild.get_role(1162708530797756466) in interaction.user.roles:
            tickets.close_ticket(interaction.channel.id)
            id = interaction.channel.name.split("-")[1]
            embed = disnake.Embed(
                title="Тикет #"+id,
                description=f"Тикет был закрыт сотрудником {interaction.author.mention}",
                color=disnake.Colour.red()
            )


            await interaction.channel.send(embed=embed)
            await interaction.channel.send(f"{interaction.guild.get_role(1162708529669492776).mention} "
                                           f"проверьте тикет на нарушения правил. ")
            await interaction.channel.edit(name=f"Staff-{id}", locked=True, reason="by staff")
    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message):
        channel = message.channel
        if tickets.exists(channel.id) and message.author != self.bot.user:
            await channel.send(f"{message.author.mention}, удалил сообщение: **{message.content}** ")

def setup(bot):
    bot.add_cog(Ticket(bot))

#💬