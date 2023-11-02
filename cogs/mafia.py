import asyncio
import random

import disnake
from disnake.ext import commands
import mafia_cfg as cfg


def choose_role(mafia_cont, detective):
    r = random.randint(1, 3)
    if r == 1 and mafia_cont == 2:
        return choose_role(mafia_cont, detective)
    elif r == 2 and detective == 1:
        return choose_role(mafia_cont, detective)
    else:
        return r


def generate_players_message(players, cfg):
    roles = {
        1: "Мафия",
        2: "Детектив",
        3: "Мирный"
    }
    t = "🌑" if cfg.is_night else "🌞️"
    started = "✅" if cfg.start else "❌"
    msg = "```"
    if len(players) != 0:
        for player in players:
            msg += f"{player['name']} - {cfg.roles[player['role']]}\n"
    else:
        msg += "Нет игроков"
    msg += "```"
    embed = disnake.Embed(
        title="Игровое состояние",
        description=f"{msg}",
    )
    embed.add_field(name=f"Начало", value=f"```{started}```")
    embed.add_field(name=f"Время", value=f"```{t}```")
    return embed


def player_role(players):
    mafia = 0
    detective = 0
    if len(players) == 0:
        for i in players:
            if i.role == 1:
                mafia += 1
            elif i.role == 2:
                detective += 1
        return mafia, detective
    else:
        return 0, 0


def get_player_by_system_id(players, id):
    for i in players:
        if i['sysid'] == id:
            return i['id']
    return None


def remove_player(players, player):
    for i in players:
        if i['id'] == player:
            players.remove(i)
    return players


