import discord
import os
import sys
import asyncio
import json
import time

from discord import option, HTTPException
from discord.commands import Option
from discord.ext import commands, pages
from discord.ext.commands import MissingPermissions
from dotenv import load_dotenv
from myfunctions import update_user, my_rank_embed_values, rank_check, new_levels, update_roles, update_channel_ignore, check_channel, update_xp_boost, check_xp_boost
from embeds import *

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.messages = True

bot = discord.Bot(intents=intents, debug_guilds=[273567091368656898, 828667775605669888, 744622412267782234])

#? Command ideas!

#? Small projects
#* /add_act : Add activity manually. used for importing

#? Large projects
#* /rank_compare : When given two users, compare their activity (similar to /myrank but with two people)

# Check if user levels up to a new rank, send special embed if True
async def check_rank(discord_object_to_send, guild_name, guild_id, user_id, user_name, user_avatar):
	# Get current guild to get current member being checked
	guild = discord.utils.get(bot.guilds, id = guild_id)
	member = guild.get_member(user_id)

	# Ignore bots
	if member.bot == True:
		return

	# Check the rank to see if the role changed after leveling up
	role_changed, new_role, old_role_id, new_role_id = await rank_check(guild_name, user_id)
	# If the role did change after checking the rank...
	if role_changed is True:
		# Get the current role and the new role
		old_role_obj = discord.utils.get(bot.get_guild(guild_id).roles, id = old_role_id)
		new_role_obj = discord.utils.get(bot.get_guild(guild_id).roles, id = new_role_id)

		# Remove the old role from the user and add the new role to the user
		# If roles don't exist, don't do anything
		try:
			await member.add_roles(new_role_obj)
			await member.remove_roles(old_role_obj)
		except AttributeError:
			pass

		# Send rcEMBED to specified discord channel (default is system channel)
		rcFILE, rcEMBED = await infoEmbeds.rcEMBED(user_name, user_avatar, new_role)
		print("Embed made")
		await discord_object_to_send(file=rcFILE, embed=rcEMBED)
		print("Sent embed")

#! Activity tracking bot events

@bot.event
async def on_ready():
	print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
	# Ignore bots
	if message.author.bot == True:
		return

	# Ignore channel if channel is ignored (/ignore_channel)
	try:
		channel_check = await check_channel(message.guild, message.channel.id)
		if channel_check == True:
			return
	except FileNotFoundError:
		channel_check == False

	# See if there is an active XP boost event, return multiplier to multiply xp by if True
	xp_boost_mult = 1
	no_xp = False
	try:
		xp_boost_mult, no_xp = await check_xp_boost(message.guild)
		if no_xp == True:
			return
	except FileNotFoundError:
		pass

	# Message counts
	await update_user(
		message.guild, message.author.id, message.author.name, # retrieve values from discord api
		"messages", # key value to change
		True, 1, 5, 1, xp_boost_mult # attributes of XP
		)

	# Image counts
	if message.attachments:
		await update_user(
			message.guild, message.author.id, message.author.name,
			"images",
			True, 1, 5, 1, xp_boost_mult
			)

	# Embed counts
	if message.embeds:
		await update_user(
			message.guild, message.author.id, message.author.name,
			"embeds",
			True, 1, 5, 1, xp_boost_mult
			)

	# Sticker counts
	if message.stickers:
		await update_user(
			message.guild, message.author.id, message.author.name,
			"stickers",
			True, 1, 3, 1, xp_boost_mult
			)

	# Send embed if user levels up
	await check_rank(
		message.guild.system_channel.send,
		message.guild,
		message.guild.id,
		message.author.id,
		message.author.name,
		message.author.display_avatar
		)

	if message.content.startswith("$test"):
		File = discord.File("Images/about.png")
		await message.channel.send(File)

