import json
import os
import sys
import discord

from operator import itemgetter

# Restart Monke Rank
def restart_bot():
	print("Restarting")
	os.execv(sys.executable, ['python3'] + sys.argv)

# Create a new json file
def new_json_file(filename, name: str):
	with open(filename, "w"):
		pass

# Create a new json array 
def new_json_objects(filename, name: str):
	new_template = {name:[]}
	with open(filename, "w") as f:
		json.dump(new_template, f, indent=2)

# Dump the data into json
#? Unused, would need to change users.json to match guild json
def json_dump(guild_id, data):
	with open("users.json", "w") as f:
		json.dump(data, f, indent=2)	

# Read the data from a json file
def json_read(filename):
	with open(filename, "r") as f:
		data = json.load(f)
	return data

# Used to append new users into the users.json file
def write_json(new_data, filename, name: str):
	with open(filename, "r+") as f:
		file_data = json.load(f)
		file_data[name].append(new_data)
		f.seek(0)
		json.dump(file_data, f, indent=2)

# Updates the user objects for the specified user in users.json file and writes new ones if not found
#? ARGUMENTS
# guild_id: guild id retrieved from discord api command
# main_id: user id retrieved from discord api command
# name: user name retrieved from discord api command
# key: The key to modify in the user json object
# dump_file: True : Dump the current changes into X Users.json
# dump_file: False : Return data of json file and the current user object being modified as variables
# amount_to_add: Amount of value to add to the specified key in the user object
# amount_of_xp: Amount of value to add to the xp in the user object, which can be...
# multiplier: ...multiplied by this value (useful for adding correct xp for >1 key value)
# premium: A boolean, used in on_member_update to know if a user is boosting the server or not (optional)
def update_user(guild_id, main_id, main_user, key : str, dump_file: bool, amount_to_add: int, amount_of_xp: int, multiplier: int, premium=None):
	template = {"user_id": main_id, "name": main_user, "xp": 0, "level": 0, "role_id": 0, "messages": 0, "reactions_added": 0, "reactions_recieved": 0, "stickers": 0, "images": 0, "embeds": 0, "voice_minutes":0, "invites":0, "special_xp":0, "is_booster":False}
	main_json = f"Data/{guild_id} Users.json"

	#* Check if missing or empty, if so, create new file and/or run new_json
	try:
		if os.stat(main_json).st_size == 0:
			new_json_objects(main_json, "users")
	except FileNotFoundError:
		new_json_file(main_json, "users")
		if os.stat(main_json).st_size == 0:
			new_json_objects(main_json, "users")

	#* Load initial users.json
	with open(main_json) as f:
		data = json.load(f)

	#* Get a list of all user ids
	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])

	#* Check if user not in users.json using user_id list, append new user if not
	# Index the user id list, find the current user for use in updating
	# If the id is not in the list, make a new json object with empty values, then return this instead
	if main_id not in user_ids:
		new_user = template
		write_json(new_user, main_json, "users")
		user_ids.append(new_user["user_id"])
		user_id_index = user_ids.index(main_id)
		# Load the appended json, then find the user id with the index
		with open(main_json) as f:
			data = json.load(f)
			user = data["users"][user_id_index]
	else:
		user_id_index = user_ids.index(main_id)
		user = data["users"][user_id_index]

	# Add amount_to_add to the specified key in the user object
	# If premium is not None, do not add, change the boolean to premium argument
	if premium is None:
		user[key] += amount_to_add
	else:
		user[key] = premium

	#* XP Block
	# Based on amount_of_xp given
	# Add xp to the specified user
	user["xp"] += amount_of_xp * multiplier

	# Update using the levels.json
	current_level = user["level"]
	current_xp = user["xp"]
	data_level = json_read("levels.json")
	next_xp = data_level["levels"][current_level]["total_xp"]
	if next_xp <= current_xp:
		user["level"] += 1
	#* XP Block

	# Using the dump_file boolean argument, should the current file be overwritten after completion?
	# If not, return data, user; to continue operation
	if dump_file == True:
		with open(main_json, "w") as f:
			json.dump(data, f, indent=2)
	else:
		return data, user;

# Create new levels with "level, xp and role_id" as the objects in a levels.json file
# For use in knowing the current levels and where each user's level currently stands
# TODO: roleid should be changed to actual roleids in Discord (probably need new definition)
def new_levels(level_factor: int, total_levels: int):
	# Create new levels key and a level object template starting at 0 for all
	i = 0
	new_data = {"level": 0, "level_xp": 100, "total_xp": 100, "role_id": 0, "role_title": "Newbie"}
	level_template = {"levels": []}

	# If the levels.json already exists, remove it to redo all calculations. Create new levels.json with level_template
	if os.path.exists("levels.json"):
		os.remove("levels.json")

	with open ("levels.json", "w") as f:
		json.dump(level_template, f, indent=2)

	write_json(new_data, "levels.json", "levels")

	# While i <= total_levels, create a new level object for each level 0 - i and calculate each variable as needed
	# TODO: Better implementation of this that allows these values to be edited easier
	while i < total_levels:
		# Create the variables
		n = i + 1
		role_title = ""
		if 0 <= n <= 2:
			role_title = "Newbie"
		elif 3 <= n <= 4:
			role_title = "Bronze"
		elif 5 <= n <= 9:
			role_title = "Silver"
		elif 10 <= n <= 24:
			role_title = "Gold"
		elif 25 <= n <= 49:
			role_title = "Platinum"
		elif 50 <= n <= 99:
			role_title = "Diamond"
		elif 100 <= n <= 149:
			role_title = "Master"
		elif 150 <= n <= 199:
			role_title = "Grandmaster"
		elif n >= 200:
			role_title = "Exalted"

		p_level = new_data["level"]
		n_level = new_data["level"] + 1

		p_level_xp = new_data["level_xp"]
		level_xp = p_level_xp + level_factor

		total_xp = new_data["total_xp"] + level_xp

		next_id = new_data["role_id"]

		# Create a new new_data object to then append and modify in the next loop
		new_data = {"level": n_level, "level_xp": level_xp, "total_xp": total_xp, "role_id": next_id, "role_title": role_title}

		write_json(new_data, "levels.json", "levels")
		i += 1

