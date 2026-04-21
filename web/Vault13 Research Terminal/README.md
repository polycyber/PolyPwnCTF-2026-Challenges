# ☢ VAULT-13 Research Terminal

**Category:** Web
**Difficulty:** Medium
**Flag:** `flag{smuggl3d_p4st_th3_w4st3l4nd_f1r3w4ll}`

---

## Scenario

Year 2287. Somewhere in the wasteland, the **Vault-13 Research Terminal** holds
classified scientific data behind a custom security layer.

The vault's engineers — convinced that no raider would ever understand HTTP —
implemented their own firewall directly in the application: any **first access**
to `/classified/research-data` on a connection is immediately blocked with a
`403 Forbidden`.

The infrastructure is composed of two services:

- **HAProxy** — exposes port 8080 to the outside world and forwards traffic to the backend.
- **Backend** — a custom Python HTTP server implementing the firewall logic and serving the classified data.

Your objective: bypass the firewall and retrieve the classified research data.

---

## Architecture

```
[Player] ──TCP──► [HAProxy :8080] ──TCP──► [Backend :5000]
```

---

## Access

The challenge is accessible at the address provided by the platform.

The home page (`/`) gives you information about the available endpoints.