class PlayerSelect(disnake.ui.Select):
    def __init__(self, players, max_values=1, t="vote"):

        self.options = [
        ]
        self.t = t
        for i in players:
            self.options.append(disnake.SelectOption(label=f"{i['sysid']} {i['name']}", value=i['sysid']))

        super().__init__(
            placeholder="Выберите игрока",
            min_values=1,
            max_values=max_values,
            options=self.options
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        if self.t == "vote":
            vote_channel = inter.guild.get_channel(cfg.vote_channel)
            for p in inter.values:
                plr = get_player_by_system_id(cfg.players, int(p))
                if plr:
                    player = inter.guild.get_member(plr)

                    embed = disnake.Embed(
                        title="Голосование",
                        description=f"Кто за {player.mention}?",
                        color=disnake.Colour.green()
                    )
                    await vote_channel.send(embed=embed)
                    await asyncio.sleep(7)
            embed = disnake.Embed(
                title="Голосование закончено",
                color=disnake.Colour.red()
            )
            await vote_channel.send(embed=embed)
        elif self.t == "kick":
            for p in inter.values:
                plr = get_player_by_system_id(cfg.players, int(p))

                if plr:
                    player = inter.guild.get_member(plr)

                    cfg.players = remove_player(cfg.players, player.id)

                    players_message: disnake.Message = await inter.guild.get_channel(
                        cfg.control_channel).fetch_message(
                        cfg.players_message)
                    view = ContolPanel()
                    await players_message.edit(embed=generate_players_message(cfg.players, cfg), view=view)
                    await player.move_to(inter.guild.get_channel(1168179736762134588), reason="Kick")
                    msg = await inter.channel.send(f"Успешно")
                    await msg.delete(delay=2.0)
        else:
            for p in inter.values:
                plr = get_player_by_system_id(cfg.players, int(p))

                if plr:
                    player = inter.guild.get_member(plr)
                    room = inter.guild.get_channel(cfg.room_channel)
                    rec = inter.guild.get_channel(cfg.fasr_rec_channel)
                    speaker_role = inter.guild.get_role(cfg.can_speak_role)

                    await player.add_roles(speaker_role)
                    await player.move_to(rec, reason="Join to mafia room")
                    await player.move_to(room, reason="Join to mafia room")
                    await asyncio.sleep(40)
                    await player.remove_roles(speaker_role)
                    await player.move_to(rec, reason="Join to mafia room")
                    await player.move_to(room, reason="Join to mafia room")
                    msg = await inter.channel.send("Время вышло!")
                    await msg.delete(delay=2.0)


class PlayerSelectView(disnake.ui.View):
    def __init__(self, players, t="vote", max_values=1):
        super().__init__()

        self.add_item(PlayerSelect(players, max_values, t))


class ContolPanel(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Начать/Рестарт", style=disnake.ButtonStyle.blurple, row=1)
    async def start(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if cfg.start:
            room = inter.guild.get_channel(cfg.room_channel)
            killedchan = inter.guild.get_channel(1168179736762134588)
            for i in room.members:
                await i.move_to(killedchan, reason="Game reset")
            cfg.players = []
            cfg.mafia = []
            cfg.mafia_killed_in_night = []
            cfg.is_night = True
            cfg.start = False
            players_message: disnake.Message = await inter.guild.get_channel(cfg.control_channel).fetch_message(
                cfg.players_message)
            view = ContolPanel()
            await players_message.edit(embed=generate_players_message(cfg.players, cfg), view=view)
            await inter.response.send_message("Рестарт", ephemeral=True)
        else:
            cfg.start = True
            players_message: disnake.Message = await inter.guild.get_channel(cfg.control_channel).fetch_message(
                cfg.players_message)
            view = ContolPanel()
            await players_message.edit(embed=generate_players_message(cfg.players, cfg), view=view)
            await inter.response.send_message("Начало", ephemeral=True)

    @disnake.ui.button(label="Ночь", style=disnake.ButtonStyle.blurple, row=2)
    async def night(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        cfg.is_night = True
        players_message: disnake.Message = await inter.guild.get_channel(cfg.control_channel).fetch_message(
            cfg.players_message)
        view = ContolPanel()
        await players_message.edit(embed=generate_players_message(cfg.players, cfg), view=view)
        await inter.response.send_message("Ночь", ephemeral=True)
        await asyncio.sleep(15)
        cfg.is_night = False
        players_message: disnake.Message = await inter.guild.get_channel(cfg.control_channel).fetch_message(
            cfg.players_message)
        view = ContolPanel()
        await players_message.edit(embed=generate_players_message(cfg.players, cfg), view=view)
        await inter.send("День", ephemeral=True)

    @disnake.ui.button(label="Голосование", style=disnake.ButtonStyle.blurple, row=1)
    async def voting(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        view = PlayerSelectView(cfg.players)
        await inter.response.send_message("Выберите игрока", view=view, ephemeral=True)

    @disnake.ui.button(label="Обсуждение", style=disnake.ButtonStyle.blurple, row=2)
    async def conversation(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.defer()
        ms = await inter.channel.send("start")
        for p in cfg.players:
            plr = get_player_by_system_id(cfg.players, int(p['sysid']))

            if plr:
                await ms.edit(content=f"Сейчас говорит: {p['name']} - {cfg.roles[p['role']]}")
                player = inter.guild.get_member(plr)
                room = inter.guild.get_channel(cfg.room_channel)
                rec = inter.guild.get_channel(cfg.fasr_rec_channel)
                speaker_role = inter.guild.get_role(cfg.can_speak_role)
                await player.add_roles(speaker_role)
                await player.move_to(rec, reason="Join to mafia room")
                await player.move_to(room, reason="Join to mafia room")
                await asyncio.sleep(60)
                await player.remove_roles(speaker_role)
                await player.move_to(rec, reason="Join to mafia room")
                await player.move_to(room, reason="Join to mafia room")
                await asyncio.sleep(5)
        await ms.delete()

    @disnake.ui.button(label="Выгнать", style=disnake.ButtonStyle.blurple, row=2)
    async def kick(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        view = PlayerSelectView(cfg.players, "kick", 1)

        await inter.response.send_message("Выберите игрока", view=view, ephemeral=True)

    @disnake.ui.button(label="Последнее слово", style=disnake.ButtonStyle.blurple, row=3)
    async def last_word(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        view = PlayerSelectView(cfg.players, "last_word", 1)

        await inter.response.send_message("Выберите игрока", view=view, ephemeral=True)


class Mafia(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def update_players_msg(self, member):
        players_message: disnake.Message = await member.guild.get_channel(cfg.control_channel).fetch_message(
            cfg.players_message)
        view = ContolPanel()
        await players_message.edit(embed=generate_players_message(cfg.players, cfg), view=view)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.channel.id == cfg.killer_channel:
            if message.author.id == self.bot.user.id:
                return
            if cfg.is_night and cfg.start:
                if message.content.isdigit() and message.author.id not in cfg.mafia_killed_in_night:
                    if 1 <= int(message.content) <= 10:
                        cfg.mafia_killed_in_night.append(message.author.id)
                        await message.add_reaction("✅")
                        await message.delete(delay=2.0)
                        plr = get_player_by_system_id(cfg.players, int(message.content))
                        player = message.guild.get_member(plr)
                        await player.move_to(message.guild.get_channel(1168179736762134588), reason="Kill")
                        cfg.players = remove_player(cfg.players, player.id)

                        await self.update_players_msg(message.author)
                        return
            await message.delete()

    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def mafia_rules(self, inter: disnake.ApplicationCommandInteraction):
        rules = (
            "1. Цель мафиози: убить всех мирных жителей или нейтральных ролей, чтобы остаться в живых и "
            "контролировать город.\n"
            "2. Цель детектива: раскрыть личности мафиози и помочь мирным жителям выиграть игру.)\n"
            "3. Игра начинается с ночного раунда, где мафиози выбирают свою жертву для убийства, а детектив выбирает "
            "игрока, чью личность хочет проверить.\n"
            "4. На следующий день, игроки обсуждают произошедшее и пытаются вычислить мафиози на основе поведения и "
            "аргументов.\n"
            "5. После обсуждения, игроки голосуют за подозреваемых. Игрок с наибольшим количеством голосов выбывает "
            "из игры и его личность раскрывается.\n"
            "6. Если детектив правильно выявил мафиози, они выбывают из игры. Если детектив ошибся или был убит "
            "мафиози, игра продолжается.\n"
            "7. Цикл ночи и дня повторяется до тех пор, пока все мафиози не будут убиты или пока мафиози не останутся "
            "в большинстве и не смогут быть пойманы мирными жителями.\n"
            "8. Победа зависит от того, кто остается в живых в конце игры: мирные жители или мафиози.\n\n"
            "Помните, что эти правила могут быть изменены и адаптированы в зависимости от предпочтений игроков. Удачи "
            "в игре!"
        )
        embed = disnake.Embed(
            title="Правила игры",
            description=rules,
            color=disnake.Colour.magenta()
        )
        await inter.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState,
                                    after: disnake.VoiceState):
        # join to join channel
        if after.channel:
            if after.channel.id == cfg.join_channel:
                room = member.guild.get_channel(cfg.room_channel)
                if len(room.members) == 0:
                    vote_channel = member.guild.get_channel(cfg.vote_channel)
                    killer_channel = member.guild.get_channel(cfg.killer_channel)
                    await vote_channel.purge(limit=200)
                    await killer_channel.purge(limit=200)
                if len(room.members) <= 10:
                    # join channel logic here
                    await member.move_to(room, reason="Join to mafia room")
                    mem = len(room.members)
                    try:
                        await member.edit(nick=f"{mem} {member.name}")
                    except:
                        pass
                    m, d = player_role(cfg.players)
                    role = choose_role(m, d)
                    cfg.players.append({
                        "sysid": mem,
                        "id": member.id,
                        "role": role,
                        "name": member.name if member.nick is None else member.nick
                    })
                    if role == 1:
                        cfg.mafia.append(member.id)
                        mafia_channel = member.guild.get_channel(cfg.killer_channel)
                        overwrites = mafia_channel.overwrites
                        overwrites[member.guild.default_role] = disnake.PermissionOverwrite(view_channel=False)
                        overwrites[member] = disnake.PermissionOverwrite(view_channel=True)
                        await mafia_channel.edit(overwrites=overwrites)

                    if len(cfg.mafia) == 2:
                        maf = ""
                        for m in cfg.mafia:
                            maf += f"<@{m}> "
                        embed = disnake.Embed(
                            title="Вы мафия",
                            description=f"Для убийства напишите номер игрока \n\nМафия в этой игре: {maf}\n\nВаша "
                                        f"цель: убить мирных",
                        )
                        await member.guild.get_channel(cfg.killer_channel).send(embed=embed)
                    mpr = member.guild.get_role(cfg.mafia_player_role)
                    await member.add_roles(mpr)
                    await member.send(f"Вы {cfg.roles[role]}")

                    await self.update_players_msg(member)

                if len(room.members) == 11:
                    j = member.guild.get_channel(cfg.join_channel)
                    await j.edit(overwrites={
                        member.guild.default_role: disnake.PermissionOverwrite(connect=False),
                    })

        # on leave
        if before.channel:
            if before.channel.id == cfg.room_channel:
                killer_channel = member.guild.get_channel(cfg.killer_channel)
                sp = False
                if after.channel:
                    if after.channel.id == cfg.fasr_rec_channel:
                        sp = True
                if not sp:
                    cfg.players = remove_player(cfg.players, member.id)
                    await self.update_players_msg(member)

                    csr = member.guild.get_role(cfg.can_speak_role)
                    mprr = member.guild.get_role(cfg.mafia_player_role)

                    try:
                        if csr in member.roles:
                            await member.remove_roles(csr)
                        if mprr in member.roles:
                            await member.remove_roles(mprr)
                        if member.id in cfg.mafia:
                            await killer_channel.set_permissions(member,
                                                                 overwrite=disnake.PermissionOverwrite(
                                                                     view_channel=False))
                            cfg.mafia.remove(member.id)

                        await member.edit(nick=None)
                    except:
                        pass

                    if len(member.guild.get_channel(cfg.room_channel).members) == 0:
                        j = member.guild.get_channel(cfg.join_channel)
                        await j.edit(overwrites={
                            member.guild.default_role: disnake.PermissionOverwrite(connect=True),
                        })
                        cfg.players = []


def setup(bot):
    bot.add_cog(Mafia(bot))
