import discord
import os
import re
import random
import math
import aiofiles
import asyncio

from matplotlib import pyplot as plt
from skimage.transform import rescale
import numpy as np

from myfunctions import templateEmbed, my_rank_embed_values, compare_rank_embed_values, sort_leaderboard, json_read, leaderboard_embed_values

VERSION = os.popen('git rev-parse HEAD').read()
COMMIT_MESSAGE = os.popen('git show --pretty=format:%s -s HEAD').read()

class infoEmbeds:
	'''infoEmbeds contains all types of embeds that are sent
	by the bot and allows them to be easily called and sent
	in the main.py file while keeping them separate from the
	main.py file'''
	async def aboutEMBED():
		'''Used for the /about command'''
		#* Since simple embed, use templateEmbed
		aboutEMBED, aboutFILE = await templateEmbed("about")

		#* Embed fields
		aboutEMBED.add_field(
			name="Maxima Rank",
			value="An activity tracker for Discord for tracking messages, time in voice, etc. and using that for levels for rewarding the most active users in a Discord",
			inline=False
			)
		aboutEMBED.add_field(
			name="Commit",
			value=str(VERSION),
			inline=False
			)
		aboutEMBED.add_field(
			name="Recent Changes",
			value=COMMIT_MESSAGE,
			inline=False
			)
		aboutEMBED.add_field(
			name="Contributors",
			value="Lolzep #5723",
			inline=False
			)

		return aboutEMBED, aboutFILE

	async def helpEMBED():
		'''Used for the /help command'''
		#* Since simple embed, use templateEmbed
		helpEMBED, helpFILE = await templateEmbed("help", "Maxima Rank Help")

		#* Embed fields
		helpEMBED.add_field(
			name="/help",
			value="You are here! Commands for Maxima Rank",
			inline=False
			)
		helpEMBED.add_field(
			name="/about",
			value="Info about the bot",
			inline=False
			)
		helpEMBED.add_field(
			name="/my_rank",
			value="Statistics about yourself",
			inline=False
			)
		helpEMBED.add_field(
			name="/rank [username]",
			value="Statistics about a specified user",
			inline=False
			)
		helpEMBED.add_field(
			name="/leaderboard [activity] [page_length]",
			value="Activity leaderboard for the server based on [activity] (default is everything). Each page has [page_length] users.",
			inline=False
			)

		return helpEMBED, helpFILE

	async def adminhelpEMBED():
		'''Used for the /adminhelp command'''
		#* Since simple embed, use templateEmbed
		adminhelpEMBED, adminhelpFILE = await templateEmbed("help", "Maxima Rank Admin Help")

		#* Embed fields
		adminhelpEMBED.add_field(
			name="/adminhelp",
			value="You are here! Admin commands for Maxima Rank",
			inline=False
			)
		adminhelpEMBED.add_field(
			name="/award_xp [user] [amount]",
			value="Gives a specified [user] [amount] xp",
			inline=False
			)
		adminhelpEMBED.add_field(
			name="/role_xp [role] [xp]",
			value="Gives a specified [role] [amount] xp",
			inline=False
			)
		adminhelpEMBED.add_field(
			name="/act_xp [user] [activity] [act_count] [xp_per_act]",
			value="Gives [activity] ([xp_per_act] * [act_count]) XP to a [user]",
			inline=False
			)
		adminhelpEMBED.add_field(
			name="/xp_boost [multiplier] [time]",
			value="Start an XP boost event which multiplies all XP by [multiplier] for [time] minutes",
			inline=False
			)
		adminhelpEMBED.add_field(
			name="/xp_boost_end",
			value="End an XP boost event manually",
			inline=False
			)
		adminhelpEMBED.add_field(
			name="/make_levels [starting_xp] [level_factor] [total_levels]",
			value="Make new levels and level barriers based on [starting_xp] where each level is [starting_xp] * level * [level_factor] for [total_levels] levels",
			inline=False
			)
		adminhelpEMBED.add_field(
			name="/role_level [level_name] [role]",
			value="Link a [level_name] in the bot to a [role] in the server",
			inline=False
			)
		adminhelpEMBED.add_field(
			name="/import_channel",
			value="In the channel this command is used, import activity to Maxima Rank",
			inline=False
			)
		adminhelpEMBED.add_field(
			name="/ignore_channel [channel ID]",
			value="Ignore a channel in the server based on the ID given",
			inline=False
			)

		return adminhelpEMBED, adminhelpFILE

	async def myrankEMBED(guild_name, main_id, main_user, avatar_id, emoji : list):
		'''Used for the /myrank command'''
		#* Some extras here, need to get values of the user using a separate function (my_rank_embed_values)
		#* This function also returns the emoji ranks to be shown next to the values in emoji_object
		field_display, emoji_object, xp, level, level_xp, progress_to_next, role_title, role_id = await my_rank_embed_values(guild_name, main_id, False)
		role_barriers = await json_read(f"Data/{guild_name} Role Barriers.json")
		role_barriers = dict(role_barriers)
		myrankFILE = discord.File(
			f"Images/Ranks/{role_title}.png",
			filename="image.png"
			)

		#* Replaces "emojiX" string values in field_display with the actual emojis
		i = 1
		for item in emoji:
			subbed = re.sub(f"\\bemoji{i}\\b", str(item), field_display)
			field_display = subbed
			i += 1

		#* Used to show the % of XP to next level
		percent_xp = 100 * progress_to_next / level_xp
		percent_xp = "%.1f" % percent_xp

		#* Embed and embed fields
		# If role is max role (Konami), show easter egg text
		if role_title != "Konami":
			myrankEMBED = discord.Embed(
				title=f"You are {role_title} rank!",
				description=f"You are {role_barriers[role_title] - xp} XP away from being the next rank!",
				color=discord.Color.purple()
				)
		else:
			myrankEMBED = discord.Embed(
				title=f"You are {role_title} rank!",
				description=f"You are max rank! Now go outside.",
				color=discord.Color.purple()
				)
		myrankEMBED.set_author(
			name=main_user,
			icon_url="attachment://image.png"
			)
		myrankEMBED.set_thumbnail(
			url=avatar_id
			)

		#* Embed fields
		myrankEMBED.add_field(
			name="Level",
			value=f"{level}",
			inline=True
			)
		myrankEMBED.add_field(
			name="XP",
			value=f"{xp}",
			inline=True
			)
		myrankEMBED.add_field(
			name="XP Progress to Next Level",
			value=f"{progress_to_next} / {level_xp} ( {percent_xp}% )",
			inline=False
			)
		myrankEMBED.add_field(
			name="Server Activity",
			value=subbed,
			inline=True
			)

		return myrankEMBED, myrankFILE

	async def rankEMBED(guild_name, main_id, main_user, avatar_id, emoji : list):
		'''Used for the /rank command
		Very similar to myrankEMBED'''
		#* Some extras here, need to get values of the user using a separate function (my_rank_embed_values)
		#* This function also returns the emoji ranks to be shown next to the values in emoji_object
		field_display, emoji_object, xp, level, level_xp, progress_to_next, role_title, role_id = await my_rank_embed_values(guild_name, main_id, False)
		role_barriers = await json_read(f"Data/{guild_name} Role Barriers.json")
		role_barriers = dict(role_barriers)
		rankFILE = discord.File(
			f"Images/Ranks/{role_title}.png",
			filename="image.png"
			)
		
		#* Replaces "emojiX" string values in field_display with the actual emojis
		i = 1
		for item in emoji:
			subbed = re.sub(f"\\bemoji{i}\\b", str(item), field_display)
			field_display = subbed
			i += 1

		#* Used to show the % of XP to next level
		percent_xp = 100 * progress_to_next / level_xp
		percent_xp = "%.1f" % percent_xp

		#* Embed and embed fields
		# If role is max role (Konami), show easter egg text
		if role_title != "Konami":
			rankEMBED = discord.Embed(
				title=f"{main_user} is {role_title} rank!",
				description=f"{main_user} is {role_barriers[role_title] - xp} XP away from being the next rank!",
				color=discord.Color.purple()
				)
		else:
			rankEMBED = discord.Embed(
				title=f"{main_user} is {role_title} rank!",
				description=f"You are max rank! Now go outside.",
				color=discord.Color.purple()
				)
		rankEMBED.set_author(
			name=main_user,
			icon_url="attachment://image.png"
			)
		rankEMBED.set_thumbnail(
			url=avatar_id
			)

		#* Embed fields
		rankEMBED.add_field(
			name="Level",
			value=f"{level}",
			inline=True
			)
		rankEMBED.add_field(
			name="XP",
			value=f"{xp}",
			inline=True
			)
		rankEMBED.add_field(
			name="XP Progress to Next Level",
			value=f"{progress_to_next} / {level_xp} ( {percent_xp}% )",
			inline=False
			)
		rankEMBED.add_field(
			name="Server Activity",
			value=subbed,
			inline=True
			)

		return rankEMBED, rankFILE

	async def c_rankEMBED(bot, guild_name, main_id1, main_id2, main_user1, main_user2, avatar_id1, avatar_id2, emoji1 : list, emoji2 : list):
		'''Used for the /compare_rank command'''
		#* Some extras here, need to get values of the user using a separate function (my_rank_embed_values)
		#* This function also returns the emoji ranks to be shown next to the values in emoji_object
		fields1, xp1, level1, role_title1 = await compare_rank_embed_values(guild_name, main_id1, False, bot)
		fields2, xp2, level2, role_title2 = await compare_rank_embed_values(guild_name, main_id2, True, bot)

		role_barriers = await json_read(f"Data/{guild_name} Role Barriers.json")
		role_barriers = dict(role_barriers)
		# c_rankFILE = discord.File(
		# 	f"Images/Ranks/{role_title1}.png",
		# 	filename="image.png"
		# 	)

		r_emoji1 = discord.utils.get(bot.emojis, name=role_title1)
		r_emoji2 = discord.utils.get(bot.emojis, name=role_title2)
		types = (
			"💬 Messages: ", 
			"😃 Reactions Added: ",
			"🥰 Reactions Recieved: ",
			"🎭 Stickers: ",
			"🖼️ Images: ",
			"🔗 Embeds: ",
			"🎙️ Voice (minutes): ",
			"✉️ Invites: ",
			"🌟 Special XP: ")

		#* Embed and embed fields
		c_rankEMBED = discord.Embed(
			title=f"{main_user1} vs. {main_user2}",
			description=f"Who games the hardest?",
			color=discord.Color.purple()
			)
		c_rankEMBED.set_author(
			name=f"{main_user1} vs. {main_user2}",
			icon_url=avatar_id1
			)
		c_rankEMBED.set_thumbnail(
			url=avatar_id2
			)

		s_field = ""
		i = 0
		for act in types:
			s_field += f"> **{act}**{fields1[i]} vs. {fields2[i]}\n"
			i += 1

		#* Embed fields
		c_rankEMBED.add_field(
			name="Level",
			value=f"{r_emoji1} {level1} vs. {level2} {r_emoji2}",
			inline=False
			)
		c_rankEMBED.add_field(
			name="Server Activity",
			value=f"{s_field}",
			inline=False
			)

		return c_rankEMBED

	async def rcEMBED(main_user, author_id, new_role):
		'''Appears when a user levels up to a new rank
		This is detected using rank_check and update_levels in myfunctions'''
		rcFILE = discord.File(
			f"Images/Ranks/{new_role}.png",
			filename="image.png")
		#* This section picks a random quote from a txt file to display in desc. of embed
		# q_quotes_raw = []
		q_quotes = []

		#! Corpses (none of these work on friend's computer)
		# with open("rank_check_quotes.txt", "r", encoding="utf8") as f:
		# 	for line in f:
		# 		q_quotes_raw.append(line)

		# data = await json_read("rank_check_quotes.json")
		# q_quotes_raw = data["rc_quotes"][0]["responses"]

		# async with aiofiles.open("rank_check_quotes.txt", mode="r") as f:
		# 	async for line in f:
		# 		q_quotes_raw.append(line)

		#! LOLZEP BOT METHOD IT IS
		q_quotes_raw = [
				"I'm so impressed I could cry! Thank you very much for your best dance!",
				"You're not an ordinary fella!",
				"This is the cool Konami sound!",
				"Can I call you a dancin' master?!",
				"Look at all that bling!",
				"You showed us... YOUR ULTIMATE DANCE! I can't stop crying buckets of tears!",
				"Excuse me, is your name Affection?",
				"Is there an earthquake 'cuz this party's crackin'!",
				"You're the king!",
				"Bling bling, yo how many carats you got on - that was golden...",
				"You're gonna break the meter! Can't wait to see it!",
				"This one's gonna be KUHRAAAAAYYYYYZEH!!!",
				"AWWWW YEAH! THAT'S WHAT I'M TALKIN' ABOUT!",
				"This is gettin' *adlib disc scratching* WHACK!",
				"You're like sunshine on a rainy day!",
				"I can see a dream in your dance, I can see tomorrow in your dance! We can call it... 'Our Hope'.",
				"Uh excuse me? Is your name perfection?",
				"Perfection is your first, last and middle name. Your skills are un... be... lievable!",
				"Music, saikou da!",
				"Make some noise! Holla! Wooooop wooooop!",
				"We're dancin', we're groovin', you know this floor is movin'!",
				"You're on fire!",
				"Superb! Perfection! Greatness...thy name suits YOU.",
				"Aww yeah! They're givin' it up fo' you, holmes!",
				"Check it out! They're cheerin' for ya!",
				"Whoooooooooo-hoo! That blew my mind!",
				"I think your 360 is starting to smoke.",
				"Toasty!",
				"You're so fantastic, I can't stop crying... buckets of tears!",
				"You're the cream of the crop!"
			]

		for quote in q_quotes_raw:
			quote = quote[:-1]
			q_quotes.append(quote)

		ran_quote = q_quotes[random.randint(0, len(q_quotes)-1)]
		#* Embed and embed fields
		rcEMBED = discord.Embed(
			title=f"{main_user} just advanced to {new_role}!",
			description=ran_quote,
			color = discord.Color.purple()
			)

		rcEMBED.set_thumbnail(url="attachment://image.png")

		rcEMBED.set_author(
			name=main_user,
			icon_url=author_id
			)

		return rcFILE, rcEMBED


	async def lbEMBED(bot, guild_name, guild_img, starting_rank, ending_rank, activity, just_pages:bool):
		'''Used for the /leaderboard command'''
		users, length = await sort_leaderboard(guild_name, activity)

		num_pages = int(math.ceil(length/ending_rank))
		if just_pages is True:
			return num_pages

		lbEMBED = discord.Embed(
			title=f"Leaderboard of activity for {guild_name} based on {activity}",
			description="Gamers",
			color = discord.Color.purple()
			)
		lbEMBED.set_author(
			name=guild_name,
			icon_url=guild_img
			)
		lbEMBED.set_thumbnail(
			url="attachment://image.png"
			)

		#* Embed fields
		i = starting_rank
		try:
			for user in users[starting_rank - 1:ending_rank]:
				field_display, emoji_object, role_title = await leaderboard_embed_values(guild_name, user[0], activity, False)

				#* Replaces "emojiX" string values in field_display with the actual emojis
				emoji = lambda item : discord.utils.get(bot.emojis, name=item)
				in_embed = map(emoji, emoji_object)
				j = 1
				for item in in_embed:
					subbed = re.sub(f"\\bemoji{j}\\b", str(item), field_display)
					field_display = subbed
					j += 1

				#* Add the emoji for the specified role_title
				r_emoji = discord.utils.get(bot.emojis, name=role_title)

				lbEMBED.add_field(
					name=f"#{i}: {user[1]} {r_emoji} {user[3]}",
					value=field_display,
					inline=False
					)
				i += 1
		except ValueError:
			for user in users[starting_rank - 1:ending_rank]:
				field_display, emoji_object, role_title = await leaderboard_embed_values(guild_name, user[0], activity, False)

				#* Replaces "emojiX" string values in field_display with the actual emojis
				emoji = lambda item : discord.utils.get(bot.emojis, name=item)
				in_embed = map(emoji, emoji_object)
				j = 1
				for item in in_embed:
					subbed = re.sub(f"\\bemoji{j}\\b", str(item), field_display)
					field_display = subbed
					j += 1

				#* Add the emoji for the specified role_title
				r_emoji = discord.utils.get(bot.emojis, name=role_title)

				lbEMBED.add_field(
					name=f"#{i}: {user[1]} {r_emoji} {user[3]}",
					value=field_display,
					inline=False
					)
				i += 1

		return lbEMBED
