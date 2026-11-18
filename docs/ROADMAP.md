# STEAL A CRYSTAL! — Roadmap

> État au 18/11/2026. Place Roblox `126196802646495` (Team Create).
> Dernière sauvegarde Roblox : **version 57**. **Rien n'est encore publié.**
> Les derniers réglages (sac collé au dos, chaussures ajustées, images des auras) ne sont **pas sauvegardés** : un test de jeu tournait.

> **Version interactive** : ce document est l'état de départ. La roadmap vivante est la web app locale [`roadmap-app/`](../roadmap-app/README.md) (`py roadmap-app/server.py`, puis http://127.0.0.1:8787).

Légende effort : **S** = moins d'une demi-journée, **M** = 1 à 2 jours, **L** = 3 jours ou plus.
Légende risque : risque de casser quelque chose en faisant le changement (**faible / moyen / élevé**).

---

## 1. Bilan : ce qui a été fait

### Monde et carte
- Tout le jeu se passe **dans une grotte** : un camp (zone sûre) avec **8 bases** (4 à gauche, 4 à droite), les boutiques, la Forge, le classement et la zone d'événements.
- **5 mines à la suite**, de 660 studs chacune : Green Cave → Ice → Lava → Shadow → Galaxy. Des portes payantes les séparent : le client voit une barrière, le serveur revérifie l'accès.
- **Refonte visuelle « réaliste »** : sol en dalles, allée pavée, monument en cristaux, étals en bois, forge avec four et enclume, stalactites, rails, étais en bois, bassins de lave, cristaux décoratifs sur les murs.
- **Arches de zone** décorées selon la zone, et bannières de zone (GREEN CAVE…) aux couleurs de la zone.
- **2 « Secret Vaults »** dans la Shadow Mine, derrière de faux murs.
- **Optimisations** : 510 lumières supprimées, 2 445 pièces décoratives sans collisions de requête (CanTouch / CanQuery désactivés), ombres coupées dans les mondes d'événements, StreamingEnabled activé (bases Persistent, portes et gardes Atomic).

### Gameplay
- **Boucle de base** : miner → sac → retour à la base → emplacements → revenus passifs → encaissement au chariot (le collecteur).
- **Cristaux** : la couleur indique la rareté (Common blanc → Divine doré), la forme indique la zone. Mutations naturelles (environ 8 %). Un nouveau cristal **repousse 3 à 5 s** après chaque cristal cassé.
- **Pioches** : 9 pioches, de Wooden à Cosmic, dont les modèles fournis par l'utilisateur. Elles sont tenues lame vers l'avant, avec des effets de particules fixés à la pioche (pas de traînée). Inferno, Celestial et Cosmic ont été retravaillées.
- **Sacs** (6 niveaux), **bottes** (6 raretés, améliorables), **auras** (11, dont BlueFlame, UltraInstinct, Hellzone et Radiance), **gardien de base** qui patrouille.
- **Tapis de course** : de +10 à +3 000 de vitesse par seconde selon le niveau. Le menu Speed a été fusionné dans Upgrades.
- **Barre de vitesse** sous le menu de gauche : on choisit sa vitesse de SLOW (8) à MAX. Le réglage est sauvegardé et appliqué par le serveur (`SpeedPct`).
- **Agrandissement de la base** jusqu'à 9 emplacements, **déblocage des mines**, **Forge** (en cas d'échec, le cristal redescend d'un rang et garde sa mutation), **Rebirth** (revenus ×1,5 ; Fire Aura au rebirth 1, Electric Aura au rebirth 4).
- **Vol de cristaux désactivé** (`Steal.Enabled = false`) à la demande de l'utilisateur. La porte qui verrouillait la base a été supprimée.
- **11 événements** (Giant Crystal, Golden Mine, Meteor Crash, Guard Overload, etc.), avec un **portail d'événement**.

