import discord
import os
import json
import asyncio

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

#* Template for reference, might use?
template = {"users": [{"user_id": 0, "name":"name", "xp": 0, "rank": 0, "messages": 0, "voice_call_hours":0, "invites":0, "special_xp":0}]}

# Used to append new users into the users.json file
def write_json(new_data, filename):
	with open(filename, "r+") as f:
		file_data = json.load(f)
		file_data["users"].append(new_data)
		f.seek(0)
		json.dump(file_data, f, indent=2)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
	# Ignore bots
	if message.author.bot == True:
		return

	# Get variables of user
	main_id = message.author.id
	main_user = message.author.name

	# Open the master json file
	with open("users.json") as f:
		data = json.load(f)

	# Get a list of all user ids, if current user not found, create a new json object
	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])
	if main_id not in user_ids:
		new_user = {"user_id": main_id, "name": main_user, "xp": 0, "rank": 0, "messages": 0, "voice_call_hours":0, "invites":0, "special_xp":0}
		write_json(new_user, "users.json")

	# Index the user id list, find the current user and update...
	user_id_index = user_ids.index(main_id)
	user = data["users"][user_id_index]

	# Message counts
	user["messages"] += 1

	with open("users.json", "w") as f:
		json.dump(data, f, indent=2)

	if message.content.startswith('$hello'):
		await message.channel.send('Hello!')


@bot.event
async def on_voice_state_update(member, before, after):
	# When user joins vc...
	if before.channel is None and after.channel is not None:
		print("start")
	# When user leaves vc...
	else:
		print("end")


@bot.slash_command(guild_ids=[273567091368656898])
async def level(ctx):
    await ctx.respond(f"Your level is {level}")

bot.run(TOKEN)
