from audioop import mul
import json
import os
import sys
import discord
import random
import aiofiles
import asyncio

from collections import OrderedDict
from operator import itemgetter

# Restart Monke Rank
# TODO: Link this to a discord command
def restart_bot():
	print("Restarting")
	os.execv(sys.executable, ['python3'] + sys.argv)

#? File writing commands
# All file writing is done with these commands
# The module "aiofiles" is used
# This helps keep track of file I/O (which doesn't natively support asyncio)
#? ARGUMENTS (for all file writing commands
# filename : Path to file name to perform func. on
# name : New file name to create
# new_data : Data variable of updated loaded json content to append to [filename] json
# text : text from a text document

# Create a new file (usually json)
async def new_file(filename):
	async with aiofiles.open(filename, "w"):
		pass

# Write to a txt file
async def txt_write(filename, text):
	async with aiofiles.open(filename, "w") as f:
		await f.write(str(text))

# Read a txt file
async def txt_read(filename):
	async with aiofiles.open(filename, "r") as f:
		data = json.loads(await f.read())
	return data

# Create a new json objects with 1 array
async def new_json_objects(filename, name):
	new_template = {name:[]}
	async with aiofiles.open(filename, "w") as f:
		await f.write(json.dumps(new_template, indent=2))

# Read the data from a json file
async def json_read(filename):
	async with aiofiles.open(filename, mode="r") as f:
		data = json.loads(await f.read())
	return data

# Dump data into the json
async def json_dump (filename, data):
	async with aiofiles.open(filename, "w") as f:
		await f.write(json.dumps(data, indent=2))

# Used to append new users into the users.json file
async def write_json(new_data, filename, name: str):
	async with aiofiles.open(filename, "r+") as f:
		file_data = json.loads(await f.read())
		file_data[name].append(new_data)
		await f.seek(0)
		await f.write(json.dumps(file_data, indent=2))

#? Main commands

# Used to update the levels, ranks, and roles of users after an xp change
#? ARGUMENTS
# guild_name: guild name retrieved from discord api command
# json_object_name: Name of the json user objects to change (ex. reading from users.json as data, user = data["users"], this arg is user)
async def update_levels(guild_name, json_object_name : str):
	#* Get levels.json data
	data_level = await json_read(f"Data/{guild_name} Levels.json")

	#* Variables we need from levels.json
	current_level = json_object_name["level"]
	current_xp = json_object_name["xp"]
	next_xp = data_level["levels"][current_level]["total_xp"]
	current_role = data_level["levels"][current_level]["role_title"]
	new_role = data_level["levels"][current_level]["role_title"]
	old_role_id = data_level["levels"][current_level]["role_id"]
	new_role_id = data_level["levels"][current_level]["role_id"]

	#* Use while loop to level up multiple times in case of large increase
	while next_xp <= current_xp:
		json_object_name["level"] += 1
		current_level = json_object_name["level"]
		current_xp = json_object_name["xp"]
		next_xp = data_level["levels"][current_level]["total_xp"]
		new_role = data_level["levels"][current_level]["role_title"]
		new_role_id = data_level["levels"][current_level]["role_id"]

	#* Update roles by detecting a rank change
	# TODO: Figure out how to connect this to the on_message event and create an embed
	role_changed = False
	if current_role != new_role:
		print(f"User went from {current_role} to {new_role}! Old role ID: {old_role_id} New rold ID: {new_role_id}")
		role_changed = True

	return role_changed, new_role, old_role_id, new_role_id

