# main.py
import os
import sqlite3
from discord.ext import commands
import discord
from dotenv import load_dotenv
from datetime import datetime

import asyncio


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
last_day_checked=0
bot = commands.Bot(command_prefix='!')

startup_bool = False

db_connection = sqlite3.connect("birthdays.db")
db_cursor = db_connection.cursor()

bday_file = discord.File("ratbday.png")


def startup_dbtable():
    command_startup_db = """CREATE TABLE IF NOT EXISTS
    birthdays(id INTEGER PRIMARY KEY, bday TEXT)"""
    try:
        db_cursor.execute(command_startup_db)
        return True
    except:
        print("Error in starting up database")
        return False



def set_db(id,birthday_text):
    command="INSERT INTO birthdays (id, bday) VALUES (?, ?)"
    try:
        db_cursor.execute(command, (id, birthday_text))
        db_connection.commit()
        return True
    except:
        print("Error when setting birthday")
        return False


def fetch_db_specific(id):
    try:
        # check = db_cursor.execute("SELECT id, bday FROM birthdays")
        db_cursor.execute("SELECT id, bday FROM birthdays WHERE id = ?", (id,))
        check= db_cursor.fetchone()
        return check
    except:
        print("Error when attempting to fetch specific birthday")
        return "Exception"


def fetch_db_all():
    try:
        db_cursor.execute("SELECT id, bday FROM birthdays")
        check = db_cursor.fetchall()
        return check
    except:
        print("Error when attempting to fetch all birthdays")
        return None

def delete_db_specific(id):
    command="DELETE FROM birthdays WHERE id = ?"
    try:
        db_cursor.execute(command,(id,))
        db_connection.commit()
        return True
    except:
        print("Error when deleting specific birthday")
        return False

def delete_db_all():
    command="DELETE FROM birthdays"
    try:
        db_cursor.execute(command)
        db_connection.commit()
        return True
    except:
        print("Error when clearing birthdays")
        return False

def update_db_specific(id,birthday_text):
    command = "UPDATE birthdays SET bday = ? WHERE id = ?"
    try:
        db_cursor.execute(command, (birthday_text, id))
        db_connection.commit()
        return True
    except:
        print("Error when updating specific birthday")
        return False



async def birthdayCheckLoop(ctx):
    while True:
        await checkDate(ctx)
        await asyncio.sleep(1200)


def birthdayConversion(day:int,month:int):
    day_lower_digit = day % 10
    suffixes={0:"th",
              1:"st",
              2:"nd",
              3:"rd",
              4:"th",
              5:"th",
              6:"th",
              7:"th",
              8:"th",
              9:"th"}
    month_names={1:"January",
                 2:"February",
                 3:"March",
                 4:"April",
                 5:"May",
                 6:"June",
                 7:"July",
                 8:"August",
                 9:"September",
                 10:"October",
                 11:"November",
                 12:"December"}

    return month_names[month]+" "+str(day)+suffixes[day_lower_digit]



@bot.command(name='set', help='Sets a birthday into the system - DD MM')
async def setBirthday(ctx, day:int, month:int):

    if  (day>31) or (day<1) or (month<1) or (month>12):
        invalid = generateEmbed("Birthday set failure", "That date is invalid! Write !set DD MM")
        await ctx.send(embed=invalid)
        return

    birthday_check= fetch_db_specific(ctx.author.id)
    if birthday_check== "Exception":
        error = generateEmbed("Birthday set failure","Error in checking if your birthday is present "
                                            +ctx.message.author.name+"!")
        await ctx.send(embed=error)
        return

    elif birthday_check is not None:
        key_already_present = generateEmbed("Birthday set failure", "You have already set your birthday "
                                           + ctx.message.author.name + "!")
        await ctx.send(embed=key_already_present)
        return

    if(day/10.0 <1):
        day_str="0"+str(day)
    else:
        day_str=str(day)
    if(month/10.0<1):
        month_str="0"+str(month)
    else:
        month_str=str(month)

    if set_db(ctx.author.id, ""+day_str+" "+month_str) is False:
        error_setting = generateEmbed("Birthday set failure", "Error in setting your birthday "
                                            + ctx.message.author.name + "!")
        await ctx.send(embed=error_setting)
        return

    response_message = ctx.message.author.name+"'s birthday was set to "+birthdayConversion(int(day_str),int(month_str))
    response_embed = generateEmbed("Birthday set!",response_message)

    await ctx.send(embed=response_embed)


def generateEmbed(str_author, str_description):
    response_embed = discord.Embed(description=str_description, color=0x674b9b)
    response_embed.set_author(name=str_author)
    return response_embed

@bot.command(name='list', help='Shows a list of all the birthdays')
async def listBirthdays(ctx):
    bday_list=""

    db_bdays= fetch_db_all()

    if not db_bdays:
        bday_list = "No birthdays have been set!"
    else:
        for k in sorted(db_bdays):
            key = k[0]
            val = k[1]
            values = val.split(' ')

            user = await ctx.guild.fetch_member(int(key))
            bday_list += user.name + " - " + birthdayConversion(int(values[0]), int(values[1])) + '\n'

    response_embed = generateEmbed("Birthday list", bday_list)
    await ctx.send(embed=response_embed)

