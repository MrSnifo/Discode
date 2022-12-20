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


class Errors:
    class CodeIsAlreadyExists(Exception):
        """Exception raised cause the code is already exists.

            Attributes:
                code -- code caused the error
                message -- explanation of the error
            """

        def __init__(self, code: str, message="This code %s is already exists."):
            self.code = code
            self.message = message % code
            super().__init__(self.message)

    class CodeNotFound(Exception):
        """Exception raised cause the code is already exists.

            Attributes:
                code -- code caused the error
                message -- explanation of the error
            """

        def __init__(self, code: str, message="This code %s does bot exist."):
            self.code = code
            self.message = message % code
            super().__init__(self.message)

    class CodeExpired(Exception):
        """Exception raised cause the code is already exists.

            Attributes:
                code -- code caused the error
                message -- explanation of the error
            """

        def __init__(self, code: str, message="This code %s is expired."):
            self.code = code
            self.message = message % code
            super().__init__(self.message)

    class CodeAlreadyUsed(Exception):
        """Exception raised cause the code is already exists.

            Attributes:
                code -- code caused the error
                message -- explanation of the error
            """

        def __init__(self, code: str, message="This code %s is already used."):
            self.code = code
            self.message = message % code
            super().__init__(self.message)
