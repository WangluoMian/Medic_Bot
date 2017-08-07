import discord
import logging
import random
import asyncio

################################################################################
logging.basicConfig(level=logging.INFO)
client = discord.Client()
################################################################################

songTime = 0
songDonePlaying = True

async def my_background_task():
    await client.wait_until_ready()
    while not client.is_closed:
        global songTime
        songTime -= 1
        await asyncio.sleep(1) # task runs every 60 seconds
        if songTime == 0:
            return

def convert_seconds_to_minutes(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


@client.event
async def on_message(message):
    #list of media
    memlist = ["mem1.jpg","mem2.jpg","mem3.jpg","mem4.jpg","mem5.jpg","mem6.jpg","mem7.jpg","mem8.jpg","mem9.jpg","mem10.jpg"]
    huglist = ["hug1.gif","hug2.gif","hug3.gif","hug4.gif"]
    bdaylist = ["bday1.gif","bday2.gif","bday3.gif"]

    #We do not want the bot to reply to itself
    if message.author == client.user:
        return

	#A list of commands for people to use
    if message.content.startswith('!meme'):
        media_to_use = random.choice(memlist)
        await client.send_file(message.channel, media_to_use)

    elif message.content.startswith('!hug'):
        media_to_use = random.choice(huglist)
        await client.send_file(message.channel, media_to_use)

    elif message.content.startswith('!breathe'):
        await client.send_file(message.channel, "breathing.gif")

    elif message.content.startswith('!happybday'):
        media_to_use = random.choice(bdaylist)
        await client.send_file(message.channel, media_to_use)

	#Music player for links with youtube
    elif message.content.startswith('!play '):
        global songTime
        global songDonePlaying
        if songTime == 0:
            msg = message.content.replace("!play ", "")
            voice = client.voice_client_in(discord.Server(id='344147579593949194'))
            player = await voice.create_ytdl_player(msg)
            player.start()
            client.loop.create_task(my_background_task())
            songTime = player.duration
            songDonePlaying = False
        else:
            timeLeft = str(convert_seconds_to_minutes(songTime))
            await client.send_message(message.channel, "Sorry the song currently playing has " + timeLeft +" minutes left, please try again when it's ended. Thank you.")

	#Panic mode
    elif message.content.startswith('!panic'):
        msg1 = 'Hello {0.author.mention}, I see you\'re\' having a panic attack. Please move to our support channel ' \
                                   'where we can better assist you.'.format(message)
        msg2= 'Hello @everyone, is anyone available to assist {0.author.mention}. Here is a gif to help you breath in the ' \
                                                                           'mean time.'.format(message)
        await client.send_message(message.channel, msg1)
        await client.send_message(discord.Object(id='272465465702350848'), msg2)
        await client.send_file(discord.Object(id='272465465702350848'), "breathing.gif")

	#Help section explaining how to use the commands
    elif message.content.startswith('!help'):
        em = discord.Embed(title='*beep...* *boop...*Hello, you\'ve\' asked for help!', description='Here are a list of some command you can do: ' \
              +'\n' +'\n' '!meme - sends a random meme'\
              +'\n' +'\n' '!hug - sends a random hug gif' \
              +'\n' +'\n' '!breathe - sends a breathing exercise gif' \
              +'\n' +'\n' '!play - e.i(!play {insert YouTube link here}) will play that youtube link in the general'
                     'voice channel' \
              +'\n' +'\n' '!panic - is for people who are having an anxiety attack'\
			  +'\n' +'\n' '!happybday - sends a random birthday gif', colour=0x00E707)
        em.set_author(name=message.author, icon_url=client.user.avatar_url)
        await client.send_message(message.channel, embed=em)

	#Admin commands
    elif message.content.startswith('!purge'):
        if str(message.author.top_role) == "Admin":
            deleted = await client.purge_from(message.channel, limit=100)
            await client.send_message(message.channel, 'Deleted {} message(s)'.format(len(deleted)))

        else:
            await client.send_message(message.channel, "*beep... boop...*Sorry you don't contain the "
                                                       "right privileges to execute that command.")

	#Message to welcome member when they join the server
@client.event
async def on_member_join(member):
    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}! Don\'t hesitate to use any of the ' \
                  '#support channels if you require immediate support  or contact @Staff if you have any questions. We\'re sure' \
                  ' you\'ll feel at home here :D'
    await client.send_message(server, fmt.format(member, server))

################################################################################
#logging in
@client.event
async def on_ready():
    print('------')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(game=discord.Game(name='Helping People'))
    await client.join_voice_channel(discord.Object(id='344147579593949194'))
################################################################################

client.run('')