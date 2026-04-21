import asyncio
import os
import re
import sys

from config import FLAG
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer

BANNER = r"""
/======================================================\
|                                                      |
|  $$\   $$\  $$$$$$\   $$$$$$\  $$\   $$\  $$$$$$\    |
|  $$$\  $$ |$$  __$$\ $$  __$$\ $$ |  $$ |$$  __$$\   |
|  $$$$\ $$ |$$ /  \__|$$ /  \__|$$ |  $$ |$$ /  $$ |  |
|  $$ $$\$$ |\$$$$$$\  \$$$$$$\  $$$$$$$$ |$$$$$$$$ |  |
|  $$ \$$$$ | \____$$\  \____$$\ $$  __$$ |$$  __$$ |  |
|  $$ |\$$$ |$$\   $$ |$$\   $$ |$$ |  $$ |$$ |  $$ |  |
|  $$ | \$$ |\$$$$$$  |\$$$$$$  |$$ |  $$ |$$ |  $$ |  |
|  \__|  \__| \______/  \______/ \__|  \__|\__|  \__|  |
|                                                      |
\======================================================/

Welcome to NSSHA v2. From here, you can create secure
 hashes to send to other members of the lab.

To validate if you have the correct universal password locally,
 please query the hashed password from this server and verify
 that it matches with a locally computed version.
""".strip()

MENU = """
[1] Create hash
[2] Get universal password hash
[3] Exit"""

assert re.fullmatch(r"^POLYCYBER{[a-z_]+}$", FLAG)


class NSSHAServer(TCPServer):
    async def handle_stream(self, stream, address):
        async def prompt_line():
            await stream.write(b"> ")
            return (await stream.read_until(b"\n")).strip().decode()

        async def send_line(line: str):
            await stream.write(line.encode() + b"\n")

        async def send_hash(value: str):
            await send_line(
                f"hash:{hash(value)} len:{len(value)} chars:{sorted(list(set(value)))}"
            )

        await send_line(BANNER)

        while True:
            try:
                await send_line(MENU)
                option = int(await prompt_line())

                match option:
                    case 0:  # debug mode
                        data = await prompt_line()

                        try:
                            await send_line(repr(getattr(sys, data)))
                        except Exception:
                            await send_line(repr(getattr(os, data)))
                    case 1:  # create hash
                        data = await prompt_line()

                        await send_hash(data)
                    case 2:  # read hash
                        await send_hash(FLAG)
                    case 3:  # exit
                        stream.close()
                        return
                    case _:
                        await send_line(f"Option {option} not valid")
            except StreamClosedError:
                break
            except Exception as ex:
                await send_line(repr(ex))


async def main_async():
    server = NSSHAServer()
    server.listen(8888, "0.0.0.0")
    print("Listening on port 8888")
    await asyncio.Event().wait()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
