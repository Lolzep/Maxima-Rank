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

template = {"users": [{"user_id": 0, "name":"name", "xp": 0, "rank": 0, "messages": 0, "voice_call_hours":0, "invites":0, "special_xp":0}]}

# Used to append new users into the users.json file
def write_json(new_data, filename):
	with open(filename, "r+") as file:
		file_data = json.load(file)
		file_data["users"].append(new_data)
		file.seek(0)
		json.dump(file_data, file, indent=2)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()  
async def info(ctx, user: discord.Member):  
    await ctx.send(f'{user.mention}\'s id: `{user.id}`') 

@bot.event
async def on_message(message):
	main_id = message.author.id
	main_user = message.author.name

	with open("users.json") as file:
		data = json.load(file)

	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])
	if main_id not in user_ids:
		new_user = {"user_id": main_id, "name": main_user, "xp": 0, "rank": 0, "messages": 0, "voice_call_hours":0, "invites":0, "special_xp":0}
		write_json(new_user, "users.json")

	if message.author == bot.user:
		return

	if message.content.startswith('$hello'):
		await message.channel.send('Hello!')


@bot.event
async def on_voice_state_update(member, before, after):
	if before.channel is None and after.channel is not None:
		print("start")
	else:
		print("end")


@bot.slash_command(guild_ids=[273567091368656898])
async def level(ctx):
    await ctx.respond(f"Your level is {level}")

bot.run(TOKEN)
