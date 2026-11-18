"""Crée data/roadmap.json à partir de docs/ROADMAP.md (état au 18/11/2026).

  py roadmap-app/seed.py           # refuse d'écraser un fichier existant
  py roadmap-app/seed.py --force   # repart de zéro
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import Store  # noqa: E402
from server import DEFAULT_DATA  # noqa: E402

DONE = [
    ("Monde", "Grotte, camp et 8 bases", "Camp en zone sûre avec 8 bases, boutiques, Forge, classement et zone d'événements."),
    ("Monde", "5 mines de 660 studs", "Green Cave → Ice → Lava → Shadow → Galaxy, portes payantes revérifiées par le serveur."),
    ("Monde", "Refonte visuelle réaliste", "Dalles, allée pavée, monument, étals, forge, stalactites, rails, étais, bassins de lave, arches de zone."),
    ("Monde", "Secret Vaults (Shadow Mine)", "2 salles secrètes derrière de faux murs."),
    ("Perfs", "Optimisations de la carte", "510 lumières supprimées, 2 445 décors sans CanTouch/CanQuery, StreamingEnabled (bases Persistent, portes et gardes Atomic)."),
    ("Gameplay", "Boucle miner → base → revenus", "Sac, dépôt à la base, emplacements, revenus passifs, encaissement au chariot."),
    ("Gameplay", "Cristaux, raretés, mutations", "Couleur = rareté, forme = zone, mutations naturelles ~8 %, repousse en 3 à 5 s."),
    ("Gameplay", "9 pioches", "De Wooden à Cosmic, tenues lame vers l'avant, effets fixés à la pioche."),
    ("Gameplay", "Sacs, bottes, auras, gardien de base", "6 sacs, 6 bottes améliorables, 11 auras, gardien qui patrouille."),
    ("Gameplay", "Tapis de course et barre de vitesse", "+10 à +3 000/s ; barre SLOW → MAX appliquée par le serveur (SpeedPct)."),
    ("Gameplay", "Forge, Rebirth, déblocages", "Base jusqu'à 9 emplacements, déblocage des mines, Forge, Rebirth ×1,5."),
    ("Gameplay", "11 événements + portail", "Giant Crystal, Golden Mine, Meteor Crash, Guard Overload, etc."),
    ("Gardes", "IA des gardes et alarme", "5-6 gardes par zone, alarme 0-100 % (CALM / SUSPICIOUS / HUNTED), détection assouplie."),
    ("Gardes", "5 modèles de gardes par zone", "Cowboy (R15), King Ice, DoomerBringer, Skeleton, casque spatial ; nom « <Zone> Guardian »."),
    ("UI", "Menus et R$ SHOP", "R$ SHOP, UPGRADES (Pickaxes / Bags / Boots / Auras), Crystals, Index, Rebirth, Admin, Settings."),
    ("UI", "Cartes Upgrades et images d'auras", "Cartes agrandies 3 par ligne, vitrine qui tourne, 11 images d'auras dessinées."),
    ("UI", "Textes stylés et notifications", "Dégradé brillant, contour teinté, notifications couleur du cristal, étiquettes au-dessus des cristaux."),
    ("UI", "HUD et réglages", "Barre de sac, barre d'alarme, étiquette de minage, collecteur, badges de passes, 5 réglages."),
    ("Tutoriel", "Tutoriel en 6 étapes avec flèche", "Flèche unique, bords assombris, consignes courtes, SKIP, fin sauvegardée côté serveur."),
    ("Robux", "4 game passes en vente", "VIP, Auto Collect, x2 Speed Training, x2 Space, icônes et badges JPEG."),
    ("Robux", "Onglet PACKS (3 starter packs)", "Starter R$ 49, Pro R$ 149, Elite R$ 399 avec les affiches (ID encore à 0)."),
    ("Assets 3D", "Bottes et sacs générés par IA", "BootAssets / BagAssets, ajustés au pied et au dos ; anciens modèles dans ServerStorage."),
    ("Admin", "Panneau admin", "Événements, annonce filtrée, morph, pouvoirs, gestion des admins par UserId."),
    ("Sécurité", "Garde-fous serveur existants", "Remote Action unique avec pcall et rate limit 12/s, minage validé (pioche, cooldown, portée), anti-vitesse, UpdateAsync + verrou de session + autosave 90 s + BindToClose."),
]

RC = [
    ("Sauvegarder la place (v58)", "Arrêter le test de jeu, Ctrl+S, vérifier sac, chaussures et images d'auras.", "S", "faible", ""),
    ("Créer les 3 Game Pass des starter packs", "Starter 49 / Pro 149 / Elite 399, renseigner les ID dans Config.GamePasses (clés NoobPack, MediumPack, ProPack).", "S", "faible", "Revérifier la propriété côté serveur à la connexion."),
    ("Produits à ID 0 : créer ou cacher", "Pioches Rainbow / Ruby et packs de vitesse Speed25/100/500 affichent « Coming soon! ».", "S", "faible", ""),
    ("ProcessReceipt idempotent (bloquant)", "Mémoriser les PurchaseId, sauvegarder avant PurchaseGranted.", "S", "faible", "Évite double livraison et paiement sans livraison."),
    ("Verrou de session forcé : ne pas charger un profil vide", "Si le UpdateAsync de reprise échoue, DataManager.Load charge defaultData() puis écrase la progression : kick à la place.", "S", "moyen", "Empêche l'écrasement de données via plusieurs serveurs."),
    ("Badge Auto Collect", "Créer le badge et renseigner Config.PassBadges.AutoCollect (0 aujourd'hui).", "S", "faible", ""),
    ("Textures des meshes IA", "Sac Medium gris, Crystal Bag marron au lieu de vert : vérifier en jeu publié, regénérer si besoin.", "S", "faible", ""),
    ("Publier + accès API Studio", "Publier le jeu et activer « Enable Studio Access to API Services ».", "S", "faible", ""),
    ("Test serveur multi-joueurs réel", "DataStore réel, vrai achat de chaque game pass, badges, classement, gardes à plusieurs.", "M", "faible", "Vérifier qu'aucun achat n'est simulé en production."),
    ("Test sur mobile", "Performances, lisibilité, barre de vitesse tactile, tutoriel.", "S", "faible", ""),
    ("Page du jeu et questionnaire de maturité", "Icône, miniatures, description, genres, Maturity & Compliance.", "S", "faible", ""),
    ("Décider l'identité « STEAL »", "Le vol est désactivé (Steal.Enabled = false) : choix assumé pour la V1 ou changement de pitch.", "S", "moyen", ""),
    ("Musique des événements", "EventManager.MusicIds est vide.", "S", "faible", ""),
    ("Flags de test neutres en prod", "TestPurchasesInStudio, TestInfiniteMoneyInStudio, IsOwner=true dans Studio : contrôler avec un compte non admin.", "S", "faible", "Aucun avantage gratuit hors Studio."),
    ("Copie .rbxl après publication", "Garder une copie de la place dans le dépôt pour revenir en arrière.", "S", "faible", ""),
]

P1 = [
    ("1.1 Achats Robux fiables", "ProcessReceipt idempotent (PurchaseId), sauvegarde avant PurchaseGranted, revérifier les passes avec UserOwnsGamePassAsync.", "S", "faible", "Le client ne déclenche jamais grantPass."),
    ("1.2 Données des joueurs", "Corriger le repli defaultData, Version + migrations, sauvegarde de secours, sauvegarde à chaque achat, envisager ProfileStore.", "M", "moyen", "Pas d'écrasement via multi-serveurs."),
    ("1.3 Validation stricte des remotes", "Types, bornes, NaN, clés ; rate limit par action (Buy, Forge, Rebirth) ; vérifier Sprint et MineOre.", "M", "faible", "Remotes à confiance zéro."),
    ("1.4 Performances", "~85 000 instances : MicroProfiler, LOD, moins de particules, coût IA des 28 gardes.", "M-L", "moyen", "Un serveur saturé rate ses sauvegardes."),
    ("1.5 Robustesse serveur", "Nettoyer les tables par joueur, pcall dans les boucles, remontée des erreurs.", "S", "faible", "Journaux pour repérer les abus."),
    ("1.6 Streaming", "Scripts clients tolérants aux objets non chargés, RequestStreamAroundAsync avant téléportation.", "S-M", "faible", ""),
    ("1.7 Anti-triche déplacement", "Anti-téléportation et anti-noclip serveur, dépôt validé dans la base.", "M", "moyen", "Ne jamais croire la position du client ; rubber-band plutôt que kick."),
    ("1.8 Admin : moindre privilège", "Journal des commandes, Money/Kick réservés au propriétaire, révocation entre serveurs.", "S", "faible", "Un admin compromis ne ruine pas l'économie."),
]

P2 = [
    ("2.1 Récompense quotidienne + codes", "Série de connexions et codes promo.", "S", "faible", "Heure serveur uniquement, codes à usage unique."),
    ("2.2 Quêtes et défis", "Journaliers / hebdomadaires.", "M", "faible", "Progression comptée par le serveur."),
    ("2.3 Remettre du « steal »", "Zone PvP, fenêtre de vol en événement, ou cristaux exposés.", "L", "élevé", "Vol 100 % serveur, anti-farm de comptes alternatifs."),
    ("2.4 Produits développeur", "Packs de vitesse, boost de chance, boost de revenus, skip de Forge.", "M", "moyen", "Après 1.1 ; expiration des boosts côté serveur."),
    ("2.5 Nouvelle zone et palier", "6e mine, nouvelles pioches / sacs / auras, rebirths au-delà de 4.", "L", "moyen", "Prix et revenus via Config, revérifiés serveur."),
    ("2.6 Social", "Bonus d'amis, récompense de groupe, objectif de likes, serveurs privés.", "S-M", "faible", "Appartenance au groupe vérifiée côté serveur."),
    ("2.7 Classements et saisons", "Le plus riche, rebirths, mutations ; reset hebdomadaire.", "M", "faible", "Valeurs issues du profil serveur, sauts anormaux plafonnés."),
    ("2.8 Événements planifiés", "Un événement automatique toutes les 30 min.", "S", "faible", ""),
    ("2.9 Échanges entre joueurs", "Trading.", "L", "élevé", "Échange atomique serveur, anti-duplication ; après 1.2."),
]


def build(path: str) -> Store:
    store = Store(path)
    for theme, title, desc in DONE:
        store.create({"actor": "claude", "column": "done", "theme": theme, "title": title, "description": desc})
    for col, rows in (("rc", RC), ("p1", P1), ("p2", P2)):
        theme = {"rc": "Release", "p1": "Stabilité", "p2": "Feature"}[col]
        for title, desc, effort, risk, sec in rows:
            store.create({"actor": "claude", "column": col, "theme": theme, "title": title, "description": desc,
                          "effort": effort, "risk": risk, "security": sec})
    return store


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=DEFAULT_DATA)
    p.add_argument("--force", action="store_true")
    a = p.parse_args()
    if os.path.exists(a.data):
        if not a.force:
            print(f"{a.data} existe déjà (utilise --force pour repartir de zéro)")
            return 1
        os.remove(a.data)
    store = build(a.data)
    print(f"{len(store.data['cards'])} cartes écrites dans {a.data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
