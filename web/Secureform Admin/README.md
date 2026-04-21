# SecureForm Admin — CTF Challenge

**Category:** Web
**Difficulty:** Medium
**Flag format:** `FLAG{...}`

---

## Contexte / Context

### Français

Une entreprise utilise **SecureForm**, une application interne de gestion de formulaires de contact.
Le panneau d'administration est censé être sécurisé par un code PIN à 4 chiffres.

Votre mission : accéder au dashboard et extraire le flag stocké dans la base de données.

L'application tente d'implémenter une sanitisation similaire à celle de WordPress — mais le
développeur a fait une erreur critique dans la gestion des paramètres de tri SQL.

### English

A company uses **SecureForm**, an internal contact form management application.
The admin panel is supposedly secured by a 4-digit PIN.

Your mission: access the dashboard and extract the flag stored in the database.

The application tries to implement WordPress-like sanitization — but the developer made
a critical mistake in how SQL sorting parameters are handled.

---

## Accès / Access

L'instance du challenge est disponible à l'URL fournie par la plateforme.

The challenge instance is available at the URL provided by the platform.

---

## Objectif / Goal

Trouvez le flag caché dans la table `secrets` de la base de données MySQL.

Find the flag hidden in the `secrets` table of the MySQL database.

---

## Fichiers fournis / Provided files

Le code source de l'application est disponible dans le dossier [`player_source/`](player_source/) pour
vous aider à analyser la logique de l'application.

The application source code is available in the [`player_source/`](player_source/) folder to help
you analyze the application logic.

---

## Indices / Hints

<details>
<summary>Indice 1 / Hint 1</summary>

Le code PIN à 4 chiffres n'a aucune protection contre les tentatives répétées.

The 4-digit PIN has no protection against repeated attempts.
</details>

<details>
<summary>Indice 2 / Hint 2</summary>

Une fois connecté, examinez les paramètres `orderby` et `order` dans l'URL du dashboard.
Testez des valeurs inattendues.

Once logged in, examine the `orderby` and `order` GET parameters in the dashboard URL.
Try unexpected values.
</details>

<details>
<summary>Indice 3 / Hint 3</summary>

La requête vulnérable construit un `ORDER BY` dynamique sans protection suffisante.
Les injections basées sur le temps sont bloquées — mais une injection booléenne aveugle
peut modifier l'**ordre de tri** des résultats selon une condition vraie/fausse.

The vulnerable query builds a dynamic `ORDER BY` without sufficient protection.
Time-based injections are blocked — but a boolean-based blind injection can modify
the **sort order** of results based on a true/false condition.
</details>
