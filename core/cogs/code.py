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
from ..utils import embed_wrong, period
# ------ Discord ------
from discord import Interaction, app_commands, Embed
from discord.ext.commands import Cog
# ------ Datetime ------
from datetime import datetime, timedelta


class Code(Cog):
    __slots__ = "bot"

    def __init__(self, bot: Bot) -> None:
        """
        Code information slash command
        """
        self.bot = bot

    @app_commands.command(name="code", description="Get information about code")
    @app_commands.default_permissions(administrator=True)
    async def slash(self, interaction: Interaction, code: str) -> None:
        async with Database() as db:
            try:
                get_code: dict = await db.get_code(guild_id=interaction.guild_id, code=code)
                # Code expire time.
                time = datetime.now() if get_code['expires_at'] is None else get_code['expires_at']
                timestamp = f"<t:{int(datetime.timestamp(time))}:R>"
                # Role duration
                if get_code['role']['expire_time'] is not None:
                    duration = period(timedelta(seconds=get_code['role']['expire_time']))
                else:
                    duration = "`lifetime`"
                max_uses = get_code['max_uses'] if get_code['max_uses'] is not None else '∞'
                description = \
                    f"> ||{code}||\n\n" \
                    f"Expire: {timestamp if get_code['expires_at'] is not None else '`lifetime`'}\n " \
                    f"Uses: `[{get_code['uses_count']}/{max_uses}]`\n " \
                    f"Role: <@&{get_code['role']['id']}>\n " \
                    f"Duration: `{duration}`"

                embed = Embed(title="Code information", description=description, colour=0x738adb)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            except Errors.CodeNotFound:
                embed = embed_wrong(msg=f"Code is not found")
                await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot) -> None: await bot.add_cog(Code(bot))
