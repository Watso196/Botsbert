from discord.ext import commands
import random
import json
import os

DATA_PATH = "data"
CHAOS_STATE_FILE = os.path.join(DATA_PATH, "chaos_state.json")
CHAOS_TABLE_FILE = os.path.join(DATA_PATH, "chaos_table.json")
BASE_DC = 2 

class ChaosMagic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if not os.path.exists(CHAOS_STATE_FILE):
            self.save_dc(BASE_DC)
        self.dc = self.load_dc()

    def load_dc(self):
        try:
            with open(CHAOS_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("dc", BASE_DC)
        except (FileNotFoundError, json.JSONDecodeError):
            return BASE_DC

    def save_dc(self, dc):
        with open(CHAOS_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"dc": dc}, f, indent=4)

    def load_chaos_table(self):
        try:
            with open(CHAOS_TABLE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @commands.group(name="chaos", invoke_without_command=True)
    async def chaos(self, ctx):
        """Roll the chaos d20 and resolve effects."""
        chaos_table = self.load_chaos_table()
        roll = random.randint(1, 20)
        dc = self.dc

        if roll >= dc:
            increment = 2 if roll == 20 else 1
            self.dc = dc + increment
            self.save_dc(self.dc)
            if roll == 20:
                await ctx.send(f"{ctx.author.mention} rolled a **{roll}** against DC {dc} — Whoa, you're on fire, Droo! 🔥 DC increases by 2 and is now **{self.dc}**.")
            else:
                await ctx.send(f"{ctx.author.mention} rolled a **{roll}** against DC {dc} — You hold it together for now. DC is now **{self.dc}**."
        )


        else:
            chaos_roll = random.randint(1, 100)
            effect = chaos_table.get(str(chaos_roll), "The chaos magic fizzles unexpectedly.")
            self.dc = BASE_DC
            self.save_dc(self.dc)
            await ctx.send(
                f"{ctx.author.mention} rolled a **{roll}** against DC {dc} and failed!\n"
                f"Chaos d100 roll: **{chaos_roll}**\n"
                f"Effect: {effect}\n"
                f"Chaos DC resets to **{self.dc}**."
            )

    @chaos.command(name="dc")
    async def chaos_dc(self, ctx):
        """Show the current Chaos Magic DC."""
        await ctx.send(f"The current Chaos Magic DC is **{self.dc}**.")

async def setup(bot):
    await bot.add_cog(ChaosMagic(bot))
