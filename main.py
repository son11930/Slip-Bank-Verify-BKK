import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True


class SlipVerifyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        if not os.path.exists('./cogs'):
            os.makedirs('./cogs')

        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                await self.load_extension(f'cogs.{filename[:-3]}')

        await self.tree.sync()
        print("Bot is ready and Cogs are loaded.")


bot = SlipVerifyBot()

if __name__ == '__main__':
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables. Please check your .env file.")
    else:
        bot.run(TOKEN)
