import discord
import time
import datetime
import os
import aiohttp
import sys
import requests
import urllib
import json
import math
import asyncio
import random
import functools
import itertools
import traceback
from async_timeout import timeout
from platform import python_version
from datetime import datetime
from discord.ext import commands
from psutil import Process, virtual_memory
from discord import utils, Activity, ActivityType, Client, Embed, Colour
from discord.ext.commands import has_permissions, Bot, Greedy
from discord.ext.commands import BadArgument, CommandNotFound, MissingPermissions, MissingRequiredArgument
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from youtube_dl import YoutubeDL
from setuptools import setup




intents = discord.Intents().all()
intents.members = True
intents.messages = True


client = commands.Bot(command_prefix="!", intents=intents)


for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and not filename.startswith("_"):
       client.load_extension(f"cogs.{filename[:-3]}")





@client.command()
async def unban(ctx, *, user=None):

    try:
        user = await commands.converter.UserConverter().convert(ctx, user)
    except:
        await ctx.send("can't be found now.")
        return

    try:
        bans = tuple(ban_entry.user for ban_entry in await ctx.guild.bans())
        if user in bans:
            await ctx.guild.unban(user, reason="moderator: "+ str(ctx.author))
        else:
            await ctx.send("this user is not banned.")
            return

    except discord.Forbidden:
        await ctx.send("i don't have perms for unban.")
        return

    except:
        await ctx.send("i don't have perms for unban.")
        return

    await ctx.send(f"unbanned {user.mention}!")





class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
 
@client.command()
async def latency(ctx):
     await ctx.send(f'southside latency is {round(client.latency * 1000)}ms.')

@client.command()
async def say(ctx, *, text):
    await ctx.send(text)




@client.command()
async def ban (ctx, member:discord.User=None, reason =None):
    if member == None or member == ctx.message.author:
        await ctx.channel.send("who wants to be banned today?")
        return
    await ctx.guild.ban(member, reason=reason)
    await ctx.channel.send(f"{member} was banned.")





@client.command(aliases=['av'])
async def avatar(ctx, member : discord.Member = None):
    member = ctx.author if not member else member

    embed = discord.Embed(
    title = f" {member.name}'s profile photo'",
    color = discord.Color.green()
    )
    embed.set_image(url='{}'.format(member.avatar_url))
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member=None):
    if not member:
        await ctx.send("you want to mute someone?")
        return
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.add_roles(role)
    await ctx.send (f" {member.mention} has been muted.")





@client.command()
@commands.has_permissions(manage_channels = True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send( ctx.channel.mention + " has been locked.")

@client.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(ctx.channel.mention + " has been unlocked.")






@client.command()
@commands.is_owner()
async def unboot(ctx):
    await ctx.send("The bot is now unbooted. ")
    await client.logout()

def restart_bot(): 
  os.execv(sys.executable, ['python'] + sys.argv)

@client.command(name= 'reboot')
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Bot has been rebooted succesfully.")
    restart_bot()





        

@client.command()
@commands.has_permissions(administrator=True)
async def purge(ctx, amount : int):
    if amount > 50: 
        amount = 50
    await ctx.channel.purge(limit= amount + 1) 



    
@client.command()
async def info(ctx, user: discord.Member=None):

    if user == None:
        user = ctx.author
    embed = discord.Embed(timestamp=ctx.message.created_at, color=ctx.author.color)
    embed.add_field(name="Nickname",  value=user.name, inline=True)
    embed.add_field(name="UserID", value=user.id, inline=True)
    embed.add_field(name="Status", value=user.status, inline=True) 
    embed.add_field(name="Number of roles", value=len(user.roles))
    embed.add_field(name="Join date", value=user.joined_at.strftime("%A, %d. %B %Y"))
    embed.add_field(name="Creation date", value=user.created_at.strftime("%A, %d. %B %Y"))
    await ctx.send(embed=embed)

@client.command()
async def botinfo(ctx):
      embed = discord.Embed(title = " southside bot info", color= ctx.author.color)
      embed.add_field(name = " version", value = f"15 sep 2023 ")
      embed.add_field(name = " creation date", value = f"11 jan 2022 ")
      await ctx.send(embed=embed)
      
@client.command()
async def clanmembers(ctx):
    embed = discord.Embed(title= "AIM Members", color= ctx.author.color)
    embed.add_field(name="Clan Leader", value= f".Kraken")
    embed.add_field(name="Clan Co-Leaders", value= f"ridvalsiberianu, callsyko4show, Kraken96, AlexyK")
    embed.add_field(name="Rank 5 Members", value= f"ciupi, excalibur_")
    embed.add_field(name="Rank 3 Members", value= f"aeexxenegger., parfumdedama")
    embed.add_field(name="Rank 2 Members", value= f"celefacma")
    embed.add_field(name="Rank 1 Members", value= f"fane, Otege69, KiddOnetSANGEDETAUR, Denis@itidaudebehai, AndreiZEW69, gTs.")
    await ctx.send(embed=embed)

@client.command()
async def claninfo(ctx):
    embed = discord.Embed(title= "AIM", color= ctx.author.color)
    embed.add_field(name="Created by", value= f"callsyko4show")
    embed.add_field(name="Clan Owner", value= f".Kraken")
    embed.add_field(name="Clan HQ", value= f"13")
    embed.add_field(name="Expiration date", value= f"18.09.2024")
    await ctx.send(embed=embed)


@client.command()
async def chq(ctx):
    await ctx.send("AIM's Clan HQ is Clan HQ 13.")

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
  return "AIM"

def run():
  app.run(host="0.0.0.0", port=8000)

def keep_alive():
  server = Thread(target=run)
  server.start()

keep_alive()
client.run("token")
