import asyncio
import math
import os
import validators

import disnake
from disnake.ext import commands
import yt_dlp as youtube_dl
from disnake.utils import get

from utils import *


def time_format(t):
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    return '%02d:%02d:%02d' % (h, m, s)


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.vc = None
        self.is_playing = False
        self.is_paused = False
        self.name = "Музыка"
        self.bot = bot

        self.ydl_options = {
            'quiet': True,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}
        self.queue = []

    # searching the item on youtube
    def search_yt(self, item):
        with youtube_dl.YoutubeDL(self.ydl_options) as ydl:
            try:
                video = ydl.extract_info(f"ytsearch:{item}", download=False)['entries'][0]
            except:
                video = ydl.extract_info(item, download=False)

        return {"url": video['webpage_url'], "title": video['title'], 'duration': video['duration'],
                'channel': video['uploader'], 'channel_url': video['uploader_url']}

    def download(self, url):
        song = os.path.isfile("song.mp3")
        try:
            if song:
                os.remove("song.mp3")
        except PermissionError:
            print("Error")

        with youtube_dl.YoutubeDL(self.ydl_options) as ydl:
            ydl.download([url])

        for file in os.listdir():
            if file.endswith(".mp3"):
                os.rename(file, "song.mp3")

    def play_next(self, ctx):
        self.queue.pop(0)
        if len(self.queue) > 0:
            print("Playing", self.queue[0][0]['url'])
            self.is_playing = True
            self.download(self.queue[0][0]['url'])
            # get the first url
            self.vc.play(disnake.FFmpegPCMAudio('song.mp3'), after=lambda e: self.play_next(ctx))

        else:
            self.is_playing = False

    async def play_music(self, ctx):
        if len(self.queue) > 0:
            self.is_playing = True

            m_url = self.queue[0][0]['url']
            # try to connect to voice channel if you are not already connected
            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.queue[0][1].connect()
                print("Connected to", self.queue[0][1])

                # in case we fail to connect
                if self.vc is None:
                    emb = EmbedManager(EmbedType.ERROR, "Произошла ошибка!").generate()
                    await ctx.send(embed=emb)
                    return
            else:
                await self.vc.move_to(self.queue[0][1])
            self.download(m_url)

            self.vc.play(disnake.FFmpegPCMAudio('song.mp3'), after=lambda e: self.play_next(ctx))
            self.vc.source = disnake.PCMVolumeTransformer(self.vc.source)
            self.vc.source.volume = 0.09
        else:
            self.is_playing = False
            print("Queue is empty")

    # searching the item on youtube
    @commands.slash_command(description="Добавить песню в очередь")
    async def play(self, inter: disnake.ApplicationCommandInteraction, query: str):
        await inter.response.defer()
        voice = inter.author.voice
        if voice is None:
            # you need to be connected so that the bot knows where to go
            emb = EmbedManager(EmbedType.ERROR, "Вы не находитесь в голосовом канале!").generate()
            await inter.send(embed=emb)
            return
        voice_channel = voice.channel
        if self.is_paused:
            self.vc.resume()
        song = self.search_yt(query)
        print(song)
        if type(song) == type(True):
            emb = EmbedManager(EmbedType.ERROR, "Не удалось найти файл!").generate()
            await inter.send(embed=emb)
        else:
            if self.is_playing:
                emb = EmbedManager(EmbedType.INFO, "Добавлено в очередь!").generate()
                msg = await inter.send(embed=emb)
            else:
                emb = EmbedManager(EmbedType.INFO, "Пожалуйста, подождите!").generate()
                msg = await inter.send(embed=emb)
            self.queue.append([song, voice_channel])
            if not self.is_playing:
                await self.now_playing(inter)
                await self.play_music(inter)

    async def now_playing(self, ctx):
        one_ot_twenty = self.queue[0][0]['duration']
        print(one_ot_twenty)
        emb = EmbedManager(EmbedType.INFO, f"Сейчас играет - {self.queue[0][0]['title']}").generate()
        await ctx.channel.send(embed=emb)

    @commands.slash_command(description="Посмотреть очередь")
    async def queue(self, inter: disnake.ApplicationCommandInteraction):
        retval = ""
        for i in range(0, len(self.queue)):
            # display a max of 5 songs in the current queue
            if i > 4: break
            retval += self.queue[i][0]['title'] + "\n"

        if retval != "":
            emb = EmbedManager(EmbedType.INFO, "Очередь", retval).generate()
            await inter.send(retval)
        else:
            emb = EmbedManager(EmbedType.ERROR, "Очередь пуста!").generate()
            await inter.send(embed=emb)

    class SkipMusic(disnake.ui.View):

        def __init__(self, message: disnake.ApplicationCommandInteraction, need: int, cog, get: int = 0):
            super().__init__(timeout=None)
            self.message = message
            self.need = need
            self.get = get
            self.cog = cog

        @disnake.ui.button(label="Пропустить", custom_id="music:skip", style=disnake.ButtonStyle.blurple, emoji="❌")
        async def lock(self, button: disnake.Button, interaction: disnake.ApplicationCommandInteraction):
            await interaction.response.defer()
            guild = interaction.guild
            user = interaction.user
            self.get += 1

            if self.get == self.need:
                button.disabled = True
                self.cog.vc.stop()
                await self.cog.play_music(interaction)
                emb = EmbedManager(EmbedType.SUCCESS, "Песня пропущена").generate()
                await self.message.edit_original_message(
                    embed=emb, view=None)
            else:
                emb = EmbedManager(EmbedType.INFO,
                                   f"Нажмите на кнопку ниже для пропуска ({self.get}/{self.need})").generate()
                await self.message.edit_original_message(embed=emb, view=self)

    @commands.slash_command(description="Пропуск песни")
    async def skip(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        if self.vc is not None and self.vc:
            if inter.author in self.vc.channel.members:
                members = self.vc.channel.members
                need = math.ceil((len(members) - 1) / 0.50)
                if len(members) - 1 == need:
                    emb = EmbedManager(EmbedType.SUCCESS, "Песня пропущена").generate()
                    await inter.send(embed=emb)
                    self.vc.stop()
                    await self.play_music(inter)
                else:
                    emb = EmbedManager(EmbedType.INFO, f"Нажмите на кнопку ниже для пропуска (0/{need})").generate()
                    await inter.send(embed=emb, view=self.SkipMusic(message=inter, need=need, cog=self))
        else:
            await inter.send("No music in queue")

    @commands.slash_command(description="Принудительно пропуск песни")
    @commands.default_member_permissions(administrator=True)
    async def forceskip(self, inter: disnake.ApplicationCommandInteraction):
        self.vc.stop()
        self.play_next(inter)
        emb = EmbedManager(EmbedType.SUCCESS, "Песня принудительно была пропущена").generate()
        await inter.send(embed=emb)

    @commands.slash_command(description="Ставит песню на паузу")
    async def pause(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        if self.vc is not None and self.vc:
            self.vc.pause()
            self.is_paused = True
            emb = EmbedManager(EmbedType.INFO, "Песня поставлена на паузу").generate()
            await inter.send(embed=emb)

    @commands.slash_command(description="Воспроизведение песни при паузе")
    async def resume(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        if self.vc is not None and self.vc:
            self.vc.resume()
            self.is_paused = False
            emb = EmbedManager(EmbedType.INFO, "Песня воспроизведена").generate()
            await inter.send(embed=emb)

    @commands.slash_command(description="Очищает очередь")
    @commands.default_member_permissions(administrator=True)
    async def qclear(self, inter: disnake.ApplicationCommandInteraction):
        self.queue = []
        emb = EmbedManager(EmbedType.SUCCESS, "Очередь очищена").generate()
        await inter.send(embed=emb)

    @commands.slash_command(description="Отключает бота с канала")
    async def leave(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        self.vc.stop()
        await self.vc.disconnect()
        emb = EmbedManager(EmbedType.SUCCESS, "Бот вышел из канала").generate()
        await inter.send(embed=emb)


def setup(bot):
    bot.add_cog(music_cog(bot))