@bot.event
async def on_reaction_add(reaction, user):
	# Ignore bots and that one guy
	if reaction.message.author.bot == True or user.id == 591118835764166678:
		print(f"{user.name} ({user.id}): Reactions ignored")
		return

	# Ignore channel if channel is ignored (/ignore_channel)
	try:
		channel_check = await check_channel(reaction.message.guild, reaction.message.channel.id)
		if channel_check == True:
			return
	except FileNotFoundError:
		channel_check == False

	# See if there is an active XP boost event, return multiplier to multiply xp by if True
	xp_boost_mult = 1
	no_xp = False
	try:
		xp_boost_mult, no_xp = await check_xp_boost(reaction.message.guild)
		if no_xp == True:
			return
	except FileNotFoundError:
		pass

	# For reactions ADDED, add values and xp to respective user
	await update_user(
		user.guild, user.id, user.name,
		"reactions_added",
		True, 1, 1, 1, xp_boost_mult
		)

	# For reactions RECIEVED, add values and xp to respective user
	await update_user(
		reaction.message.guild, reaction.message.author.id, reaction.message.author.name,
		"reactions_recieved",
		True, 1, 1, 1, xp_boost_mult
		)

	# Send embed if user levels up
	await check_rank(
		reaction.message.guild.system_channel.send,
		reaction.message.guild,
		reaction.message.guild.id,
		reaction.message.author.id,
		reaction.message.author.name,
		reaction.message.author.display_avatar
		)


@bot.event
async def on_voice_state_update(member, before, after):
	# ActivityRank: Voiceminutes are 5 XP
	voice_minutes = 0
	# See if there is an active XP boost event, return multiplier to multiply xp by if True
	xp_boost_mult = 1
	no_xp = False
	try:
		xp_boost_mult, no_xp = await check_xp_boost(member.guild)
		if no_xp == True:
			return
	except FileNotFoundError:
		pass

	# While the user is in a voice chat (including switching to different voice chats)...
	while before.channel is None and after.channel is not None:
		# Add 1 voice_minute every 60 seconds
		await asyncio.sleep(60)
		voice_minutes += 1

		# Update voice_minutes to the users.json every 5 minutes
		if voice_minutes % 5 == 0:
			await update_user(
				member.guild , member.id, member.name,
				"voice_minutes",
				True, 5, 3, 5, xp_boost_mult
				)
			# Send embed if user levels up
			await check_rank(
				member.guild.system_channel.send,
				member.guild,
				member.guild.id,
				member.id,
				member.name,
				member.display_avatar
				)
			continue

		# When the user leaves voice chat...
		# Update users.json with updated voice_minutes, xp, and levels
		# Add voice_minutes not added to the user (1-4 minutes extra)
		if before.channel is None and after.channel is None:
			await update_user(
				member.guild , member.id, member.name,
				"voice_minutes",
				True, voice_minutes % 5, 3, voice_minutes % 5, xp_boost_mult
				)

			# Send embed if user levels up
			await check_rank(
				member.guild.system_channel.send,
				member.guild,
				member.guild.id,
				member.id,
				member.name,
				member.display_avatar
				)

			break

# TODO: Make sure this well... works? No way to test boosted members (without paying ofc)
@bot.event
async def on_member_update(before, after):
	# See if there is an active XP boost event, return multiplier to multiply xp by if True
	xp_boost_mult = 1
	no_xp = False
	try:
		xp_boost_mult, no_xp = await check_xp_boost(before.guild)
		if no_xp == True:
			return
	except FileNotFoundError:
		pass

	if before.premium_since is None and after.premium_since is not None:
		await update_user(
			before.guild, before.id, before.name,
			"is_booster",
			True, 0, 1000, 1, 1, True
			)
		print(f"{before.name} is now a booster! They got 1000 XP!")
		await before.guild.system_channel.send(f"{before.name} was given 1000 XP for becoming a booster!")
	elif before.premium_since is not None and after.premium_since is None:
		await update_user(
			before.guild, before.id, before.name,
			"is_booster",
			True, 0, 0, 0, 1, False
			)
		print(f"{before.name} is no longer a booster.")


	try:
		# Send embed if user levels up
		await check_rank(
			before.guild.system_channel.send,
			before.guild,
			before.guild.id,
			before.id,
			before.name,
			before.display_avatar
			)
	except json.JSONDecodeError:
		# Used to add a new user if they don't exist
		await update_user(
			before.guild, before.id, before.name,
			"special_xp",
			True, 0, 0, 0, 1
		)
	except UnboundLocalError:
		await update_user(
			before.guild, before.id, before.name,
			"special_xp",
			True, 0, 0, 0, 1
		)

#! Normal User Commands (Commands used by regular members of the server)

