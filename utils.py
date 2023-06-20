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

# ------ Discord ------
from discord import Embed

# ------ Generating code ------
from secrets import choice
from string import ascii_uppercase, digits

# ------ Generating code ------
from datetime import timedelta


def text_to_seconds(text: str) -> int:
    seconds: int = 0
    for element in text.split():
        time: str = element[-1].lower()
        value: int = int(element[0:-1])
        match time.lower():
            case "s":
                seconds += value
            case "m":
                seconds += value * 60
            case "h":
                seconds += value * 3600
            case "d":
                seconds += value * 86400
            case "y":
                seconds += value * (525_600 * 60)
        # 317 years is the limit.
        if seconds >= 100_00_000_000:
            raise ValueError
    return seconds


def period(delta: timedelta) -> str:
    pattern: str = ""
    d = {'d': delta.days}

    if delta.days != 0:
        pattern += "{d} days "

    d['h'], rem = divmod(delta.seconds, 3600)
    if d['h'] != 0:
        pattern += "{h} hours "

    d['m'], d['s'] = divmod(rem, 60)

    if d['m'] != 0:
        pattern += "{m} minutes "

    if d['s'] != 0 and not delta.days >= 1:
        pattern += "{s} seconds"

    return pattern.strip().format(**d)


def embed_wrong(msg: str) -> Embed:
    """
    This function will generate embed message.

    :return:`discord.Embed`
    """
    embed = Embed(description=f"**It seems something wrong** :speak_no_evil:\n{msg}", colour=0x36393f)
    return embed


def gen_rnd_string(n: int = 4) -> str:
    return ''.join(choice(ascii_uppercase + digits)for _ in range(n))


def generate_code(n: int = 5) -> str:
    return "-".join(gen_rnd_string() for _ in range(n))
