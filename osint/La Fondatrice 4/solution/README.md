# La Fondatrice 4

## Write-up

### Français

L'objectif de ce défi était de comprendre les multiples indices et de les rassembler en une seule recherche intelligente.

Nous cherchions:
- Une série de romans (pour jeunes adultes, si vous regardiez l'indice).
- La série a des références vers Beethoven, Harry Houdini et Edmond Halley.
- Le 1er livre de la série révèle un élément secret à sa fin.

Pour retrouver cela, il fallait utiliser des techniques comme du Google Dorking (recherche avancée avec des combinaisons de résultats exactes), ou bien un outil comme Wikipédia!

**Exemple de solution avec Wikipedia:**

Voici une recherche avancée combinant ces informations sur Wikipedia: https://en.wikipedia.org/w/index.php?search=%22edmond+halley%22+%22harry+houdini%22+%22beethoven%22+novel+OR+book+OR+series&title=Special%3ASearch&profile=advanced&fulltext=1&advancedSearch-current=%7B%22fields%22%3A%7B%22phrase%22%3A%22%5C%22edmond+halley%5C%22+%5C%22harry+houdini%5C%22+%5C%22beethoven%5C%22%22%2C%22or%22%3A%5B%22novel%22%2C%22book%22%2C%22series%22%5D%7D%7D&ns0=1

On tombait sur la page "List of The 39 Clues characters", et en pivotant avec cette information on découvre que le 1er livre de cette série s'appelle "The Maze of Bones" (https://en.wikipedia.org/wiki/The_Maze_of_Bones). La fin du résumé explique qu'ils trouvent le premier indice, qui est le fer ("iron solute" en anglais). L'information existait aussi en français dans des wikis du roman.

Et voilà, le fer (ou soluté de fer, ou solution de fer) était la réponse à l'énigme!

### English

The goal of this challenge was to understand the multiple clues, and join them together in a single smart search.

We were looking for:
- A series of novels (for young adults, if you looked at the hint).
- The series has references to Beethoven, Harry Houdini, and Edmond Halley.
- The first book in the series reveals a secret element at the end.

To find this, we had to use techniques such as Google Dorking (advanced search with exact result combinations), or a tool like Wikipedia!

**Solution example with Wikipedia:**

Here is an advanced search combining this information on Wikipedia: https://en.wikipedia.org/w/index.php?search=%22edmond+halley%22+%22harry+houdini%22+%22beethoven%22+novel+OR+book+OR+series&title=Special%3ASearch&profile=advanced&fulltext=1&advancedSearch-current=%7B%22fields%22%3A%7B%22phrase%22%3A%22%5C%22edmond+halley%5C%22+%5C%22harry+houdini%5C%22+%5C%22beethoven%5C%22%22%2C%22or%22%3A%5B%22novel%22%2C%22book%22%2C%22series%22%5D%7D%7D&ns0=1

We come across the page “List of The 39 Clues characters,” and using this information, we discover that the first book in this series is called “The Maze of Bones” (https://en.wikipedia.org/wiki/The_Maze_of_Bones). The end of the summary explains that the characters find the first clue, which is iron (“iron solute”). This information was also available in fan-made wikis about the book.

And there you have it, iron (or iron solute) was the answer to the riddle!

## Flag

`fer`, ou `solutiondefer`, ou `solutedefer`, ou `iron`, ou `ironsolute`