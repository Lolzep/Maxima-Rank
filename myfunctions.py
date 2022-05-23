import json
import os
import sys
import discord

from operator import itemgetter

#? ARGUMENTS (for json defs)
# filename : Path to file name to perform func. on
# name : New file name to create
# new_data : Data variable of updated loaded json content to append to [filename] json

# Restart Monke Rank
def restart_bot():
	print("Restarting")
	os.execv(sys.executable, ['python3'] + sys.argv)

# Create a new json file
def new_json_file(filename):
	with open(filename, "w"):
		pass

# Create a new json objects with 2 arrays
def new_json_objects(filename, name1, name2):
	new_template = {name1:[], name2:[]}
	with open(filename, "w") as f:
		json.dump(new_template, f, indent=2)

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

# Used to update the levels, ranks, and roles  of users after an xp change
#? ARGUMENTS
# json_object_name: Name of the json user objects to change (ex. reading from users.json as data, user = data["users"], this arg is user)
# levels_json_data: The variable name of the loaded json data of "levels.json", by default this is none
# 	In loops, use this argument to avoid so many i/o operations
def update_levels(json_object_name : str, levels_json_data=None):
	#* Get levels.json data
	data_level = levels_json_data
	if levels_json_data is None:
		data_level = json_read("levels.json")

	#* Variables we need from levels.json
	current_level = json_object_name["level"]
	current_xp = json_object_name["xp"]
	next_xp = data_level["levels"][current_level]["total_xp"]

	current_role = data_level["levels"][current_level]["role_title"]
	new_role = data_level["levels"][current_level]["role_title"]

	#* Use while loop to level up multiple times in case of large increase
	while next_xp <= current_xp:
		json_object_name["level"] += 1
		current_level = json_object_name["level"]
		current_xp = json_object_name["xp"]
		next_xp = data_level["levels"][current_level]["total_xp"]
		new_role = data_level["levels"][current_level]["role_title"]
	
	#* Update roles by detecting a rank change
	# TODO: Figure out how to connect this to the on_message event and create an embed
	role_changed = False
	if current_role != new_role:
		print(f"User went from {current_role} to {new_role}!")
		role_changed = True
	
	return role_changed, current_role, new_role

# Updates the user objects for the specified user in users.json file and writes new ones if not found
#? ARGUMENTS
# guild_id: guild id retrieved from discord api command
# main_id: user id retrieved from discord api command
# main_user: user name retrieved from discord api command
# key: The key to modify in the user json object
# dump_file:
# 	True: Dump the current changes into X Users.json
# 	False: Return data of json file and the current user object being modified as variables
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
			new_json_objects(main_json, "users", "role_ids")
	except FileNotFoundError:
		new_json_file(main_json)
		if os.stat(main_json).st_size == 0:
			new_json_objects(main_json, "users", "role_ids")

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

	#* Add amount_to_add to the specified key in the user object
	# If premium is not None, do not add, change the boolean to premium argument
	if premium is None:
		user[key] += amount_to_add
	else:
		user[key] = premium

	#* XP Block
	# Based on amount_of_xp given
	# Add xp to the specified user
	user["xp"] += amount_of_xp * multiplier
	role_changed, current_role, new_role = update_levels(user)

	#* Using the dump_file boolean argument, should the current file be overwritten after completion?
	# Return role changes and updates if True as well for embed to be sent if changed
	# If not, return json data, and user object to continue operation
	if dump_file == True:
		with open(main_json, "w") as f:
			json.dump(data, f, indent=2)
		return role_changed, current_role, new_role
	else:
		return data, user;

