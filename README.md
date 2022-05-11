# **Monke Rank**

This is mainly a way to replace ActivityRank in our current server (Nanahira Monke). Trying to have less reliance on random bots from outside sources and by making our own bot, we'll have full customization and features that ActivityRank won't have (such as extra XP for boosted members or adding role images to users).

Probably will be appended into [kanadeBot](kanadeBot) at some point, but should get working standalone first to make sure it gets put in smoothly.

#### **TODO:**
- Create new users in the users.json file
- Be able to calculate each of the values inside the users.json file
- Transfer over/export current ActivityRank levels to this bot (will need to be done manually but not too hard)
- Read off this json file to do things in the Monke server, such as change roles depending on level
- Track new things that ActivityRanker does not: Reaction counts, images/embeds sent counts, amount of channels active in the past week, guess future ranks by extrapolation?
- Special things for boosted members, such as extra xp
- Create embeds that show users level, xp, message count, etc.
- Return of a special ranking...
