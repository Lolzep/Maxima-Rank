import discord
import os
import asyncio
import json
import time

from discord.commands import Option
from discord.ext import commands, pages
from dotenv import load_dotenv
from myfunctions import update_user, my_rank_embed_values, update_boosters, rank_check
from embeds import *

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.messages = True

bot = discord.Bot(intents=intents, debug_guilds=[273567091368656898, 828667775605669888])

#? Command ideas!

#? Small projects
#* [DONE] async def about(): Show information about the bot (Defintion, Github commits and changes, Contributors) in an embed
#* [DONE] def restart(): Put restart_bot def in a command
#* [DONE] async def help(): Shows all commands and generic help info in an embed
#* [DONE] async def booster(): Retrieve all boosters in a discord server from json, give specified "special_xp" to each booster
# "special_xp" also gets added to "xp"!
#* async def new_invite(ctx, name): Increase "invites" count by 1 for specified user and give specified xp
#* async def set_role_ids(): Set the role_ids in the Users.json role_ids section so that the correct roles are given when roles need to be updated

#? Large projects 
#* [DONE] def my_rank(ctx): Shows your ranking and detailed statistics about yourself in an embed
#* [Maybe not needed?] def my_progress(ctx): Shows progress to next level and role in an embed
#* [DONE] In level_update function: Detect when a user surpasses a new rank
#* async def set_xp(): Set all xp values in a slash command embed (admin panel)
#* async def top_rankers(): Leaderboard of activity, similar to ActivityRank's style
#* def update_roles(): Using role_ids from users.json and on_message event, update the roles in the server on rank change

# Used to send discord embeds in channels
# TODO: Not implemented yet
async def sendEmbed(api_call, embed_object, file_object):
	embed_object, file_object = await infoEmbeds.embed_object()
	await api_call(file=file_object, embed=embed_object)

class View(discord.ui.View): # Create a class called View that subclasses discord.ui.View
    @discord.ui.button(label="Next page", style=discord.ButtonStyle.primary, emoji="➡️") # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
	# Ignore bots
	if message.author.bot == True:
		return

	# Message counts
	await update_user(
		message.guild, message.author.id, message.author.name, # retrieve values from discord api
		"messages", # key value to change
		True, 1, 5, 1 # attributes of XP
		)

	# Image counts
	if message.attachments:
		await update_user(
			message.guild, message.author.id, message.author.name, 
			"images", 
			True, 1, 10, 1
			)
	
	# Embed counts
	if message.embeds:
		await update_user(
			message.guild, message.author.id, message.author.name, 
			"embeds", 
			True, 1, 10, 1
			)

	# Sticker counts
	if message.stickers:
		await update_user(
			message.guild, message.author.id, message.author.name, 
			"stickers", 
			True, 1, 10, 1
			)

	# Check if user levels up to a new rank, send special embed if True
	role_changed, new_role = await rank_check(message.guild, message.author.id)
	if role_changed is True:
		rcFILE, rcEMBED = await infoEmbeds.rcEMBED(message.author.name, message.author.display_avatar, new_role)
		await message.channel.send(file=rcFILE, embed=rcEMBED)

	if message.content.startswith("$test"):
		File = discord.File("Images/about.png")
		await message.channel.send(File)

@bot.event
async def on_reaction_add(reaction, user):
	# For reactions ADDED, add values and xp to respective user
	await update_user(
		user.guild, user.id, user.name, 
		"reactions_added",
		True, 1, 5, 1
		)

	# For reactions RECIEVED, add values and xp to respective user
	await update_user(
		reaction.message.guild, reaction.message.author.id, reaction.message.author.name, 
		"reactions_recieved",
		True, 1, 5, 1
		)

	#* Send rank_update embed if rank changed
	role_changed, new_role = await rank_check(reaction.message.guild, reaction.message.author.id)
	if role_changed is True:
		rcFILE, rcEMBED = await infoEmbeds.rcEMBED(reaction.message.author.name, reaction.message.author.display_avatar, new_role)
		await reaction.message.channel.send(file=rcFILE, embed=rcEMBED)
		return
		

@bot.event
async def on_voice_state_update(member, before, after):
	# ActivityRank: Voiceminutes are 5 XP
	voice_minutes = 0
	# While the user is in a voice chat (including switching to different voice chats)...
	# Add 1 voice_minute every 60 seconds
	while before.channel is None and after.channel is not None:
		print("in_channel")
		await asyncio.sleep(2)
		voice_minutes += 1
		print(f"Voice Minutes: {voice_minutes}")
		# When the user leaves voice chat...
		# Update users.json with updated voice_minutes, xp, and levels
		if before.channel is None and after.channel is None:
			await update_user(
				member.guild , member.id, member.name, 
				"voice_minutes", 
				True, voice_minutes, 5, voice_minutes
				)
			role_changed, new_role = await rank_check(member.guild , member.id)
			
			#* Send rank_update embed if rank changed
			if role_changed is True:
				rcFILE, rcEMBED = await infoEmbeds.rcEMBED(member.name, member.display_avatar, new_role)
				await member.guild.system_channel.send(file=rcFILE, embed=rcEMBED)
				return
			print("out_of_channel")
			break