# Updates the user objects for the specified user in users.json file and writes new ones if not found
#? ARGUMENTS
# guild_name: guild name retrieved from discord api command
# main_id: user id retrieved from discord api command
# main_user: user name retrieved from discord api command
# key: The key to modify in the user json object
# dump_file:
# 	True: Dump the current changes into X Users.json
# 	False: Return data of json file and the current user object being modified as variables
# amount_to_add: Amount of value to add to the specified key in the user object
# amount_of_xp: Amount of value to add to the xp in the user object, which can be...
# act_mult: ...multiplied by this value (useful for adding correct xp for >1 key value)
# boost_mult: ...multiplied again by this value (for xp boosts)
# premium: A boolean, used in on_member_update to know if a user is boosting the server or not (optional)
async def update_user(guild_name, main_id, main_user, key : str, dump_file: bool, amount_to_add: int, amount_of_xp: int, act_mult: int, boost_mult: int, premium=None):
	template = {
		"user_id": main_id,
		"name": main_user,
		"xp": 0,
		"level": 0,
		"role_id": 0,
		"messages": 0,
		"reactions_added": 0,
		"reactions_recieved": 0,
		"stickers": 0,
		"images": 0,
		"embeds": 0,
		"voice_minutes": 0,
		"invites": 0,
		"special_xp": 0,
		"is_booster": False
		}
	main_json = f"Data/{guild_name} Users.json"

	#* Check if missing or empty, if so, create new file and/or run new_json
	try:
		if os.stat(main_json).st_size == 0:
			await new_json_objects(main_json, "users")
	except FileNotFoundError:
		await new_file(main_json)
		if os.stat(main_json).st_size == 0:
			await new_json_objects(main_json, "users")

	#* Load initial users.json
	data = await json_read(main_json)

	#* Get a list of all user ids
	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])

	#* Check if user not in users.json using user_id list, append new user if not
	# Index the user id list, find the current user for use in updating
	# If the id is not in the list, make a new json object with empty values, then return this instead
	if main_id not in user_ids:
		new_user = template
		await write_json(new_user, main_json, "users")
		user_ids.append(new_user["user_id"])
		user_id_index = user_ids.index(main_id)
		# Load the appended json, then find the user id with the index
		data = await json_read(main_json)
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

	#* Add amount_of_xp to the sepcified key in the user object
	#? Ranks are updated in main.py with rank_check
	user["xp"] += amount_of_xp * act_mult * boost_mult

	#* Using the dump_file boolean argument, should the current file be overwritten after completion?
	# Return role changes and updates if True as well for embed to be sent if changed
	# If not, return json data, and user object to continue operation
	if dump_file == True:
		await json_dump(main_json, data)
		return
	else:
		return data, user

# Similar to new_levels
# Using the same level_factor and total_levels args, makes a dict of level barriers for each rank
# Useful for knowing XP needed to next rank
#? ARGUMENTS
# guild_name: Guild that these levels are for
# starting_xp: What should the XP be to reach level 1?
# level_factor: How much XP should each level increase by?
# total_levels: How many levels should there be?
# rl (kwargs): What should the levels be called and what should the minimum for each level be? Ex. Newbie=0, Bronze=3, etc.
async def level_barriers(guild_name, starting_xp: int, level_factor: int, total_levels: int, make_json: bool, rl: dict):
	#* Use the following json files
	main_json = f"Data/{guild_name} Levels.json"
	rb_json = f"Data/{guild_name} Role Barriers.json"
	rid_json = f"Data/{guild_name} Role IDs.json"

	# If it exists, add role_ids to the level objects (else it's 0)
	role_id = 0
	try:
		rid_data = await json_read(rid_json)
		for role in rid_data["role_ids"]:
			if role["role_name"] == rl[0][0]:
				role_id = role["role_id"]
	except FileNotFoundError:
		role_id = 0

	# Create variables for i (to iterate), role_barriers, and a new_data template for starting level
	i = 0
	role_barriers = {}
	new_data = {
		"level": 0,
		"level_xp": starting_xp,
		"total_xp": starting_xp,
		"role_id": role_id,
		"role_title": rl[0][0]
		}

	# Create a role_barriers dict, used to know the max XP for each role (rank check embeds)
	for level in rl:
		role_barriers[level[0]] = 0

	# Create a new_data object for each level from level 1 - [total_levels] (already have level 0 as new_data)
	while i < total_levels:
		# n: Current level
		n = i + 1
		# Variables for XP calc (next level, previous level xp, current level xp, total xp to get to current level)
		n_level = new_data["level"] + 1
		p_level_xp = new_data["level_xp"]
		level_xp = p_level_xp + level_factor
		total_xp = new_data["total_xp"] + level_xp

		# Get current level based on diff in levels given in rl kwargs
		cur_level = [(role_name, lvl_min) for role_name, lvl_min in rl[::-1] if n >= lvl_min]
		cur_level = cur_level[0][0]

		# Get role_id for current level
		try:
			for role in rid_data["role_ids"]:
				if role["role_name"] == cur_level:
					role_id = role["role_id"]
		except FileNotFoundError:
			role_id = 0

		# Update the role_barrier as the current total_xp for the level
		role_barriers[cur_level] = total_xp

		new_data = {
			"level": n_level,
			"level_xp": level_xp,
			"total_xp": total_xp,
			"role_id": role_id,
			"role_title": cur_level
			}


		if make_json == True:
			await write_json(new_data, main_json, "levels")
		i += 1

	await json_dump(rb_json, role_barriers)

	return role_barriers, rl