### Gardes (IA)
- Un **GuardManager** côté serveur gère 5 à 6 gardes par zone, qui patrouillent, enquêtent, poursuivent, attrapent puis retournent à leur base.
- **Barre d'alarme de 0 à 100 %** : CALM sous 30 %, SUSPICIOUS de 30 à 60 %, HUNTED au-delà. Les gardes n'attrapent qu'à partir de SUSPICIOUS.
- **Détection assouplie** : alarme environ 3 fois plus lente, vue 40 % plus courte, champ de vision plus étroit, abandon de la poursuite plus rapide, enquête seulement à moins de 50 studs.
- **5 modèles de gardes**, un par zone : cowboy (R15), King Ice, DoomerBringer, Skeleton et casque spatial (R6). Les rigs ont été reconstruits, et les scripts et sons des modèles gratuits supprimés. Au-dessus de chaque garde s'affiche « <Zone> Guardian ».
- **Marche** : remise sur l'animation Roblox par défaut. Les animations Walk3 / Run2 importées sont désactivées mais restent dans le jeu.
- Les gardes restent immobiles quand aucun joueur n'est dans leur zone, pour économiser le serveur.

### Interface (UI)
- **Menus** : R$ SHOP, UPGRADES (onglets PICKAXES / BAGS / BOOTS / AURAS), CRYSTALS, INDEX, REBIRTH, ADMIN, et SETTINGS derrière une icône d'engrenage.
- **Cartes d'Upgrades agrandies** (3 par ligne), avec une vitrine où l'objet tourne et un halo de la couleur de la rareté. **11 images d'auras** dessinées et uploadées (`assets/ui/auras`).
- **Textes** : style brillant avec un dégradé et un contour teinté (TextStyler). Les notifications prennent la couleur du cristal miné et apparaissent en « pop ». Les étiquettes des cristaux posés dans la base sont au-dessus du cristal.
- **HUD** : barre de sac marron, barre d'alarme, étiquette de minage avec pourcentage, collecteur avec une icône de pièce, badges de game pass sur le côté.
- **Interface modifiable en mode édition** (système EditLayout / UISandbox).
- **Réglages** (5 interrupteurs) : effets réduits, musique, sons, effets des autres joueurs, champ de vision large.

