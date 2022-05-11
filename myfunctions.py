import json
import threading

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