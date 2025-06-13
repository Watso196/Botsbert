import discord
from discord.ext import commands
import json
import random
import time

INSULT_COOLDOWN = 30  # 30 seconds per user
INSULT_BAIL_CHANCE = 0.15

class OsbertInsults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}  # user_id -> last insult time

        # Load insults from file
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

        # Cooldown check
        if user_id in self.cooldowns and now - self.cooldowns[user_id] < INSULT_COOLDOWN:
            await ctx.send(random.choice(self.flustered_lines))
            return

        # Bail-out chance
        if random.random() < INSULT_BAIL_CHANCE:
            await ctx.send("*No, I don't want to keep being mean!*")
            return

        # Select insult
        if user_id in self.insults.get("user_specific", {}):
            pool = self.insults["user_specific"][user_id]
            insult = random.choice(pool) if random.random() < 0.7 else random.choice(self.insults["general"])
        else:
            insult = random.choice(self.insults["general"])

        self.cooldowns[user_id] = now
        await ctx.send(f"{member.mention}, {insult}")


async def setup(bot):
    await bot.add_cog(OsbertInsults(bot))
