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
		if message.author.bot == True:
			return

		message_count, image_count, embeds_count, stickers_count = 0, 0, 0, 0
		xp_message, xp_image, xp_embeds, xp_stickers = 5, 10, 10, 10
		
		# Message counts
		data, user = update_user(message.author.id, message.author.name, "messages", False, 1)
		message_count += 1
		xp = xp_message

		# Image counts
		if message.attachments:
			data, user = update_user(message.author.id, message.author.name, "images", False, 1)
			image_count += 1
			xp = xp_image
		
		# Embed counts
		if message.embeds:
			data, user = update_user(message.author.id, message.author.name, "embeds", False, 1)
			embeds_count += 1
			xp = xp_embeds

		# Sticker counts
		if message.stickers:
			data, user = update_user(message.author.id, message.author.name, "embeds", False, 1)
			stickers_count += 1
			xp = xp_stickers

		# XP
		# ActivityRank: Messages are 10 XP
		user["xp"] += xp 

		# Rank
		# ActivityRank: Level Factor
		current_level = user["level"]
		current_xp = user["xp"]
		data_level = json_read("levels.json")
		next_xp = data_level["levels"][current_level]["total_xp"]

		if next_xp < current_xp:
			data, user = update_user(message.author.id, message.author.name, "level", False, 1)

		json_dump(data)

		if message.content.startswith('$hello'):
			await message.channel.send('Hello!')
	except PermissionError:
		print("Error!!")
		await restart_bot()

@bot.event
async def on_reaction_add(reaction, user):
	update_user(user.id, user.name, "reactionsadded", True)
	update_user(reaction.message.author.id, reaction.message.author.name, "reactionsrecieved", True, 1)


@bot.event
async def on_voice_state_update(member, before, after):
	# ActivityRank: Voiceminutes are 5 XP
	voice_minutes = 0
	voice_xp = 5
	# While the user is in a voice chat (including switching to different voice chats)...
	# Add 1 voice_minute every 60 seconds
	while before.channel is None and after.channel is not None:
		print("in_channel")
		await asyncio.sleep(60)
		voice_minutes += 1
		print(f"Voice Minutes: {voice_minutes}")
		# When the user leaves voice chat...
		# Update users.json with update voice_minutes and xp
		if before.channel is None and after.channel is None:
			data, user = update_user(member.id, member.name, "voice_minutes", False, voice_minutes)
			voice_xp = voice_xp * voice_minutes
			xp = voice_xp
			user["xp"] += xp 
			json_dump(data)
			print("out_of_channel")
			break

# @bot.slash_command(guild_ids=[273567091368656898])
# async def level(ctx):
#     await ctx.respond(f"Your level is {level}")


bot.run(TOKEN)