# TODO: Make it so it doesn't check for premium on EVERY member update, only when premium for a member changes
# TODO: Make sure this well... works? No way to test boosted members (without paying ofc)
@bot.event
async def on_member_update(before, after):
	if before.premium_since is None and after.premium_since is not None:
		await update_user(
			before.guild, before.id, before.name, 
			"is_booster", 
			True, 0, 1000, 1, True
			)
		print("booster!")
	elif before.premium_since is not None and after.premium_since is None:
		await update_user(
			before.guild, before.id, before.name, 
			"is_booster", 
			True, 0, 0, 0, False
			)
		print("no longer a booster...")

	#* Used to add a new user if they don't exist 
	await update_user(
		before.guild, before.id, before.name, 
		"special_xp", 
		True, 0, 0, 0
	)

	#* Send rank_update embed if rank changed
	role_changed, new_role = await rank_check(before.guild, before.id)
	if role_changed is True:
		rcFILE, rcEMBED = await infoEmbeds.rcEMBED(before.name, before.display_avatar, new_role)
		await before.guild.system_channel.send(file=rcFILE, embed=rcEMBED)
		return

@bot.slash_command(description="Sends information about the bot")
async def about(ctx):
	aboutEMBED, aboutFILE = await infoEmbeds.aboutEMBED()
	await ctx.respond(file=aboutFILE, embed=aboutEMBED)

@bot.slash_command(description="Commands and their usage")
async def help(ctx):
	helpEMBED, helpFILE = await infoEmbeds.helpEMBED()
	await ctx.respond(file=helpFILE, embed=helpEMBED)

@bot.slash_command(description="Admin commands and their usage")
@commands.has_permissions(manage_messages=True)
async def adminhelp(ctx):
	adminhelpEMBED, adminhelpFILE = await infoEmbeds.adminhelpEMBED()
	await ctx.respond(file=adminhelpFILE, embed=adminhelpEMBED)

@bot.slash_command(name="award_xp", description="Add XP to a specified user or users for being such a good person")
@commands.has_permissions(manage_messages=True)
async def award_xp(
	ctx: discord.ApplicationContext, 
	member: Option(discord.Member, "Member to get id from", required = True), 
	xp: Option(int, "Amount of XP to give to user", required=True)
):

	await update_user(
		member.guild ,member.id, member.name, 
		"special_xp", 
		True, xp, xp, 1
		)
	await ctx.respond(f"You gave {member.name} {xp} XP!")

	#* Send rank_update embed if rank changed
	role_changed, new_role = await rank_check(member.guild , member.id)
	if role_changed is True:
		rcFILE, rcEMBED = await infoEmbeds.rcEMBED(member.name, member.display_avatar, new_role)
		await member.guild.system_channel.send(file=rcFILE, embed=rcEMBED)
		return

@bot.slash_command(name="invite_xp", description="Increase invite count for a user and give a specified amount of XP for doing so")
@commands.has_permissions(manage_messages=True)
async def invite_xp(
	ctx: discord.ApplicationContext, 
	member: Option(discord.Member, "Member to get id from", required = True), 
	invite_count: Option(int, "Amount of invites the user gave", required=True), 
	xp: Option(int, "Amount of XP to give for each invite", required=True)
):
	
	await update_user(
		member.guild ,member.id, member.name, 
		"invites", 
		True, invite_count, xp, invite_count
		)
	await ctx.respond(f"You verifyed that {member.name} gave {invite_count} invite(s) and doing so increased their XP by {xp * invite_count}!")

	#* Send rank_update embed if rank changed
	role_changed, new_role = await rank_check(member.guild , member.id)
	if role_changed is True:
		rcFILE, rcEMBED = await infoEmbeds.rcEMBED(member.name, member.display_avatar, new_role)
		await member.guild.system_channel.send(file=rcFILE, embed=rcEMBED)
		return

@bot.slash_command(name="booster_xp", description="Add XP to all boosted users")
@commands.has_permissions(manage_messages=True)
async def booster_xp(
	ctx: discord.ApplicationContext, 
	xp: Option(int, "Amount of XP to give to boosted members", required=True)
):

	#* Use the update_booster function to get a list of boosters and if their role changed or not due to XP increase
	count, rc_dict, nr_list = await update_boosters(ctx.user.guild, ctx.user.id, xp)

	#* For each user that is a booster AND their ranks updated as a result, send a rank_update embed
	i = 0
	for key in rc_dict:
		user2 = await ctx.guild.fetch_member(key)
		rcFILE, rcEMBED = await infoEmbeds.rcEMBED(user2.name, user2.display_avatar, nr_list[i])
		await ctx.guild.system_channel.send(file=rcFILE, embed=rcEMBED)
		i += 1
	await ctx.respond(f"You gave everyone who is currently boosting the server {xp} XP!\n Count of boosted members: {count}")

