# StreamCap

StreamCap est une interface graphique en Python 3 et QT5 pour Vobcopy, une ligne de commande pour récupérer un Dvd sur votre disque dur.
Cette version n'est que la mise à jour de l'outil existant écrit en Python 2.7 et QT4 (appelé StreamCap). 

A propos
-----

Simple Gui pour vobcopy, StreamCap est simple à utiliser. L'idée principale de ce projet est de le rendre facile à installer et à utiliser. Aucune ligne de commande n'est nécessaire.
La première version de ce projet n'a pas été créée par moi mais par razorfoss.com. Vous pouvez obtenir le code original (la version 0.11 à l'adresse <a href = http://sourceforge.net/projects/streamcap/> Streamcap </a>)

Fonctionnalités
--------

* Interface agréable
* Facile à utiliser
* Conserve les préférences en mémoire
* Caractéristiques essentielles de Vobcopy
* Aucune ligne de commande pour Vobcopy

Screenshots
-----------

<img src="streamcap/images/streamcap.png" alt="Streamcap" width="500">

Dépendances
------------

* python 2
* PyQt 4
* Qt4
* vobcopy

Installation
------------

Pour l'instant, ouvrez simplement une console dans le dossier streamcap et tapez :

```
python streamcap.py
```

* Manjaro

    Python3 est la version par défaut donc tapez :
    ```
    python2 streamcap.py
    ```

* Linux Mint/Ubuntu

    Cependant, la version par défaut de python est la version 2 et non la version 3 jusqu'à 17.10. Après, vous devriez faire la même chose que pour Manjaro. Donc tapez :

    ```
    python streamcap.py
    ```

TODO
----

Ce qui est prévu pour les prochaines versions quand j'aurai le temps pour cela.

* version 0.13 Introduire de nouveaux langages
* version 0.14 Introduire les nouvelles versions de Signals et slot
* version 0.15 Introduire python 3 par défaut
* version 0.16 (Peut être) Introduire PyQt5 ~~et une interface UI~~