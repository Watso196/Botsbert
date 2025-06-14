import discord
from discord.ext import commands
import json
import random
import time

COOLDOWN = 60  # seconds
CHANCE = 0.35  # percentage chance

class OsbertMisfires(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_misfire_times = {}  # Track cooldowns per category

        # Load misfire data
        with open("data/interjections.json", "r", encoding="utf-8") as f:
            self.misfire_data = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()
        current_time = time.time()

        for category, data in self.misfire_data.items():
            last_time = self.last_misfire_times.get(category, 0)
            if current_time - last_time >= COOLDOWN:
                if any(trigger in content for trigger in data["triggers"]):
                    if random.random() < CHANCE:
                        response = random.choice(data["responses"])
                        await message.channel.send(response)
                        self.last_misfire_times[category] = current_time
                        break  # Still only one response per message

async def setup(bot):
    await bot.add_cog(OsbertMisfires(bot))
