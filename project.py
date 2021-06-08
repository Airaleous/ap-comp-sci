import discord
from discord.ext import commands
import os.path
import asyncio
import os
import json
import random

client = commands.Bot(command_prefix = '!')
token = open("token.txt","r").read()
client.remove_command("help")

def setup():
    if os.path.exists('./money.json') == False:
        with open("./money.json", "w") as file:
            file.write("{}")

@client.event
async def on_ready():
    print('{0.user} is now active.'.format(client))
    setup()

def createUser(user):
    with open('./money.json', 'r') as file:
        data = json.load(file)
        data["{}".format(user.id)] = 1000
    with open('./money.json', 'w+') as outfile:
        json.dump(data, outfile)

def checkUser(user):
    file = open('./money.json', 'r')
    data = json.load(file)
    file.close()
    if (str(user.id) in data)==False:
        createUser(user)

def readBalance(user):
    checkUser(user)
    file = open('./money.json', 'r')
    data = json.load(file)
    return(data["{}".format(user.id)])

def updateBalance(user, change):
    checkUser(user)
    with open('./money.json', 'r') as file:
        data = json.load(file)
        data["{}".format(user.id)] += change
    with open('./money.json', 'w+') as outfile:
        json.dump(data, outfile)

def setUserBalance(user, amount):
    checkUser(user)
    with open('./money.json', 'r') as file:
        data = json.load(file)
        data["{}".format(user.id)] = amount
    with open('./money.json', 'w+') as outfile:
        json.dump(data, outfile)



@client.command(aliases=['money','bal','bank'])
async def balance(ctx):
    user = ctx.message.author
    await ctx.message.delete()
    if len(ctx.message.mentions) == 0:
        embed = discord.Embed(title="Your Balance", color=0x7289DA)
        #embed.set_author(name=str(user.display_name), icon_url=client.user.avatar_url)
        embed.add_field(name=user.display_name, value="${:,}".format(readBalance(user)), inline=True)
    else:
        embed = discord.Embed(title="User Balances", color=0x7289DA)
        #embed.set_author(name=str(user.display_name), icon_url=client.user.avatar_url)
        for member in ctx.message.mentions:
            embed.add_field(name=str(member.display_name), value="${:,}".format(readBalance(member)), inline=True)
    await ctx.channel.send(embed=embed)

@client.command(aliases=['setmoney','newbalance', 'setbal'])
@commands.has_permissions(administrator=True)
async def setbalance(ctx, amount="1000"):
    user = ctx.message.author
    await ctx.message.delete()
    if amount.isnumeric() == False:
        await ctx.channel.send("Enter a valid amount such as \"1000\"", delete_after=4)
        return
    if len(ctx.message.mentions) == 0:
        setUserBalance(user, int(amount))
    else:
        for member in ctx.message.mentions:
            setUserBalance(member, int(amount))

@client.command(aliases=['addmoney'])
@commands.has_permissions(administrator=True)
async def addbalance(ctx, amount="1000"):
    user = ctx.message.author
    await ctx.message.delete()
    if amount.isnumeric() == False:
        await ctx.channel.send("Enter a valid amount such as \"1000\"", delete_after=4)
        return
    if len(ctx.message.mentions) == 0:
        updateBalance(user, int(amount))
    else:
        for member in ctx.message.mentions:
            updateBalance(member, int(amount))

@client.command()
async def gamble(ctx, amount="100"):
    min = -100 #In percent. If set above, users can't lose money
    max = 100 # In percent. 100% means users can double their money at most
    user = ctx.message.author
    await ctx.message.delete()
    if amount.isnumeric() == False:
        await ctx.channel.send("Enter a valid amount such as \"100\"", delete_after=4)
        return
    if readBalance(user) < int(amount):
        await ctx.channel.send("Not enough money!", delete_after=4)
        return
    winnings = int(round(int(amount)*(random.randint(min, max)/100), 0))
    updateBalance(user, winnings)
    if winnings >= 0:
        await ctx.channel.send("You gambled ${:,} and won ${:,}. You now have ${:,}".format(int(amount), int(winnings), int(readBalance(user))), delete_after=5)
    else:
        await ctx.channel.send("You gambled ${:,} and lost ${:,}. You now have ${:,}".format(int(amount), abs(int(winnings)), int(readBalance(user))), delete_after=5)


client.run(token)
