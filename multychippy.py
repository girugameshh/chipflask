import discord
import platform
import os
from dotenv import load_dotenv
import time
from datetime import datetime
from flask import Flask, render_template
import logging
import requests
import asyncio
from threading import Thread

load_dotenv()
app: Flask = Flask(__name__, static_url_path='/static')
TOKEN = os.getenv("TOKEN")
logging.basicConfig(filename='error.log', encoding='utf-8')

class LilChippy(discord.Client):
    bob = 163398788029874176
    bane = 351014464457539594
    nasra = 252227984717512704

    def __init__(self, *args, **kwargs):
        self.images = {}
        super(LilChippy, self).__init__(*args, **kwargs)
        self.client = None
        self.executable_path = "ffmpeg.exe" \
            if platform.system() == "Windows" \
            else "/usr/bin/ffmpeg"
        self.last_played = datetime.now()
        self.user_id_dict = {351014464457539594: "giru",
                             163398788029874176: "bob",
                             769993633641529344: "zaka",
                             307600011561009154: "zda",
                             252227984717512704: "nasra",
                             352518058377478148: "ukpa",
                             177883731598508032: "kejv",
                             219201628782329867: "gile"}

        self.trigger_words = []
        self.info_msg = self.generate_default_info_msg()
        if os.path.exists("info_message.txt"):
            with open("info_message.txt", "r") as file:
                self.info_msg = file.read()

    async def on_ready(self):
        print('Logged on as', self.user)
        channel = self.get_channel(445253726165270543)
        self.client = await channel.connect()
        print('Joined #General')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='!info'))

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

    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None and after.channel.name == "General":
            current_time = datetime.now()
            delta = current_time - self.last_played

            if self.client is not None \
                    and not self.client.is_playing() and delta.seconds > 2:

                member_name = self.user_id_dict.get(member.id, None)
                if member_name is None:
                    return
                time.sleep(1)
                audio = discord.FFmpegPCMAudio(executable=self.executable_path, source=f"users/{member_name}.mp3",
                                               options='-filter:a "volume=0.4"')
                try:
                    self.client.play(audio)
                except Exception as e:
                    logging.error(e)
                    self.on_ready()
                    self.client.play(audio)

                self.last_played = current_time

    async def on_message(self, message):
        if self.user.id == message.author.id:
            return
        current_time = datetime.now()
        delta = current_time - self.last_played
        msg = message.content.lower()
        message_parts = msg.split(" ")
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
                func = getattr(self, f"handle_{handler_name}")
                await func(message)

            except AttributeError as e:
                print(e)
                await message.channel.send("No such command. Try !info")

        elif self.client is not None \
                and not self.client.is_playing() and delta.seconds > 3:
            if msg not in self.generate_sound_list()[0]:
                return
            volume = f"volume = {0.07 if msg != 'rdm' else 0.5}"
            audio = discord.FFmpegPCMAudio(executable=self.executable_path, source=f"sounds/{msg}.mp3",
                                           options=f'-filter:a "{volume}"')
            try:
                self.client.play(audio)

            except Exception as e:
                logging.error(e)
                self.on_ready()
                self.client.play(audio)

            self.last_played = current_time

    async def handle_upload(self, message = None, url = None):
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

    def generate_default_info_msg(self):
        return f':bangbang: `!join`, `!leave` \n \n '


@app.route('/')
def index():
    sound_files = os.listdir("sounds")
    sound_names = [os.path.splitext(file)[0] for file in sound_files]
    return render_template("index.html", sound_files=sound_names)


intents = discord.Intents.default()
intents.voice_states = True
intents.messages = True
intents.message_content = True
client = LilChippy(intents=intents)

def run():
    asyncio.run(client.run(TOKEN))


control_thread = Thread(target=run, daemon=True)
control_thread.start()
app.run()
