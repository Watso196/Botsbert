import discord
from discord.ext import commands
import json
import random
import time

BASE_COOLDOWN = 30  # Seconds between insults
MAX_INSULTS_BEFORE_FLUSTERED = 2
RESET_TIME = 300  # Reset counter if it's been 5 minutes

class OsbertInsults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}  # user_id -> {"last_insult": time, "count": int}

        with open("data/insults.json", "r", encoding="utf-8") as f:
            self.insults = json.load(f)

        self.flustered_lines = [
            "*No, I can't! I already said something rude! Let me recover!*",
            "*Please! I'm flickering with guilt!*",
            "*Being cruel is emotionally exhausting, okay??? I'm done for now!*",
            "*What if they cry?! What if **I** cry?? I can't do it.*",
            "*No! I'm not just a floating skull with feelings—I'm a floating skull with **regrets**.*"
        ]

    @commands.command(name="insult")
    async def insult(self, ctx, member: discord.Member):
        now = time.time()
        user_id = str(member.id)

        cooldown = self.cooldowns.get(user_id, {"last_insult": 0, "count": 0})

        # Reset count if enough time has passed
        if now - cooldown["last_insult"] > RESET_TIME:
            cooldown["count"] = 0

        # Flustered if too many recent insults
        if cooldown["count"] >= MAX_INSULTS_BEFORE_FLUSTERED and now - cooldown["last_insult"] < BASE_COOLDOWN:
            await ctx.send(random.choice(self.flustered_lines))
            return

        # Choose insult
        if user_id in self.insults.get("user_specific", {}):
            pool = self.insults["user_specific"][user_id]
            insult = random.choice(pool)
        else:
            insult = random.choice(self.insults["general"])

        cooldown["last_insult"] = now
        cooldown["count"] += 1
        self.cooldowns[user_id] = cooldown

        await ctx.send(f"{member.mention}, {insult}")

# ✅ Setup method so your bot can load the cog
async def setup(bot):
    await bot.add_cog(OsbertInsults(bot))
