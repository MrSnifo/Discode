"""
The MIT License (MIT)

Copyright (c) 2022-present MrSniFo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

# ------ Core ------
from .models import logger

# ------ Discord ------
import discord
from discord.ext import commands
from discord.errors import LoginFailure, DiscordException

# ------ Environment ------
from dotenv import load_dotenv
from pathlib import Path
import os


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents, command_prefix=None)
        # logging event.
        self.logger = logger()

    async def on_connect(self) -> None:
        self.logger.info(f"Connected as {self.user} with ID {self.user.id}")

    async def on_ready(self) -> None:
        """
        This function called when the bot is ready.
        """
        self.logger.info(msg=f"Bot is now ready with latency of {self.latency * 1000:,.0f}ms")
        self.logger.info(msg=f"Invitation link:"
                             f" https://discord.com/api/oauth2/authorize?client_id={self.application_id}"
                             f"&permissions=8&scope=bot%20applications.commands")

    async def setup_hook(self) -> None:
        # ------------------
        # Loading extensions.
        for extension in ["code", "create", "remove", "redeem", "logging", "loop"]:
            try:
                await self.load_extension(name=f'core.cogs.{extension}')
            except DiscordException:
                self.logger.error(msg=f"Unable to load `{extension}` extension.")
        # -------------------
        # sync slash commands.
        # syncing globally may take an hour.
        await self.tree.sync()

    async def run_bot(self) -> None:
        async with self:
            try:
                # -----------------------------
                # Loading bot environment TOKEN.
                dotenv_path = Path('.env')
                load_dotenv(dotenv_path=dotenv_path)
                token = os.getenv('TOKEN')
                self.logger.info("Launching the bot...")
                if (token is not None) and token:
                    await self.start(token=os.getenv('TOKEN'), reconnect=True)
                else:
                    self.logger.error(msg=f"Bot environment TOKEN not found.")
            except LoginFailure as error:
                self.logger.error(msg=f"Login failed due to {error}.")
