from discord.ext import commands
import json
import os
import random

MEMORY_PATH = "data/memories.json"

class MemoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[DEBUG] MemoryCog loaded")

    def load_memories(self):
        if not os.path.exists(MEMORY_PATH):
            return []
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_memories(self, data):
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @commands.command(name="recall")
    async def remember(self, ctx, subcommand=None, *args):
        sub = subcommand.lower() if subcommand else None

        if not sub:
            await ctx.send("Try `!recall add <memory>`, `!recall forget <memory>`, or `!recall <keyword>`.")
            return

        if sub == "add":
            if not args:
                await ctx.send("Try `!recall add <memory>`.")
                return
            memory = " ".join(args)
            memories = self.load_memories()
            memories.append(memory)
            self.save_memories(memories)
            await ctx.send(f"*I’ll try to remember:* \"{memory}\"")

        elif sub == "list":
            memories = self.load_memories()
            if not memories:
                await ctx.send("*I don’t seem to remember anything yet...*")
            else:
                formatted = "\n".join(f"{i+1}. {m}" for i, m in enumerate(memories))
                await ctx.send(f"**Here’s everything I recall:**\n{formatted}")

        elif sub == "forget":
            if not args:
                await ctx.send("Try `!recall forget <number>` or `!recall forget <phrase>`.")
                return

            memories = self.load_memories()
            keyword = " ".join(args).lower()

            # Check if it's a number
            if keyword.isdigit():
                index = int(keyword) - 1
                if 0 <= index < len(memories):
                    removed = memories.pop(index)
                    self.save_memories(memories)
                    await ctx.send(f"*I’ve forgotten:* \"{removed}\"")
                else:
                    await ctx.send("*That memory number doesn't exist! Don't confuse me with brain math!*")
            else:
                updated = [m for m in memories if keyword not in m.lower()]
                if len(updated) == len(memories):
                    await ctx.send("*I don’t remember anything like that to forget!*")
                else:
                    self.save_memories(updated)
                    await ctx.send("*Consider it forgotten... probably.*")

        else:
            # Default: Treat subcommand as a search term
            keyword = " ".join([sub] + list(args)).lower()
            memories = self.load_memories()
            matches = [mem for mem in memories if keyword in mem.lower()]
            if matches:
                response = "**Oh, oh, I do know something like that!**\n" + "\n".join(f"• {mem}" for mem in matches)
            else:
                response = "*Hmmm... I don’t remember anything like that.*"
            await ctx.send(response)


async def setup(bot):
    await bot.add_cog(MemoryCog(bot))
