import asyncio
import configparser
import json

import discord
import requests
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext

# To read the ini file
configs = configparser.ConfigParser()
configs.read('config.ini', encoding='utf-8')

# Login discord
TOKEN = configs["Discord"]["Token"]
bot = Bot(command_prefix="$")
slash = SlashCommand(bot, sync_commands=True)

# Webhook URL
webhook_url = configs["Webhook"]["URL"]

# Guild ID
guild_ids=[int(configs["Discord"]["guild_id"])]

# Show after login
@bot.event
async def on_ready():
    
    login_text = "Bot logged in with no problem." # Text to be displayed when logging in
    print(login_text)

    await bot.change_presence(
        activity=discord.Game(name=str(configs["Discord"]["status"])) # Change status messages
    )

# Definition and processing part of the slash command
@slash.slash(name="images", description="Summarizes the specified number of images posted before this command.", guild_ids=guild_ids)
async def images(ctx, *args):

    if int(args[0]) > 4 or int(args[0]) < 2: # If the value is not 2~4, stop processing.
        msg = await ctx.send("The value should be between 2~4.👾")
        await asyncio.sleep(3)
        await msg.delete()
        return
    
    temp_message = await ctx.send("One moment, please.🕛", hidden=True) # mystery??????

    images_url = []
    messages_ = []
    count = 0

    author_id = ctx.author.id
    messages = await ctx.channel.history(limit=30).flatten() # Get history

    for msg in messages:
        if msg.author.id == author_id: # Omit messages that are not from the executor of the command.
            if msg.attachments != []: # Extract only images posted in the past

                count += 1 # The Primitive Way!!

                if count > int(args[0]):
                    break

                images_url.append(msg.attachments[0].url)
                messages_.append(msg) # Preserve image URLs and objects

    images_url.reverse() # Reverse the list to match the order.

    if len(images_url) == 2:
        content = {
            "embeds": [
                {
                    "url": "https://twitter.com", # Apparently, it's important to Twitter the link here.
                    "description": f"From：<@!{ctx.author.id}>",
                    "image": {"url": images_url[0]},
                },
                {"url": "https://twitter.com", "image": {"url": images_url[1]}},
            ]
        }

    elif len(images_url) == 3:
        content = {
            "embeds": [
                {
                    "url": "https://twitter.com",
                    "description": f"From：<@!{ctx.author.id}>",
                    "image": {"url": images_url[0]},
                },
                {"url": "https://twitter.com", "image": {"url": images_url[1]}},
                {"url": "https://twitter.com", "image": {"url": images_url[2]}},
            ]
        }

    elif len(images_url) == 4:
        content = {
            "embeds": [
                {
                    "url": "https://twitter.com",
                    "description": f"From：<@!{ctx.author.id}>",
                    "image": {"url": images_url[0]},
                },
                {"url": "https://twitter.com", "image": {"url": images_url[1]}},
                {"url": "https://twitter.com", "image": {"url": images_url[2]}},
                {"url": "https://twitter.com", "image": {"url": images_url[3]}},
            ]
        }

    else: # Processing when an exception occurs
        msg = await ctx.send("An error has occurred.\nThere may not be more than the specified number of images.")
        await asyncio.sleep(3)
        await msg.delete()
        return

    requests.post(
        webhook_url, json.dumps(content), headers={"Content-Type": "application/json"} # This is the part that goes without saying.
    )

    for msg in messages_: # Delete images by default
        await msg.delete()

bot.run(TOKEN)