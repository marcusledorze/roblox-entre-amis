# roblox-entre-amis — consignes pour Claude

- Réponds en français.
- Jeu : « STEAL A CRYSTAL! », place Roblox `126196802646495`. Ne touche jamais au jeu « Test » (place `100777728208107`).
- **Roadmap** : la source de vérité est l'app locale `roadmap-app/`. Voir [roadmap-app/README.md](roadmap-app/README.md).
  - En début de travail, lis la file : `py roadmap-app/roadmap.py queue`.
  - Pour chaque carte « à traiter » : analyse-la, classe-la (colonne, effort, risque, œil sécurité) ou fais le travail demandé, puis lance `py roadmap-app/roadmap.py resolve <id> "<ce qui a été fait>" [--column ...]`.
  - Une carte qui demande de modifier le jeu ne se traite pas pendant un playtest : vérifie d'abord l'état de Studio.
  - Quand une fonctionnalité est livrée, déplace sa carte dans `done` avec une note.
- **Avant chaque commit** : `py -m unittest discover -s roadmap-app/tests` doit passer.
