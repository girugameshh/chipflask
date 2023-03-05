import discord
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
import logging
import asyncio
from threading import Thread
import openai
import platform
import datetime
import time
import requests
import pyttsx3
from gtts import gTTS

load_dotenv()
app = Flask(__name__, static_url_path='/static')
TOKEN = os.getenv("DISCORD_TOKEN")
logging.basicConfig(filename='error.log', encoding='utf-8')
voice_client = None
openai.api_key = "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"


class LilChippy(discord.Client):
    bob = 163398788029874176
    bane = 351014464457539594
    nasra = 252227984717512704

    def __init__(self, *args, **kwargs):
        super(LilChippy, self).__init__(*args, **kwargs)
        self.client = None
        self.executable_path = "ffmpeg.exe" \
            if platform.system() == "Windows" \
            else "/usr/bin/ffmpeg"
        self.last_played = datetime.datetime.now()
        self.user_id_dict = {351014464457539594: "giru",
                             163398788029874176: "bob",
                             769993633641529344: "zaka",
                             307600011561009154: "zda",
                             252227984717512704: "nasra",
                             352518058377478148: "ukpa",
                             177883731598508032: "kejv",
                             219201628782329867: "gile"}

        self.info_msg = self.generate_default_info_msg()
        if os.path.exists("info_message.txt"):
            with open("info_message.txt", "r") as file:
                self.info_msg = file.read()

    #@client.event
    async def on_ready(self):
        global voice_client
        print(f'Logged on as {client.user}')
        channel = client.get_channel(472163974977159199)
        voice_client = await channel.connect()
        print(f'Joined {channel.name}')


    #@client.event
    async def on_voice_state_update(self, member, before, after):

        member_name = self.user_id_dict.get(member.id, None)

        if member_name is None:
            return

        global voice_client
        if voice_client is None:
            return

        if before.channel is None and after.channel is not None and after.channel.name == "cuck-gold":
            await asyncio.sleep(2)
            audio_source = discord.FFmpegPCMAudio(executable=self.executable_path,
                                                  source=f"users/{member_name}.mp3")
            voice_client.play(audio_source)

    def generate_default_info_msg(self):
        return "Go to lilchippy.vip"

    async def send_message(self, message, text):
        await message.channel.send(text)


    #@client.event
    async def on_message(self, message):
        if self.user.id == message.author.id:
            return
        global voice_client
        current_time = datetime.datetime.now()
        delta = current_time - self.last_played
        msg = message.content.lower()
        message_parts = msg.split(" ")
        guild_id = message.guild.id
        channel_id = message.channel.id

        if message.author.id in (self.bob, self.bane, self.nasra) and message.attachments:
            audio_only = True
            for attachment in message.attachments:
                if "audio/" not in attachment.content_type:
                    audio_only = False
                else:
                    await self.handle_upload(url=attachment.url)
            if audio_only:
                await message.channel.send("Audio files downloaded")

        if msg == "!info reset":
            if message.author.id in (self.bob, self.bane):
                self.info_msg = self.generate_default_info_msg()
                with open("info_message.txt", "w") as file:
                    file.write(self.info_msg)
                await self.send_message(message, "Info message set to default.")
            else:
                await message.channel.send("Admin command. No permission.")

        elif message_parts[0][0] == "!":
            handler_name = message_parts[0][1:]

            try:
                func = getattr(client, f"handle_{handler_name}")
                await func(message)

            except AttributeError as e:
                print(e)
                await message.channel.send("No such command. Try !info")

        elif voice_client is not None \
                and not voice_client.is_playing() and delta.seconds > 3:
            if msg not in self.generate_sound_list()[0]:
                return
            audio = discord.FFmpegPCMAudio(executable=self.executable_path, source=f"sounds/{msg}.mp3")
            try:
                voice_client.play(audio)

            except Exception as e:
                logging.error(e)
                self.on_ready()
                voice_client.play(audio)

        if message.content.startswith("!tts"):
            text = message.content.replace("!tts ", "")
            if message.guild is not None and message.channel is not None:
                await client.handle_tts(text, guild_id, channel_id)
            else:
                print("message.guild or message.channel is None")

    def generate_sound_list(self):
        my_list = []
        max_len = 0
        for root, subfolders, files in os.walk("sounds"):
            for file in files:
                file_split = os.path.splitext(file)
                if file_split[1] != ".mp3":
                    continue
                file = file_split[0]
                if file not in self.user_id_dict.values():
                    my_list.append(file)
                    max_len = max_len if max_len >= len(file) else len(file)
        my_list.sort()
        max_len += 3
        return my_list, max_len

    async def handle_tts(self, text, guild_id, channel_id):
        engine = pyttsx3.init()
        tts = gTTS(text)
        tts.save("tts.mp3")
        engine.runAndWait()

        guild = self.get_guild(guild_id)
        voice_client = guild.voice_client

        if voice_client is not None:
            audio = discord.FFmpegPCMAudio(executable=self.executable_path, source=f"tts.mp3",
                                           options='-filter:a "volume=0.4"')
            try:
                voice_client.play(audio)
            except Exception as e:
                logging.error(e)
                print("ERROR TTS WTH")

    async def handle_upload(self, message=None, url=None):
        if message:
            msg = message.content.lower()
            url = msg.replace('!upload ', '')
        response = requests.get(url)
        naziv = url.split("/")[-1]
        path = os.path.join("sounds", naziv)
        with open(path, "wb") as f:
            f.write(response.content)
        if message:
            await message.channel.send('Sound Saved!')

    async def handle_join(self, message):
        channel = self.get_channel(472163974977159199)
        if self.voice_clients:
            await message.channel.send("I am already in a voice channel.")
        else:
            await message.channel.send("Success!")
            self.client = await channel.connect()

    async def handle_kill(self, message):
        if message.author.id in (self.bob, self.bane):
            embed = discord.Embed(description=':warning: Killing Myself in 5 Seconds. :warning:')
            await message.channel.send(embed=embed)
            time.sleep(5)
            await self.close()
        else:
            embed = discord.Embed(description=":warning: Admin command. No permission. :warning:")
            await message.channel.send(embed=embed)

    async def handle_leave(self, message):
        if message.author.id in (self.bob, self.bane):
            if message.guild.voice_client:
                await message.channel.send("Leaving...")
                await message.guild.voice_client.disconnect()
            else:
                await message.channel.send("I am not connected to a voice channel.")

    async def handle_clear(self, message):
        msg = message.content.lower()
        msg_parts = msg.split(" ")
        if message.author.id in (self.bob, self.bane):
            limit = 20
            if len(msg_parts) == 2 and msg_parts[1].isnumeric():
                limit = int(msg_parts[1])
            await self.send_message(message, f"Deleting {limit} messages in 3 seconds...")
            time.sleep(3)
            await message.channel.purge(limit=limit)
        else:
            await self.send_message(message, "No permission ese")

    async def handle_delete(self, message):
        msg = message.content.lower()
        filename = msg.replace("!delete ", "")
        path = os.path.join("sounds", f"{filename}.mp3")
        if message.author.id in (self.bob, self.bane):
            if os.path.exists(path):
                os.remove(path)
                await message.channel.send(f"{filename} deleted.")
                return
        else:
            await self.send_message(message, "No permission ese")

    async def handle_price(self, message):
        msg = message.content.lower()
        key = '5c89316d-8692-4b42-803f-ebf154e06711'
        symbol = msg.replace('!price ', '')
        base_url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY={key}'
        url_info = f'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info?CMC_PRO_API_KEY={key}'
        url = f'{base_url}&slug={symbol}'
        try:
            data = requests.get(url).json()
            if data["status"]["error_message"] is not None:
                url = f'{base_url}&symbol={symbol}'
                data = requests.get(url).json()

            for coin in data["data"].values():
                url = f'{url_info}&id={coin["id"]}'
                metadata = requests.get(url).json()
                coin_data = coin['quote']['USD']
                coin_id = coin['id']
                metadata = metadata['data'][str(coin_id)]
                metadata_desc = metadata.get('description', None)
                metadata_explorer = metadata['urls'].get('explorer', [])[:1]
                metadata_website = metadata['urls'].get('website', [])[:1]
                rank = coin['cmc_rank']
                metadata_explorer = metadata_explorer[0] if metadata_explorer else "None"
                metadata_website = metadata_website[0] if metadata_website else "None"
                percentage_change24 = coin_data['percent_change_24h']
                weekly_percentage = coin_data['percent_change_7d']
                monthly_percentage = coin_data['percent_change_30d']
                market_cap = "{:,.0f}".format(coin_data['market_cap'])
                volume = "{:,.0f}".format(coin_data['volume_24h'])
                price = coin_data['price']
                decimals = 2 if int(price) > 0 else 6
                price = round(price, decimals)
                decimale = 2
                percentage_change24 = round(percentage_change24, decimale)
                weekly_percentage = round(weekly_percentage, decimale)
                monthly_percentage = round(monthly_percentage, decimale)
                embed = discord.Embed(description=f' :dollar: {coin["name"]} is **${price}** \n \n'
                                                  f' :medal: Current rank : **{rank}** \n \n'
                                                  f' :date: 24h Volume : **${volume}** \n \n'
                                                  f' :chart_with_upwards_trend: 24h percentage change : **{percentage_change24}** % \n \n'
                                                  f' :chart_with_upwards_trend: 7d percentage change : **{weekly_percentage}** % \n \n'
                                                  f' :chart_with_upwards_trend: 30d percentage change : **{monthly_percentage}** % \n \n'
                                                  f' :moneybag: Current Market Cap : **${market_cap}** \n \n'
                                                  f'_ _ \n \n'
                                      , title="Price Info", colour=0xffd700)
                embed.add_field(name=':earth_africa: Website', value=f'{metadata_website}')
                embed.add_field(name=':mag_right: Explorer', value=f'{metadata_explorer}')

                embed.set_thumbnail(url=f'https://s2.coinmarketcap.com/static/img/coins/64x64/{coin_id}.png')

                await message.channel.send(embed=embed)

        except Exception as e:
            await self.send_message(message, 'Bad Request')
            print(e)

    async def handle_info(self, message):
        msg = message.content.lower()
        msg_parts = msg.split(" ")

        if msg_parts[0] == "!info":
            if len(msg_parts) >= 2 and msg_parts[1] != "":
                if message.author.id in (self.bob, self.bane):
                    msg_parts = msg_parts[1:]
                    msg = " ".join(msg_parts)
                    with open("info_message.txt", "w") as file:
                        file.write(msg)
                    self.info_msg = msg
                    await self.send_message(message, "Info message updated.")
            elif len(msg_parts) <= 2:
                embed = discord.Embed(description=self.info_msg,
                                      title=":large_blue_diamond: Info Panel :large_blue_diamond:",
                                      color=0xFF5733)
                embed.set_thumbnail(url="https://i.ibb.co/NjrfNmN/info.jpg")
                await message.channel.send(embed=embed)

    async def handle_sounds(self, message):
        sounds_lista, max_len = self.generate_sound_list()
        sounds_per_line = 5
        line = "=".join(['=' * max_len] * sounds_per_line) + "=="
        max_msg_len = 2000
        table = ""
        tables = []
        for i, sound in enumerate(sounds_lista):
            if i % sounds_per_line == 0:
                if len(table) != 0:
                    table += "=\n"
                table += f"{line}\n"
                max_msg_len -= len(line) * 3
            if max_msg_len <= 0:
                tables.append(table)
                table = f"{line}\n"
                max_msg_len = 2000
            table += f"={sound.center(max_len)}"

        if len(table) + len(f"=\n{line}") < 2000:
            table += f"=\n{line}"
        tables.append(table)

        for table in tables:
            await message.channel.send(f"```{table}```")

    async def handle_gpt(self, message):
        msg = message.content.replace("!gpt ", "")
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=msg,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        response_message = response.choices[0].text if response.choices else "Chat GPT Error"
        await message.channel.send(response_message)

    async def handle_dalle(self, message):
        msg = message.content.replace("!dalle ", "")
        response = openai.Image.create(
            prompt=msg,
            n=1,
            size="1024x1024"
        )
        image_url = response["data"][0]["url"]
        await message.channel.send(image_url)


    async def handle_epic(self, message):
        url = "https://free-epic-games.p.rapidapi.com/free"
        headers = {
            "X-RapidAPI-Key": "30e46b4729msh62195aa9730c7e6p114471jsn245b10abb966",
            "X-RapidAPI-Host": "free-epic-games.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers).json()

        current_free_games = []
        for game in response['freeGames']['current']:
            game_description = game['description']
            free_game_title = game['title']
            image_url = None
            for image in game['keyImages']:
                if image["type"] == "OfferImageWide":
                    image_url = image["url"]
                    break
            current_free_games.append((free_game_title, game_description, image_url))
        free_games_str = "\n".join([game[0] for game in current_free_games])

        upcoming_free_games = []
        for game in response['freeGames']['upcoming']:
            free_upcoming_game = game['title']
            upcoming_game_description = game['description']
            image_url = None
            for image in game['keyImages']:
                if image["type"] == "OfferImageWide":
                    image_url = image["url"]
                    break
            upcoming_free_games.append((free_upcoming_game, upcoming_game_description, image_url))

        free_current_game_str = ':red_circle: **Free Games This Week on Epic Games :red_circle:** \n \n'
        for name, desc, url in current_free_games:
            free_current_game_str += f':white_check_mark: **{name}** \n \n' \
                                     f' **Description:** \n \n' \
                                     f'*{desc}* \n \n' \

        free_upcoming_game_str = ':red_circle: **Free Games Next Week on Epic Games :red_circle:** \n \n'
        for name, desc, url in upcoming_free_games:
            free_upcoming_game_str += f':white_check_mark: **{name}** \n \n' \
                                      f' **Description:** \n \n' \
                                      f'*{desc}* \n \n' \

        embed = discord.Embed(description=f'{free_current_game_str}{free_upcoming_game_str} \n'
                                                      f'https://store.epicgames.com/en-US/free-games', colour=0xF200FD)
        embed.set_thumbnail(url='https://i.ibb.co/TrT5p9J/epik.jpg')

        await message.channel.send(embed=embed)

    async def handle_biza(self, message):
        await message.channel.send('https://i.ibb.co/Nsh3rFV/biza-mafija-pesak-nemoj-da-mi-glumis-mafiju.gif')

    async def handle_rust(self, message):
        msg = message.content.replace("!rust ", "")
        response = requests.get(f'https://scmm.app/api/profile/{msg}/inventory/value')

        if response.status_code == 200:
            data = response.json()
            value = int(data['marketValue'])
            final = value / 100
            name = data['name']
            avatar = data['avatarUrl']
            items = data['items']
            market_change = data['marketMovementValue']
            final_movement = market_change / 100

            embed = discord.Embed(description=f':man_pouting: User - {name} \n \n'
                                              f':arrow_forward: Number of skins - {items} \n \n'
                                              f':moneybag: Inventory value - ${final} \n \n'
                                              f':bar_chart: Inventory Price Movement - $ {final_movement}',

                                  title=':large_blue_diamond: Rust Skins Inventory Value',
                                  color=0xFF5733)
            embed.set_thumbnail(url=f"{avatar}")

            await message.channel.send(embed=embed)

        elif response.status_code == 401:
            await message.channel.send('Error - Inventory is Empty / Set to Private')

        elif response.status_code == 404:
            await message.channel.send('Error - Profile Cannot be Found')

        elif response.status_code == 500:
            await message.channel.send('Error - The server encountered a technical issue completing the request.')

    async def handle_steam(self, message):
        url = "https://www.cheapshark.com/api/1.0/deals?storeID=1&upperPrice=15"
        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload).json()
        games = ""
        for deal in response:
            game_name = deal['title']
            normal_price = deal['normalPrice']
            current_price = deal['salePrice']
            score = float(deal['metacriticScore'])
            if score <= 85:
                continue
            savings = round(float(deal['savings']), 2)
            games += f":money_with_wings: {game_name} - **${current_price}**/${normal_price} **({savings}%)**\n"

        embed = discord.Embed(description=f'**Steam Deals (New price/Old price/Savings)** \n \n'
                                          f'**Metacritics Score Over -> 85** \n \n'
                                          f'{games} \n \n'
                              , colour=0xF200FD)
        embed.set_thumbnail(url='https://i.ibb.co/XLYZF2H/steam.jpg')
        await message.channel.send(embed=embed)

@app.route('/')
def index():
    sound_files = os.listdir("sounds")
    sound_names = [os.path.splitext(file)[0] for file in sound_files]
    return render_template("index.html", sound_files=sound_names, client=client)



async def play_sound(sound_file):
    if voice_client is None:
        return
    sound_path = os.path.join("sounds", f"{sound_file}.mp3")
    if not os.path.exists(sound_path):
        return
    source = discord.FFmpegPCMAudio(sound_path)
    voice_client.play(source)


@app.route('/button-clicked', methods=['POST'])
def button_clicked():
    button_name = request.form['button_name']
    asyncio.run(play_sound(button_name))
    return 'OK'

@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    message = data['message']
    guild_id = data['guild_id']
    channel_id = data['channel_id']
    asyncio.run(client.handle_tts(guild_id, channel_id, message))
    return '', 204




intents = discord.Intents.default()
intents.voice_states = True
intents.messages = True
intents.message_content = True
client = LilChippy(intents=intents)


def run():
    return asyncio.run(client.start(TOKEN))



control_thread = Thread(target=run, daemon=True)
control_thread.start()
app.run(debug=False)
