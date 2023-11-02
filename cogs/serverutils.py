import disnake
from disnake.ext import commands


class ServerUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.channel.id == 1168892448622248026 and message.author != self.bot.user:
            await message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(1168892448622248026)
        await channel.purge(limit=1000)
        embed = disnake.Embed(
            title="Почему нет сообщений?",
            description="Наш бот удаляет их автоматически",
            color=disnake.Colour.magenta()
        )
        await channel.send(embed=embed)


    @commands.slash_command()
    @commands.has_permissions(administrator=True)
    async def rules(self, interaction: disnake.CommandInteraction):
        r = {
            "1. Oбщение": "1.1. Уважительное общение на сервере приветствуется, но не является обязательным. На \"ты\" можно общаться свободно с любым участником сервера НЕ зависимо от роли.\n"
                       "1.2. Нецензурная лексика не запрещена, если применяется в умеренном количестве. (в остальном на усмотрение модерации)\n"
                       "1.3. Оскорбления запрещены в любой форме, кроме высказываний не предполагающих оскорбление личности человека. (Примеры: пошел н###й, отъ##ись). Однако человек в сторону которого было это сказано имеет правило пожаловаться на оскорбление, поэтому не рекомендуется использовать подобную лексику.\n"
                       "1.4. Спам и флуд запрещены! Чаты по типу \"флудилка\" предназначены НЕ для спама и флуда, а для общения без какой-либо темы без ограничений по частоте отправки сообщений.\n"
                       "1.5. Любые разговоры про политику или религию, а также разговоры имеющие политический или религиозный подтекст запрещены без исключений.\n"
                       "1.6. Учтите, что сообщение должно соответствовать тематике канала в котором вы пишите. (для команд используйте чаты \"команды\" или \"флудильня\")\n",
            "2. Контент": "2.1. Торговля и реклама запрещены, за исключением если таковые есть в вашем описании профиля. Обучающие или развлекательные ролики из ютуба и/или другой платформы НЕ будут считаться рекламой, если они явно не представляют её или представлены как шутка. (ссылка на дискорд сервер или телеграм канал и т.п. БУДУТ считаться рекламой)\n"
                       "2.2. NSFW контент (18+ контент) запрещен в любой форме без исключений.\n",
            "3. Взаимодействие с персоналом": "3.1. Пинг администрации или модерации сервера сервера без причины запрещен. ( <@&1162708530797756466>  также относятся к персоналу). Наказание за пинг без уважительной причины будет решать лично человек которого пинганули, за исключением владельца сервера. Уважительной причиной для пинга может быть ответ на личное сообщение, личная просьба, указание на нарушение правил или спорную ситуацию.\n"
                                           "3.2. Если человек сообщивший о нарушении причастен к его совершению (подталкивание, введение в заблуждение, разжигание или поддержка спора или конфликта), то к нему также могут быть применены наказания\n",
            "4. Остальное": " 4.1. Запрещается разглашение любой личной информации о человеке, если таковая не была распространена им самим. (например: адрес электронной почты, телефонные номера, адреса проживания). Модераторы сервера могут удалить подобное сообщение БЕЗ выяснения причин его отправки.\n"
                         "4.2. По поводу вопросов по серверу вы можете писать в \"служба-поддержки\"\n",
            "5. Преступление и наказание": "5.1. Во всех случаях наказание в первую очередь определяют <@&1162708527870115840>, <@&1162708509985603594>,  <@&1167925333111091252>, <@&1162708529669492776>, <@&1162708530797756466> . Если вы считаете, что наказание было несправедливым, вы можете указать на это другому модератору или администратору. В таком случае ваше наказание может быть пересмотрено.\n"
                                        "5.2. Обход блокировок с помощью любых способов (в том числе других аккаунтов, если есть весомые доказательства для администрации, что это другой аккаунт наказанного человека) будет наказываться блокировкой.\n",
            "6. Типы наказаний": "mute (мьют/мут) - человек лишается доступа общения в даннам чате или на всём сервере. Даётся за не особо крупные нарушения.\n"
                               "warn (варн/предупреждение) - человек лишается возможности общения на сервере на при первом нарушение на 30 минут(дальше больше), после получения 5 предупреждений человек исключается с сервера! Снимаются спустя месяц. Даётся за более серьёзные нарушения\n"
                               "ban (бан) - исключение с сервера на определённое время/навсегда. Высшая степень наказания, даётся за особо крупные нарушения или массовые нарушерия.\n"
                              "\n"
                              "В голосовых чатах действуют все вышеописанные правила!\n"
                              "Администрация сервера оставляет за собой право в любое время дополнять/изменять правила сервера.\n"
                              "\n"
                              "ПОМНИТЕ! Если вы заметили нарушение, можете обратить на это внимание <@&1162708529669492776> при помощи команды !репорт [причина] (должно быть ответом на сообщение!)"
        }
        embeds = []
        for k,v in r.items():
            embed = disnake.Embed(
                title=k,
                description=v,
                colour=disnake.Colour.magenta()
            )
            embeds.append(embed)
        await interaction.channel.send(embeds=embeds)

    @commands.Cog.listener()
    async def on_message(self, message):
        print(message.content)

