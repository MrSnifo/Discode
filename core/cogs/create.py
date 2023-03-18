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
from ..utils import embed_wrong, period, text_to_seconds, generate_code
# ------ Discord ------
from discord import Interaction, app_commands, ui, Role, Embed
from discord.ext.commands import Cog
# ------ Datetime ------
from datetime import datetime, timedelta


class Create(Cog):
    __slots__ = "bot"

    def __init__(self, bot: Bot) -> None:
        """
        Create code slash command
        """
        self.bot = bot

    @app_commands.command(name="create", description="Create a code.")
    @app_commands.default_permissions(administrator=True)
    async def slash(self, interaction: Interaction, role: Role, code: str = None) -> None:
        bot_role = interaction.guild.get_member(self.bot.user.id).top_role
        # Checks if the bot top role higher than the role that will give.
        if bot_role > role:
            async with Database() as db:
                try:
                    if code is None:
                        while True:
                            # Generating a random code.
                            code = generate_code(n=4)
                            # Checks if the code exist.
                            await db.get_code(code=code, guild_id=interaction.guild_id)
                    else:
                        await db.get_code(code=code, guild_id=interaction.guild_id)
                    embed = embed_wrong(msg=f"Code is already exists")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except Errors.CodeNotFound:
                    modal = MyModal(code=code, role=role)
                    await interaction.response.send_modal(modal)
        else:
            embed = embed_wrong(msg=f"{bot_role.mention} Role have to be Higher then {role.mention}.")
            await interaction.response.send_message(embed=embed, ephemeral=True)


class MyModal(ui.Modal):
    __slots__ = ("code", "role_id", "expire_in", "role_expire_time", "max_uses")

    def __init__(self, code: str, role: Role):
        self.code = code
        self.role = role

        super().__init__(title=f"Editing {code}")

        self.expire_in = ui.TextInput(label="Code expire in",
                                      placeholder="Leave it empty for lifetime use",
                                      required=False)

        self.role_expire_time = ui.TextInput(label="Role expire time",
                                             placeholder="Leave it empty for lifetime role",
                                             required=False)

        self.max_uses = ui.TextInput(label="Max uses", placeholder="Leave it empty for unlimited uses",
                                     required=False)

        for item in [self.expire_in, self.max_uses, self.role_expire_time]:
            self.add_item(item)

    async def on_submit(self, interaction: Interaction) -> None:
        try:
            expire_in = None
            role_expire_time = None
            max_uses = None
            # Code expire time.
            if str(self.expire_in.value) != "":
                expire_in = datetime.now().replace(microsecond=0) \
                            + timedelta(seconds=text_to_seconds(text=str(self.expire_in.value)))
            # Role expire time
            if str(self.role_expire_time.value) != "":
                role_expire_time = text_to_seconds(text=str(self.role_expire_time.value))
            # Max code uses.
            if str(self.max_uses.value) != "":
                max_uses = abs(int(self.max_uses.value))
            async with Database() as db:
                try:
                    # -----------------
                    # Creating the code.
                    guild = await db.create_code(guild_id=interaction.guild_id,
                                                 code=self.code,
                                                 expire_in=expire_in,
                                                 max_uses=max_uses,
                                                 role_id=self.role.id,
                                                 role_expire_time=role_expire_time)
                    timestamp = f"<t:{int(datetime.timestamp(datetime.now() if expire_in is None else expire_in))}:R>"
                    duration = period(timedelta(seconds=role_expire_time)) if \
                        role_expire_time is not None else "lifetime"
                    description = \
                        f"> ||{self.code}||\n\n" \
                        f"Expire: {timestamp if expire_in is not None else '`lifetime`'}\n " \
                        f"Max Uses: `{max_uses if max_uses is not None else 'unlimited'}`\n " \
                        f"Role:{self.role.mention}\n " \
                        f"Duration: `{duration}`"
                    embed = Embed(title="Code as been created!", description=description, colour=0x738adb)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    # Logging
                    await self.logger(interaction=interaction, guild=guild, description=description)
                except Errors.CodeIsAlreadyExists:
                    embed = embed_wrong(msg=f"Code is already exists")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError:
            embed = embed_wrong(msg=f"Invalid Modal values.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @staticmethod
    async def logger(interaction: Interaction, guild: dict, description: str) -> None:
        if guild["channel_id"] is not None:
            channel = interaction.guild.get_channel(guild["channel_id"])
            if channel is not None:
                embed = Embed(title="Created a code", description=description, colour=0x1f8b4c)
                if interaction.user.avatar is None:
                    embed.set_author(name=interaction.user)
                else:
                    embed.set_author(name=interaction.user,
                                     icon_url=interaction.user.avatar.url)
                await channel.send(embed=embed)


async def setup(bot) -> None: await bot.add_cog(Create(bot))
