import discord
from discord.ext import commands
import json
import os
import random

GOSSIP_PATH = "data/gossips.json"
CHANCE_TO_REMEMBER = 0.35

class GossipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_gossip(self):
        if not os.path.exists(GOSSIP_PATH):
            return {}
        with open(GOSSIP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_gossip(self, data):
        with open(GOSSIP_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


    @commands.command(name="gossip")
    async def gossip(self, ctx, *, text: str):
        # Handle input like: "arolyn: She's totally untrustworthy"
        if ":" in text:
            topic, opinion = [part.strip() for part in text.split(":", 1)]
            topic_key = topic.lower()
            data = self.load_gossip()

            if topic_key not in data:
                data[topic_key] = []

            if random.random() < CHANCE_TO_REMEMBER:
                data[topic_key].append(opinion)
                self.save_gossip(data)
                await ctx.send(f"*Oh, I agree! I'll remember that about {topic}... maybe forever!!*")

            else:
                await ctx.send("*Hmm… interesting. Thanks for sharing with me!*")
        else:
            # Treat it as a request for gossip
            topic_key = text.lower().strip()
            data = self.load_gossip()
            responses = data.get(topic_key, [])
            if responses:
                await ctx.send(f"**About {text}…** {random.choice(responses)}")
            else:
                await ctx.send(f"*I don’t have any opinions about {text}... yet.*")

async def setup(bot):
    await bot.add_cog(GossipCog(bot))