@bot.slash_command(name="about", description="Sends information about the bot")
async def about(ctx):
	aboutEMBED, aboutFILE = await infoEmbeds.aboutEMBED()
	await ctx.respond(file=aboutFILE, embed=aboutEMBED)

@bot.slash_command(name="help", description="Commands and their usage")
async def help(ctx):
	helpEMBED, helpFILE = await infoEmbeds.helpEMBED()
	await ctx.respond(file=helpFILE, embed=helpEMBED)

@bot.slash_command(name="myrank", description="Statistics about yourself")
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
	ctx: discord.ApplicationContext,
	activity: Option(
		str,
		"Choose what you want to sort by",
		choices=[
			"messages",
			"reactions_added",
			"reactions_recieved",
			"stickers",
			"images",
			"embeds",
			"voice_minutes",
			"invites",
			"special_xp"
			],
			default="Everything",
			required=False
			),
	page_length: Option(
		int,
		"How many users on each page?",
		min_value=2,
		max_value=20,
		default=10,
		required=False
		)
):
	#* starting_rank and ending_rank indicate how many users are on each page of the leaderboard embed
	starting_rank = 1
	ending_rank = page_length
	ranks_per_page = ending_rank # Keeps a constant ending_rank

	#* Get the number of pages that need to be made based on user count and users/page
	num_pages = await infoEmbeds.lbEMBED(
		bot,
		ctx.guild,
		ctx.guild.icon.url,
		starting_rank,
		ending_rank,
		activity,
		True
		)

	#* Create a new leaderboard embed page based on above values, append to a list of embeds
	i = 1
	embeds = []
	while i <= num_pages:
		lbEMBED = await infoEmbeds.lbEMBED(
			bot,
			ctx.guild,
			ctx.guild.icon.url,
			starting_rank,
			ending_rank,
			activity,
			False
			)
		embeds.append(lbEMBED)
		i += 1
		starting_rank += ranks_per_page
		ending_rank += ranks_per_page

	#* Using a "paginator" from discord commands, use the list of embeds to create pages of leaderboards from 1 - num_users
	paginator = pages.Paginator(pages=embeds, author_check=False)
	await paginator.respond(ctx.interaction)

#! Admin Commands (Commands used by admins of the server)

@bot.slash_command(name="adminhelp", description="Admin commands and their usage")
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
		True, xp, xp, 1, 1
		)
	await ctx.respond(f"You gave {member.mention} {xp} XP!")

	# Send embed if user levels up
	await check_rank(
		member.guild.system_channel.send,
		member.guild,
		member.guild.id,
		member.id,
		member.name,
		member.display_avatar
		)

@bot.slash_command(name="role_xp", description="Give XP to a specific role")
@commands.has_permissions(manage_messages=True)
async def role_xp(
	ctx: discord.ApplicationContext,
	role: Option(discord.Role, "Select a role", required=True),
	xp: Option(int, "Amount of XP to give to the users of this role", required=True)
):

	for user in role.members:
		await update_user(
			user.guild ,user.id, user.name,
			"special_xp",
			True, xp, xp, 1, 1
			)

		# Send embed if user levels up
		await check_rank(
			user.guild.system_channel.send,
			user.guild,
			user.guild.id,
			user.id,
			user.name,
			user.display_avatar
			)
	await ctx.respond(f"You gave users with the {role.mention} role {xp} XP!")

@bot.slash_command(name="act_xp", description="Increase activity and XP for that activity")
@commands.has_permissions(manage_messages=True)
async def act_xp(
	ctx: discord.ApplicationContext,
	member: Option(discord.Member, "Member to get id from", required = True),
	activity: Option(
		str,
		"Choose the activity to add to",
		choices=[
			"messages",
			"reactions_added",
			"reactions_recieved",
			"stickers",
			"images",
			"embeds",
			"voice_minutes",
			"invites",
			"special_xp"
			],
			required=True
			),
	act_count: Option(int, "Amount of the activity", required=True),
	xp: Option(int, "Amount of XP to give for each activity", required=True)
):

	await update_user(
		member.guild ,member.id, member.name,
		activity,
		True, act_count, xp, act_count, 1
		)
	await ctx.respond(f"You verifyed that {member.mention} had {act_count} '{activity}' and doing so increased their XP by {xp * act_count}!")

	# Send embed if user levels up
	await check_rank(
		member.guild.system_channel.send,
		member.guild,
		member.guild.id,
		member.id,
		member.name,
		member.display_avatar
		)

