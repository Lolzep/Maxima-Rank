import discord
import os
import re

from myfunctions import templateEmbed, my_rank_embed_values, level_barriers

VERSION = os.popen('git rev-parse HEAD').read()
COMMIT_MESSAGE = os.popen('git show --pretty=format:%s -s HEAD').read()

class infoEmbeds:
	'''infoEmbeds contains all types of embeds that are sent
	by the bot and allows them to be easily called and sent
	in the main.py file while keeping them separate from the
	main.py file'''
	def aboutEMBED():
		'''Used for the /about command'''
		aboutEMBED, aboutFILE = templateEmbed("about")

		aboutEMBED.add_field(name="Maxima Rank", value="An activity tracker for Discord for tracking messages, time in voice, etc. and using that for levels for rewarding the most active users in a Discord", inline=False)
		aboutEMBED.add_field(name="Commit", value=str(VERSION), inline=False)
		aboutEMBED.add_field(name="Recent Changes", value=COMMIT_MESSAGE, inline=False)
		aboutEMBED.add_field(name="Contributors", value="Lolzep #5723", inline=False)

		return aboutEMBED, aboutFILE
	
	def helpEMBED():
		'''Used for the /help command'''
		helpEMBED, helpFILE = templateEmbed("help", "Maxima Rank Help")

		helpEMBED.add_field(name="/help", value="You are here! Commands for Maxima Rank", inline=False)
		helpEMBED.add_field(name="/about", value="Info about the bot", inline=False)
		helpEMBED.add_field(name="/my_rank", value="Statistics about yourself", inline=False)
		helpEMBED.add_field(name="/rank [username]", value="Statistics about a specified user", inline=False)

		return helpEMBED, helpFILE

	def adminhelpEMBED():
		'''Used for the /adminhelp command'''
		adminhelpEMBED, adminhelpFILE = templateEmbed("help", "Maxima Rank Admin Help")

		adminhelpEMBED.add_field(name="/adminhelp", value="You are here! Admin commands for Maxima Rank", inline=False)
		adminhelpEMBED.add_field(name="/award_xp [user] [amount]", value="Gives a specified [user] [amount] xp", inline=False)
		adminhelpEMBED.add_field(name="/booster_xp [amount]", value="Gives [amount] xp to all boosted users", inline=False)

		return adminhelpEMBED, adminhelpFILE
	
	def myrankEMBED(guild_id, main_id, main_user, avatar_id, emoji : list):
		'''Used for the /myrank command'''
		#* Some extras here, need to get values of the user using a separate function (my_rank_embed_values)
		#* This function also returns the emoji ranks to be shown next to the values in emoji_object
		field_display, emoji_object, xp, level, level_xp, progress_to_next, role_title, role_id = my_rank_embed_values(guild_id, main_id, False)
		role_barriers = level_barriers(100, 20, 300, False)
		myrankFILE = discord.File(f"Images/Ranks/{role_title}.png", filename="image.png")

		#* Replaces "emojiX" string values in field_display with the actual emojis
		i = 1
		for item in emoji:
			subbed = re.sub(f"\\bemoji{i}\\b", str(item), field_display)
			field_display = subbed
			i += 1

		#* Used to show the % of XP to next level
		percent_xp = 100 * progress_to_next / level_xp
		percent_xp = "%.1f" % percent_xp

		#* If role is max role (Exalted), show easter egg text
		if role_title != "Exalted":
			myrankEMBED = discord.Embed(title=f"You are {role_title} Rank!", description=f"You are {role_barriers[role_title] - xp} XP away from being the next rank!", color=discord.Color.purple())
		else:
			myrankEMBED = discord.Embed(title=f"You are {role_title} Rank!", description=f"You are max rank! Now go outside.", color=discord.Color.purple())
		
		#* Embed fields
		myrankEMBED.set_author(name=main_user, icon_url="attachment://image.png")
		myrankEMBED.set_thumbnail(url=avatar_id)

		myrankEMBED.add_field(name="Level", value=f"{level}", inline=True)
		myrankEMBED.add_field(name="XP", value=f"{xp}", inline=True)
		myrankEMBED.add_field(name="XP Progress to Next Level", value=f"{progress_to_next} / {level_xp} ( {percent_xp}% )", inline=False)
		myrankEMBED.add_field(name="Server Activity", value=subbed, inline=True)

		return myrankEMBED, myrankFILE

	def rankEMBED(guild_id, main_id, main_user, avatar_id, emoji : list):
		'''Used for the /rank command
		Very similar to myrankEMBED'''
		#* Some extras here, need to get values of the user using a separate function (my_rank_embed_values)
		#* This function also returns the emoji ranks to be shown next to the values in emoji_object
		field_display, emoji_object, xp, level, level_xp, progress_to_next, role_title, role_id = my_rank_embed_values(guild_id, main_id, False)
		role_barriers = level_barriers(100, 20, 300, False)
		rankFILE = discord.File(f"Images/Ranks/{role_title}.png", filename="image.png")

		#* Replaces "emojiX" string values in field_display with the actual emojis
		i = 1
		for item in emoji:
			subbed = re.sub(f"\\bemoji{i}\\b", str(item), field_display)
			field_display = subbed
			i += 1

		#* Used to show the % of XP to next level
		percent_xp = 100 * progress_to_next / level_xp
		percent_xp = "%.1f" % percent_xp

		#* If role is max role (Exalted), show easter egg text
		if role_title != "Exalted":
			rankEMBED = discord.Embed(title=f"{main_user} is {role_title} Rank!", description=f"{main_user} is {role_barriers[role_title] - xp} XP away from being the next rank!", color=discord.Color.purple())
		else:
			rankEMBED = discord.Embed(title=f"{main_user} is {role_title} Rank!", description=f"You are max rank! Now go outside.", color=discord.Color.purple())
		
		#* Embed fields
		rankEMBED.set_author(name=main_user, icon_url="attachment://image.png")
		rankEMBED.set_thumbnail(url=avatar_id)

		rankEMBED.add_field(name="Level", value=f"{level}", inline=True)
		rankEMBED.add_field(name="XP", value=f"{xp}", inline=True)
		rankEMBED.add_field(name="XP Progress to Next Level", value=f"{progress_to_next} / {level_xp} ( {percent_xp}% )", inline=False)
		rankEMBED.add_field(name="Server Activity", value=subbed, inline=True)

		return rankEMBED, rankFILE
	
	def leaderboardEMBED(guild_id):
		pass

	def rankupEMBED():
		pass





