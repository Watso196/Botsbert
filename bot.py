# bot.py
import discord
from discord.ext import commands
import random
from config import TOKEN, PREFIX
from utils.response_picker import get_random_response
import asyncio
import re
import json

### TO DO LIST
# Create a !gossip command - player can ask Osbert about a topic or tell him about something.
#   He will potentially store their opinion in his gossip responses

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True  # Important for reading messages
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"Botsbert is online! Logged in as {bot.user.name}")

@bot.command(name="joke")
async def tell_joke(ctx):
    joke = get_random_response("data/jokes.json")
    await ctx.send(joke)

@bot.command(name="compliment")
async def compliment(ctx, member: discord.Member):
    with open("data/compliments.json", "r", encoding="utf-8") as f:
        compliments = json.load(f)

    user_id = str(member.id)
    if user_id in compliments.get("user_specific", {}):
        pool = compliments["user_specific"][user_id]
        # 70% chance for specific, 30% fallback to general
        if random.random() < 0.7:
            compliment = random.choice(pool)
        else:
            compliment = random.choice(compliments["general"])
    else:
        compliment = random.choice(compliments["general"])

    await ctx.send(f"{member.mention}, {compliment}")


@bot.command(name="flashback")
async def flashback(ctx):
    memory = get_random_response("data/flashbacks.json")
    await ctx.send(f"*{memory}*")

    # 50% chance of a follow-up
    if random.random() < 0.35:
        follow_ups = [
            "Anyway, want to see me eat a bug? They always come out black!",
            "Wait, was that out loud??",
            "Ha ha ha! Emotions are weird.",
            "Did I tell you I once swallowed a key? Never found it.",
            "My skull itches when I remember things. Is that normal?"
        ]
        follow_up = random.choice(follow_ups)
        await ctx.send(follow_up)


@bot.command(name="roll")
async def roll_dice(ctx, *, dice: str):
    advantage = "adv" in dice
    disadvantage = "dis" in dice
    dice = dice.replace("adv", "").replace("dis", "").strip()

    match = re.fullmatch(r"(\d*)d(\d+)([+-]\d+)?", dice.replace(" ", ""))
    if not match:
        await ctx.send("That doesn't look like a proper roll, bonehead! Try `!roll d20` or `!roll d20 adv`.")
        return

    num_dice = int(match.group(1)) if match.group(1) else 1
    dice_sides = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0

    if num_dice > 100 or dice_sides > 1000:
        await ctx.send("That's too many dice! I can't handle the math!!!")
        return

    # ADV/DIS handling
    if (advantage or disadvantage):
        if num_dice != 1 or dice_sides != 20:
            await ctx.send("Advantage/Disadvantage only works on a single d20, foolish flesh-person.")
            return
        first = random.randint(1, 20)
        second = random.randint(1, 20)
        chosen = max(first, second) if advantage else min(first, second)
        total = chosen + modifier
        roll_type = "Advantage" if advantage else "Disadvantage"
        if chosen == 20:
            emoji = "🎯"
            flair = "🔥 NAT 20!! 🔥 *You’re on fire! Wait… that's me!*"
        elif chosen == 1:
            emoji = "💀"
            flair = "💀 NAT 1... 💀 *Oh no... oh no, oh no.*"
        else:
            emoji = ""
            flair = get_random_response("data/roll_flairs.json")
        await ctx.send(
            f"{ctx.author.mention} rolled with **{roll_type}**:\n"
            f"→ `{first}` and `{second}` → Chose **{chosen}** + {modifier} = **{total}**\n"
            f"{emoji} *{flair}*"
        )
    else:
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        rolls_str = " + ".join(str(r) for r in rolls)
        if dice_sides == 20 and num_dice == 1:
            if rolls[0] == 20:
                emoji = "🎯"
                flair = "🔥 NAT 20!! 🔥 I haven't seen a shot that hot since I got set on fire permanently!"
            elif rolls[0] == 1:
                emoji = "💀"
                flair = "💀 NAT 1... 💀 Somebody do something quick! Save their skin!"
            else:
                emoji = ""
                flair = get_random_response("data/roll_flairs.json")
        else:
            emoji = ""
            flair = get_random_response("data/roll_flairs.json")

        await ctx.send(
            f"{ctx.author.mention} rolled: `{rolls_str}` + {modifier} = **{total}**\n"
            f"{emoji} *{flair}*"
        )
        

@bot.command(name="osbert")
async def help_command(ctx):
    embed = discord.Embed(
        title="🧠 Osbert’s Skills",
        description="*You rang? Here’s what I remember I can do!*",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🎭 Social Commands",
        value=(
            "`!joke` – I tell a joke. Quality not guaranteed.\n"
            "`!compliment @user` – I say something nice. It's fun for everyone!\n"
            "`!insult @user` – I give someone an insult. But I won't like it!\n"
            "`!flashback` – I share a randomly recalled memory. Sometimes sad.\n"
        ),
        inline=False
    )

    embed.add_field(
        name="🎲 Dice Rolling",
        value=(
            "`!roll d20` – Roll a d20. You can also use `adv` or `dis` for advantage/disadvantage.\n"
            "`!roll 2d6+1` – Roll multiple dice and apply a modifier. I handle the math!\n"
        ),
        inline=False
    )

    embed.add_field(
        name="🔮 Chaos Magic",
        value=(
            "`!chaos` – Check for a surge of wild magical energy on Droo's behalf. I also track the DC and roll on the table!\n",
            "`!chaos rest` - Reset the DC when you take a long rest.\n",
            "`!chaos dc` - Check the current Chaos Magic DC."
        ),
        inline=False
    )

    embed.add_field(
        name="💰 Loot Management",
        value=(
            "`!loot` – View the party’s shared inventory and gold.\n"
            "`!loot add <item>` – Add an item or gold (e.g., `!loot add 100`).\n"
            "`!loot remove <item>` – Remove an item from the inventory.\n"
            "`!loot gold` - Check the current funds.\n"
            "`!loot add/sub <amount>` – Add or subtract gold from party funds.\n"
        ),
        inline=False
    )

    embed.add_field(
        name="📝 Remember Info",
        value=(
            "`!recall add` - Add a note that Osbert can recall later. Though he may not always recall info right away...\n"
            "`!recall list - List all of the notes Osbert has been asked to remember.`\n"
            "`!recall forget <id> - Remove a note that was previously added.`\n"
            "`!recall <search term> - Search for a specific note that was previously added.`\n"
        ),
        inline=False
    )

    embed.add_field(
        name=" Gossip",
        value=(
            "`!gossip <topic>` - Ask Osbert his opinion on a topic, such as a person or place!\n"
            "`!gossip <topic> : <your thoughts>` - Tell Osbert your opinion about a topic! He may adopt it as one of his own views.\n"
        )
    )

    embed.set_footer(text="That’s all I can recall. I might remember more if someone gave me an update!")

    await ctx.send(embed=embed)


@bot.event
async def on_message(message):
    await bot.process_commands(message)



# Load extensions and run bot
async def main():
    await bot.load_extension("cogs.loot_tracker")
    await bot.load_extension("cogs.chaos_magic")
    await bot.load_extension("cogs.interjections")
    await bot.load_extension("cogs.insults")
    await bot.load_extension("cogs.recall")
    await bot.load_extension("cogs.gossip")

    await bot.start(TOKEN)


asyncio.run(main())