@bot.slash_command(name="xp_boost", description="Give an XP boost to the server for a specified amount of minutes")
@option("multiplier", description="How much should XP be multiplied by?")
@option("time", description="How long should it last in minutes?")
@commands.has_permissions(manage_messages=True)
async def xp_boost(
	ctx: discord.ApplicationContext,
	multiplier: int,
	time: int
):
	await update_xp_boost(ctx.guild, True, multiplier, False)
	print("XP Boost started!")
	await ctx.respond(f"XP boost event started for {time} minutes with a {multiplier} multiplier!")
	await asyncio.sleep(time * 60)
	await update_xp_boost(ctx.guild, False, multiplier, False)
	await ctx.respond(f"{ctx.author.mention} The XP boost event has ended!")

@bot.slash_command(name="xp_boost_end", description="End an XP boost manually")
@commands.has_permissions(manage_messages=True)
async def xp_boost_end(
	ctx: discord.ApplicationContext
):
	multiplier = 1
	await update_xp_boost(ctx.guild, False, multiplier, False)
	print("XP Boost ended!")

@bot.slash_command(name="no_xp", description="Stop all activity tracking for a specified amount of minutes")
@option("multiplier", description="How much should XP be multiplied by?")
@option("time", description="How long should it last in minutes?")
@commands.has_permissions(manage_messages=True)
async def no_xp(
	ctx: discord.ApplicationContext,
	time: int
):
	multiplier = 1
	await update_xp_boost(ctx.guild, False, multiplier, True)
	await ctx.respond(f"Activity tracking disabled for {time} minutes!")
	await asyncio.sleep(time * 60)
	await update_xp_boost(ctx.guild, False, multiplier, False)
	await ctx.respond(f"{ctx.author.mention} Activity tracking has been reenabled")

#! Management Commands (Also admin commands, but should only be used once for making new things)

@bot.slash_command(name="make_levels", description="Make new levels and level barriers")
@commands.has_permissions(manage_messages=True)
async def make_levels(
	ctx: discord.ApplicationContext,
	starting_xp: Option(int, "How much XP for level 1?", required=True),
	level_factor: Option(int, "How much XP should each level increase by?", required=True),
	total_levels: Option(int, "How many levels should be made? (Higher takes longer to make)", required=True)
):
	s_time = time.time()
	await ctx.respond(f"Now making new levels...")
	role_barriers, rl = await new_levels(
		ctx.guild,
		starting_xp,
		level_factor,
		total_levels,
		True,
		Newbie=0,
		Bronze=3,
		Silver=5,
		Gold=10,
		Platinum=25,
		Diamond=50,
		Master=100,
		Grandmaster=150,
		Exalted=175,
		Galaxy=200,
		Konami=573
	)

	e_time = time.time()
	t_time = e_time - s_time
	t_time = "{:.2f}".format(t_time)
	await ctx.respond(f"New levels created! This took {t_time} seconds.\n\n**Each level name and starting level is:**\n{rl}\n\n**Barriers for XP are:**\n{role_barriers}")

