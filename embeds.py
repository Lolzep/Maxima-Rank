import discord
import os

VERSION = os.popen('git rev-parse HEAD').read()
COMMIT_MESSAGE = os.popen('git show --pretty=format:%s -s HEAD').read()

class infoEmbeds:
	def aboutEMBED():
		aboutEMBED = discord.Embed(colour = discord.Colour.purple())

		aboutFILE = discord.File("Images/about.png", filename="image.png")
		aboutEMBED.set_thumbnail(url="attachment://image.png")

		aboutEMBED.add_field(name="Monke Rank", value="An activity tracker for Discord for tracking messages, time in voice, etc. and using that for levels for rewarding the most active users in a Discord", inline=False)
		aboutEMBED.add_field(name="Commit", value=str(VERSION), inline=False)
		aboutEMBED.add_field(name="Recent Changes", value=COMMIT_MESSAGE, inline=False)
		aboutEMBED.add_field(name="Contributors", value="Lolzep #5723", inline=False)

		return aboutEMBED, aboutFILE

