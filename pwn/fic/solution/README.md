# FIC

## Write-up

### 1) Understand the verification model

The binary maintains:
1. a callback pointer called at the end of the flow
2. a whitelist `allowed[]`

The business check is of the form:

```c
callback == allowed[0] || callback == allowed[1]
```

This is not a "strong" control flow. It's an equality test on pointers that can be manipulated in memory.

### 2) Find the memory vulnerability

A user read overflows a stack buffer and overwrites the following fields (in order):
1. `callback`
2. an intermediate slot (padding/alignment)
3. `allowed[0]`
4. possibly `allowed[1]` depending on the length sent

So we can make the check true while choosing our target.

### 3) Choose the right callback target

Interesting symbols:
1. `safe_echo`
2. `safe_reverse`
3. `undercode`

`undercode` is the useful target because its path executes a `system("/bin/sh")`.

### 4) Build a "valid + malicious" state

Idea:
1. `callback = undercode`
2. `allowed[0] = undercode`

Since the condition is an OR, `allowed[1]` becomes useless.

Official payload:

```python
payload  = b"A" * 64
payload += p64(undercode)
payload += b"A" * 8
payload += p64(undercode)
```

Pedagogical reading:
1. `64` bytes: padding up to the callback
2. first `p64`: callback diverted to `undercode`
3. `8` bytes: intermediate slot
4. second `p64`: whitelist aligned on the same target

Result:
1. logical check valid
2. final callback execution
3. shell

### 5) How a player can rediscover this without the solve

Checklist:
1. identify the security logic (here, pointer equality)
2. verify if the control pointers live in an overwritable area
3. choose a legitimate target according to the program (`undercode`)
4. forge a memory state that respects the check while diverting execution

The script `shFIC.py` automates this chain.

### 6) Reproduction

```bash
cd challenges/pwn/fic/solution
python3 shFIC.py
```

## Flag
`POLYCYBER{CFI_Bypass_ICP_12e6fdbe860cd970037ecdacbc4c59c8}`
