# Furbulous Cat - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/fabienbounoir/furbulous-litterbox-home-assistant.svg)](https://github.com/fabienbounoir/furbulous-litterbox-home-assistant/releases)
[![HomeKit Compatible](https://img.shields.io/badge/HomeKit-Compatible-blue.svg)](docs/HOMEKIT_COMPATIBILITY.md)

Intégration **complète et optimisée** pour les litières connectées **Furbulous Cat** dans Home Assistant avec support HomeKit.

---

## 🎯 Fonctionnalités

### ✅ Version 1.1.0 
- ✅ **Interface simplifiée** - 50% d'entités en moins, zéro doublon
- ✅ **6 Sensors essentiels** - Poids, utilisations, durée, erreur, firmware, pet info
- ✅ **5 Binary Sensors** - Chat détecté (30s), bac plein, connecté, child lock, sommeil
- ✅ **1 Button** - Nettoyage manuel (testé et fonctionnel)
- ✅ **4 Switches HomeKit** - Auto clean, mode auto, DND, child lock
- ✅ **Connectivité améliorée** - Retry automatique, detection token robuste
- ✅ **Fast Updates** - Chat dans litière : **30 secondes** ⚡ / Autres : 5 minutes
- ✅ **HomeKit Support** - Compatible avec HomeKit Bridge + Siri
- ✅ **Auto Token Refresh** - Renouvellement automatique avec retry intelligent

### 📊 Total: ~20 entités par installation
- 6 sensors (poids, usage, erreurs, firmware, pet info)
- 5 binary_sensors (chat détecté 30s, bac plein, connectivité, sécurité, sommeil)
- 1 button (nettoyage manuel)
- 4 switches HomeKit (contrôles essentiels)
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
```
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

- **[INSTALLATION.md](docs/INSTALLATION.md)** - Guide installation détaillé
- **[API_ENDPOINTS.md](docs/API_ENDPOINTS.md)** - 86 endpoints API documentés

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

**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Auteur**: [@fabienbounoir](https://github.com/fabienbounoir)  
**HomeKit**: ✅ Compatible  
**HACS**: ✅ Supporté