@bot.slash_command(description="Statistics about yourself")
async def myrank(ctx):
	emoji_object = await my_rank_embed_values(ctx.user.guild, ctx.user.id, True)
	emoji = lambda item : discord.utils.get(bot.emojis, name=item)
	in_embed = map(emoji, emoji_object)

	# in_embed = []
	# for item in emoji_object:
	# 	emoji = discord.utils.get(bot.emojis, name=item)
	# 	in_embed.append(emoji)

	myrankEMBED, myrankFILE = await infoEmbeds.myrankEMBED(ctx.user.guild, ctx.user.id, ctx.user.display_name, ctx.user.display_avatar, in_embed)
	await ctx.respond(file=myrankFILE, embed=myrankEMBED)

@bot.slash_command(name="rank", description="Statisitcs about a specified user")
async def rank(
	ctx: discord.ApplicationContext, 
	member: Option(discord.Member, "Member to get id from", required = True)
):
	
	emoji_object = await my_rank_embed_values(member.guild, member.id, True)
	emoji = lambda item : discord.utils.get(bot.emojis, name=item)
	in_embed = map(emoji, emoji_object)
	
	# in_embed = []
	# for item in emoji_object:
	# 	emoji = discord.utils.get(bot.emojis, name=item)
	# 	in_embed.append(emoji)

	rankEMBED, rankFILE = await infoEmbeds.rankEMBED(member.guild, member.id, member.display_name, member.display_avatar, in_embed)
	await ctx.respond(file=rankFILE, embed=rankEMBED)

@bot.slash_command(name="leaderboard", description="Activity leaderboard for the server")
async def leaderboard(
	ctx: discord.ApplicationContext
):
	#* starting_rank and ending_rank indicate how many users are on each page of the leaderboard embed
	starting_rank = 1
	ending_rank = 10
	ranks_per_page = ending_rank # Keeps a constant ending_rank

	#* Get the number of pages that need to be made based on user count and users/page
	num_pages = await infoEmbeds.lbEMBED(
		ctx.guild, 
		ctx.guild.icon.url, 
		starting_rank, 
		ending_rank, 
		True
		)

	#* Create a new leaderboard embed page based on above values, append to a list of embeds
	i = 1
	embeds = []
	while i <= num_pages:
		lbEMBED = await infoEmbeds.lbEMBED(
			ctx.guild, 
			ctx.guild.icon.url, 
			starting_rank, 
			ending_rank, 
			False
			)
		embeds.append(lbEMBED)
		i += 1
		starting_rank += ranks_per_page
		ending_rank += ranks_per_page

	#* Using a "paginator" from discord commands, use the list of embeds to create pages of leaderboards from 1 - num_users
	paginator = pages.Paginator(pages=embeds)
	await paginator.respond(ctx.interaction)

#! THE TEST ZONE (not final commands)

@bot.slash_command(name="import_channel", description="In the channel this command is used, import activity to Maxima Rank")
@commands.has_permissions(manage_messages=True)
async def import_channel(
	ctx: discord.ApplicationContext
):
	s_time = time.time()
	# messages = await ctx.history(limit=5000).flatten()
	# print(messages)
	i = 0
	await ctx.respond("Now starting message parsing...")
	async for message in ctx.history(limit=100000):
		#* Same code from on_message, just does it for every message that exists in the channel
		# Ignore bots
		if message.author.bot == True:
			i += 1
			continue

		# Message counts
		await update_user(
			message.guild, message.author.id, message.author.name, # retrieve values from discord api
			"messages", # key value to change
			True, 1, 5, 1 # attributes of XP
			)
		print(f"Increased message count, gave 5 XP to {message.author}")

		# Image counts
		if message.attachments != []:
			await update_user(
				message.guild, message.author.id, message.author.name, 
				"images", 
				True, 1, 10, 1
				)
			print(f"Increased image count, gave 10 XP to {message.author}")
		
		# Embed counts
		if message.embeds != []:
			await update_user(
				message.guild, message.author.id, message.author.name, 
				"embeds", 
				True, 1, 10, 1
				)
			print(f"Increased embeds count, gave 10 XP to {message.author}")

		# Sticker counts
		if message.stickers != []:
			await update_user(
				message.guild, message.author.id, message.author.name, 
				"stickers", 
				True, 1, 10, 1
				)
			print(f"Increased stickers count, gave 10 XP to {message.author}")

		# Check if user levels up to a new rank, send special embed if True
		role_changed, new_role = await rank_check(message.guild, message.author.id)
		if role_changed is True:
			rcFILE, rcEMBED = await infoEmbeds.rcEMBED(message.author.name, message.author.display_avatar, new_role)
			await message.channel.send(file=rcFILE, embed=rcEMBED)
		i += 1
	e_time = time.time()
	t_time = e_time - s_time
	t_time = "{:.2f}".format(t_time)
	await ctx.respond(f"Message history parsed for {i} messages in #{message.channel}.\nTime taken: {t_time} seconds")
	

@bot.slash_command(name='greet', description='Greet someone!', guild_ids=[273567091368656898])
async def greet(ctx, name: Option(str, "Enter your friend's name", required = False, default = '')):
    await ctx.respond(f'Hello {name}!')

bot.run(TOKEN)