# Create new levels with "level, xp and role_id" as the objects in a levels.json file
# For use in knowing the current levels and where each user's level currently stands
#? ARGUMENTS
# guild_name: Guild that these levels are for
# starting_xp: What should the XP be to reach level 1?
# level_factor: How much XP should each level increase by?
# total_levels: How many levels should there be?
# disc_cmd: If not None, return role_barriers and rl for use in discord commands
# rl (kwargs): What should the levels be called and what should the minimum for each level be? Ex. Newbie=0, Bronze=3, etc.
async def new_levels(guild_name, starting_xp: int, level_factor: int, total_levels: int, disc_cmd=None, **rl):
	main_json = f"Data/{guild_name} Levels.json"
	rid_json = f"Data/{guild_name} Role IDs.json"
	rl = OrderedDict(rl)
	rl = list(rl.items())

	# If it exists, add role_id to level 0 level object, else its 0
	role_id = 0
	try:
		rid_data = await json_read(rid_json)
		for role in rid_data["role_ids"]:
			if role["role_name"] == rl[0][0]:
				role_id = role["role_id"]
				print(role_id)
				print(rl[0][0])
	except FileNotFoundError:
		role_id = 0

	# Create a new levels template (array and object) and make a new levels.json if it doesnt exist
	i = 0
	new_data = {
		"level": 0,
		"level_xp": starting_xp,
		"total_xp": starting_xp,
		"role_id": role_id,
		"role_title": rl[0][0]
		}
	level_template = {
		"levels": []
		}

	# If the levels.json already exists, remove it to redo all calculations.
	if os.path.exists(main_json):
		os.remove(main_json)
	await new_file(main_json)
	await json_dump(main_json, level_template)
	await write_json(new_data, main_json, "levels")

	# level_barriers: Creates all the new level objects
	role_barriers, rl = await level_barriers(guild_name, starting_xp, level_factor, total_levels, True, rl)

	if disc_cmd is not None:
		return role_barriers, rl

# Update roles inside the *role IDs.json file (used by /role_level)
#? ARGUMENTS
# guild_name: Guild that these ids are for
# level_name: Name of the level to change (from /role_level)
# role_id: Role ID to change it to (from /role_level)
async def update_roles(guild_name, level_name, role_id):
	rid_json = f"Data/{guild_name} Role IDs.json"
	rid_template = {
		"role_ids": []
		}
	template = {
		"role_name": level_name,
		"role_id": role_id
	}

	try:
		data = await json_read(rid_json)
		# Read, then write, which might give repeat objects
		data = data["role_ids"]
		await write_json(template, rid_json, "role_ids")
		# Read again, this time with the repeat objects
		data = await json_read(rid_json)
		data = data["role_ids"]
		# Filter out these unique objects with dict comprehension
		unique = {each["role_name"] : each for each in data}
		unique = list(unique.values())
		# Write only the unique roles and role IDs to the JSON
		template = {"role_ids": unique}
		await json_dump(rid_json, template)
	except FileNotFoundError:
		# If file hasn't been made, just makes a new one with a role object
		await new_file(rid_json)
		await json_dump(rid_json, rid_template)
		data = await json_read(rid_json)
		data = data["role_ids"]
		await write_json(template, rid_json, "role_ids")

