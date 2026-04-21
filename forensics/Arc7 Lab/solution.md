# ARC-7 — solution (reference)

## Flag

`polycyber{arc7_vault_txt_recovery}`

## Parameters

| Item | Value |
|------|--------|
| Zone | `vault.arc7.lemaires.fr` |
| Chain head label | `XyQ2wLp9` |
| Decoy label (ignore for flag) | `Qm9nVXM0` → gzip text `ACCESS_DENIED…` |

## Where the head + zone are on the player page

- `<html>` CSS variable `--chassis-barcode` → zone (also near-invisible footer text).
- HTML comment: `silo-ticket# ARC7-DEEP XyQ2wLp9`.
- Hidden node: `data-plate="XyQ2wLp9"`.

## Chain protocol (`*.vault.arc7.lemaires.fr` TXT)

1. Concatenate all TXT character-strings / DoH `Answer` TXT RRs for that name in order.
2. If payload starts with `END`: remainder is the final base64 piece; stop.
3. Else: next label = first 8 chars; base64 chunk = rest. Go to step 1 for `nextlabel.zone`.
4. Join all base64, decode, **gunzip** → manifest text.

## Manifest → flag

- Table lines: `DEPTH|TOKEN|…`
- Sort by numeric `DEPTH`; drop tokens starting with `JUNK` or `NULL`.
- For remaining tokens in order: TXT at `TOKEN.vault.arc7.lemaires.fr` = **raw base64** (no gzip). Decode, concatenate bytes → flag.

## Verify (live DNS)

```bash
python ctf-arc7-lab/tools/solve_live.py
```

Options: `--zone`, `--head`, `--doh`, `-v`.

## Organizers

- Generate records: `python ctf-arc7-lab/tools/build_challenge_dns.py` → `dns/arc7_txt_records.json`, `records.bind.snippet`, `records.tsv`.
- TXT segments ≤255 octets per DNS string; longer logical values use multiple strings (handled in generator / Terraform).
- Deploy: `ctf-arc7-lab/terraform/` + `terraform apply` (zone default `lemaires.fr`, subdomains like `XyQ2wLp9.vault.arc7`). Auth: `./ovh.conf` or `OVH_APPLICATION_KEY` / `OVH_APPLICATION_SECRET` / `OVH_CONSUMER_KEY`.
- Change flag: `FLAG_PARTS` in `build_challenge_dns.py`, regenerate, re-apply.