### Tutoriel
- **Tutoriel en 6 étapes**, avec une seule flèche droite (qui se colle au bord de l'écran si la cible est hors champ, avec la distance affichée), les bords de l'écran assombris, une consigne courte par étape et un bouton SKIP.
- Étapes : aller à la mine → miner → ramener à la base → encaisser → courir sur le tapis → ouvrir UPGRADES.
- Si un garde t'attrape pendant le retour, le tutoriel revient à l'étape « miner ». La fin du tutoriel est sauvegardée côté serveur (réglage `TutorialDone`).

### Économie et Robux
- **4 game passes en vente**, avec leurs ID : VIP (2092244953), Auto Collect (2092424962), x2 Speed Training (2094470903), x2 Space (2093102924). Les icônes sont personnalisées et des badges JPEG sont exportés.
- **Badges liés** : VIP, x2 Training et x2 Space. Le badge Auto Collect n'a pas d'ID (0).
- **R$ SHOP** : pastille « PACKS! », onglet PACKS avec **3 starter packs** (Starter R$ 49, Pro R$ 149, Elite R$ 399) et les affiches de l'utilisateur (`assets/ui/packs`). Leurs ID valent encore 0.
- **Pioches exclusives** (Rainbow, Ruby) et **packs de vitesse** (Speed25 / 100 / 500, produits développeur) : les ID valent 0.
- Les achats sont simulés gratuitement dans Studio (`TestPurchasesInStudio`). Dans le jeu publié, les achats sans ID affichent « Coming soon! ».
- **Classement mondial** (OrderedDataStore `StealACrystal_Richest_v1`).

### Assets 3D (générés par IA aujourd'hui)
- **Bottes** : 6 baskets en 3D générées par IA (`ReplicatedStorage.BootAssets`), orientées et ajustées au pied.
- **Sacs** : 6 sacs en 3D générés par IA (`ReplicatedStorage.BagAssets`), plaqués dans le dos. Les bretelles n'ont pas pu être supprimées ; elles sont enfoncées dans le dos.
- Les anciens modèles et les modèles bruts sont gardés en secours dans **ServerStorage**.

### Admin
- **Panneau admin** avec 5 onglets : EVENTS (dont le portail), CHAT (annonce filtrée par TextService), MORPH (en garde ou en cristal), POWERS (speed, fly, noclip, god, goto, bring, kick, money) et ADMINS (donner l'accès par UserId, réservé au propriétaire, enregistré dans un DataStore).

### Sécurité déjà en place (vérifié dans le code)
- **Un seul remote d'actions** (`Remotes.Action`) avec un dispatch côté serveur, chaque appel protégé par `pcall`. Rate limit global : 12 actions par seconde et par joueur.
- **Minage validé par le serveur** : la pioche tenue doit être celle équipée, le délai entre deux coups (cooldown) est respecté, la portée est vérifiée, et le serveur contrôle les points de vie du cristal.
- **Vitesse calculée par le serveur**, avec un anti-triche sur la vitesse horizontale (SpeedManager).
- **Données sauvegardées** avec `UpdateAsync`, un verrou de session (expiration 150 s), une sauvegarde automatique toutes les 90 s, `BindToClose` et des nouvelles tentatives en cas d'échec.
- **Commandes admin** vérifiées côté serveur (`IsAdmin` dans EventManager et AdminManager).
- **Réglages** : seules les clés de la liste autorisée (ALLOWED) sont acceptées, avec vérification du type (booléen, ou nombre limité entre 0 et 1 pour `SpeedPct`).

---

## 2. Release candidate : checklist go / no-go pour la V1

**Bloquants (NO-GO tant que ce n'est pas fait)**

- [ ] **Sauvegarder la place** : arrêter le test de jeu, faire Ctrl+S, et vérifier que le sac, les chaussures et les images d'auras sont bien dans la version 58.
- [ ] **Créer les 3 Game Pass des starter packs** sur le Creator Dashboard (Starter 49, Pro 149, Elite 399) et renseigner leurs ID dans `Config.GamePasses` (clés internes `NoobPack`, `MediumPack`, `ProPack`). Attention : les noms affichés ne correspondent pas aux clés.
- [ ] **Décider du sort des produits restés à ID 0** : pioches exclusives Rainbow / Ruby et packs de vitesse Speed25 / 100 / 500. Soit on les crée, soit on les **cache dans l'UI**, plutôt que d'afficher « Coming soon! » au lancement.
- [ ] **Rendre `ProcessReceipt` idempotent AVANT de mettre en vente un produit développeur** (packs de vitesse). Aujourd'hui, il ne garde pas trace des `PurchaseId` déjà traités : en cas de nouvel essai de Roblox, le joueur peut recevoir le pack deux fois, et si le serveur tombe avant la sauvegarde, le joueur peut avoir payé sans rien recevoir. Voir la stabilité, point 1.
- [ ] **Corriger le cas « verrou de session forcé »** dans `DataManager.Load` : si le `UpdateAsync` de reprise échoue, le joueur repart avec `defaultData()`, et la prochaine sauvegarde **écrase toute sa progression**. Il faut le kick au lieu de charger un profil vide.
- [ ] **Badge Auto Collect** : créer le badge et renseigner `Config.PassBadges.AutoCollect` (actuellement 0).
- [ ] **Vérifier les textures des meshes générés par IA** dans le jeu publié : le sac Medium s'affichait gris, et le Crystal Bag est marron au lieu de vert. Regénérer les meshes si besoin.
- [ ] **Publier le jeu** et activer « Enable Studio Access to API Services » pour tester le vrai DataStore.
- [ ] **Test sur un vrai serveur multi-joueurs** (au moins 2 comptes, idéalement 4 à 8 joueurs) :
  - DataStore réel : la progression est conservée après avoir quitté puis rejoint, ou changé de serveur ;
  - **un vrai achat Robux** de chaque game pass, sur un compte de test ;
  - attribution des badges ;
  - classement mondial ;
  - gardes et alarme quand plusieurs joueurs sont dans la même zone.
- [ ] **Test sur mobile** (vrai téléphone) : performances, lisibilité de l'UI, barre de vitesse tactile, tutoriel.

**Fortement recommandés avant l'ouverture au public**

- [ ] Remplir le **questionnaire de maturité** (Maturity & Compliance) et ajouter l'icône, les miniatures, la description et les genres de la page du jeu.
- [ ] **Identité « STEAL »** : le vol de cristaux est désactivé. C'est soit un choix assumé pour la V1, soit le jeu doit changer de pitch : à trancher avant le marketing.
- [ ] **Musique des événements** : `EventManager.MusicIds` est vide. Fournir des ID de musique publics, ou retirer l'option.
- [ ] **Garde cowboy (Green Cave, R15)** : vérifier en jeu que sa marche et sa course paraissent naturelles.
- [ ] Vérifier que les flags de test sont neutres en production : `TestPurchasesInStudio` et `TestInfiniteMoneyInStudio`, mais aussi `AdminManager.IsOwner`, qui renvoie toujours `true` dans Studio. Ce flag est bien limité à Studio, mais il faut le contrôler en jeu publié avec un compte qui n'est pas admin.
- [ ] **Faire une copie** de la place (.rbxl) dans le dépôt après la publication, pour pouvoir revenir en arrière.
- [ ] Mettre le **rendu de l'éclairage en Future** (`Lighting.Technology`) si les performances sur mobile le permettent. Ce réglage n'est pas modifiable par le MCP.

---

## 3. Améliorations suggérées, dans l'ordre

Chaque point a son « œil sécurité ». Principe général : **le client ne décide jamais** ; il demande, et le serveur vérifie et applique.

### Priorité 1 — Stabilité

| # | Amélioration | Pourquoi | Effort | Risque | Œil sécurité |
|---|---|---|---|---|---|
| 1.1 | **Achats Robux fiables** : `ProcessReceipt` idempotent. Enregistrer chaque `PurchaseId` dans les données du joueur, sauvegarder, et seulement ensuite renvoyer `PurchaseGranted`. Garder aussi `PromptGamePassPurchaseFinished`, mais revérifier l'achat avec `UserOwnsGamePassAsync`. | On ne doit jamais faire payer un joueur sans le livrer, ni lui livrer deux fois. C'est la confiance des joueurs et la conformité Roblox. | S | faible | Évite la double livraison. Le client ne doit jamais pouvoir déclencher `grantPass` lui-même. |
| 1.2 | **Données des joueurs** : corriger le repli `defaultData()` après une reprise de verrou ratée. Ajouter un champ `Version` et des migrations, une **sauvegarde de secours** (clé `backup` ou historique `ListVersionsAsync`), une sauvegarde à chaque achat Robux, et un journal des échecs. Envisager **ProfileStore**. | La perte de progression est la pire chose qui puisse arriver à un jeu de ce genre : elle crée des avis négatifs et des demandes de remboursement. | M | moyen | Un joueur ne doit pas pouvoir provoquer un écrasement de ses données en rejoignant deux serveurs (multi-onglets). |
| 1.3 | **Validation stricte de tous les arguments des remotes** : types, bornes, clés existantes et NaN, pour Buy, Equip, PlaceOre, StoreOre, SellSlot, Forge, etc. Faire un **rate limit par action** (par exemple 2 par seconde pour Buy, Forge et Rebirth), en plus de la limite globale de 12 par seconde. Vérifier aussi `Sprint` et `MineOre`. | Un exploiteur peut envoyer n'importe quoi. Une erreur côté serveur peut aussi casser l'état d'un joueur. | M | faible | Le cœur de l'anti-triche : des « remotes de confiance zéro ». |
| 1.4 | **Performances** : environ 85 000 instances dans le workspace. Mesurer avec le MicroProfiler et la Developer Console sur un vrai serveur. Fusionner ou simplifier les décors, utiliser des meshes avec LOD, limiter les particules et les auras visibles, et vérifier le coût des 28 gardes (pathfinding et boucle IA). | Le public Roblox joue surtout sur mobile : sous 30 FPS, ou si la mémoire du client sature, on perd les joueurs. | M-L | moyen | Pas de risque direct, mais un serveur saturé fait aussi rater les sauvegardes. |
| 1.5 | **Robustesse du serveur** : nettoyer toutes les tables par joueur dans `PlayerRemoving` (`lastHit`, `lastFullMsg`, `rate`…), protéger chaque boucle `while true` par `pcall`, et surveiller les erreurs avec `ScriptContext.Error` et les `AnalyticsService` / Error Report. | Ça évite les fuites de mémoire sur les serveurs qui tournent longtemps, et une boucle de revenus qui s'arrête en silence. | S | faible | Les journaux permettent de repérer les exploits et les abus. |
| 1.6 | **Streaming** : vérifier que chaque script client tolère les objets pas encore chargés (`WaitForChild` avec délai, ou `StreamingEnabled`-safe) : tutoriel, GuardAnimator, étiquettes de base, portes. Utiliser `RequestStreamAroundAsync` avant les téléportations admin et événement. | Les bugs de streaming n'apparaissent qu'en vrai serveur, avec une vraie latence. | S-M | faible | — |
| 1.7 | **Anti-triche de déplacement et de vol** : compléter l'anti-vitesse existant avec des contrôles anti-téléportation et anti-noclip côté serveur (distance parcourue, passage à travers les portes payantes). Valider côté serveur le dépôt à la base (le joueur doit être dans sa base). | Un tricheur qui se téléporte dans la Galaxy Mine sans l'avoir payée casse l'économie. | M | moyen (faux positifs) | Ne jamais faire confiance à la position envoyée par le client. Tolérer la latence et privilégier le retour en arrière (rubber-band) plutôt que le kick. |
| 1.8 | **Admin** : journaliser chaque commande (qui, quoi, quand), interdire `Money` et `Kick` aux admins qui ne sont pas propriétaires, et vérifier la révocation entre serveurs (DataStore `AdminList_v1`). | Un admin compromis ou malveillant peut ruiner l'économie de tout le monde. | S | faible | Principe du moindre privilège. |

### Priorité 2 — Features (contenu, rétention, monétisation)

| # | Amélioration | Pourquoi | Effort | Risque | Œil sécurité |
|---|---|---|---|---|---|
| 2.1 | **Récompense quotidienne et série de connexions** (daily streak), plus des **codes promo** (Twitter / Discord). | C'est le levier de rétention au jour 1 et au jour 7 le moins cher. | S | faible | Horodatage côté serveur (`os.time()`), jamais l'heure du client. Codes à usage unique enregistrés dans le profil. |
| 2.2 | **Quêtes et défis** (journaliers et hebdomadaires : « mine 50 cristaux Ice », etc.). | Ça donne un objectif à chaque session et guide vers les zones suivantes. | M | faible | Progression comptée par le serveur à partir d'événements serveur, jamais d'un « j'ai fini » envoyé par le client. |
| 2.3 | **Remettre du « steal »** sous une forme maîtrisée : vol uniquement en zone PvP, ou fenêtre de vol pendant un événement, ou cristaux « exposés » à la base. Garder la protection des nouveaux joueurs. | C'est le nom du jeu et le moteur social du genre « Steal a … ». | L | élevé (équilibrage, frustration) | Toute la logique de vol côté serveur (distance, propriété, cooldown). Anti-farm entre comptes alternatifs. |
| 2.4 | **Produits développeur** : packs de vitesse, boost de chance pour la rareté, boost de revenus temporaire, « skip » de la Forge. | Revenus récurrents, en complément des game passes qu'on n'achète qu'une fois. | M | moyen | Uniquement après le point 1.1 (ProcessReceipt idempotent). Effets des boosts calculés côté serveur, avec une date d'expiration dans le profil. |
| 2.5 | **Nouvelle zone et nouveau palier** (6e mine, nouvelles pioches, sacs et auras), plus des rebirths au-delà du 4e. | Contenu de fin de jeu pour les joueurs les plus actifs. Ça prolonge la durée de vie du jeu. | L | moyen | Les nouveaux prix et revenus doivent passer par Config et être revérifiés par le serveur. |
| 2.6 | **Social** : bonus d'amis (+X % de revenus par ami dans le serveur), récompense pour avoir rejoint le groupe, objectif de likes, serveurs privés. | Croissance organique et viralité. | S-M | faible | Vérifier l'appartenance au groupe avec `GetRankInGroup` côté serveur (avec cache). |
| 2.7 | **Classements et saisons** (le plus riche, le plus de rebirths, la plus grosse mutation), remis à zéro chaque semaine avec des récompenses cosmétiques. | Compétition et retour régulier des joueurs. | M | faible | Les valeurs envoyées à l'OrderedDataStore viennent uniquement du profil serveur. Plafonner les sauts anormaux. |
| 2.8 | **Événements planifiés automatiques** (par exemple un événement toutes les 30 min), en plus des événements admin. | Le serveur reste vivant sans admin connecté. | S | faible | — |
| 2.9 | **Échanges (trading) entre joueurs**. | Économie entre joueurs et rétention forte. | L | élevé | Échange atomique côté serveur avec confirmation des 2 joueurs, verrou anti-duplication, journal. **À ne faire qu'après le point 1.2.** |

### Ordre recommandé
1. **Avant le lancement** : section 2 (checklist), puis les points **1.1** et **1.2**.
2. **Semaine 1 après le lancement** : **1.3**, **1.5**, **1.6**, puis **1.4** à partir des vraies mesures, et **2.1** (récompense quotidienne et codes).
3. **Semaines 2 à 4** : **1.7**, **1.8**, puis **2.2**, **2.4** et **2.6**.
4. **Ensuite** : **2.3** (le vol), **2.5**, **2.7**, **2.8**, puis **2.9** (trading) en dernier.