# Update/make the Ignored Channels json
#? ARGUMENTS
# guild_name: Guild name that these channels are for
# guild_id: Guild id that these channels are for
# channel: Channel ID of the channel to add (18 character int)
async def update_channel_ignore(guild_name, guild_id, channel):
	ch_json = f"Data/{guild_name} Ignored Channels.json"
	ch_template = {
		"channels": []
		}
	template = {
		"channel": channel
	}

	try:
		data = await json_read(ch_json)
		# Read, then write, which might give repeat objects
		data = data["channels"]
		await write_json(template, ch_json, "channels")
		# Read again, this time with the repeat objects
		data = await json_read(ch_json)
		data = data["channels"]
		# Filter out these unique objects with dict comprehension
		unique = {each["channel"] : each for each in data}
		unique = list(unique.values())
		# Write only the unique channel ids to the JSON
		template = {"channels": unique}
		await json_dump(ch_json, template)
	except FileNotFoundError:
		# If file hasn't been made, just makes a new one with a channel object
		await new_file(ch_json)
		await json_dump(ch_json, ch_template)
		data = await json_read(ch_json)
		data = data["channels"]
		await write_json(template, ch_json, "channels")

# Checks the Ignored Channels.json for ignored channels and returns True if ignored
#? ARGUMENTS
# guild_name: Guild that these channels are for
# guild_channel_id: Channel ID to be checked
async def check_channel(guild_name, guild_channel_id):
	ch_json = f"Data/{guild_name} Ignored Channels.json"
	data = await json_read(ch_json)
	data = data["channels"]
	channel_check = False
	for channel in data:
		if channel["channel"] == guild_channel_id:
			channel_check = True
	return channel_check

# Updates/make XP Boost.json
#? ARGUMENTS
# guild_name: Guild that the boost is for
# is_active: Bool, set to True to start a new event, False to end an event
# multiplier: Int, How much should XP be multiplied by?
async def update_xp_boost(guild_name, is_active, multiplier, no_xp=False):
	xp_json = f"Data/{guild_name} XP Boost.json"
	xp_template = {"xp_boost" : [{
		"is_active": is_active,
		"multiplier": multiplier,
		"no_xp": no_xp
	}]}
	try:
		await json_read(xp_json)
		# Read, then write
		await json_dump(xp_json, xp_template)
		print(f"XP Boost file updated with is_active set to {is_active}, multiplier set to {multiplier} and no_xp set to {no_xp}")
	except FileNotFoundError:
		# If file hasn't been made, just makes a new one with a xp_boost object
		await new_file(xp_json)
		await json_dump(xp_json, xp_template)
		print(f"New XP Boost file created")

# Checks the XP Boost.json for an active XP boost event, returns a mult of 1 if False or the current mult if True
#? ARGUMENTS
# guild_name: Guild that the boost is for
async def check_xp_boost(guild_name):
	xp_json = f"Data/{guild_name} XP Boost.json"
	xp_data = await json_read(xp_json)

	no_xp = xp_data["xp_boost"][0]["no_xp"]

	xp_obj = xp_data["xp_boost"]
	xp_boost_mult = 1
	if xp_obj[0]["is_active"] == True:
		xp_boost_mult = xp_obj[0]["multiplier"]

	print(f"XP Boost: {xp_boost_mult} multiplier with No XP being set to {no_xp}")

	return xp_boost_mult, no_xp