@bot.slash_command(name="role_level", description="Set a level to be tied to a role")
@option(
	"l_name",
	description="Choose a role to edit",
	choices=["Newbie", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster", "Exalted", "Galaxy", "Konami"]
	)
@commands.has_permissions(manage_messages=True)
async def role_level(
	ctx: discord.ApplicationContext,
	l_name: str,
	role: Option(discord.Role, "Select a role to link to this level", required=True)
):
	await update_roles(ctx.guild, l_name, role.id)
	await ctx.respond(f"Set the role ID for {l_name} as {role.mention}!")

@bot.slash_command(name="import_channel", description="In the channel this command is used, import activity to Maxima Rank")
@commands.has_permissions(manage_messages=True)
async def import_channel(
	ctx: discord.ApplicationContext
):
	s_time = time.time()
	i = 0
	await ctx.respond(f"Now getting the channel activity for all users in {ctx.channel.mention}.")
	await update_xp_boost(ctx.guild, True, 1, True)
	msg_dict = {}
	att_dict = {}
	emb_dict = {}
	stk_dict = {}

	#* Make dicts of each activity with {user_id: messages} etc.
	bot_msg = await ctx.channel.send(f"Currently 0 messages in...\n*(Activity tracking is disabled while running)*\n*(This may take awhile. Expect ~5000 messages/minute)*")
	async for message in ctx.history(limit=100000):
		# Ignore bots
		if message.author.bot == True:
			i += 1
			continue

		# Message counts
		data, user = await update_user(
			message.guild, message.author.id, message.author.name,
			"messages",
			False, 1, 5, 1, 1
			)

		if user["user_id"] not in msg_dict.keys():
			msg_dict[user["user_id"]] = 1
		else:
			msg_dict[user["user_id"]] += 1

		# print(f"{message.author.name}: Message XP Added")

		# Image counts
		if message.attachments != []:
			data, user = await update_user(
				message.guild, message.author.id, message.author.name,
				"images",
				False, 1, 5, 1, 1
				)

			if user["user_id"] not in att_dict.keys():
				att_dict[user["user_id"]] = 1
			else:
				att_dict[user["user_id"]] += 1

		# print(f"{message.author.name}: Message XP Added")

		# Embed counts
		if message.embeds != []:
			data, user = await update_user(
				message.guild, message.author.id, message.author.name,
				"embeds",
				False, 1, 5, 1, 1
				)

			if user["user_id"] not in emb_dict.keys():
				emb_dict[user["user_id"]] = 1
			else:
				emb_dict[user["user_id"]] += 1

		# print(f"{message.author.name}: Message XP Added")

		# Sticker counts
		if message.stickers != []:
			data, user = await update_user(
				message.guild, message.author.id, message.author.name,
				"stickers",
				False, 1, 3, 1, 1
				)

			if user["user_id"] not in stk_dict.keys():
				stk_dict[user["user_id"]] = 1
			else:
				stk_dict[user["user_id"]] += 1

		# print(f"{message.author.name}: Message XP Added")

		# i = History count
		i += 1
		if i % 250 == 0:
			await bot_msg.edit(content=f"Currently {i} messages in...\n*(Activity tracking is disabled while running)*\n*(This may take awhile. Expect ~5000 messages/minute)*")

	#* Append these dicts into the json file all at once for each user (decrease I/O operations)
	# Messages
	await bot_msg.edit(content=f"Finished reading all data! Now adding activity and XP to each user.\nCurrently on messages...")
	for users, messages in msg_dict.items():
		print(f"Added {users} messages count")
		member = ctx.guild.get_member(users)
		try:
			await update_user(
				member.guild, member.id, member.name,
				"messages",
				True, messages, 5, messages, 1
				)
			# Check if user levels up to a new rank, send special embed if True
			await check_rank(
				member.guild.system_channel.send,
				member.guild,
				member.guild.id,
				member.id,
				member.name,
				member.display_avatar
				)
		except AttributeError:
			pass
		except json.JSONDecodeError:
			pass
		await asyncio.sleep(0.1)

	await bot_msg.edit(content=f"Finished reading all data! Now adding activity and XP to each user.\nCurrently on images...")
	# Images
	for users, images in att_dict.items():
		print(f"Added {users} images count")
		member = ctx.guild.get_member(users)
		try:
			await update_user(
				member.guild, member.id, member.name,
				"images",
				True, images, 5, images, 1
				)
			# Check if user levels up to a new rank, send special embed if True
			await check_rank(
				member.guild.system_channel.send,
				member.guild,
				member.guild.id,
				member.id,
				member.name,
				member.display_avatar
				)
		except AttributeError:
			pass
		except json.JSONDecodeError:
			pass
		await asyncio.sleep(0.1)

	await bot_msg.edit(content=f"Finished reading all data! Now adding activity and XP to each user.\nCurrently on embeds...")
	# Embeds
	for users, embeds in emb_dict.items():
		print(f"Added {users} embeds count")
		member = ctx.guild.get_member(users)
		try:
			await update_user(
				member.guild, member.id, member.name,
				"embeds",
				True, embeds, 5, embeds, 1
				)
			# Check if user levels up to a new rank, send special embed if True
			await check_rank(
				member.guild.system_channel.send,
				member.guild,
				member.guild.id,
				member.id,
				member.name,
				member.display_avatar
				)
		except AttributeError:
			pass
		except json.JSONDecodeError:
			pass
		await asyncio.sleep(0.1)

	await bot_msg.edit(content=f"Finished reading all data! Now adding activity and XP to each user.\nCurrently on stickers...")
	# Stickers
	for users, stickers in stk_dict.items():
		print(f"Added {users} sticker count")
		member = ctx.guild.get_member(users)
		try:
			await update_user(
				member.guild, member.id, member.name,
				"stickers",
				True, stickers, 3, stickers, 1
				)
			# Check if user levels up to a new rank, send special embed if True
			await check_rank(
				member.guild.system_channel.send,
				member.guild,
				member.guild.id,
				member.id,
				member.name,
				member.display_avatar
				)
		except AttributeError:
			pass
		except json.JSONDecodeError:
			pass
		await asyncio.sleep(0.1)

	e_time = time.time()
	t_time = e_time - s_time
	f_t_time = "{:.0f}".format(t_time)
	await bot_msg.delete()
	if t_time <= 1:
		await ctx.channel.send(f"**Total Messages:** {i} in {message.channel.mention}.\n**Time taken:** < 1 second")
	else:
		await ctx.channel.send(f"**Total Messages:** {i} in {message.channel.mention}.\n**Time taken:** {f_t_time} seconds")
	await update_xp_boost(ctx.guild, True, 1, False)

@bot.slash_command(name="ignore_channel", description="Set a channel to ignore")
@option("channel", description="Put in a channel ID to ignore", required=True)
@commands.has_permissions(manage_messages=True)
async def ignore_channel(
	ctx: discord.ApplicationContext,
	channel: str,
):
	if len(channel) != 18:
		await ctx.respond(f"Please enter a valid channel ID")
		return
	try:
		channel = int(channel)
	except ValueError:
		await ctx.respond(f"Please enter a valid channel ID")
		return

	await update_channel_ignore(ctx.guild.name, ctx.guild_id, channel)
	await ctx.respond(f"The selected channel is now ignored")

@bot.slash_command(name="restart", description="Restart the bot")
@commands.has_permissions(manage_messages=True)
async def restart(ctx):
	await ctx.respond("Restarting Kanade Bot")
	os.execv(sys.executable, ['python3'] + sys.argv)

@bot.slash_command(name="gitpull", description="Pull latest version from Github repo")
@commands.has_permissions(manage_messages=True)
async def gitpull(ctx):
	await ctx.respond(os.popen('git pull').read())

@bot.slash_command(name="setup", description="What to do on first joining")
@commands.has_permissions(manage_messages=True)
async def setup(ctx):
	await ctx.respond(f"1. Add any channels you want to ignore with: ```/ignore_channel```\n2. Add roles you want to assign to ranks in the bot with: ```/role_level```\n3. Make new levels and XP barriers to your liking with: ```/make_levels```\n4. Should just work and track activity!")

@bot.slash_command(name="reset_users", description="Reset all user activity (DANGEROUS! MAKE SURE YOU REALLY WANT TO DO THIS)")
@commands.has_permissions(manage_messages=True)
async def reset_users(ctx):
	guild_name = ctx.guild
	os.remove(f"Data/{guild_name} Users.json")
	await ctx.respond(f"User activity for {guild_name} has been reset!")

#! Error handling for permissions

# @adminhelp.error
# async def permission_errors(ctx, error):
#     if isinstance(error, MissingPermissions):
#         await ctx.respond(":warning: You don't have permission to do this!")

# @award_xp.error
# async def permission_errors(ctx, error):
#     if isinstance(error, MissingPermissions):
#         await ctx.respond(":warning: You don't have permission to do this!")

# @role_xp.error
# async def permission_errors(ctx, error):
#     if isinstance(error, MissingPermissions):
#         await ctx.respond(":warning: You don't have permission to do this!")

# @invite_xp.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

# @booster_xp.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

# @xp_boost.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

# @xp_boost_end.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

# @make_levels.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

# @role_level.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

# @import_channel.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

# @ignore_channel.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

# @restart.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

# @gitpull.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

# @setup.error
# async def permission_errors(ctx, error):
# 	if isinstance(error, MissingPermissions):
# 		await ctx.respond(":warning: You don't have permission to do this!")

bot.run(TOKEN)
