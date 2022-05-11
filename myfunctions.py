import json
import threading
import os

# Used to make sure that files are not open at multiple times
# "open" statements must wait until the current "open" statement is finished
# Must add "global file_lock" to all definitions that use an "open" statement
file_lock = threading.Lock()

# Dump the data into json while keeping the file_lock
def json_dump(data):
	global file_lock
	file_lock.acquire()
	with open("users.json", "w") as f:
		json.dump(data, f, indent=2)
	file_lock.release()	

# Used to append new users into the users.json file
def write_json(new_data, filename):
	global file_lock
	file_lock.acquire()
	with open(filename, "r+") as f:
		file_data = json.load(f)
		file_data["users"].append(new_data)
		f.seek(0)
		json.dump(file_data, f, indent=2)
	file_lock.release()

# Adds new users to the master json file
# Finds the current user in the json file from discord context (message, reactions, etc.)
# Returns data: New .json file with modifyed values or the .json values, user: the current user object in the json file by user_id
async def update_user(main_id, main_user, key : str, dump_file: bool):
	global file_lock
	template = {"user_id": main_id, "name": main_user, "xp": 0, "rank": 0, "messages": 0, "reactionsadded": 0, "reactionsrecieved": 0, "images": 0, "embeds": 0, "voice_call_hours":0, "invites":0, "special_xp":0}
	# Load initial json
	file_lock.acquire()
	with open("users.json") as f:
		data = json.load(f)
	file_lock.release()

	# Get a list of all user ids, if current user not found, create a new json object
	user_ids = []
	for items in data["users"]:
		user_ids.append(items["user_id"])

	# Index the user id list, find the current user for use in updating
	# If the id is not in the list, make a new json object with empty values, then return this instead
	if main_id not in user_ids:
		new_user = template
		write_json(new_user, "users.json")
		user_ids.append(new_user["user_id"])
		user_id_index = user_ids.index(main_id)
		# Load the appended json, then find the user id with the index
		file_lock.acquire()
		with open("users.json") as f:
			data = json.load(f)
			user = data["users"][user_id_index]
		file_lock.release()
	else:
		user_id_index = user_ids.index(main_id)
		user = data["users"][user_id_index]

	user[key] += 1

	if dump_file == True:
		file_lock.acquire()
		with open("users.json", "w") as f:
			json.dump(data, f, indent=2)
		file_lock.release()
	else:
		return data, user;

# Create new levels with "level, xp and role_id" as the objects in a levels.json file
# For use in knowing the current levels and where each user's level currently stands
# TODO: roleid should be changed to actual roleids in Discord (probably need new definition)
def new_levels(level_factor: int):
	# Create new levels key and a level object template starting at 0 for all
	i = 0
	new_data = {"level": 0, "xp": 0, "role_id": 0}
	level_template = {"levels": []}

	# If the levels.json already exists, remove it to redo all calculations. Create new levels.json with level_template
	if os.path.exists("levels.json"):
		os.remove("levels.json")
	with open ("levels.json", "w") as f:
		json.dump(level_template, f, indent=2)

	# While i <= total_levels, create a new level object for each level 0 - i and calculate each variable as needed
	while i <= 301:
		previous_level = new_data["level"]
		next_level = new_data["level"] + 1

		previous_xp = new_data["xp"]
		next_xp = previous_xp + (previous_level * level_factor) + 100

		previous_roleid = new_data["role_id"]
		next_id = new_data["role_id"]

		new_data = {"level": next_level, "xp": next_xp, "role_id": next_id}

		with open("levels.json", "r+") as f:
			file_data = json.load(f)
			file_data["levels"].append(new_data)
			f.seek(0)
			json.dump(file_data, f, indent=2)
		i += 1