# Creates a simple embed for the most general of embed implementations (help, about, etc.)
#? ARGUMENTS
# command (string): What command from the bot it should be used on
# description (default=None, string): Set the description of the embed, optional 
def templateEmbed(command : str, description=None):
	tempEmbed = discord.Embed(color = discord.Color.purple())

	if description is not None:
		tempEmbed.set_author(name=description)
	else:
		pass

	tempFile = discord.File(f"Images/{command}.png", filename="image.png")
	tempEmbed.set_thumbnail(url="attachment://image.png")

	return tempEmbed, tempFile

# Activity values to be used inside the "/myrank" command embed
# Values also have a specific rank emoji assigned to them based on the max value in the server used
# The command returns everything needed to be used in the "embeds.py" file (fields, calc. values, etc.)
#? ARGUMENTS
# guild_id: guild id retrieved from discord api command
# main_id: user id retrieved from discord api command
# simple (boolean): If True, returns only the emoji list (useful for using in main.py and other cases where not everything needs to be returned)
def my_rank_embed_values(guild_id, main_id, simple : bool):
	#* Load initial json, find user who sent command
	main_json = f"Data/{guild_id} Users.json"
	with open(main_json) as f:
		data = json.load(f)

	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])

	user_id_index = user_ids.index(main_id)
	user = data["users"][user_id_index]

	#* Find current level in levels.json
	level = user["level"]
	xp = user["xp"]

	data_level = json_read("levels.json")
	data_level = data_level["levels"][level]

	#* A metric ton of variables for appending as a field in embed
	# Users.json values
	xp = user["xp"]
	level = user["level"]
	next_xp = data_level["total_xp"]
	level_xp = data_level["level_xp"]
	role_title = data_level["role_title"]
	role_id = data_level["role_id"]
	progress_to_next = level_xp - (next_xp - xp)
	
	# Users.json values to be used in the embed field
	types = ("messages", "reactions_added", "reactions_recieved", "stickers", "images", "embeds", "voice_minutes", "invites", "special_xp")
	
	# Dicts and lists to match json object keys to json object values and emoji ranks, as well as calculate max_values
	amounts = {}
	max_values = {}
	ranks = {"MR_D": 0.00, "MR_C": 0.16, "MR_B": 0.33, "MR_A": 0.50, "MR_S": 0.66, "MR_SS": 0.82, "MR_MAX": 1.00}
	embed_emj = "MR_D"
	emoji_object = []

	#* Match keys in "types" to keys in Users.json and calculate the max_value using itemgetter
	# Append all to respective dicts (amounts, max_values)
	for key in types:
		amounts[key] = user[key]

		max_value = max(data["users"], key=itemgetter(key))
		max_values[key] = max_value[key]

	#* Calculate what emoji to be used for the respective amount based on the max_value
	# ie. User has 6 messages, max messages in the server is 60, 6/60 = 10% = D Rank Emoji
	# Append each emoji for each activity in a list
	for (k,amt), (k2, mx) in zip(amounts.items(), max_values.items()):
		try:
			ratio = amt / mx
		except ZeroDivisionError:
			ratio = 0.00

		for (emj, k3) in ranks.items():
			if ratio < k3:
				continue
			else:
				embed_emj = emj
		emoji_object.append(embed_emj)

	#* Embed field to be used in "/myrank"
	field_display = f"> emoji1 **💬 Messages**: {amounts['messages']}\n> emoji2 **😃 Reactions Added**: {amounts['reactions_added']}\n> emoji3 **🥰 Reactions Recieved**: {amounts['reactions_recieved']}\n> emoji4 **🎭 Stickers**: {amounts['stickers']}\n> emoji5 **🖼️ Images**: {amounts['images']}\n> emoji6 **🔗 Embeds**: {amounts['embeds']}\n> emoji7 **🎙️ Voice (minutes)**: {amounts['voice_minutes']}\n> emoji8 **✉️ Invites**: {amounts['invites']}\n> emoji9 **🌟 Special XP**: {amounts['special_xp']}"
	
	#* return embed field, emoji list for embed field, and other values for current user
	# if simple explained in arguments
	if simple == True:
		return emoji_object
	else:
		return field_display, emoji_object, xp, level, level_xp, progress_to_next, role_title, role_id