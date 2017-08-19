import discord
import random
import asyncio
import requests
import sys, os
import config
import praw
from bs4 import BeautifulSoup
import youtube_dl

# setting media dir
script_dir = sys.path[0]
img_path = os.path.join(script_dir, 'media')

# suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, ytdl.extract_info, url)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await client.change_presence(game=discord.Game(name='Helping People'))
        channel = client.get_channel(config.voice_channel_id)
        global voice
        voice = await discord.VoiceChannel.connect(channel)

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        # panic attack command
        if message.content.startswith('!panic'):
            if message.channel.id == config.panic_channel_id:
                msg = 'Hello @here, is anyone available to assist {0.author.mention}.'.format(message)
                await message.channel.send(msg)
            else:
                msg1 = 'Hello {0.author.mention}, I see you\'re having a panic attack. Please move to our support channel ' \
                       'where we can better assist you.'.format(message)
                msg2 ='Hello @here, is anyone available to assist {0.author.mention}.'.format(message)
                await message.channel.send(msg1)
                await client.get_channel(config.panic_channel_id).send(msg2)

        elif message.content.startswith('!meme'):
            media_to_use = random.choice(config.memlist)
            await message.channel.send(file=discord.File(fp=img_path + media_to_use))

        elif message.content.startswith('!hug'):
            media_to_use = random.choice(config.huglist)
            await message.channel.send(file=discord.File(fp=img_path + media_to_use))

        elif message.content.startswith('!breathe'):
            await message.channel.send(file=discord.File(fp=img_path + "/breathing.gif"))

        elif message.content.startswith('!happybday'):
            media_to_use = random.choice(config.bdaylist)
            await message.channel.send(file=discord.File(fp=img_path + media_to_use))

        # music player for links with youtube
        elif message.content.startswith('!play '):
            global voice
            url = message.content.replace("!play ", "")
            player = await YTDLSource.from_url(url)
            if voice.is_playing():
                voice.stop()
            voice.play(player)

        # help command
        elif message.content.startswith('!help'):
            em = discord.Embed(title='*beep...* *boop...*Hello, you\'ve\' asked for help!',
                               description='Here are a list of some command you can do: ' \
                                           '\n''\n' '!meme - sends a random meme' \
                                           '\n''\n' '!hug - sends a random hug gif' \
                                           '\n''\n' '!breathe - sends a breathing exercise gif' \
                                           '\n''\n' '!panic - is for people who are having an anxiety attack' \
                                           '\n''\n' '!happybday - sends a random birthday gif' \
                                           '\n''\n' '!play - play any youtube link you would like. e.g.(!play {insert link here})' \
                                           '\n''\n' '!urbanD - e.i(!urbanD anxiety) will return the top definition for that word' \
                                           '\n''\n' '~This is a bot made by @Philzeey, feel free to send me any messages for complaints or suggestions.',
                               colour=0x00E707)
            em.set_author(name=message.author, icon_url=client.user.avatar_url)
            await message.channel.send(embed=em)

        # admin commands
        elif message.content.startswith('!purge'):
            amount = message.content.replace("!purge ", "")

            if (str(message.author.top_role) == "Admin" or str(message.author.top_role) == "Moderators") and int(amount) <= 100:
                await message.channel.purge(limit=int(amount))

            else:
                await message.channel.send("*beep... boop...*Sorry you don't contain the right privileges to execute that command, or wanted to delete to many. Please limit to <=100.")

        # urbanDictionary word finder
        elif message.content.startswith('!urbanD '):
            msg = message.content.replace('!urbanD ', '')
            r = requests.get("http://www.urbandictionary.com/define.php?term={}".format(msg))
            soup = BeautifulSoup(r.content, "html.parser")
            definition = soup.find("div", attrs={"class": "meaning"}).text
            await message.channel.send("From Urban Dictionary, " + "**" + msg + "**" + " is defined as:"'\n''\n' + "*" + definition + "*")

    # on member join message
    async def on_member_join(self, member):
        msg = 'Welcome {0.mention} to {1.name}! Don\'t hesitate to use any of the ' \
              '#support channels if you require immediate support or contact ' + config.staff_role_id + ' if you have any questions. Please read our ' + config.welcome_channel_id + \
              ' channel so you can be familiar with our server rules. Type !help for any bot commands.'
        guild = member.guild
        await guild.default_channel.send(msg.format(member, guild))

    # reddit bot feed task
    async def my_background_task(self):
        await self.wait_until_ready()
        reddit = praw.Reddit(client_id=config.client_id,
                             client_secret=config.client_secret,
                             user_agent=config.user_agent)

        id = ""
        while not self.is_closed():
            subreddit = reddit.subreddit("healthanxiety")
            submissions = subreddit.new(limit=1)
            for submission in submissions:
                if submission.id == id:
                    break
                else:
                    await client.get_channel(config.redditFeed_channel_id).send(submission.title +'\n'+submission.url)
                    id = submission.id
            await asyncio.sleep(60) #recheck every 60 seconds

client = MyClient()
client.run(config.token)