# Creates a simple embed for the most general of embed implementations (help, about, etc.)
#? ARGUMENTS
# command (string): What command from the bot it should be used on
# description (default=None, string): Set the description of the embed, optional
async def templateEmbed(command : str, description=None):
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
# guild_name: guild name retrieved from discord api command
# main_id: user id retrieved from discord api command
# simple (boolean): If True, returns only the emoji list (useful for using in main.py and other cases where not everything needs to be returned)
async def my_rank_embed_values(guild_name, main_id, simple : bool):
	#* Load initial json, find user who sent command
	main_json = f"Data/{guild_name} Users.json"
	levels_json = f"Data/{guild_name} Levels.json"
	data = await json_read(main_json)

	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])

	user_id_index = user_ids.index(main_id)
	user = data["users"][user_id_index]

	#* Find current level in levels.json
	level = user["level"]
	xp = user["xp"]

	data_level = await json_read(levels_json)
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
	types = (
		"messages",
		"reactions_added",
		"reactions_recieved",
		"stickers",
		"images",
		"embeds",
		"voice_minutes",
		"invites",
		"special_xp"
		)

	# Dicts and lists to match json object keys to json object values and emoji ranks, as well as calculate max_values
	amounts = {}
	max_values = {}
	ranks = {"MR_D": 0.00, "MR_C": 0.02, "MR_B": 0.05, "MR_A": 0.20, "MR_S": 0.50, "MR_SS": 0.75, "MR_MAX": 1.00}
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
	field_display = f"> emoji1 **💬 Messages**: {amounts['messages']}\n> emoji2 **😃 Reactions Added**: {amounts['reactions_added']}\n> emoji3 **🥰 Reactions Earned**: {amounts['reactions_recieved']}\n> emoji4 **🎭 Stickers**: {amounts['stickers']}\n> emoji5 **🖼️ Images**: {amounts['images']}\n> emoji6 **🔗 Embeds**: {amounts['embeds']}\n> emoji7 **🎙️ Voice (minutes)**: {amounts['voice_minutes']}\n> emoji8 **✉️ Invites**: {amounts['invites']}\n> emoji9 **🌟 Special XP**: {amounts['special_xp']}"

	#* return embed field, emoji list for embed field, and other values for current user
	# if simple explained in arguments
	if simple == True:
		return emoji_object
	else:
		return field_display, emoji_object, xp, level, level_xp, progress_to_next, role_title, role_id

async def compare_rank_embed_values(guild_name, main_id, right_or_left=False, bot_object=None, simple=None):
	#* Load initial json, find user who sent command
	main_json = f"Data/{guild_name} Users.json"
	levels_json = f"Data/{guild_name} Levels.json"
	data = await json_read(main_json)

	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])

	user_id_index = user_ids.index(main_id)
	user = data["users"][user_id_index]

	#* Find current level in levels.json
	level = user["level"]
	xp = user["xp"]

	data_level = await json_read(levels_json)
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
	types = (
		"messages",
		"reactions_added",
		"reactions_recieved",
		"stickers",
		"images",
		"embeds",
		"voice_minutes",
		"invites",
		"special_xp"
		)

	# Dicts and lists to match json object keys to json object values and emoji ranks, as well as calculate max_values
	amounts = {}
	max_values = {}
	ranks = {"MR_D": 0.00, "MR_C": 0.02, "MR_B": 0.05, "MR_A": 0.20, "MR_S": 0.50, "MR_SS": 0.75, "MR_MAX": 1.00}
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
		emoji = lambda item : discord.utils.get(bot_object.emojis, name=item)
		in_embed = list(map(emoji, emoji_object))

	#* Embed fields to be used in "/myrank"
	fields = []
	i = 0
	for act in types:
		if right_or_left == False:
			field = f"{in_embed[i]} {amounts[act]}"
			fields.append(field)
			i += 1
		elif right_or_left == True:
			field = f"{amounts[act]} {in_embed[i]}"
			fields.append(field)
			i += 1

	#* return embed field, emoji list for embed field, and other values for current user
	# if simple explained in arguments
	if simple is not None:
		return emoji_object, in_embed
	else:
		return fields, xp, level, role_title


# Update the xp values of boosted members in the server
#? ARGUMENTS
# guild_name: guild name retrieved from discord api command
# xp: Amount of xp retrieved from discord slash command argument
async def update_boosters(guild_name, xp):
	#* Load initial jsons (User, levels)
	count = 0
	main_json = f"Data/{guild_name} Users.json"
	data = await json_read(main_json)

	rc_dict = {}
	nr_list = []

	for item in data["users"]:
		if item["is_booster"] == True:
			#* Add xp specified, increase levels, and increase count
			item["special_xp"] += xp
			item["xp"] += xp
			count += 1
			role_changed, new_role, old_role_id, new_role_id = await update_levels(guild_name, item)
			#* Update Users.json and append values to list
			rc_dict[item["user_id"]] = role_changed
			nr_list.append(new_role)
			await asyncio.sleep(0.2)
			await json_dump(main_json, data)

	#* Return count and lists
	return count, rc_dict, nr_list

