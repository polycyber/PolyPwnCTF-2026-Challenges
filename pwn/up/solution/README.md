# UP

## Write-up

### 1) Recon

The binary provides two primitives:
1. a format string primitive on the first input
2. a stack overflow on the second input

General strategy:
1. use the format string leak to retrieve runtime protections (canary + PIE base)
2. use the overflow to regain control of execution flow

### 2) Leak stage

The official solve sends:

```python
fmt = b"%15$p|%25$p"
```

Why this is important:
1. `%15$p` returns a stable canary value
2. `%25$p` returns a `main` address (PIE leak)

Then:

```python
elf.address = pie_leak - elf.sym["main"]
```

We convert the leaked address into a usable PIE base.

### 3) Overflow stage

Payload layout starts with:
1. `b"A" * (64 + 8)` to reach the canary
2. `p64(canary)` to pass the SSP check
3. `b"B" * 8` for the saved rbp

Control is taken using two gadgets:
1. `g1 = pop r12 ; jmp r12`
2. `g2 = pop rdi ; jmp r12`

The script then sets:
1. `system = elf.sym["system"]`
2. `binsh = elf.address + 0x2010`

Execution flow:
1. return to `g1`, next qword is `system`
2. `g1` sets `r12 = system`, then jumps to `system`
3. return to `g2`, next qword is `binsh`
4. `g2` sets `rdi = binsh`, then `jmp r12`
5. `r12` still holds `system`, so this ends up calling `system("/bin/sh")`

Key insight:
`r12` is callee-saved on amd64, so it survives between the gadget transitions.

### 4) How a player can rediscover this without the solve

Checklist:
1. check runtime protections (`checksec`)
2. confirm the format string primitive and enumerate useful `%<n>$p` values
3. confirm the overflow offset with pattern/cyclic
4. find the gadgets in the PIE binary
5. validate the payload locally, then adapt for remote

The `shUP.py` script automates these steps.

