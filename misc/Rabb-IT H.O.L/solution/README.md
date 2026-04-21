# Nom du défi

Rabb-IT H.O.L

## Write-up

Le challenge est conçu pour être une suite de rabbit-holes (d'où le nom), et donner l'apparence d'un serveur avec beaucoup de vulnérabilités. Le flag est contenu dans les métadonnées du favicon, accessible dès le chargement de la page web. Les mauvaises pistes sont les suivantes :
- LFI : un fichier `flag.txt` est accessible directement via LFI, ne contenant rien d'utile
- Fausse communication réseau : une requête réseau contient un message en base 64 disant que le flag n'est pas dans les communications réseau
- SQLi : la page de connexion est défectueuse et contient une SQLi. Il est possible de voir la requête SQL en activant le mode débug (`?debug=1`) mentionné dans les commentaires de la page
- Base de données : une entrée portant le nom `flag` est présente dans la base de données, mentionnant que le flag serait trop simple à trouver si contenu dans la base de données
- `robots.txt` : le fichier `robots.txt` redirige vers une page cachée, `secret_dev_notes.php`, qui mentionne plusieurs vulnérabilités sur le serveur, et contient le mot de passe de l'administrateur dans un div caché sur la page (`admin:admin123`) ainsi que le fait que le serveur a son port SSH ouvert. Le joueur peut ainsi accéder au mot de passe administrateur en le trouvant sur cette page, ou bien en récupérant le contenu de la base de données.
- `txt.galf` : une fois connecté en SSH avec les identifiants de l'administrateur, un fichier `txt.galf` est présent, contenant un message en base 64 à l'envers. Le joueur doit comprendre que le message est inversé en raison du nom du fichier, ainsi qu'à cause des symboles `==` démarrant le message, et non pas le terminant
- `.flag.txt` : dans le même dossier, un fichier caché dit à l'utilisateur qu'il s'enfonce profond dans le rabbit-hole et que le lapin s'éloigne de plus en plus

Les indices parsemés tout au long du challenge sont les suivants :
- index.php : `Debug mode: Enabled` --> là pour indiquer au joueur qu'il s'agit d'un serveur de développement
- documentaion.php : `Note: This development server may have debug features enabled. Please report any issues to security@rabb-it.hol.local` --> idem
- login.php : ` Remove development mode before pushing to production. Access it with ?debug=1 ` --> Commentaire de la page pour indiquer comment activer le mode debug, utile uniquement sur la page de login pour voir la requête SQL effectuée en backend
- secret_dev_notes.php : 
    - Informations sur la page directement
        ```
        The real treasure isn't always where you expect it to be.

        Sometimes the most obvious things are the most overlooked. # <-- le favicon est souvent ignoré

        Think smaller. # <-- le favicon est petit

        Not all valuable data is in files or databases.

        Sometimes it's the little details. # <-- le favicon est un détail
        ```

        ```
      [ ] Change admin password, too weak (URGENT!)
      [ ] Disable SSH access                        
      # les deux lignes permettent de déduire qu'un accès SSH est possible avec le compte admin
        ```

    - Informations cachées dans un div :

        ```
        Note: change the admin password from "admin123" to something stronger ASAP!
        ```
- SSH : 
  - `txt.galf` : `I wish that was the flag... But keep looking for it! That rabbit is looking very small from here though :/` --> mention du lapin, et du fait qu'il est très loin d'ici, incitant le joueur à revenir sur le site et chercher le lapin
  - `.flag.txt` : `Keep digging, my little rabbit...` --> le lapin est de nouveau mentionné


## Flag

`POLYCYBER{4LW4YS_CH3CK_7H3_F4V1C0N}`