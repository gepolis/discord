import math
import random
import string
from datetime import datetime

import disnake
from database import mafia


class CreateGameModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Игроков(6-20)",
                custom_id="players",
            ),
        ]

        super().__init__(title="Создать игру", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer()
        players = inter.text_values["players"]
        if players.isdigit():
            players = int(players)
            if 6 <= players <= 20:
                if inter.user.voice:
                    mafia_count = math.floor(players / 3)
                    if 6 <= players <= 8:
                        mafia_count = 2
                    elif 9 <= players <= 10:
                        mafia_count = 3
                    elif 11 <= players <= 14:
                        mafia_count = 4

                    players = int(players)
                    inv_code = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
                    overwrites = {
                        inter.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                        inter.user: disnake.PermissionOverwrite(view_channel=True),
                    }
                    overwrites_staff = {
                        inter.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                        inter.user: disnake.PermissionOverwrite(view_channel=False),
                    }
                    category = await inter.guild.create_category(f"Mafia {inv_code}", overwrites=overwrites)
                    control = await category.create_text_channel('💻│управление', overwrites=overwrites_staff)
                    vote = await category.create_text_channel('📋│голосование')
                    room = await category.create_voice_channel('🎮│комната', user_limit=players)
                    owner_channel = await category.create_text_channel('👤│управление', overwrites=overwrites)

                    mafia.MafiaRooms.create(
                        owner_id=inter.user.id,
                        max_players=players,
                        mafia_count=mafia_count,
                        invite=inv_code,
                        category_id=category.id,
                        control_channel=control.id,
                        vote_channel=vote.id,
                        room_channel=room.id,
                        owner_channel=owner_channel.id
                    )
                    embed = disnake.Embed(
                        title="Информация о комнате",
                        colour=disnake.Colour.blue()
                    )
                    embed.add_field(name="Игроков", value=f"```{players}```")
                    embed.add_field(name="Мафия", value=f"```{mafia_count}```")
                    embed.add_field(name="Код игры", value=f"```{inv_code}```")
                    embed.set_footer(text=f"Создана: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
                    await owner_channel.send(embed=embed)
                    await inter.user.move_to(room)
