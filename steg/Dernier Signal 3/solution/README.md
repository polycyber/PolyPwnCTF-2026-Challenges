# Dernier Signal 3

## Write-up FR

Avec le code 29556, il est possible d'extraire un fichier encodé dans le fichier "tr@nm!ss!0n*��.wav" en utilisant la commande :
stegolsb wavsteg -r -i tr@nm!ss!0n*��.wav -o output -b 29556

Ensuite, en analysant les bits du fichier output, nous pouvons remarquer que l'entête est "50 4B 03 04" et que les 8 derniers bits sont "FF FF FF FF". Ceci peut correspondre à un fichier docx avec 8 bits supplémentaire

En utilisant hexedit, nous pouvons enlever les 8 bits de trop pour obtenir un fichier docx.

Ensuite, nous pouvons ctrl+a, ctrl+c le texte du document word et le décoder avec "https://www.irongeek.com/i.php?page=security/unicode-steganography-homoglyph-encoder"

Nous obtenons le nom "CARRION" que nous pouvons mettre dans polycyber{...} et obtenir le flag.

## Write-up EN

Using the code 29556, it is possible to extract a file encoded in the file "tr@nm!ss!0n*��.wav" using the command:
stegolsb wavsteg -r -i tr@nm!ss!0n*��.wav -o output -b 29556

Then, by analyzing the bytes of the output file, we can notice that the header is "50 4B 03 04" and that the last 8 bytes are "FF FF FF FF". This corresponds to a docx file with 8 extra bytes.

Using hexedit, we can remove the 8 extra bytes to obtain a valid docx file.

Then, we can ctrl+a, ctrl+c the text from the Word document and decode it with "https://www.irongeek.com/i.php?page=security/unicode-steganography-homoglyph-encoder"

We obtain the name "CARRION" which we can put in polycyber{...} to get the flag.

## Flag

`polycyber{CARRION}`
