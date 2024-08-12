import discord
import pymysql.cursors
import settings
import logging
import init

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
# intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

init.initialize()

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object())
    print(f'We have logged in as {client.user}')

@tree.command(
    name="help",
    description="My first application Command",
)
async def first_command(interaction):
    await interaction.response.send_message('''**Commands For Everyone**
help - View this message
register [character name] - Making a character
delete [character name] - Deleting a character
view [character name] - Look at the character's amount of money
history [character name] - Views the character's transaction history (shows descriptions)
currency - View all the types of currency
currency [currency name] - View the specific currency and its description
leaderboard [currency name] - See who's the richest in this currency, for fun (optional)

**Commands Only For Storytellers**
pay [character name] [amount] [currency] [description (optional)] - Pays the character the money in that currency with a description
remove [character name] [amount] [currency] [description (optional)] - Removes the amount of money from character
removeall [character name] - Removes all the money from the character
currency-register [currency name] [description] - Makes the new currency
currency-edit [currency name] [new description] - Edits existing currency's description
currency- delete [currency name] - Deletes the currency''')

""" @client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$help'):
        await message.channel.send('''**Commands For Everyone**
help - View this message
register [character name] - Making a character
delete [character name] - Deleting a character
view [character name] - Look at the character's amount of money
history [character name] - Views the character's transaction history (shows descriptions)
currency - View all the types of currency
currency [currency name] - View the specific currency and its description
leaderboard [currency name] - See who's the richest in this currency, for fun (optional)

**Commands Only For Storytellers**
pay [character name] [amount] [currency] [description (optional)] - Pays the character the money in that currency with a description
remove [character name] [amount] [currency] [description (optional)] - Removes the amount of money from character
removeall [character name] - Removes all the money from the character
currency-register [currency name] [description] - Makes the new currency
currency-edit [currency name] [new description] - Edits existing currency's description
currency- delete [currency name] - Deletes the currency''') """

print("Init Complete")
client.run(settings.BOTTOKEN, log_handler=handler, log_level=logging.DEBUG)