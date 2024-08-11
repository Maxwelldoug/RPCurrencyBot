import discord
import pymysql.cursors
import settings
import logging

# sample code

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('world!')

client.run(settings.BOTTOKEN, log_handler=handler, log_level=logging.DEBUG)