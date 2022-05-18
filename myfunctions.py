import json
import os
import sys
import discord

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
def update_user(guild_id, main_id, main_user, key : str, dump_file: bool, amount_to_add: int, amount_of_xp: int, multiplier: int):
	template = {"user_id": main_id, "name": main_user, "xp": 0, "level": 0, "role_id": 0, "messages": 0, "reactions_added": 0, "reactions_recieved": 0, "stickers": 0, "images": 0, "embeds": 0, "voice_minutes":0, "invites":0, "special_xp":0}
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

	user[key] += amount_to_add

	#* XP Block
	# Based on amount_of_xp given
	# Add xp to the specified user
	user["xp"] += amount_of_xp * multiplier

	# Update using the levels.json
	current_level = user["level"]
	current_xp = user["xp"]
	data_level = json_read("levels.json")
	next_xp = data_level["levels"][current_level]["total_xp"]
	if next_xp < current_xp:
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
def new_levels(level_factor: int):
	# Create new levels key and a level object template starting at 0 for all
	i = 0
	new_data = {"level": 0, "level_xp": 0, "total_xp": 0, "role_id": 0}
	level_factor = 20
	level_template = {"levels": []}

	# If the levels.json already exists, remove it to redo all calculations. Create new levels.json with level_template
	if os.path.exists("levels.json"):
		os.remove("levels.json")

	with open ("levels.json", "w") as f:
		json.dump(level_template, f, indent=2)

	# While i <= total_levels, create a new level object for each level 0 - i and calculate each variable as needed
	while i <= 301:
		# Create the variables
		p_level = new_data["level"]
		n_level = new_data["level"] + 1

		p_level_xp = new_data["level_xp"]
		level_xp = p_level_xp + (p_level * level_factor) + 100

		total_xp = new_data["total_xp"] + level_xp

		previous_roleid = new_data["role_id"]
		next_id = new_data["role_id"]

		# Create a new new_data object to then append and modify in the next loop
		new_data = {"level": n_level, "level_xp": level_xp, "total_xp": total_xp, "role_id": next_id}

		write_json(new_data, "levels.json", "levels")
		i += 1

def templateEmbed(command : str, description=None):
	tempEmbed = discord.Embed(color = discord.Color.purple())

	if description is not None:
		tempEmbed.set_author(name=description)
	else:
		pass

	tempFile = discord.File(f"Images/{command}.png", filename="image.png")
	tempEmbed.set_thumbnail(url="attachment://image.png")

	return tempEmbed, tempFile

def my_rank(guild_id, main_id, main_user):
	main_json = f"Data/{guild_id} Users.json"

	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])

	user_id_index = user_ids.index(main_id)

	with open(main_json) as f:
		data = json.load(f)
		user = data["users"][user_id_index]
	
	print(user)
