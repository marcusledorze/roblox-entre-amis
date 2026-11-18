# Roadmap STEAL A CRYSTAL! (web app locale)

Un tableau en colonnes pour suivre la roadmap du jeu : **Idées**, **Release candidate (avant V1)**, **P1 · Stabilité**, **P2 · Features**, **En cours**, **Fait**.
La version rédigée de départ est dans [`docs/ROADMAP.md`](../docs/ROADMAP.md). Depuis la création de l'app, c'est **l'app qui fait foi**.

## Lancer

Il faut Python 3.10 ou plus récent, sans aucune dépendance.

```bash
py roadmap-app/server.py
```

Ouvre ensuite <http://127.0.0.1:8787>. Les données sont dans `roadmap-app/data/roadmap.json`, et ce fichier est versionné avec git.

## Utiliser

- **+** en haut d'une colonne : ajouter une carte (une idée, un bug, une feature).
- **Cliquer sur une carte** : la modifier, voir les notes de Claude, ou la supprimer.
- **Glisser-déposer** une carte pour la changer de colonne ou d'ordre.
- Chaque carte que tu crées ou modifies (titre, description, colonne…) reçoit le badge orange **À traiter**. Simplement réordonner une carte dans sa colonne ne la marque pas.
- La case **À traiter seulement** filtre ces cartes. La page se met à jour toute seule toutes les 4 s.

## Traitement par Claude

Claude lit la file d'attente, traite chaque carte, puis la marque comme traitée en laissant une note. Selon la carte, traiter peut vouloir dire :
- analyser une idée et la classer dans la bonne colonne, avec un effort et un risque ;
- implémenter la carte dans le jeu ;
- vérifier un point qu'on a marqué comme fait.

```bash
py roadmap-app/roadmap.py queue
py roadmap-app/roadmap.py show <id>
py roadmap-app/roadmap.py resolve <id> "ce qui a été fait" --column done
py roadmap-app/roadmap.py add "titre" --column p1 --effort S --risk faible
py roadmap-app/roadmap.py move <id> doing
```

L'outil passe par le serveur s'il tourne (la page se met alors à jour), sinon il écrit directement dans le fichier. Les actions de Claude sont signées `claude` et ne remettent jamais une carte « à traiter ».

## Tests (à lancer avant chaque commit)

```bash
py -m unittest discover -s roadmap-app/tests -v
```

## Sécurité

- Le serveur n'écoute que sur `127.0.0.1`.
- L'en-tête `Host` est vérifié, ce qui protège contre le DNS rebinding.
- Les écritures qui viennent d'une autre origine sont refusées (`Origin` / `Sec-Fetch-Site`), ce qui protège contre le CSRF.
- Seul le JSON est accepté, avec une limite de 64 Ko, une validation stricte des champs et une liste fermée de colonnes, d'efforts et de risques.
- Les en-têtes CSP, `nosniff` et `frame-ancestors 'none'` sont envoyés.
- Seuls 3 fichiers statiques sont servis, donc aucun accès possible au reste du disque.
- Côté page, tout le texte est inséré avec `textContent` (pas de XSS).
