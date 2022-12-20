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

from logging import Logger, getLogger, FileHandler, StreamHandler, Formatter


def logger(level: int = 10) -> Logger:
    """
    This function will report events that occur during normal operation of a program.

    :param level:`int`
        CRITICAL: 50
        ERROR 40
        WARNING	30
        INFO: 20
        DEBUG: 10
        NOTSET: 0

    :return:`logging.Logger`
    """
    # ----- Discord -----
    discord = getLogger("discord")
    discord.setLevel(level)
    # create file handler which logs even debug messages
    fh = FileHandler("debug.log", "w", encoding="utf-8")
    fh.setLevel(level)
    # create formatter and add it to the handlers
    fh.setFormatter(Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    discord.addHandler(fh)

    # ----- Bot -----
    _logger = getLogger("discode")
    _logger.setLevel(level)
    # create console handler with a higher log level
    ch = StreamHandler()
    ch.setLevel(level)
    # create formatter and add it to the handlers
    ch.setFormatter(Formatter("[%(levelname)s] %(message)s"))
    # add the handlers to logger
    _logger.addHandler(ch)
    return _logger
