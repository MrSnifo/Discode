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

from aiosqlite import connect, Connection, Cursor
from datetime import datetime, timedelta
from .errors import Errors


class Database(object):
    __slots__ = ('connection', 'cursor')

    def __init__(self):
        self.connection: Connection | None = None
        self.cursor: Cursor | None = None

    async def __aenter__(self):
        self.connection = await connect(database="guilds.db", detect_types=3)
        self.cursor = await self.connection.cursor()

        # guilds(*id, created_at)
        await self.cursor.execute("""CREATE TABLE IF NOT EXISTS guilds(
                                                            id INTEGER PRIMARY KEY,
                                                            channel INTEGER,
                                                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL);
                                                            """)

        # Roles(*id, role_id, expire_time)
        await self.cursor.execute("""CREATE TABLE IF NOT EXISTS roles(
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            role_id INTEGER NOT NULL,
                                                            expire_time INTEGER);
                                                            """)

        # Codes(*id, code, expires_at, max_uses, uses_count, **role_id, **guild_id, created_at)
        await self.cursor.execute("""CREATE TABLE IF NOT EXISTS codes(
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            code TEXT NOT NULL,
                                                            expires_at TIMESTAMP,
                                                            max_uses INTEGER,
                                                            uses_count INTEGER DEFAULT 0,
                                                            role_id INTEGER NOT NULL,
                                                            guild_id INTEGER NOT NULL,
                                                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                                            FOREIGN KEY(guild_id) REFERENCES guilds(id),
                                                            FOREIGN KEY(role_id) REFERENCES roles(id));
                                                            """)

        # Redemption(user_id, **role_id, **code_id, expires_at, redeemed_at)
        await self.cursor.execute("""CREATE TABLE IF NOT EXISTS redemption(  
                                                            user_id INTEGER NOT NULL,
                                                            role_id INTEGER NOT NULL,
                                                            code_id INTEGER NOT NULL,
                                                            expires_at TIMESTAMP,
                                                            redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                                            FOREIGN KEY (code_id) REFERENCES codes(id),
                                                            FOREIGN KEY (role_id) REFERENCES roles(id));
                                                            """)
        return self

    async def get_guild(self, guild_id: int) -> dict:
        # -------------------------
        # Checks if the guild exists.
        get_guild = await self.cursor.execute("""SELECT * FROM guilds WHERE id = ?;""", (guild_id,))
        fetch_guild = await get_guild.fetchone()
        if fetch_guild is None:
            await self.cursor.execute("""INSERT INTO guilds(id) VALUES(?);""", (guild_id,))
            await self.connection.commit()
            return {"guild_id": guild_id, "channel_id": None}
        else:
            return {"id": fetch_guild[0], "channel_id": fetch_guild[1]}

    async def get_code(self, guild_id: int, code: str) -> dict:
        # -------------------------
        # Checks if the code exists.
        sql: str = """SELECT * FROM codes WHERE code = ? AND guild_id = ?;"""
        get_code = await self.cursor.execute(sql, (code, guild_id))
        fetch_code = await get_code.fetchone()
        if fetch_code is not None:
            sql = """SELECT * FROM roles where id = ?;"""
            get_role = await self.cursor.execute(sql, (fetch_code[5],))
            fetch_role = await get_role.fetchone()
            return {"expires_at": fetch_code[2], "max_uses": fetch_code[3], "uses_count": fetch_code[4],
                    "role": {"id": fetch_role[1], "expire_time": fetch_role[2]}}
        else:
            raise Errors.CodeNotFound(code=code)

    async def redeem(self, guild_id: int, code: str, user_id: int) -> dict:
        # -------------------------
        # Checks if the code exists.
        sql: str = """SELECT * FROM codes WHERE code = ? AND guild_id = ?;"""
        get_code = await self.cursor.execute(sql, (code, guild_id))
        fetch_code = await get_code.fetchone()
        if fetch_code is not None:
            # --------------------------------
            # checks if the code is fully used.
            if fetch_code[3] is not None and fetch_code[3] == fetch_code[4]:
                raise Errors.CodeExpired(code=code)
            else:
                # -----------------------------
                # Checks if the code is expired.
                if (fetch_code[2] is not None) and (datetime.now() >= fetch_code[2]):
                    raise Errors.CodeExpired(code=code)
                else:
                    # ---------------------------------------------
                    # Checks if the user already used the same code.
                    sql = """SELECT * FROM redemption where user_id = ? AND code_id = ?;"""
                    get_redemption = await self.cursor.execute(sql, (user_id, fetch_code[0]))
                    if await get_redemption.fetchone() is None:
                        sql = """SELECT * FROM roles where id = ?;"""
                        get_role = await self.cursor.execute(sql, (fetch_code[5],))
                        fetch_role = await get_role.fetchone()
                        # --------------------------------------
                        # Adding user to the redemption database.
                        sql = """INSERT INTO redemption(user_id, role_id, code_id, expires_at) VALUES(?, ?, ?, ?);"""
                        if fetch_role[-1] is None:
                            time = None
                        else:
                            time = datetime.now().replace(microsecond=0) + timedelta(seconds=fetch_role[-1])
                        await self.cursor.execute(sql, (user_id, fetch_role[0], fetch_code[0], time))
                        # -----------------------------------
                        # Updating the uses count of the code.
                        sql = """UPDATE codes SET uses_count = ? WHERE id = ?;"""
                        await self.cursor.execute(sql, (int(fetch_code[4]) + 1, fetch_code[0]))
                        await self.connection.commit()
                        # retrieving logging channel.
                        get_guild = await self.get_guild(guild_id=guild_id)
                        return {"guild": get_guild,
                                "role": {"id": fetch_role[1], "expire_time": fetch_role[2]}}
                    else:
                        raise Errors.CodeAlreadyUsed(code=code)
        else:
            raise Errors.CodeNotFound(code=code)

    async def set_channel(self, guild_id: int, channel_id: int) -> bool:
        # -------------------------
        # Checks if the guild exists.
        get_guild = await self.cursor.execute("""SELECT * FROM guilds WHERE id = ?;""", (guild_id,))
        fetch_guild = await get_guild.fetchone()
        if fetch_guild is None:
            await self.cursor.execute("""INSERT INTO guilds(id, channel) VALUES(?, ?);""", (guild_id, channel_id))
        else:
            if fetch_guild[1] == channel_id:
                await self.cursor.execute("""UPDATE guilds SET channel = ? WHERE id = ?""", (None, guild_id))
            else:
                await self.cursor.execute("""UPDATE guilds SET channel = ? WHERE id = ?""", (channel_id, guild_id))

            await self.connection.commit()
            return fetch_guild[1] != channel_id

    async def create_code(self, guild_id: int, code: str, expire_in: datetime | None, max_uses: int | None,
                          role_id: int, role_expire_time: int | None) -> dict:
        # -------------------------
        # Checks if the guild exists.
        get_guild = await self.get_guild(guild_id=guild_id)

        # -------------------------
        # Checks if the code exists.
        get_code = await self.cursor.execute("""SELECT * FROM codes WHERE code = ? AND guild_id = ?;""",
                                             (code, guild_id))
        if await get_code.fetchone() is None:
            # ----------------------------
            # Adding the role and the code.
            sql: str = """INSERT INTO roles(role_id, expire_time) VALUES(?, ?);"""
            role_id = await self.cursor.execute(sql, (role_id, role_expire_time))
            # --------------------------------------------
            # Adding the code and linking it with the role.
            sql = """INSERT INTO codes(code, expires_at, max_uses, guild_id, role_id) VALUES(?, ?, ?, ?, ?);"""
            await self.cursor.execute(sql, (code, expire_in, max_uses, guild_id, role_id.lastrowid))
            await self.connection.commit()
            return get_guild

        else:
            raise Errors.CodeIsAlreadyExists(code=code)

    async def remove_code(self, guild_id: int, code: str) -> dict:
        # -------------------------
        # Checks if the guild exists.
        get_guild = await self.get_guild(guild_id=guild_id)

        # -------------------------
        # Checks if the code exists.
        sql: str = """SELECT * FROM codes WHERE code = ? AND guild_id = ?;"""
        get_code = await self.cursor.execute(sql, (code, guild_id))
        fetch_code = await get_code.fetchone()
        if fetch_code is not None:
            # ----------------------------
            # Deleting the code from codes.
            sql = """DELETE FROM codes WHERE id = ?;"""
            await self.cursor.execute(sql, (fetch_code[0],))

            # ----------------------------
            # Deleting the role from roles.
            sql = """DELETE FROM roles WHERE id = ?;"""
            await self.cursor.execute(sql, (fetch_code[5],))

            # ----------------------------
            # Deleting the code from codes.
            sql = """DELETE FROM redemption WHERE code_id = ? AND role_id = ?;"""
            await self.cursor.execute(sql, (fetch_code[0], fetch_code[5]))
            await self.connection.commit()
            return get_guild

        else:
            raise Errors.CodeNotFound(code=code)

    async def expired_roles(self) -> iter:
        sql: str = """SELECT * FROM redemption WHERE expires_at IS NOT NULL AND datetime('now', 'localtime') > 
        expires_at; """
        get_expired_roles = await self.cursor.execute(sql)
        fetch_expired_roles = await get_expired_roles.fetchall()
        get_guild = None
        for user in fetch_expired_roles:
            sql = """SELECT * FROM roles, codes where roles.id = ? AND codes.role_id = ? ORDER BY codes.guild_id;"""
            get_code_role = await self.cursor.execute(sql, (user[2], user[2]))
            fetch_role = await get_code_role.fetchone()
            # ---------------------------------
            # Deleting the user from redemption.
            sql = """DELETE FROM redemption WHERE user_id = ? AND role_id = ? AND code_id = ?;"""
            await self.cursor.execute(sql, (user[0], user[1], user[2]))
            if fetch_role is not None:
                if get_guild != fetch_role[9]:
                    get_guild = await self.get_guild(guild_id=fetch_role[9])

                yield {"guild_id": get_guild["id"], "channel_id": get_guild["channel_id"],
                       "user_id": user[0], "role_id": fetch_role[1]}

        await self.connection.commit()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()
