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


class Redeem(Cog):
    __slots__ = "bot"

    def __init__(self, bot: Bot) -> None:
        """
        Redeem a code slash command
        """
        self.bot = bot

    @app_commands.command(name="redeem", description="Redeem a code that gives you a role.")
    async def slash(self, interaction: Interaction, code: str) -> None:
        async with Database() as db:
            try:
                guild: dict = await db.redeem(guild_id=interaction.guild_id, code=code, user_id=interaction.user.id)
                role = interaction.guild.get_role(guild["role"]["id"])
                # Role time format
                if guild["role"]["expire_time"] is not None:
                    time = datetime.now().replace(microsecond=0) + \
                           timedelta(seconds=guild["role"]["expire_time"])
                    timestamp = f"<t:{int(datetime.timestamp(time))}:R>"
                    duration = period(timedelta(seconds=guild["role"]["expire_time"]))
                else:
                    duration = "lifetime"
                    timestamp = duration
                await self.logger(interaction=interaction, guild=guild, code=code, timestamp=timestamp)
                if role is not None:
                    bot_role = interaction.guild.get_member(self.bot.user.id).top_role
                    # Checks if the bot top role higher than the role that will give.
                    if bot_role > role:
                        await interaction.user.add_roles(role)
                        description = \
                            f"> ||{code}||\n\n" \
                            f"Role: <@&{guild['role']['id']}>\n " \
                            f"Duration: `{duration}`"
                        embed = Embed(title="Successfully redeemed", description=description, colour=0x738adb)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                    else:
                        embed = embed_wrong(msg=f"Unable to add role\n"
                                                f"{bot_role.mention} Role have to be Higher then {role.mention}\n"
                                                f"> Please contact server administrator")
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = embed_wrong(msg=f"Role not found\n> Please contact server administrator")
                    await interaction.response.send_message(embed=embed)

            except Errors.CodeNotFound:
                embed = embed_wrong(msg=f"Code is not found")
                await interaction.response.send_message(embed=embed, ephemeral=True)

            except Errors.CodeExpired:
                embed = embed_wrong(msg=f"Code is expired")
                await interaction.response.send_message(embed=embed, ephemeral=True)

            except Errors.CodeAlreadyUsed:
                embed = embed_wrong(msg=f"Code is already used")
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @staticmethod
    async def logger(interaction: Interaction, guild: dict, code: str, timestamp: str) -> None:
        if guild["guild"]["channel_id"] is not None:
            channel = interaction.guild.get_channel(guild["guild"]["channel_id"])
            if channel is not None:
                description = \
                    f"> ||{code}||\n\n" \
                    f"Role: <@&{guild['role']['id']}>\n " \
                    f"Expire: {timestamp}"
                embed = Embed(title="Redeemed a code", description=description, colour=0xf1c40f)
                if interaction.user.avatar is None:
                    embed.set_author(name=interaction.user)
                else:
                    embed.set_author(name=interaction.user,
                                     icon_url=interaction.user.avatar.url)
                await channel.send(embed=embed)


async def setup(bot) -> None: await bot.add_cog(Redeem(bot))
