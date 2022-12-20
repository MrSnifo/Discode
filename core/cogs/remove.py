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
from ..bot import Bot
from ..models import Database, Errors
from ..utils import embed_wrong
# ------ Discord ------
from discord import Interaction, app_commands, Embed
from discord.ext.commands import Cog


class Remove(Cog):
    __slots__ = "bot"

    def __init__(self, bot: Bot) -> None:
        """
        Remove code slash command
        """
        self.bot = bot

    @app_commands.command(name="remove", description="Remove a code.")
    @app_commands.default_permissions(administrator=True)
    async def slash(self, interaction: Interaction, code: str) -> None:
        async with Database() as db:
            try:
                guild = await db.remove_code(guild_id=interaction.guild_id, code=code)
                embed = Embed(title="Code as been removed!", description=f"> `{code}`", colour=0x738adb)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                await self.logger(interaction=interaction, guild=guild, code=code)
            except Errors.CodeNotFound:
                embed = embed_wrong(msg=f"Code is not found")
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @staticmethod
    async def logger(interaction: Interaction, guild: dict, code: str) -> None:
        if guild["channel_id"] is not None:
            channel = interaction.guild.get_channel(guild["channel_id"])
            if channel is not None:
                embed = Embed(title="Removed a code", description=f"> `{code}`", colour=0xe74c3c)
                if interaction.user.avatar is None:
                    embed.set_author(name=interaction.user)
                else:
                    embed.set_author(name=interaction.user,
                                     icon_url=interaction.user.avatar.url)
                await channel.send(embed=embed)


async def setup(bot) -> None: await bot.add_cog(Remove(bot))
