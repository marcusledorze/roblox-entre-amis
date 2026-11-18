# STEAL A CRYSTAL!

Jeu Roblox de minage dans une grotte de cristaux, développé avec Roblox Studio (place `126196802646495`).

- **Page web de la roadmap** (la plus lisible) : https://claude.ai/artifact/FDjoZW8VJtjuWtVp3WfPZa. Elle est privée : il faut être connecté à Claude.
- **Roadmap ci-dessous**, mise à jour depuis l'app locale.
- Le détail (bilan, checklist V1, priorités et sécurité) est dans [docs/ROADMAP.md](docs/ROADMAP.md).
- La version modifiable est dans [roadmap-app/](roadmap-app/README.md).

<!-- ROADMAP:START (généré par roadmap-app/roadmap.py export, ne pas modifier à la main) -->
## Roadmap

_Mise à jour : 18/11/2026 19:03 · 69 cartes · 0 à traiter._ Version modifiable : l'app locale `py roadmap-app/server.py` → http://127.0.0.1:8787

### 🚦 Release candidate (avant V1) (19)

- [ ] **Sauvegarder la place (v58)** — Arrêter le test de jeu, Ctrl+S, vérifier sac, chaussures et images d'auras. · _effort S · risque faible_
- [ ] **Produits à ID 0 : créer ou cacher** — Pioches Rainbow / Ruby et packs de vitesse Speed25/100/500 affichent « Coming soon! ». · _effort S · risque faible_
- [ ] **ProcessReceipt idempotent (bloquant)** — Mémoriser les PurchaseId, sauvegarder avant PurchaseGranted. · _effort S · risque faible_
  - 🔒 Évite double livraison et paiement sans livraison.
- [ ] **Verrou de session forcé : ne pas charger un profil vide** — Si le UpdateAsync de reprise échoue, DataManager.Load charge defaultData() puis écrase la progression : kick à la place. · _effort S · risque moyen_
  - 🔒 Empêche l'écrasement de données via plusieurs serveurs.
