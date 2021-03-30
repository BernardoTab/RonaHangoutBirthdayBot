# main.py
import os
from keep_alive import keep_alive
from discord.ext import commands
import discord
from dotenv import load_dotenv
from datetime import datetime

import asyncio
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
last_day_checked=0
bot = commands.Bot(command_prefix='!')
birthdayDict = {}
startup_bool = False

async def birthdayCheckLoop(channel):
    while True:
        await checkDate(channel)
        await asyncio.sleep(3600)


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



@bot.command(name='set', help='Sets a birthday into the system')
async def setBirthday(ctx, day:int, month:int):

    if ctx.message.author.id in birthdayDict:
        key_already_present = generateEmbed("Birthday set failure","You have already set your birthday "
                                            +ctx.message.author.name+"!")
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
    birthdayDict[ctx.message.author.id] = ""+day_str+" "+month_str
    response_message = ctx.message.author.name+"'s birthday was set to "+birthdayConversion(int(day_str),int(month_str))
    response_embed = generateEmbed("Birthday set!",response_message)

    await ctx.send(embed=response_embed)


def generateEmbed(str_author, str_description):
    response_embed = discord.Embed(description=str_description, color=0x674b9b)
    response_embed.set_author(name=str_author)
    return response_embed

@bot.command(name='list', help='Shows a list of all the birthdays')
async def listBirthdays(ctx):
    list=""
    for k, v in sorted(birthdayDict.items()):
        values=v.split(' ')
        user = await ctx.guild.fetch_member(k)
        list+=user.name+" - "+birthdayConversion(int(values[0]),int(values[1]))+'\n'

    if(not bool(birthdayDict)):
        list = "No birthdays have been set!"

    response_embed = generateEmbed("Birthday list", list)
    await ctx.send(embed=response_embed)

@bot.command(name='clear', help='Clears the birthday list')
async def clearBirthdays(ctx):
    birthdayDict.clear()

    response_embed = generateEmbed("Clear", "Birthday list has been cleared!")
    await ctx.send(embed=response_embed)

@bot.command(name='remove', help='Removes your birthday from the list')
async def removeBirthday(ctx):
    if ctx.message.author.id in birthdayDict:
        del birthdayDict[ctx.message.author.id]
        response_embed = generateEmbed("Birthday removal", ctx.message.author.name + "'s birthday was removed!")
        await ctx.send(embed=response_embed)
    else:
        response_embed = generateEmbed("Birthday removal", "You haven't set a birthday yet!")
        await ctx.send(embed=response_embed)

@bot.command(name='force-announce', help='Force announce a birthday')
async def forceAnnounceBirthday(ctx, name):
    response_embed = generateEmbed("BIRTHDAY ALARM!", "It's "+name+"'s birthday today! Wish them a jolly good one")
    msg = await ctx.send(content="@everyone",embed=response_embed)
    await birthdayReact(msg)


async def checkDate(ctx):
    date = datetime.date(datetime.now())
    date_args=str(date).split('-')
    month = date_args[1]
    day = date_args[2]
    global last_day_checked

    if day == last_day_checked:
        return

    for k, v in sorted(birthdayDict.items()):
        values=v.split(' ')
        if day==values[0] and month==values[1]:
            user= await ctx.guild.fetch_member(k)
            response_embed = generateEmbed("BIRTHDAY ALARM!",
                                           "It's " + user.name + "'s birthday today! Wish them a jolly good one")
            msg= await ctx.send(content="@everyone", embed=response_embed)
            await birthdayReact(msg)
    last_day_checked=day

async def birthdayReact(msg):
    await reactToEmbed(msg,'\U0001F389')
    await reactToEmbed(msg,'\U0001F38A')
    await reactToEmbed(msg,'\U00002728')

async def reactToEmbed(msg,emoji):
    await msg.add_reaction(emoji)

@bot.command(name='startup', help='Starts the bot setup')
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

keep_alive()
bot.run(TOKEN)