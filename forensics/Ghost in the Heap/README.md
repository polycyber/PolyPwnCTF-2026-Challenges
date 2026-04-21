# Ghost in the Heap

**Category:** Forensics
**Difficulty:** Medium
**Files:** `memdump.raw` (768 MB)

---

## Description

An anomaly was detected on one of our servers. Before the incident response team could intervene, an unknown process had already run and exited. The only artifact recovered is a raw physical memory dump captured moments after the process terminated.

Analysts noted that the process appeared to be performing network activity, but no suspicious traffic was observed on the wire. Whatever it sent — or tried to send — is gone from the network. The process also seemed to take deliberate steps to erase its tracks from memory before the dump was taken.

Or did it?

**Your mission:** analyze the memory dump and recover the exfiltrated data.

---

## Files

| File | SHA-256 |
|------|---------|
| `memdump.raw` | *(see challenge page)* |

---

## Flag format

`polycyber{...}`
