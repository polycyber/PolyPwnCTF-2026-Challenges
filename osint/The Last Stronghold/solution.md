# The Last Stronghold

## Write-up EN

The challenge data is hidden within the file itself. By using the `strings` command and piping to `tail`, we can extract the:

```bash
strings panacea.jpg | tail
```

This will output the Base64-encoded string: `NzgxNDA5TjE1MjkyOUU=`. Using the terminal or a tool like CyberChef, we can decode the Base64 string to reveal the plaintext:

```bash
echo "NzgxNDA5TjE1MjkyOUU=" | base64 -d
```

This will output the plaintext `781409N152929E`. It corresponds to the coordinate 78°14'09"N 15°29'29"E.

A web search reveals the coordinate to point to the "Svalbard Global Seed Vault" or "Svalbard globale frøhvelv" in Norwegian.

## Write-up FR

Les données du défi sont cachées à l'intérieur du fichier lui-même. En utilisant la commande `strings` et en effectuant un pipe vers `tail`, nous pouvons extraire :

```bash
strings panacea.jpg | tail
```

Cela affichera la chaîne encodée en Base64 : `NzgxNDA5TjE1MjkyOUU=`. En utilisant le terminal ou un outil comme CyberChef, nous pouvons décoder la chaîne Base64 pour révéler le texte en clair :

```bash
echo "NzgxNDA5TjE1MjkyOUU=" | base64 -d
```

Cela affichera le texte en clair `781409N152929E`. Cela correspond aux coordonnées 78°14'09"N 15°29'29"E.

Une recherche sur le Web révèle que ces coordonnées pointent vers le "Svalbard Global Seed Vault" (Réserve mondiale de semences du Svalbard) ou la "Svalbard globale frøhvelv" en norvégien.

## Flag

`POLYCYBER{svalbard-globale-frøhvelv}`
