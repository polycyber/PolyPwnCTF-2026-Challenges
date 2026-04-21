# Null Return

## Write-up FR

Le challenge présente un vieil ordinateur avec un terminal "NeuralOS". L'interface expose plusieurs commandes dont `lire <fichier>` et `chercher <mot-clé>`.

Ces deux commandes passent l'input utilisateur directement dans un `subprocess.run(..., shell=True)`, ce qui permet une injection de commande.

Utilisez la commande : `lire x; cat /flag.txt`
pour lire le flag caché dans le système de fichiers.

## Write-up EN

The challenge presents an old computer with a "NeuralOS" terminal. The interface exposes several commands including `lire <file>` and `chercher <keyword>`.

Both commands pass user input directly into `subprocess.run(..., shell=True)`, enabling command injection.

Use the command: `lire x; cat /flag.txt`
to read the flag hidden in the filesystem.

## Flag

`polycyber{n3ur4l_c0r3_br34ch}`