# Similar to new_levels
# Using the same level_factor and total_levels args, makes a dict of level barriers for each rank
# Useful for knowing XP needed to next rank
#? ARGUMENTS
# starting_xp: What should the XP be to reach level 1?
# level_factor: How much XP should each level increase by?
# total_levels: How many levels should there be?
def level_barriers(starting_xp: int, level_factor: int, total_levels: int, make_json: bool):
	#* Create new levels key and a level object template starting at 0 for all
	i = 0
	new_data = {"level": 0, "level_xp": starting_xp, "total_xp": starting_xp, "role_id": 0, "role_title": "Newbie"}

	role_barriers = {"Newbie": 0, "Bronze": 0, "Silver": 0, "Gold": 0, "Platinum": 0, "Diamond": 0, "Master": 0, "Grandmaster": 0, "Exalted": 0}

	#* For all levels 1 - i, update the key:value pairs until max is reached then move to next pair
	# TODO: Implement this in a better way that makes it easier to update
	while i < total_levels:
		next_id = new_data["role_id"]
		n_level = new_data["level"] + 1
		p_level_xp = new_data["level_xp"]
		level_xp = p_level_xp + level_factor
		total_xp = new_data["total_xp"] + level_xp

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
		
		role_barriers[role_title] = total_xp

		new_data = {"level": n_level, "level_xp": level_xp, "total_xp": total_xp, "role_id": next_id, "role_title": role_title}

		if make_json == True:
			write_json(new_data, "levels.json", "levels")
		i += 1

	return role_barriers

# Create new levels with "level, xp and role_id" as the objects in a levels.json file
# For use in knowing the current levels and where each user's level currently stands
#? ARGUMENTS
# starting_xp: What should the XP be to reach level 1?
# level_factor: How much XP should each level increase by?
# total_levels: How many levels should there be?
# TODO: roleid should be changed to actual roleids in Discord (probably need new definition)
def new_levels(starting_xp: int, level_factor: int, total_levels: int):
	# Create new levels key and a level object template starting at 0 for all
	i = 0
	new_data = {"level": 0, "level_xp": starting_xp, "total_xp": starting_xp, "role_id": 0, "role_title": "Newbie"}
	level_template = {"levels": []}
	role_barriers = level_barriers(100, 20, 300, True)
	role_title = ""

	# If the levels.json already exists, remove it to redo all calculations. Create new levels.json with level_template
	if os.path.exists("levels.json"):
		os.remove("levels.json")

	with open ("levels.json", "w") as f:
		json.dump(level_template, f, indent=2)

	write_json(new_data, "levels.json", "levels")

	# While i <= total_levels, create a new level object for each level 0 - i and calculate each variable as needed
	while i < total_levels:
		n_level = new_data["level"] + 1

		p_level_xp = new_data["level_xp"]
		level_xp = p_level_xp + level_factor

		total_xp = new_data["total_xp"] + level_xp

		next_id = new_data["role_id"]

		# Using level_barriers(), find the role title for the current level object
		for (title,xp) in role_barriers.items():
			if total_xp <= xp:
				role_title = title
				break
			else:
				continue

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

# Update the xp values of boosted members in the server
#? ARGUMENTS
# guild_id: guild id retrieved from discord api command
# xp: Amount of xp retrieved from discord slash command argument
def update_boosters(guild_id, xp):
	#* Load initial jsons (User, levels)
	count = 0
	main_json = f"Data/{guild_id} Users.json"
	with open(main_json) as f:
		data = json.load(f)
	data_level = json_read("levels.json")

	for item in data["users"]:
		if item["is_booster"] == True:
			#* Add xp specified, increase levels, and increase count
			item["special_xp"] += xp
			item["xp"] += xp
			count += 1
			update_levels(item, data_level)

	#* Update Users.json
	with open(main_json, "w") as f:
		json.dump(data, f, indent=2)
	

	return count

# Return a rank update embed to send if the check for a role change is true
#? ARGUMENTS
# guild_id: guild id retrieved from discord api command
# main_id: user id retrieved from discord api command
# main_user: user name retrieved from discord api command
# From update_levels()
# 	role_changed: If the role of the user changed when adding XP to the user, boolean
# 	current_role: Role before rank change
# 	new_role: Role after rank change
def rank_check(guild_id, main_id, main_user, avatar_id, role_changed, current_role, new_role):
	if role_changed is True:
		rcEmbed = discord.Embed(color = discord.Color.purple(), description=main_user)
		rcEmbed.set_author(name=f"{main_user} just advanced to {new_role} from {current_role}!")
	else:
		return