# Connected to update_levels
# Adds ability to connect the updated levels/ranks to discord api
#? ARGUMENTS
# guild_name: guild name retrieved from discord api command
# main_id: user id retrieved from discord api command
async def rank_check(guild_name, main_id):
	#* Load some jsons
	main_json = f"Data/{guild_name} Users.json"
	data = await json_read(main_json)

	#* Get a list of all user ids
	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])

	try:
		user_id_index = user_ids.index(main_id)
		user = data["users"][user_id_index]
		#* Return the changed role and new role from update_levels and dump
		role_changed, new_role, old_role_id, new_role_id = await update_levels(guild_name, user)
		await json_dump(main_json, data)
	except ValueError:
		role_changed = False
		new_role = "Newbie"

	return role_changed, new_role, old_role_id, new_role_id

# Sort the server leaderboard based on [activity] of each user
#? ARGUMENTS
# guild_name: guild name retrieved from discord api command
# activity: The current activity (messages, voice, embeds, etc.) gotten from /leaderboard. Default is "Everything"
async def sort_leaderboard(guild_name, activity):
	#* Load initial users.json
	main_json = f"Data/{guild_name} Users.json"
	data = await json_read(main_json)

	#* Create a list of tuples where each tuple is a user and the list contains all users
	i_users = []
	for user in data["users"]:
		i_tuple = (
			user["user_id"],
			user["name"],
			user["xp"],
			user["level"],
			user["messages"],
			user["reactions_added"],
			user["reactions_recieved"],
			user["stickers"],
			user["images"],
			user["embeds"],
			user["voice_minutes"],
			user["invites"],
			user["special_xp"],
			user["is_booster"])
		i_users.append(i_tuple)

	#* Bubble sort the users by activity
	# TODO: Please code this better aaaaaa
	length = len(i_users)
	# How many users have already been sorted
	for user in range(0, length):
		# For every user not sorted yet, compare with next user in list
		for n_user in range(0, length-user-1):
			if activity == "Everything":
				# If next user in list has less XP, then flip the two user positions
				if i_users[n_user][2] < i_users[n_user + 1][2]:
					temp = i_users[n_user]
					i_users[n_user] = i_users[n_user + 1]
					i_users[n_user + 1] = temp
			elif activity == "messages":
				if i_users[n_user][4] < i_users[n_user + 1][4]:
					temp = i_users[n_user]
					i_users[n_user] = i_users[n_user + 1]
					i_users[n_user + 1] = temp
			elif activity == "reactions_added":
				if i_users[n_user][5] < i_users[n_user + 1][5]:
					temp = i_users[n_user]
					i_users[n_user] = i_users[n_user + 1]
					i_users[n_user + 1] = temp
			elif activity == "reactions_recieved":
				if i_users[n_user][6] < i_users[n_user + 1][6]:
					temp = i_users[n_user]
					i_users[n_user] = i_users[n_user + 1]
					i_users[n_user + 1] = temp
			elif activity == "stickers":
				if i_users[n_user][7] < i_users[n_user + 1][7]:
					temp = i_users[n_user]
					i_users[n_user] = i_users[n_user + 1]
					i_users[n_user + 1] = temp
			elif activity == "images":
				if i_users[n_user][8] < i_users[n_user + 1][8]:
					temp = i_users[n_user]
					i_users[n_user] = i_users[n_user + 1]
					i_users[n_user + 1] = temp
			elif activity == "embeds":
				if i_users[n_user][9] < i_users[n_user + 1][9]:
					temp = i_users[n_user]
					i_users[n_user] = i_users[n_user + 1]
					i_users[n_user + 1] = temp
			elif activity == "voice_minutes":
				if i_users[n_user][10] < i_users[n_user + 1][10]:
					temp = i_users[n_user]
					i_users[n_user] = i_users[n_user + 1]
					i_users[n_user + 1] = temp
			elif activity == "invites":
				if i_users[n_user][11] < i_users[n_user + 1][11]:
					temp = i_users[n_user]
					i_users[n_user] = i_users[n_user + 1]
					i_users[n_user + 1] = temp
			elif activity == "special_xp":
				if i_users[n_user][12] < i_users[n_user + 1][12]:
					temp = i_users[n_user]
					i_users[n_user] = i_users[n_user + 1]
					i_users[n_user + 1] = temp

	#* Return sorted list of tuples to be used in leaderboard embed
	return i_users, length