def setup(bot):
    bot.add_cog(ServerUtils(bot))
# 1. Общение:
#
# 1.1. Уважительное общение на сервере приветствуется, но не является обязательным. На "ты" можно общаться свободно с любым участником сервера НЕ зависимо от роли.
#  1.2. Нецензурная лексика не запрещена, если применяется в умеренном количестве. (в остальном на усмотрение модерации)
#  1.3. Оскорбления запрещены в любой форме, кроме высказываний не предполагающих оскорбление личности человека. (Примеры: пошел н###й, отъ##ись). Однако человек в сторону которого было это сказано имеет правило пожаловаться на оскорбление, поэтому не рекомендуется использовать подобную лексику.
#  1.4. Спам и флуд запрещены! Чаты по типу "флудильня" и "оффтоп" предназначены НЕ для спама и флуда, а для общения без какой-либо темы без ограничений по частоте отправки сообщений.
#  1.5. Любые разговоры про политику или религию, а также разговоры имеющие политический или религиозный подтекст запрещены без исключений.
#  1.6. Учтите, что сообщение должно соответствовать тематике канала в котором вы пишите. (для команд используйте чаты "для-команд" или "флудильня")
#
#  2. Контент:
#
#  2.1. Торговля и реклама запрещены, за исключением если таковые есть в вашем описании профиля. Обучающие или развлекательные ролики из ютуба и/или другой платформы НЕ будут считаться рекламой, если они явно не представляют её или представлены как шутка. (ссылка на дискорд сервер или телеграм канал и т.п. БУДУТ считаться рекламой)
#  2.2. NSFW контент (18+ контент) запрещен в любой форме без исключений.
#
#  3. Взаимодействие с персоналом:
#
#  3.1. Пинг администрации или модерации сервера сервера без причины запрещен. ( @・Assistent  также относятся к персоналу). Наказание за пинг без уважительной причины будет решать лично человек которого пинганули, за исключением владельца сервера. Уважительной причиной для пинга может быть ответ на личное сообщение, личная просьба, указание на нарушение правил или спорную ситуацию.
#  3.2. Если человек сообщивший о нарушении причастен к его совершению (подталкивание, введение в заблуждение, разжигание или поддержка спора или конфликта), то к нему также могут быть применены наказания
#  4. Остальное:
#
#  4.1. Запрещается разглашение любой личной информации о человеке, если таковая не была распространена им самим. (например: адрес электронной почты, телефонные номера, адреса проживания). Модераторы сервера могут удалить подобное сообщение БЕЗ выяснения причин его отправки.
#  4.2. По поводу вопросов по серверу вы можете писать в "служба-поддержки"
#
#  5. Преступление и наказание:
#
#  5.1. Во всех случаях наказание в первую очередь определяют   @・Administrator,  @・Main Moderator, @・Moderator, @・Assistent . Если вы считаете, что наказание было несправедливым, вы можете указать на это другому модератору или администратору. В таком случае ваше наказание может быть пересмотрено.
#  5.2. Обход блокировок с помощью любых способов (в том числе других аккаунтов, если есть весомые доказательства для администрации, что это другой аккаунт наказанного человека) будет наказываться блокировкой.
#
#  Типы наказаний:
#  mute (мьют/мут) - человек лишается доступа общения в даннам чате или на всём сервере. Даётся за не особо крупные нарушения.
#  warn (варн/предупреждение) - человек лишается возможности общения на сервере на при первом нарушение на 30 минут(дальше больше), после получения 5 предупреждений человек исключается с сервера! Снимаются спустя месяц. Даётся за более серьёзные нарушения
#  ban (бан) - исключение с сервера на определённое время/навсегда. Высшая степень наказания, даётся за особо крупные нарушения или массовые нарушерия.
#
#  В голосовых чатах действуют все вышеописанные правила!
#
# Администрация сервера оставляет за собой право в любое время дополнять/изменять правила сервера.
#
#  ПОМНИТЕ! Если вы заметили нарушение, можете обратить на это внимание  @・Moderator  при помощи команды !репорт [причина] (должно быть ответом на сообщение!)