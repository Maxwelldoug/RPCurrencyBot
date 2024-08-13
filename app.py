import discord
import pymysql.cursors
import settings
import logging
import init
import re

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

cursor = init.initialize()
db = cursor[0]
cursor = cursor[1]

def is_author_admin(message: discord.Message) -> bool:
    # Get the admin role ID from settings
    admin_role_id = settings.ADMINROLE
    
    # Check if the author has the role with the specified ID
    return any(role.id == admin_role_id for role in message.author.roles)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if ('--' in message.content):
        await message.channel.send('Nice try, no SQL injection for you.')
        return
    
    if ('#' in message.content):
        await message.channel.send('Nice try, no SQL injection for you.')
        return
    
    if ('/*' in message.content):
        await message.channel.send('Nice try, no SQL injection for you.')
        return
    
    if ('*/' in message.content):
        await message.channel.send('Nice try, no SQL injection for you.')
        return
    
    if ('"' in message.content):
        await message.channel.send('Nice try, no SQL injection for you.')
        return
    
    if ('\'' in message.content):
        await message.channel.send('Nice try, no SQL injection for you.')
        return

    if (';' in message.content):
        await message.channel.send('Nice try, no SQL injection for you.')
        return

    if message.content.startswith('$help'):
        await message.channel.send('''*The square brackets [] are mandatory. Arguments outside of brackets will be ignored.*
**Commands For Everyone**
help - View this message
register [character name] - Making a character
delete [character name] - Deleting a character
view [character name] - Look at the character's amount of money
history [character name] - Views the character's transaction history (shows descriptions)
currency - View all the types of currency.
currency [currency name] - View the specific currency and its description
leaderboard [currency name] - See who's the richest in this currency, for fun (optional)

**Commands Only For Admins**
pay [ping user] [character name] [amount] [currency] [description (optional)] - Pays the character the money in that currency with a description
remove [ping user] [character name] [amount] [currency] [description (optional)] - Removes the amount of money from character
removeall [ping user] [character name] - Removes all the money from the character
currregister [currency name] [description] - Makes the new currency
curredit [currency name] [new description] - Edits existing currency's description
currdelete [currency name] - Deletes the currency''')

    if message.content.startswith('$register'):
        try:
            ret = ''
            uid = int(message.author.id)
            arg = message.content.removeprefix('$register ')
            res = re.findall(r'\[.*?\]', arg)
            if (len(res) != 1):
                ret = 'Too Many or Not Enough Arguments'
            else:
                cursor.execute('SELECT CharacterName FROM Characters WHERE OwnerID = ' + str(uid) + ';')
                result = cursor.fetchall()
                dup = False
                res = re.sub('[\[\]]', '', res[0])
                for row in result:
                    if (row['CharacterName'] == res):
                        dup = True
                if (dup):
                    ret = 'You already have a character with that name.'
                else:
                    sql = "AddCharacter"
                    sqlargs = [res, uid]
                    cursor.callproc(sql, sqlargs)
                    result = cursor.fetchall()
                    db.commit()
                    ret = 'Registered Character ' + res + ' for user <@' + str(uid) + '>!'
            await message.channel.send(ret)
            return
        except Exception as e:
            await message.channel.send("Paging <@206008886438658048>, something's broke:\n" + str(e))
            return

    if message.content.startswith('$delete'):
        try:
            ret = ''
            uid = int(message.author.id)
            arg = message.content.removeprefix('$delete ')
            res = re.findall(r'\[.*?\]', arg)
            if (len(res) != 1):
                ret = 'Too Many or Not Enough Arguments'
            else:
                cursor.execute('SELECT CharacterName FROM Characters WHERE OwnerID = ' + str(uid) + ';')
                result = cursor.fetchall()
                exi = True
                res = re.sub('[\[\]]', '', res[0])
                for row in result:
                    if (row['CharacterName'] == res):
                        exi = False
                if (exi):
                    ret = 'You do not have a character with that Name.'
                else:
                    sql = "DelCharacter"
                    sqlargs = [res, uid]
                    cursor.callproc(sql, sqlargs)
                    result = cursor.fetchall()
                    db.commit()
                    ret = 'Deleted Character ' + res + ' for user <@' + str(uid) + '>!'
            await message.channel.send(ret)
            return
        except Exception as e:
            await message.channel.send("Paging <@206008886438658048>, something's broke:\n" + str(e))
            return
    
    if message.content.startswith('$view'):
        try:
            ret = ''
            uid = int(message.author.id)
            arg = message.content.removeprefix('$view ')
            res = re.findall(r'\[.*?\]', arg)
            if (len(res) != 1):
                ret = 'Too Many or Not Enough Arguments'
            else:
                cursor.execute('SELECT CharacterName FROM Characters WHERE OwnerID = ' + str(uid) + ';')
                result = cursor.fetchall()
                exi = True
                res = re.sub('[\[\]]', '', res[0])
                for row in result:
                    if (row['CharacterName'] == res):
                        exi = False
                if (exi):
                    ret = 'You do not have a character with that Name.'
                else:
                    cursor.execute('SELECT CurrencyName, Balance FROM Accounts WHERE OwnerID = "' + str(uid) + '" AND CharacterName = "' + res + '";')
                    result = cursor.fetchall()
                    ret = '***' + res + '***'
                    for row in result:
                        ret = ret + '\n\t' + str(row['CurrencyName'] + ': ' + str(row['Balance']))          
            await message.channel.send(ret)
            return
        except Exception as e:
            await message.channel.send("Paging <@206008886438658048>, something's broke:\n" + str(e))
            return

    if message.content.startswith('$currency'):
        try:
            ret = ''
            arg = message.content.removeprefix('$currency ')
            res = re.findall(r'\[.*?\]', arg)
            if (len(res) == 0):
                arg = '[]'
            if (len(res) > 1):
                ret = 'Too Many Arguments'
            else:
                if (len(res) == 0):
                    cursor.execute('SELECT CurrencyName, CurrencyDesc FROM Currencies;')
                    result = cursor.fetchall()
                    for row in result:
                        ret = ret + row['CurrencyName'] + '\n'
                else:
                    res = re.sub('[\[\]]', '', res[0])
                    cursor.execute('SELECT CurrencyDesc FROM Currencies WHERE CurrencyName = "' + res + '";')
                    result = cursor.fetchall()
                    ret = '***' + res + '***' + '\n'
                    for row in result:
                        ret = ret + '\n' + str(row['CurrencyDesc'])
            await message.channel.send(ret)
            return
        except Exception as e:
            await message.channel.send("Paging <@206008886438658048>, something's broke:\n" + str(e))
            return

    if message.content.startswith('$leaderboard'):
        try:
            ret = ''
            arg = message.content.removeprefix('$leaderboard ')
            res = re.findall(r'\[.*?\]', arg)

            if (len(res) != 1):
                ret = 'Too Many or Not Enough Arguments'
            else:
                res = re.sub('[\[\]]', '', res[0])
                cursor.execute('SELECT CharacterName, Balance FROM Accounts WHERE CurrencyName = "' + res + '";')
                result = cursor.fetchall()
                newlist = sorted(result, key=lambda d: d['Balance'], reverse=True)
                newlist = newlist[:10]
                ret = '**Leaderboards for ' + res + '**'
                for row in newlist:
                    ret = ret + '\n' + row['CharacterName'] + ': ' + str(row['Balance'])
            await message.channel.send(ret)
            return
        except Exception as e:
            await message.channel.send("Paging <@206008886438658048>, something's broke:\n" + str(e))
            return
    
    if message.content.startswith('$curr'):
        try:
            ret = ''
            if (is_author_admin(message)):
                arg = message.content.removeprefix('$curr')
                res = re.findall(r'\[.*?\]', arg)
                if arg.startswith('register'):
                    pass
                elif arg.startswith('edit'):
                    pass
                elif arg.startswith('delete'):
                    if (len(res) == 1):
                        exi = False
                        us = re.sub('[\[\]]', '', res[0])
                        cursor.execute("SELECT CurrencyName FROM Currencies;")
                        result = cursor.fetchall()
                        for row in result:
                            if (row['CurrencyName'] == us):
                                exi = True
                        if (exi):
                            sql = "DelCurrency"
                            sqlargs = [us]
                            cursor.callproc(sql, sqlargs)
                            result = cursor.fetchall()
                            db.commit()
                            ret = us + " was deleted."
                        else:
                            ret = "No such currency exists."
                    else:
                        ret = 'Too Many or Not Enough Arguments'
                else:
                    return
            else:
                ret = 'You do not have the required role to perform this command.'
            await message.channel.send(ret)
            return
        except Exception as e:
            await message.channel.send("Paging <@206008886438658048>, something's broke:\n" + str(e))
            return

            

print("Init Complete")
client.run(settings.BOTTOKEN, log_handler=handler, log_level=logging.DEBUG)