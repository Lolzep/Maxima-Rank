import discord
import os

from myfunctions import templateEmbed, my_rank_embed_values

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
	
	def myrankEMBED(guild_id, main_id, avatar_id, emoji : list):
		field_display, emoji_object, progress_to_next, role_title, role_id = my_rank_embed_values(guild_id, main_id, False)
		myrankFILE = discord.File(f"Images/about.png", filename="image.png")

		myrankEMBED = discord.Embed(title="You are Master Rank!", description="You are 49300 XP away from Grandmaster", color=discord.Color.purple())
		myrankEMBED.set_author(name="Lolzep", icon_url="attachment://image.png")
		myrankEMBED.set_thumbnail(url=avatar_id)

		myrankEMBED.add_field(name="Level", value="4\n", inline=True)
		myrankEMBED.add_field(name="XP", value="1000\n", inline=True)
		myrankEMBED.add_field(name="Next Level XP", value="1340", inline=False)
		myrankEMBED.add_field(name="Server Activity", value=field_display, inline=True)

		return myrankEMBED, myrankFILE





