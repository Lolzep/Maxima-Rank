# **Monke Rank**

This is mainly a way to replace ActivityRank in our current server (Nanahira Monke). Trying to have less reliance on random bots from outside sources and by making our own bot, we'll have full customization and features that ActivityRank won't have (such as extra XP for boosted members or adding role images to users).

Probably will be appended into [kanadeBot](https://github.com/LEOIIDX/kanadeBot) at some point, but should get working standalone first to make sure it gets put in smoothly.

#### **TODO:**
- **In progress** Change roles in a server depending on level of user 
- **In progress** Create embeds that show users level, xp, message count, etc. 
- **In progress** Create a leaderboard of all top users in the server that shows xp, level, messages, etc. 
- Transfer over/export current ActivityRank levels to this bot (will need to be done manually but not too hard)
- Special things for boosted members, such as extra xp
- Return of a special ranking...
- Amount of channels active in the past week
- Guess future ranks and time of arrival by extrapolation?
- Make a command that gives extra xp for a specified amount of time (used for an event in the server to promote engagement)

#### **Done!:**
- ~~Create new users in the users.json file~~
- ~~Be able to calculate each of the values inside the users.json file~~
- ~~Track voice call time in minutes~~
- ~~Track new things that ActivityRanker does not: Reaction counts, images/embeds sent counts~~
- ~~Send an embed using a command to show the current user's level and activity~~
