import discord
import os
import re

from myfunctions import templateEmbed, my_rank_embed_values, level_barriers

VERSION = os.popen('git rev-parse HEAD').read()
COMMIT_MESSAGE = os.popen('git show --pretty=format:%s -s HEAD').read()

class infoEmbeds:
	def aboutEMBED():
		aboutEMBED, aboutFILE = templateEmbed("about")

		aboutEMBED.add_field(name="Monke Rank", value="An activity tracker for Discord for tracking messages, time in voice, etc. and using that for levels for rewarding the most active users in a Discord", inline=False)
		aboutEMBED.add_field(name="Commit", value=str(VERSION), inline=False)
		aboutEMBED.add_field(name="Recent Changes", value=COMMIT_MESSAGE, inline=False)
		aboutEMBED.add_field(name="Contributors", value="Lolzep #5723", inline=False)

		return aboutEMBED, aboutFILE
	
	def helpEMBED():
		helpEMBED, helpFILE = templateEmbed("help", "Monke Rank Help")

		helpEMBED.add_field(name="/help", value="You are here! Commands for Monke Rank", inline=False)
		helpEMBED.add_field(name="/about", value="Info about the bot", inline=False)
		helpEMBED.add_field(name="/my_progress", value="Shows your progress to next level and role", inline=False)
		helpEMBED.add_field(name="/my_rank", value="Statistics about yourself", inline=False)

		return helpEMBED, helpFILE
	
	def myrankEMBED(guild_id, main_id, main_user, avatar_id, emoji : list):
		field_display, emoji_object, xp, level, level_xp, progress_to_next, role_title, role_id = my_rank_embed_values(guild_id, main_id, False)
		role_barriers = level_barriers(100, 20, 300)
		myrankFILE = discord.File(f"Images/Ranks/{role_title}.png", filename="image.png")

		i = 1
		for item in emoji:
			subbed = re.sub(f"\\bemoji{i}\\b", str(item), field_display)
			field_display = subbed
			i += 1

		percent_xp = 100 * progress_to_next / level_xp
		percent_xp = "%.1f" % percent_xp

		if role_title != "Exalted":
			myrankEMBED = discord.Embed(title=f"You are {role_title} Rank!", description=f"You are {role_barriers[role_title] - xp} XP away from being the next rank!", color=discord.Color.purple())
		else:
			myrankEMBED = discord.Embed(title=f"You are {role_title} Rank!", description=f"You are max rank! Now go outside.", color=discord.Color.purple())
		myrankEMBED.set_author(name=main_user, icon_url="attachment://image.png")
		myrankEMBED.set_thumbnail(url=avatar_id)

		myrankEMBED.add_field(name="Level", value=f"{level}", inline=True)
		myrankEMBED.add_field(name="XP", value=f"{xp}", inline=True)
		myrankEMBED.add_field(name="XP Progress to Next Level", value=f"{progress_to_next} / {level_xp} ( {percent_xp}% )", inline=False)
		myrankEMBED.add_field(name="Server Activity", value=subbed, inline=True)

		return myrankEMBED, myrankFILE





