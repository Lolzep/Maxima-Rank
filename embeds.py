import discord
import os

from myfunctions import templateEmbed

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
	
	def myrankEMBED(main_id):
		# testing
		main_id = "https://i.imgur.com/U9fnXER.jpeg"
		# testing

		myrankEMBED = discord.Embed(color=discord.Color.purple())
		myrankEMBED.set_author(name="Lolzep", icon_url=main_id)

		myrankEMBED.add_field(name="Level", value="4\n", inline=True)
		myrankEMBED.add_field(name="XP", value="1000\n", inline=True)
		myrankEMBED.add_field(name="Progress to Next Level", value="🟩🟩🟩🟩🟩🟩⬛⬛⬛⬛", inline=False)
		myrankEMBED.add_field(name="Server Activity", value="> Messages\n> Reactions Added\n> Reactions Recieved\n> Stickers\n> Images\n> Embeds\n> Voice (minutes)\n> Invites\n> Special XP", inline=True)
		myrankEMBED.add_field(name="Values", value="> 2302\n> 15\n> 40\n> 23\n> 32\n> 44\n> 1020\n> 1\n> 0", inline=True)
		myrankEMBED.add_field(name="Rate", value="> 🟩🟩🟩🟩🟩🟩🟩\n> 🟩\n> 🟩🟩\n> 🟩\n> 🟩🟩\n> 🟩🟩\n> 🟩🟩🟩🟩🟩\n> 🟩\n> ❌", inline=True)

		myrankFILE = discord.File(f"Images/about.png", filename="image.png")
		myrankEMBED.set_thumbnail(url="attachment://image.png")

		return myrankEMBED, myrankFILE
	
	def myrankM_EMBED(main_id):	
		# testing
		main_id = "https://i.imgur.com/U9fnXER.jpeg"
		# testing

		myrankEMBED = discord.Embed(color=discord.Color.purple())
		myrankEMBED.set_author(name="Lolzep", icon_url=main_id)

		myrankEMBED.add_field(name="Level", value="4\n", inline=True)

		myrankFILE = discord.File(f"Images/about.png", filename="image.png")
		myrankEMBED.set_thumbnail(url="attachment://image.png")

		return myrankEMBED, myrankFILE





