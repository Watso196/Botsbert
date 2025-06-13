import discord
from discord.ext import commands
import json
import os

LOOT_FILE = "data/loot.json"

# Ensure the loot file exists
def ensure_loot_file():
    if not os.path.exists(LOOT_FILE):
        with open(LOOT_FILE, "w", encoding="utf-8") as f:
            json.dump({"gold": 0, "items": []}, f)

def load_loot():
    with open(LOOT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_loot(data):
    with open(LOOT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class LootTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        ensure_loot_file()

    @commands.command(name="loot")
    async def manage_loot(self, ctx, subcommand=None, *args):
        loot = load_loot()

        if subcommand is None:
            items = "\n".join(f"- {item}" for item in loot["items"]) or "*None*"
            await ctx.send(f"**Party Gold:** {loot['gold']} gp\n**Items:**\n{items}")
            return

        sub = subcommand.lower()

        if sub == "gold":
            await ctx.send(f"The party has **{loot['gold']} gold pieces**.")
        elif sub == "add":
            try:
                amount = int(args[0])
                loot["gold"] += amount
                save_loot(loot)
                await ctx.send(f"Added **{amount} gp**. New total: {loot['gold']} gp.")
            except (IndexError, ValueError):
                await ctx.send("Try `!loot add <amount>` — no funny business.")
        elif sub == "remove":
            try:
                amount = int(args[0])
                loot["gold"] = max(0, loot["gold"] - amount)
                save_loot(loot)
                await ctx.send(f"Removed **{amount} gp**. New total: {loot['gold']} gp.")
            except (IndexError, ValueError):
                await ctx.send("Try `!loot remove <amount>` and be careful with the coins!")
        elif sub == "item":
            item_name = " ".join(args).strip()
            if item_name:
                loot["items"].append(item_name)
                save_loot(loot)
                await ctx.send(f"Added **{item_name}** to the party inventory.")
            else:
                await ctx.send("You need to name the item, genius. Try `!loot item Potion of Speed`.")
        elif sub == "removeitem":
            item_name = " ".join(args).strip()
            if item_name in loot["items"]:
                loot["items"].remove(item_name)
                save_loot(loot)
                await ctx.send(f"Removed **{item_name}** from the inventory.")
            else:
                await ctx.send(f"Couldn’t find **{item_name}** in the inventory!")
        elif sub == "items":
            items = "\n".join(f"- {item}" for item in loot["items"]) or "*None*"
            await ctx.send(f"**Party Inventory:**\n{items}")
        else:
            await ctx.send("Unrecognized subcommand. Try `!loot`, `!loot add`, `!loot item`, etc.")

async def setup(bot):
    await bot.add_cog(LootTracker(bot))
