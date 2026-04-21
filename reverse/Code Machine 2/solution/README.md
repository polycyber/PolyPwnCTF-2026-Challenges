# Nom du défi

## Write-up

Pour mieux comprendre le fonctionnement du programme, on peut écrire un
désassembleur qui transforme le code compilé en code texte. Voir le fichier
[Disassembler.h](Disassembler.h) pour un exemple d'implémentation.

Pour trouver où sont les data par rapport au code, on peut repérer l'instruction
`stop`, et voir qu'après ça ce sont plein d'instructions `add` (car un nombre
petit aura ces 8 premiers bits = 0, ce qui est l'opcode de `add`).

On trouve que le `.data` commence à l'adresse 59. On obtient ensuite le code
décompilé dans [code.s](code.s).

À la ligne 42, on voit l'instruction `in`, qui permet de demander un input à
l'utilisateur, ce qui devrait donc correspondre à un caractère du flag. On
soustrait ensuite la valeur lue au contenu de `var_9`, et on jump à `label_6`
si le résultat est égal à 0.

## Flag

`polycyber{yxlmcras51gijnugtasfvkilhu3rawdp}`