@bot.command(name='clear', help='[Mod Only] Clears the birthday list ')
@commands.has_any_role('God King','Angel Knight')
async def clearBirthdays(ctx):
    check= delete_db_all()
    if check:

        response_embed = generateEmbed("Clear", "Birthday list has been cleared!")
    else:

        response_embed = generateEmbed("Clear", "Error when attempting to clear the birthday list")
    await ctx.send(embed=response_embed)

@bot.event
async def on_command_error(ctx, error):
    print("Error!")
    if isinstance(error, commands.MissingAnyRole):
        response_embed = generateEmbed("Command Error", "You cannot use this function, only mods can!")
        await ctx.send(embed=response_embed)

@bot.command(name='remove', help='Removes your birthday from the list')
async def removeBirthday(ctx):

    if fetch_db_specific(ctx.author.id) is not None:
        check=delete_db_specific(ctx.author.id)
        if check:
            response_embed = generateEmbed("Birthday removal", ctx.message.author.name + "'s birthday was removed!")
            await ctx.send(embed=response_embed)
        else:
            response_embed = generateEmbed("Error when attempting to remove your birthday")
            await ctx.send(embed=response_embed)

    else:
        response_embed = generateEmbed("Birthday removal", "You haven't set a birthday yet!")
        await ctx.send(embed=response_embed)

@bot.command(name='force-announce', help='[Mod Only] Force announce a birthday')
@commands.has_any_role('God King','Angel Knight')
async def forceAnnounceBirthday(ctx, name):
    response_embed = generateEmbed("BIRTHDAY ALARM!", "It's "+name+"'s birthday today! Wish them a jolly good one")
    msg = await ctx.send(content="@everyone",embed=response_embed,file=bday_file)
    await birthdayReact(msg)


@bot.command(name='update', help='Update your birthday')
async def updateBirthday(ctx, day:int, month:int):

    if (day>31) or (day<1) or (month<1) or (month>12):
        invalid = generateEmbed("Birthday update failure", "That date is invalid! Write !update DD MM")
        await ctx.send(embed=invalid)
        return

    if (day / 10.0 < 1):
        day_str = "0" + str(day)
    else:
        day_str = str(day)
    if (month / 10.0 < 1):
        month_str = "0" + str(month)
    else:
        month_str = str(month)

    check=update_db_specific(ctx.author.id,day_str+" "+month_str)

    if check:

        response_embed = generateEmbed("Birthday Update", ctx.author.name + "'s birthday has been updated")
    else:

        response_embed = generateEmbed("Birthday Update", "Error when attempting to update the birthday")
    await ctx.send(embed=response_embed)


async def checkDate(ctx):
    date = datetime.date(datetime.now())
    date_args=str(date).split('-')
    month = date_args[1]
    day = date_args[2]
    global last_day_checked

    if day == last_day_checked:
        return

    db_bdays = fetch_db_all()

    try:
        for k in sorted(db_bdays):
            # for k, v in sorted(birthdayDict.items()):
            key = k[0]
            val = k[1]
            values = val.split(' ')

            if day == values[0] and month == values[1]:
                user = await ctx.guild.fetch_member(int(key))

                print("success user get check")
                response_embed = generateEmbed("BIRTHDAY ALARM!",
                                               "It's " + str(user) + "'s birthday today! Wish them a jolly good one")
                channel = discord.utils.get(ctx.guild.text_channels, name='🙃-general')

                print("success channel check")
                msg = await channel.send(content="@everyone", embed=response_embed,file=bday_file)
                await birthdayReact(msg)

        print("success birthday check")
        last_day_checked = day
    except Exception as e:
        print("Error in regular birthday check!")
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)


async def birthdayReact(msg):
    await reactToEmbed(msg,'\U0001F389')
    await reactToEmbed(msg,'\U0001F38A')
    await reactToEmbed(msg,'\U00002728')

async def reactToEmbed(msg,emoji):
    await msg.add_reaction(emoji)

@bot.command(name='startup', help='Starts the bot setup')
@commands.has_any_role('God King','Angel Knight')
async def startup(ctx):
    global startup_bool
    if startup_bool:
        response_embed = generateEmbed("Startup Failure",
                                       "The bot has already gone through startup!")
        await ctx.send(embed=response_embed)
        return
    bot.loop.create_task(birthdayCheckLoop(ctx))
    response_embed = generateEmbed("Startup Success",
                                   "Bot has been started up - use !help to find the available commands")
    await ctx.send(embed=response_embed)
    startup_bool=True
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name='you sleep'))

@bot.event
async def on_guild_join(guild):
    general = discord.utils.find(lambda x: x.name == '🙃-general',  guild.text_channels)
    response_embed = generateEmbed("Birthday Bot is in town!","""
                                   Hello @everyone, Birthday Bot here. I've heard some of yall will be having birthdays soon.
                                   
                                   😑 😢
                                   
                                   What a shame and here I was hoping that most of you wouldn't survive another day but here we are.
                                   
                                   If you want to try me out write !help to see which commands you have access to, they are prefixed with '!' 
                                   
                                   Any bugs that you wish to report or suggestions to add, plz contact the Mod Team :D""")
    await general.send(embed=response_embed)

startup_dbtable()
bot.run(TOKEN)