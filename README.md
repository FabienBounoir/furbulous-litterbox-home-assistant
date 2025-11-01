# Furbulous Cat - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/fabienbounoir/furbulous-litterbox-home-assistant.svg)](https://github.com/fabienbounoir/furbulous-litterbox-home-assistant/releases)
[![HomeKit Compatible](https://img.shields.io/badge/HomeKit-Compatible-blue.svg)](docs/HOMEKIT_COMPATIBILITY.md)

Intégration complète pour les litières connectées **Furbulous Cat** dans Home Assistant avec support HomeKit.

---

## 🎯 Fonctionnalités

### ✅ Version 1.2.0
- ✅ **Authentication** - Connexion avec email/password ou token direct
- ✅ **Device Discovery** - Détection automatique des litières
- ✅ **22 Sensors** - Poids, utilisations, état, modes, versions, pet info, etc.
- ✅ **10 Binary Sensors** - Connectivité, erreurs, modes, chat dans litière
- ✅ **4 Buttons** - Nettoyage, vidage, emballage, DND
- ✅ **4 Switches** - Contrôles HomeKit (auto clean, mode auto, DND, child lock)
- ✅ **Pet Sensors** - Informations complètes sur chaque chat
- ✅ **Error Detection** - 11 codes d'erreur avec sévérité
- ✅ **Fast Updates** - Chat dans litière : **30 secondes** / Autres : 5 minutes
- ✅ **HomeKit Support** - Compatible avec HomeKit Bridge + Siri
- ✅ **Auto Token Refresh** - Renouvellement automatique du token

### 📊 Total: ~40 entités par installation
- 22 sensors (état, poids, utilisations, versions, pet info, etc.)
- 10 binary_sensors (connectivité, modes, erreurs, présence chat)
- 4 buttons (contrôle manuel)
- 4 switches (contrôle HomeKit)
- 1+ pet sensors (un par chat)

---

## 📦 Installation

### Option 1: HACS (Recommandé)

1. **Ouvrir HACS** dans Home Assistant
2. Aller dans **Intégrations**
3. Cliquer sur les **3 points** en haut à droite → **Dépôts personnalisés**
4. Ajouter l'URL : `https://github.com/fabienbounoir/furbulous-litterbox-home-assistant`
5. Catégorie : **Integration**
6. Rechercher "Furbulous Cat"
7. Cliquer sur **Télécharger**
8. Redémarrer Home Assistant

### Option 2: Installation manuelle

1. **Copier les fichiers**
   ```bash
   cd /path/to/homeassistant/config
   mkdir -p custom_components
   cp -r custom_components/furbulous custom_components/
   ```

2. **Redémarrer Home Assistant**
   - Via UI: **Paramètres** → **Système** → **Redémarrer**

### Configuration

1. **Ajouter l'intégration**
   - **Paramètres** → **Appareils et services** → **Ajouter une intégration**
   - Rechercher "Furbulous Cat"
   - Entrer email + mot de passe (compte Furbulous)

2. **HomeKit (Optionnel)**
   - Voir [HOMEKIT_COMPATIBILITY.md](docs/HOMEKIT_COMPATIBILITY.md)
   - Exposer les switches et binary sensors recommandés
   - Contrôler avec Siri et l'app Maison

---

## 📊 Entités principales

### 🔘 Switches (HomeKit Compatible)
- `switch.furbulous_box_nettoyage_automatique` - Nettoyage auto après utilisation
- `switch.furbulous_box_mode_auto_complet` - Mode auto complet
- `switch.furbulous_box_ne_pas_deranger` - Mode silencieux (nuit)
- `switch.furbulous_box_verrouillage_enfant` - Sécurité enfants

### 🔴 Binary Sensors
- ⭐ `binary_sensor.furbulous_box_chat_dans_la_litiere` - Détection chat (**30s**)
- `binary_sensor.furbulous_box_connecte` - État connexion
- `binary_sensor.furbulous_box_erreur` - Détection erreurs
- `binary_sensor.furbulous_box_boite_poubelle_pleine` - Bac à déchets plein

### 📊 Sensors
- `sensor.furbulous_box_poids_du_chat` - Poids en grammes
- `sensor.furbulous_box_utilisations_quotidiennes` - Nombre d'utilisations
- `sensor.furbulous_box_etat_de_fonctionnement` - État (Idle/Working/Cleaning)
- `sensor.furbulous_box_erreur` - Code erreur détaillé
- `sensor.furbulous_cat_<nom>` - Infos chat (âge, poids, race)

### 🔘 Buttons
- `button.furbulous_box_manual_clean` - Nettoyage manuel
- `button.furbulous_box_vider` - Vider le bac
- `button.furbulous_box_emballage_automatique` - Emballage auto

[📖 Liste complète des 40+ entités](docs/INSTALLATION.md)

---

## 🏠 HomeKit

L'intégration est **100% compatible** avec HomeKit Bridge :

✅ **4 switches** - Contrôle complet via Siri et app Maison  
✅ **Binary sensor chat** - Détection présence toutes les 30 secondes  
✅ **Binary sensors alertes** - Erreurs, bac plein, connexion  

**Commandes Siri :**
- *"Dis Siri, active le nettoyage automatique"*
- *"Dis Siri, est-ce que le chat est dans la litière ?"*

[📖 Guide complet HomeKit](docs/HOMEKIT_COMPATIBILITY.md)

---

## 🎨 Exemples d'automatisations

### Notification présence chat
```yaml
automation:
  - alias: "Chat détecté dans litière"
    trigger:
      platform: state
      entity_id: binary_sensor.furbulous_box_chat_dans_la_litiere
      to: 'on'
    action:
      service: notify.mobile_app
      data:
        message: "🐱 Milo utilise la litière"
```

### DND automatique la nuit
```yaml
automation:
  - alias: "DND nocturne"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      service: switch.turn_on
      target:
        entity_id: switch.furbulous_box_ne_pas_deranger
```

### Alerte bac plein
```yaml
automation:
  - alias: "Bac à déchets plein"
    trigger:
      platform: state
      entity_id: binary_sensor.furbulous_box_boite_poubelle_pleine
      to: 'on'
    action:
      service: notify.mobile_app
      data:
        title: "�️ Furbulous"
        message: "Le bac à déchets est plein - Vider maintenant"
```

[📖 Plus d'exemples](docs/EXAMPLES.md)

---

## 🔄 Mises à jour

| Intervalle | Entités concernées |
|------------|-------------------|
| **30 secondes** | Chat dans litière (binary_sensor) |
| **5 minutes** | Tous les autres capteurs |

Le capteur de présence du chat utilise un **coordinateur rapide** pour une détection quasi temps-réel.

---

## 🔍 Codes d'erreur

| Code | Message | Sévérité |
|------|---------|----------|
| 0 | No error | info |
| 1 | Weight sensor error | warning |
| 2 | IR sensor error | warning |
| 4 | Motor blocked | error |
| 8 | Motor overload | error |
| 16 | Litter full | warning |
| 32 | Normal operation | info |
| 64 | Drawer not in place | warning |
| 128 | Cover open | warning |
| 256 | Temperature error | error |
| 512 | Communication error | error |

---

## 📚 Documentation

- **[HOMEKIT_COMPATIBILITY.md](docs/HOMEKIT_COMPATIBILITY.md)** - Configuration HomeKit
- **[INSTALLATION.md](docs/INSTALLATION.md)** - Guide installation détaillé
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Résolution problèmes
- **[API_ENDPOINTS.md](docs/API_ENDPOINTS.md)** - 86 endpoints API documentés
- **[CHANGELOG.md](docs/CHANGELOG.md)** - Historique versions

---

## 📝 Changelog

### v1.2.0 (1 novembre 2025)
- ✨ **4 switches HomeKit** - Contrôle complet via Siri
- ✨ **Binary sensor chat** - Détection présence (30 secondes)
- ✨ **Coordinateur rapide** - Mise à jour différenciée
- ✨ **HomeKit compatible** - Support complet Bridge
- � Documentation HomeKit complète

### v1.1.0 (1 novembre 2025)
- ✨ Boutons supplémentaires (Vider, Emballage auto)
- ✨ Binary sensor bac plein
- ✨ Auto refresh token
- 🐛 Corrections timezone et properties

### v1.0.0 (31 octobre 2025)
- 🎉 Version initiale
- ✨ 19 sensors, 8 binary sensors, 2 buttons
- ✨ Support multi-chats
- ✨ Détection erreurs

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT - voir [LICENSE](LICENSE)

---

## 🙏 Remerciements

- API Furbulous pour la litière connectée
- Communauté Home Assistant
- Tous les contributeurs

---

**Version**: 1.2.0  
**Status**: ✅ Production Ready  
**Auteur**: [@fabienbounoir](https://github.com/fabienbounoir)  
**HomeKit**: ✅ Compatible  
**HACS**: ✅ Supporté
