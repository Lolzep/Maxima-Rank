import discord
import os
import asyncio

from discord.commands import Option
from discord.ext import commands
from dotenv import load_dotenv
from myfunctions import update_user, my_rank_embed_values
from embeds import *

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = discord.Bot(intents=intents, debug_guilds=[273567091368656898, 828667775605669888])

#? Command ideas!

#? Small projects
#* def about(): Show information about the bot (Defintion, Github commits and changes, Contributors) in an embed
#* def restart(): Put restart_bot def in a command
#* def help(): Shows all commands and generic help info in an embed
#* def booster(): Retrieve all boosters in a discord server from json, give specified "special_xp" to each booster
# "special_xp" also gets added to "xp"!
#* def invite(ctx, name): Increase "invites" count by 1 for specified user and give specified xp

#? Large projects 
#* def set_xp(): Set all xp values in a slash command embed (admin panel)
#* def top_rankers(): Leaderboard of activity, similar to ActivityRank's style
#* def my_rank(ctx): Shows your ranking and detailed statistics about yourself in an embed
#* def my_progress(ctx): Shows progress to next level and role in an embed

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
	# Ignore bots
	if message.author.bot == True:
		return

	# Image counts
	if message.attachments:
		update_user(message.guild, message.author.id, message.author.name, "images", True, 1, 10, 1)
	
	# Embed counts
	if message.embeds:
		update_user(message.guild, message.author.id, message.author.name, "embeds", True, 1, 10, 1)

	# Sticker counts
	if message.stickers:
		update_user(message.guild, message.author.id, message.author.name, "stickers", True, 1, 10, 1)

	# Message counts
	update_user(message.guild, message.author.id, message.author.name, "messages", True, 1, 5, 1)

	if message.content.startswith("$test"):
		File = discord.File("Images/about.png")
		await message.channel.send(File)

@bot.event
async def on_reaction_add(reaction, user):
	# For reactions added and reactions recieved, add values and xp to respective user
	update_user(user.guild ,user.id, user.name, "reactions_added", True, 1, 5, 1)
	update_user(reaction.message.guild, reaction.message.author.id, reaction.message.author.name, "reactions_recieved", True, 1, 5, 1)


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
		# Update users.json with update voice_minutes and xp
		if before.channel is None and after.channel is None:
			update_user(member.guild ,member.id, member.name, "voice_minutes", True, voice_minutes, 5, voice_minutes)
			print("out_of_channel")
			break

@bot.event
async def on_member_update(before, after):
	if before.premium_since is None and after.premium_since is not None:
		update_user(before.guild, before.id, before.name, "is_booster", True, 0, 1000, 1, True)
	else:
		update_user(before.guild, before.id, before.name, "is_booster", True, 0, 0, 0, False)

@bot.slash_command(description="Sends information about the bot")
async def about(ctx):
	aboutEMBED, aboutFILE = infoEmbeds.aboutEMBED()
	await ctx.respond(file=aboutFILE, embed=aboutEMBED)

@bot.slash_command(description="Commands and their usage")
async def help(ctx):
	helpEMBED, helpFILE = infoEmbeds.helpEMBED()
	await ctx.respond(file=helpFILE, embed=helpEMBED)

@bot.slash_command(name="award_xp", description="Add XP to a specified user or users")
@commands.has_permissions(manage_messages=True)
async def award_xp(ctx: discord.ApplicationContext, member: Option(discord.Member, "Member to get id from", required = True), xp: Option(int, "Amount of XP to give to user", required=True)):
	update_user(member.guild ,member.id, member.name, "special_xp", True, xp, xp, 1)
	await ctx.respond(f"You gave {member.name} {xp} XP!")

@bot.slash_command(description="Statistics about yourself")
async def myrank(ctx):
	emoji_object = my_rank_embed_values(ctx.user.guild, ctx.user.id, True)
	in_embed = []
	for item in emoji_object:
		emoji = discord.utils.get(bot.emojis, name=item)
		in_embed.append(emoji)

	myrankEMBED, myrankFILE = infoEmbeds.myrankEMBED(ctx.user.guild, ctx.user.id, ctx.user.display_name, ctx.user.display_avatar, in_embed)
	await ctx.respond(file=myrankFILE, embed=myrankEMBED)

@bot.slash_command(name="rank", description="Statisitcs about a specified user")
async def rank(ctx: discord.ApplicationContext, member: Option(discord.Member, "Member to get id from", required = True)):
	emoji_object = my_rank_embed_values(member.guild, member.id, True)
	in_embed = []
	for item in emoji_object:
		emoji = discord.utils.get(bot.emojis, name=item)
		in_embed.append(emoji)

	rankEMBED, rankFILE = infoEmbeds.rankEMBED(member.guild, member.id, member.display_name, member.display_avatar, in_embed)
	await ctx.respond(file=rankFILE, embed=rankEMBED)

@bot.slash_command(name='greet', description='Greet someone!', guild_ids=[273567091368656898])
async def greet(ctx, name: Option(str, "Enter your friend's name", required = False, default = '')):
    await ctx.respond(f'Hello {name}!')

bot.run(TOKEN)