# Activity values to be used inside the "/leaderboard" command embed
# Values also have a specific rank emoji assigned to them based on the max value of [activity] in the server used
# The command returns everything needed to be used in the "embeds.py" file (fields, calc. values, etc.)
#? ARGUMENTS
# guild_name: guild name retrieved from discord api command
# main_id: user id retrieved from discord api command
# activity: The current activity (messages, voice, embeds, etc.) gotten from /leaderboard. Default is "Everything"
# simple (boolean): If True, returns only the emoji list (useful for using in main.py and other cases where not everything needs to be returned)
async def leaderboard_embed_values(guild_name, main_id, activity, simple: bool):
	#* Load initial jsons
	main_json = f"Data/{guild_name} Users.json"
	level_json = f"Data/{guild_name} Levels.json"
	rb_json = f"Data/{guild_name} Role Barriers.json"
	data = await json_read(main_json)

	#* Find current user in users.json
	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])

	user_id_index = user_ids.index(main_id)
	user = data["users"][user_id_index]

	#* Find current level in levels.json
	level = user["level"]
	xp = user["xp"]

	data_level = await json_read(level_json)
	data_level = data_level["levels"][level]

	#* Find current role from role barriers.json
	data_rb = await json_read(rb_json)
	data_rb = OrderedDict(data_rb)

	for role, exp in data_rb.items():
		if xp < exp:
			rb_role = role
		else:
			rb_role = role[-1]

	#* A metric ton of variables for appending as a field in embed
	# Users.json values
	xp = user["xp"]
	level = user["level"]
	messages = user["messages"]
	voice_minutes = user["voice_minutes"]
	invites = user["invites"]
	special_xp = user["special_xp"]

	try:
		act = user[activity]
	except:
		pass

	role_title = data_level["role_title"]

	# Users.json values to be used in the embed field
	types = (
		"xp",
		"messages",
		"reactions_added",
		"reactions_recieved",
		"stickers",
		"images",
		"embeds",
		"voice_minutes",
		"invites",
		"special_xp"
		)

	# Dicts and lists to match json object keys to json object values and emoji ranks, as well as calculate max_values
	amounts = {}
	max_values = {}
	ranks = {"MR_D": 0.00, "MR_C": 0.02, "MR_B": 0.05, "MR_A": 0.20, "MR_S": 0.50, "MR_SS": 0.75, "MR_MAX": 1.00}
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

	#* Embed field to be used in "/leaderboard"
	# TODO: Code this better at some point
	if activity == "Everything":
		field_display = f"> emoji1 **{xp} XP** : 💬 {messages} | 🎙️ {voice_minutes} | ✉️ {invites} | 🌟 {special_xp}"
	elif activity == "messages":
		field_display = f"> emoji2 💬 {act}"
	elif activity == "reactions_added":
		field_display = f"> emoji3 😃 {act}"
	elif activity == "reactions_recieved":
		field_display = f"> emoji4 🥰 {act}"
	elif activity == "stickers":
		field_display = f"> emoji5 🎭 {act}"
	elif activity == "images":
		field_display = f"> emoji6 🖼️ {act}"
	elif activity == "embeds":
		field_display = f"> emoji7 🔗 {act}"
	elif activity == "voice_minutes":
		field_display = f"> emoji8 🎙️ {act}"
	elif activity == "invites":
		field_display = f"> emoji9 ✉️ {act}"
	elif activity == "special_xp":
		field_display = f"> emoji10 🌟 {act}"

	#* return embed field, emoji list for embed field, and other values for current user
	if simple == True:
		return emoji_object
	else:
		return field_display, emoji_object, role_title
