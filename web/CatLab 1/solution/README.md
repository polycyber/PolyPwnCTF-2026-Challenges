# CatLab 1

## Write-up

The application presents a simple registration and login interface. After registering an account and logging in, we can observe in the browser's dev tools that **two cookies** are set: `access_token` and `refresh_token`.

The existence of a separate refresh token hints at a token-refresh mechanism — there is likely an endpoint that exchanges a refresh token for a new access token. Checking the page sources and network requests, we find `/refresh.php`.

---

### Step 1 — Forging an Admin Session

#### Guessing the refresh token scheme

Registering with a username like `testuser` and inspecting the `refresh_token` cookie value reveals it is `5d9c68c6c50ed3d02a2fcf54f63993b6` — exactly `md5('testuser')`. Registering a second account confirms the pattern: the refresh token is simply `md5(username)`.

This means we can compute the admin refresh token without any credentials:

```
md5('admin') = 21232f297a57a5a743894a0e4a801fc3
```

#### Using the refresh endpoint to impersonate the admin

Sending the forged token to the refresh endpoint with no other credentials yields a valid admin `access_token`:

```
POST /refresh.php
Cookie: refresh_token=21232f297a57a5a743894a0e4a801fc3
```

The server responds by setting a fresh `access_token` cookie belonging to the admin account. There is no additional verification (no CSRF token, no IP binding, no check that the original session still exists).

---

### Step 2 — SSRF to Read the Flag

#### Discovering the admin panel

With the forged admin `access_token` cookie in place, navigating to the application reveals an extra page: **experiment.php**, labelled the "Transmogrification Chamber". It exposes a form that accepts a URL and fetches it server-side using curl, displaying the raw response in the page.

#### Exploiting the unrestricted file fetch

The endpoint places no restrictions on the URL scheme, so the `file://` scheme can be used to read local files from the server. Since we are looking for the flag and the page itself is `experiment.php`, we point curl at its own source:

```
POST /experiment.php
Cookie: access_token=<admin_token>

url=file:///var/www/html/experiment.php
```

Because curl fetches the file as raw bytes (without PHP execution), the full PHP source is returned and displayed in the page. The flag is embedded as a comment in that source:

```
// polycyber{s0m37hing_is_wr0ng_wi7h_my_c47}
```

---

### Automated Exploit

See [solve.py](solve.py) for the full automated exploit. It:

1. Computes `md5('admin')` and sends it to `/refresh.php` to obtain an admin `access_token`.
2. POSTs `file:///var/www/html/experiment.php` to `/experiment.php`.
3. Extracts and prints the flag from the response.

```
$ python3 solve.py
[+] Admin session obtained
[+] experiment.php source code obtained
[+] Flag: polycyber{s0m37hing_is_wr0ng_wi7h_my_c47}
```

---

## Flag

`polycyber{s0m37hing_is_wr0ng_wi7h_my_c47}`
