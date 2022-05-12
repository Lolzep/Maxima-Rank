import discord
import os
import asyncio
from datetime import datetime
import time

from dotenv import load_dotenv
from myfunctions import update_user, json_dump, json_read, restart_bot

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
	try:
		# Ignore bots
		# if message.author.bot == True:
		# 	return

		# Image counts
		if message.attachments:
			update_user(message.author.id, message.author.name, "images", True, 1, 10, 1)
		
		# Embed counts
		if message.embeds:
			update_user(message.author.id, message.author.name, "embeds", True, 1, 10, 1)

		# Sticker counts
		if message.stickers:
			update_user(message.author.id, message.author.name, "embeds", True, 1, 10, 1)

		# Message counts
		update_user(message.author.id, message.author.name, "messages", True, 1, 5, 1)

		if message.content.startswith('$hello'):
			await message.channel.send('Hello!')
	except PermissionError:
		print("Error!!")
		await restart_bot()

@bot.event
async def on_reaction_add(reaction, user):
	# For reactions added and reactions recieved, add values and xp to respective user
	update_user(user.id, user.name, "reactionsadded", True, 1, 5, 1)
	update_user(reaction.message.author.id, reaction.message.author.name, "reactionsrecieved", True, 1, 5, 1)


@bot.event
async def on_voice_state_update(member, before, after):
	# ActivityRank: Voiceminutes are 5 XP
	voice_minutes = 0
	# While the user is in a voice chat (including switching to different voice chats)...
	# Add 1 voice_minute every 60 seconds
	while before.channel is None and after.channel is not None:
		print("in_channel")
		await asyncio.sleep(2)
		voice_minutes += 1
		print(f"Voice Minutes: {voice_minutes}")
		# When the user leaves voice chat...
		# Update users.json with update voice_minutes and xp
		if before.channel is None and after.channel is None:
			update_user(member.id, member.name, "voice_minutes", True, voice_minutes, 5, voice_minutes)
			print("out_of_channel")
			break

# @bot.slash_command(guild_ids=[273567091368656898])
# async def level(ctx):
#     await ctx.respond(f"Your level is {level}")

bot.run(TOKEN)