- [ ] **Badge Auto Collect** — Créer le badge et renseigner Config.PassBadges.AutoCollect (0 aujourd'hui). · _effort S · risque faible_
- [ ] **Textures des meshes IA** — Sac Medium gris, Crystal Bag marron au lieu de vert : vérifier en jeu publié, regénérer si besoin. · _effort S · risque faible_
- [ ] **Publier + accès API Studio** — Publier le jeu et activer « Enable Studio Access to API Services ». · _effort S · risque faible_
- [ ] **Test serveur multi-joueurs réel** — DataStore réel, vrai achat de chaque game pass, badges, classement, gardes à plusieurs. · _effort M · risque faible_
  - 🔒 Vérifier qu'aucun achat n'est simulé en production.
- [ ] **Test sur mobile** — Performances, lisibilité, barre de vitesse tactile, tutoriel. · _effort S · risque faible_
- [ ] **Page du jeu et questionnaire de maturité** — Icône, miniatures, description, genres, Maturity & Compliance. · _effort S · risque faible_
- [ ] **Décider l'identité « STEAL »** — Le vol est désactivé (Steal.Enabled = false) : choix assumé pour la V1 ou changement de pitch. · _effort S · risque moyen_
- [ ] **Musique des événements** — EventManager.MusicIds est vide. · _effort S · risque faible_
- [ ] **Flags de test neutres en prod** — TestPurchasesInStudio, TestInfiniteMoneyInStudio, IsOwner=true dans Studio : contrôler avec un compte non admin. · _effort S · risque faible_
  - 🔒 Aucun avantage gratuit hors Studio.
- [ ] **Copie .rbxl après publication** — Garder une copie de la place dans le dépôt pour revenir en arrière. · _effort S · risque faible_
- [ ] **Créer le produit Robux « Skip a Day » (49 R$)** — Le créer sur le Creator Dashboard (produit développeur), puis renseigner son ID dans Config.DailySkip.Id. En attendant : gratuit dans Studio, « Coming soon! » dans le jeu publié. · _effort S · risque faible_
  - 📝 L'ID 2093583130 reçu est un Game Pass (achetable une seule fois) : pas utilisable pour un SKIP répétable. Il faut un produit développeur. Carte laissée dans Avant la V1.
- [ ] **Mettre hors vente le Game Pass « skip a day »** — Le Game Pass 2093583130 est en vente mais ne donne rien dans le jeu : le désactiver sur le Creator Dashboard pour qu'aucun joueur ne l'achète. · _effort S · risque faible_
  - 🔒 Éviter un achat Robux sans contrepartie (remboursements, signalements).
- [ ] **Renommer le Game Pass Elite sur Roblox** — Son nom sur Roblox est « elite\_pack.png » : c'est ce que voient les joueurs dans la fenêtre d'achat. Le renommer « Elite Pack ». · _effort S · risque faible_
- [ ] **Créer le Game Pass x2 Money et le produit Tapis +1 niveau** — Creator Dashboard : Game Pass « x2 Money » (prix au choix, 199 R$ proposé) et Developer Product « Treadmill +1 Level » (49 R$). Renseigner Config.GamePasses.DoubleMoney.Id et Config.TreadmillRobux.Id. En attendant : gratuits dans Studio, « Coming soon! » en ligne. · _effort S · risque faible_
  - 📝 x2 Money branché (Game Pass 2093541135, R$ 259, place v73). « skip treadmill » (2092935142) est un Game Pass : il faut un Developer Product pour le tapis aussi. Création automatique refusée : la permission developer-product:write n'est pas accordée.
- [ ] **Mettre hors vente le Game Pass « skip treadmill »** — Le Game Pass 2092935142 est en vente mais ne donne rien dans le jeu : le désactiver sur le Creator Dashboard. · _effort S · risque faible_
  - 🔒 Éviter un achat Robux sans contrepartie.

### 🔧 En cours (0)

_Vide._

### 🛠️ P1 · Stabilité (9)

- [ ] **1.1 Achats Robux fiables** — ProcessReceipt idempotent (PurchaseId), sauvegarde avant PurchaseGranted, revérifier les passes avec UserOwnsGamePassAsync. · _effort S · risque faible_
  - 🔒 Le client ne déclenche jamais grantPass.
- [ ] **1.2 Données des joueurs** — Corriger le repli defaultData, Version + migrations, sauvegarde de secours, sauvegarde à chaque achat, envisager ProfileStore. · _effort M · risque moyen_
  - 🔒 Pas d'écrasement via multi-serveurs.
- [ ] **1.3 Validation stricte des remotes** — Types, bornes, NaN, clés ; rate limit par action (Buy, Forge, Rebirth) ; vérifier Sprint et MineOre. · _effort M · risque faible_
  - 🔒 Remotes à confiance zéro.
- [ ] **1.4 Performances** — ~85 000 instances : MicroProfiler, LOD, moins de particules, coût IA des 28 gardes. · _effort M-L · risque moyen_
  - 🔒 Un serveur saturé rate ses sauvegardes.
- [ ] **1.5 Robustesse serveur** — Nettoyer les tables par joueur, pcall dans les boucles, remontée des erreurs. · _effort S · risque faible_
  - 🔒 Journaux pour repérer les abus.
- [ ] **1.6 Streaming** — Scripts clients tolérants aux objets non chargés, RequestStreamAroundAsync avant téléportation. · _effort S-M · risque faible_
- [ ] **1.7 Anti-triche déplacement** — Anti-téléportation et anti-noclip serveur, dépôt validé dans la base. · _effort M · risque moyen_
  - 🔒 Ne jamais croire la position du client ; rubber-band plutôt que kick.
- [ ] **1.8 Admin : moindre privilège** — Journal des commandes, Money/Kick réservés au propriétaire, révocation entre serveurs. · _effort S · risque faible_
  - 🔒 Un admin compromis ne ruine pas l'économie.
- [ ] **Limite des codes très utilisés** — Un code à utilisations limitées écrit un compteur partagé (1 écriture toutes les 6 s par clé DataStore). Pour un code très populaire, préférer des codes sans limite ou un compteur réparti. · _effort S · risque faible_
  - 🔒 Le compteur reste côté serveur (UpdateAsync).

### ✨ P2 · Features (8)

- [ ] **2.2 Quêtes et défis** — Journaliers / hebdomadaires. · _effort M · risque faible_
  - 🔒 Progression comptée par le serveur.
- [ ] **2.3 Remettre du « steal »** — Zone PvP, fenêtre de vol en événement, ou cristaux exposés. · _effort L · risque élevé_
  - 🔒 Vol 100 % serveur, anti-farm de comptes alternatifs.
- [ ] **2.4 Produits développeur** — Packs de vitesse, boost de chance, boost de revenus, skip de Forge. · _effort M · risque moyen_
  - 🔒 Après 1.1 ; expiration des boosts côté serveur.
- [ ] **2.5 Nouvelle zone et palier** — 6e mine, nouvelles pioches / sacs / auras, rebirths au-delà de 4. · _effort L · risque moyen_
  - 🔒 Prix et revenus via Config, revérifiés serveur.
- [ ] **2.6 Social** — Bonus d'amis, récompense de groupe, objectif de likes, serveurs privés. · _effort S-M · risque faible_
  - 🔒 Appartenance au groupe vérifiée côté serveur.
- [ ] **2.7 Classements et saisons** — Le plus riche, rebirths, mutations ; reset hebdomadaire. · _effort M · risque faible_
  - 🔒 Valeurs issues du profil serveur, sauts anormaux plafonnés.
- [ ] **2.8 Événements planifiés** — Un événement automatique toutes les 30 min. · _effort S · risque faible_
- [ ] **2.9 Échanges entre joueurs** — Trading. · _effort L · risque élevé_
  - 🔒 Échange atomique serveur, anti-duplication ; après 1.2.

### 💡 Idées (1)

- [ ] **Images d'auras sans anneaux au sol** — Les 11 anciennes images de cartes d'aura ont encore des anneaux au sol : les redessiner dans le style de la Prism si on veut tout uniformiser.

### ✅ Fait (32)

<details><summary>Voir tout ce qui a été fait</summary>

- [x] **Grotte, camp et 8 bases** — Camp en zone sûre avec 8 bases, boutiques, Forge, classement et zone d'événements.
- [x] **5 mines de 660 studs** — Green Cave → Ice → Lava → Shadow → Galaxy, portes payantes revérifiées par le serveur.
- [x] **Refonte visuelle réaliste** — Dalles, allée pavée, monument, étals, forge, stalactites, rails, étais, bassins de lave, arches de zone.
- [x] **Secret Vaults (Shadow Mine)** — 2 salles secrètes derrière de faux murs.
- [x] **Optimisations de la carte** — 510 lumières supprimées, 2 445 décors sans CanTouch/CanQuery, StreamingEnabled (bases Persistent, portes et gardes Atomic).
- [x] **Boucle miner → base → revenus** — Sac, dépôt à la base, emplacements, revenus passifs, encaissement au chariot.
- [x] **Cristaux, raretés, mutations** — Couleur = rareté, forme = zone, mutations naturelles ~8 %, repousse en 3 à 5 s.
- [x] **9 pioches** — De Wooden à Cosmic, tenues lame vers l'avant, effets fixés à la pioche.
- [x] **Sacs, bottes, auras, gardien de base** — 6 sacs, 6 bottes améliorables, 11 auras, gardien qui patrouille.
- [x] **Tapis de course et barre de vitesse** — +10 à +3 000/s ; barre SLOW → MAX appliquée par le serveur (SpeedPct).
- [x] **Forge, Rebirth, déblocages** — Base jusqu'à 9 emplacements, déblocage des mines, Forge, Rebirth ×1,5.
- [x] **11 événements + portail** — Giant Crystal, Golden Mine, Meteor Crash, Guard Overload, etc.
- [x] **IA des gardes et alarme** — 5-6 gardes par zone, alarme 0-100 % (CALM / SUSPICIOUS / HUNTED), détection assouplie.
- [x] **5 modèles de gardes par zone** — Cowboy (R15), King Ice, DoomerBringer, Skeleton, casque spatial ; nom « &lt;Zone&gt; Guardian ».
- [x] **Menus et R$ SHOP** — R$ SHOP, UPGRADES (Pickaxes / Bags / Boots / Auras), Crystals, Index, Rebirth, Admin, Settings.
- [x] **Cartes Upgrades et images d'auras** — Cartes agrandies 3 par ligne, vitrine qui tourne, 11 images d'auras dessinées.
- [x] **Textes stylés et notifications** — Dégradé brillant, contour teinté, notifications couleur du cristal, étiquettes au-dessus des cristaux.
- [x] **HUD et réglages** — Barre de sac, barre d'alarme, étiquette de minage, collecteur, badges de passes, 5 réglages.
- [x] **Tutoriel en 6 étapes avec flèche** — Flèche unique, bords assombris, consignes courtes, SKIP, fin sauvegardée côté serveur.
- [x] **4 game passes en vente** — VIP, Auto Collect, x2 Speed Training, x2 Space, icônes et badges JPEG.
- [x] **Onglet PACKS (3 starter packs)** — Starter R$ 49, Pro R$ 149, Elite R$ 399 avec les affiches (ID encore à 0).
- [x] **Bottes et sacs générés par IA** — BootAssets / BagAssets, ajustés au pied et au dos ; anciens modèles dans ServerStorage.
- [x] **Panneau admin** — Événements, annonce filtrée, morph, pouvoirs, gestion des admins par UserId.
- [x] **Garde-fous serveur existants** — Remote Action unique avec pcall et rate limit 12/s, minage validé (pioche, cooldown, portée), anti-vitesse, UpdateAsync + verrou de session + autosave 90 s + BindToClose.
- [x] **2.1 Récompense quotidienne + codes** — Série de connexions et codes promo. · _effort S · risque faible_
  - 🔒 Heure serveur uniquement, codes à usage unique.
  - 📝 Livré (place v66) : cadeaux quotidiens sur 7 jours (bouton cadeau à côté de l'engrenage, Prism Aura LIMITED au jour 7, jour calculé par le serveur) + onglet CODES dans le R$ SHOP (création réservée aux admins, codes plafonnés, 1 utilisation par joueur, anti force brute). Testé en Play, pas encore publié.
- [x] **Vérifier à l'écran la fenêtre DAILY GIFTS et l'onglet CODES** — Logique testée en Play, mais pas le rendu visuel : la fenêtre de Studio était réduite. Ouvrir le bouton cadeau et R$ SHOP &gt; CODES. · _effort S · risque faible_
  - 📝 Vérifié à l'écran en Play : fenêtre DAILY GIFTS refaite et onglet CODES lisibles (place v69).
- [x] **Cadeaux v2 : grosses récompenses + SKIP 49 R$** — Jours 2/4/6 : +500 / +1 000 / +5 000 de vitesse, argent jusqu'à 10M au jour 7. Bouton SKIP (49 R$ par jour sauté). Nouvelle fenêtre avec cartes colorées, pièces d'or et chaussures, barre de série en 7 points. Testé en Play (7 jours via SKIP).
  - 🔒 Reçu Robux enregistré dans la sauvegarde du joueur (PurchaseId) et sauvegardé avant validation : jamais donné deux fois.
- [x] **Auras plus belles** — Contour lumineux et anneaux néon retirés, remplacés par des volutes d'énergie. Image dédiée pour la Prism Aura.
- [x] **Formulaire admin CREATE CODE plus clair** — 3 étapes numérotées (nom, récompenses avec icônes et choix d'aura, limites), aperçu en direct de ce que les joueurs recevront.
- [x] **Créer les 3 Game Pass des starter packs** — Starter 49 / Pro 149 / Elite 399, renseigner les ID dans Config.GamePasses (clés NoobPack, MediumPack, ProPack). · _effort S · risque faible_
  - 🔒 Revérifier la propriété côté serveur à la connexion.
  - 📝 ID renseignés (place v70) : Starter 2093673183 (R$ 59), Pro 2092851170 (R$ 99), Elite 2093529130 (R$ 159). Prix du jeu alignés sur Roblox. Un pack acheté hors du jeu donne maintenant son contenu à la connexion.
- [x] **Pass x2 Money** — Nouveau Game Pass (R$ 199 proposé) : double l'argent des cristaux, se cumule avec le VIP. Médaillon dans les badges de droite et carte dans R$ SHOP &gt; GAMEPASSES. Testé en Play (place v72).
  - 🔒 Bonus appliqué par le serveur (PlayerIncome), propriété revérifiée à la connexion.
- [x] **Amélioration du tapis en Robux** — Bouton vert « LV N NOW! · R$ 49 » sous le panneau du tapis, dans les 8 bases : +1 niveau tout de suite. Testé en Play (clic sur le bouton, niveau 1 vers 2).
  - 🔒 Produit développeur : reçu enregistré dans la sauvegarde du joueur et sauvegardé avant validation. Seul le propriétaire de la base peut cliquer.

</details>
<!-- ROADMAP:END -->
