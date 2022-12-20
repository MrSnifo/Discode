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
from ..models import Database
# ------ Discord ------
from discord import TextChannel, Embed, Member, Role
from discord.ext.commands import Cog
from discord.ext import tasks


class Loop(Cog):
    __slots__ = "bot"

    def __init__(self, bot: Bot) -> None:
        """
        Checks for expired roles
        """
        self.bot = bot
        self.task.start()

    @tasks.loop(seconds=30)
    async def task(self):
        await self.bot.wait_until_ready()
        removes: int = 0
        fails: int = 0
        guild = None
        channel = None

        try:
            async with Database() as db:
                async for user in db.expired_roles():
                    if user["guild_id"] != guild:
                        guild = self.bot.get_guild(user["guild_id"])
                        if (guild is not None) and (user["channel_id"] is not None):
                            channel = guild.get_channel(user["channel_id"])
                    if guild is not None:
                        role = guild.get_role(user["role_id"])
                        member = guild.get_member(user["user_id"])
                        if (role is not None) and (member is not None):
                            # Checks if the bot top role higher than the role that will give.
                            if guild.get_member(self.bot.user.id).top_role > role:
                                await member.remove_roles(role)
                                removes += 1
                                await self.logger(channel=channel, member=member, role=role)
                            else:
                                fails += 1
                        else:
                            fails += 1
                    else:
                        fails += 1

            if fails + removes != 0:
                self.bot.logger.info(f"[LOOP] {removes} roles has been removed with {fails} fails.")

        except Exception as error:
            self.bot.logger.error(error)

    @staticmethod
    async def logger(channel: TextChannel | None, member: Member, role: Role) -> None:
        if channel is not None:
            embed = Embed(description=f"{role.mention} has been removed.", colour=0x71368a)
            if member.avatar is None:
                embed.set_author(name=member)
            else:
                embed.set_author(name=member,
                                 icon_url=member.avatar.url)
            await channel.send(embed=embed)


async def setup(bot) -> None: await bot.add_cog(Loop(bot))

