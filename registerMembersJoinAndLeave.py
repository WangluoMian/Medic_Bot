import discord

client = discord.Client()

@client.event
async def on_member_join(member):
    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}! Don\'t hesitate to use any of the ' \
                  '#support channels if you require immediate support  or contact @staff if you have any questions. We\'re sure' \
                  ' you\'ll feel at home here :D'
    await client.send_message(server, fmt.format(member, server))

@client.event
async def on_member_remove(member):
    server = member.server
    fmt = 'Sad to see {0.mention} leave our beloved {1.name}! We will cherish the moments we spent together.'
    await client.send_message(server, fmt.format(member, server))