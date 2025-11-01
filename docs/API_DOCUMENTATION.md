# Guide de développement - Furbulous Cat Integration

## Structure de l'API

### Authentification

**Endpoint:** `POST https://app.api.fr.furbulouspet.com:1443/app/v1/auth/login`

**Body:**
```json
{
  "account_type": 1,
  "account": "email@example.com",
  "password": "votre_mot_de_passe"
}
```

**Response:**
```json
{
  "code": 0,
  "message": "Success！",
  "data": {
    "token": "eu-central-1_xxxxx",
    "phone": "",
    "email": "",
    "identityid": "xxxxx"
  }
}
```

### Liste des appareils

**Endpoint:** `GET https://app.api.fr.furbulouspet.com:1443/app/v1/device/list`

**Headers requis:**
```
Host: app.api.fr.furbulouspet.com:1443
Content-Type: application/json
appid: a0baae0630f444b0811ea3c2eb212179
accept: */*
version: 1.0.0
authorization: <token_from_auth>
priority: u=3, i
accept-language: fr
platform: ios
User-Agent: Furbulous/2.0.1 (com.furbulous.pet; build:202507031750; iOS 26.0.1) Alamofire/4.9.1
ts: <timestamp>
sign: <md5_hash>
```

**Response:**
```json
{
  "code": 0,
  "message": "Success！",
  "data": [{
    "id": 848,
    "name": "Furbulous Box",
    "device_name": "849dc2f4f30b",
    "iotid": "849DC2F4F30B",
    "is_disturb": 0,
    "product_id": 1,
    "product_name": "Furbulous Box",
    "product_key": "a1nBr6nDezL",
    "aws_product_key": "YTHPLL",
    "product_variety": 2,
    "icon": "https://...",
    "username": "user@example.com",
    "device_online": 1,
    "active_time": 1761928860,
    "is_share": 0,
    "platform": 2
  }]
}
```

### Propriétés d'un appareil

**Endpoint:** `GET https://app.api.fr.furbulouspet.com:1443/app/v1/device/properties/get?iotid=<IOTID>`

**Headers requis:** (identiques à l'endpoint device/list)

**Response:**
```json
{
  "code": 0,
  "message": "Success！",
  "data": {
    "ConnectType": {
      "time": 1761928861000,
      "value": "online"
    },
    "catWeight": {
      "time": 1761932835000,
      "value": 7762
    },
    "excreteTimesEveryday": {
      "time": 1761932835000,
      "value": 1
    },
    "excreteTimerEveryday": {
      "time": 1761932835000,
      "value": 50
    },
    "workstatus": {
      "time": 1761932835000,
      "value": 0
    },
    "errorReportEvent": {
      "time": 1761932836000,
      "value": 32
    },
    "catLitterType": {
      "time": 1761928862000,
      "value": 0
    },
    "FullAutoModeSwitch": {
      "time": 1761928862000,
      "value": 1
    },
    "catCleanOnOff": {
      "time": 1761928862000,
      "value": 1
    },
    "childLockOnOff": {
      "time": 1761928862000,
      "value": 0
    },
    "masterSleepOnOff": {
      "time": 1761928862000,
      "value": 0
    },
    "DisplaySwitch": {
      "time": 1761928862000,
      "value": 0
    },
    "handMode": {
      "time": 1761946512000,
      "value": 1
    },
    "mcuversion": {
      "time": 1761928861000,
      "value": "uvw-212"
    },
    "wifivertion": {
      "time": 1761928861000,
      "value": 132
    },
    "trdversion": {
      "time": 1761928861000,
      "value": "0.0.1"
    }
  }
}
```

### Propriétés disponibles

| Propriété | Type | Description | Valeurs possibles |
|-----------|------|-------------|-------------------|
| `ConnectType` | string | Type de connexion | "online", "offline" |
| `catWeight` | int | Poids du chat en grammes | 0-20000 |
| `excreteTimesEveryday` | int | Nombre d'utilisations par jour | 0-99 |
| `excreteTimerEveryday` | int | Durée totale d'utilisation par jour (secondes) | 0-86400 |
| `workstatus` | int | État de fonctionnement | 0=Inactif, 1=Fonctionnement, 2=Nettoyage, 3=Pause |
| `errorReportEvent` | int | Code d'erreur | 0=Aucune, 32=Capteur, 64=Moteur, 128=Pleine |
| `catLitterType` | int | Type de litière | 0=Standard, 1=Bentonite, 2=Tofu, 3=Mixte |
| `FullAutoModeSwitch` | int | Mode automatique complet | 0=Désactivé, 1=Activé |
| `catCleanOnOff` | int | Nettoyage automatique | 0=Désactivé, 1=Activé |
| `childLockOnOff` | int | Verrouillage enfant | 0=Désactivé, 1=Activé |
| `masterSleepOnOff` | int | Mode sommeil | 0=Désactivé, 1=Activé |
| `DisplaySwitch` | int | Affichage | 0=Désactivé, 1=Activé |
| `handMode` | int | Mode manuel | 0=Désactivé, 1=Activé |
| `completionStatus` | int | Statut de complétude | 0=Incomplet, 1=Complet |
| `sleepTimeStart` | int | Heure début sommeil | 0-2359 |
| `sleepTimeStop` | int | Heure fin sommeil | 0-2359 |
| `catBathroomTimeStart` | int | Début utilisation | timestamp |
| `catBathroomTimeStop` | int | Fin utilisation | timestamp |
| `mcuversion` | string | Version MCU | ex: "uvw-212" |
| `wifivertion` | int | Version WiFi | ex: 132 |
| `trdversion` | string | Version TRD | ex: "0.0.1" |
| `LocalTime` | int | Temps local appareil | timestamp |
| `timingShoveledShit` | string | Programmation nettoyage | hex string |
| `unitSwitch` | int | Unité de mesure | 0=Métrique, 1=Impérial |

## Paramètres de l'API

### Sign Generation

Le paramètre `sign` est un hash MD5 généré à partir de :
- `timestamp` (ts)
- `appid`
- `token`

**Note:** L'algorithme exact peut nécessiter des ajustements selon la validation de l'API.

### Timestamps

Le paramètre `ts` est un timestamp Unix (secondes depuis epoch).

## Test de l'API

Pour tester l'API avec curl :

```bash
# 1. Authentification
curl -X POST "https://app.api.fr.furbulouspet.com:1443/app/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "account_type": 1,
    "account": "votre.email@example.com",
    "password": "votre_mot_de_passe"
  }'

# 2. Récupérer la liste des appareils (remplacer TOKEN par le token reçu)
curl -H "Host: app.api.fr.furbulouspet.com:1443" \
  -H "content-type: application/json" \
  -H "appid: a0baae0630f444b0811ea3c2eb212179" \
  -H "accept: */*" \
  -H "version: 1.0.0" \
  -H "authorization: TOKEN" \
  -H "accept-language: fr" \
  -H "platform: ios" \
  -H "User-Agent: Furbulous/2.0.1 (com.furbulous.pet; build:202507031750; iOS 26.0.1) Alamofire/4.9.1" \
  -H "ts: $(date +%s)" \
  -H "sign: SIGN_HASH" \
  "https://app.api.fr.furbulouspet.com:1443/app/v1/device/list"
```

## Capteurs créés

Pour chaque litière Furbulous détectée, l'intégration crée :

### Capteurs classiques (sensor)
1. **Status** - État général (Active/Inactive)
2. **Connexion** - État de la connexion (En ligne/Hors ligne)
3. **Dernière activité** - Timestamp de la dernière activité
4. **Poids du chat** - Poids en grammes lors de la dernière utilisation
5. **Utilisations quotidiennes** - Nombre de fois que la litière a été utilisée aujourd'hui
6. **Durée quotidienne** - Temps total d'utilisation en secondes
7. **État de fonctionnement** - Inactif, En fonctionnement, Nettoyage, Pause
8. **Erreur** - Code et description de l'erreur actuelle
9. **Type de litière** - Standard, Bentonite, Tofu, Mixte
10. **Statut de complétude** - État du cycle de nettoyage
11. **Mode auto complet** - Activé/Désactivé
12. **Nettoyage auto** - Activé/Désactivé
13. **Verrouillage enfant** - Activé/Désactivé
14. **Mode sommeil** - Activé/Désactivé
15. **Affichage** - Activé/Désactivé
16. **Mode manuel** - Activé/Désactivé
17. **Version MCU** - Version du microcontrôleur
18. **Version WiFi** - Version du module WiFi
19. **Version TRD** - Version TRD

### Binary Sensors (binary_sensor)
1. **Connecté** - Device connectivity
2. **Mode auto complet** - État on/off
3. **Nettoyage automatique** - État on/off
4. **Verrouillage enfant** - État on/off (lock icon)
5. **Mode sommeil** - État on/off
6. **Affichage** - État on/off (monitor icon)
7. **Mode manuel** - État on/off
8. **Erreur détectée** - Problem sensor (on si erreur)

## Attributs disponibles

Chaque capteur expose des attributs supplémentaires :
- `device_id` - ID unique de l'appareil
- `device_name` - Nom technique de l'appareil
- `iot_id` - ID IoT
- `product_name` - Nom du produit
- `product_id` - ID du produit
- `platform` - Plateforme (AWS/Other)
- `is_shared` - Appareil partagé (oui/non)
- `icon_url` - URL de l'icône

## Prochaines fonctionnalités à implémenter

Lorsque de nouveaux endpoints seront fournis :
- État de la litière (propre, sale, etc.)
- Niveau de remplissage
- Historique d'utilisation
- Actions de contrôle (nettoyage, etc.)
- Notifications
- Statistiques

## Déboguer

Pour activer les logs détaillés dans Home Assistant, ajoutez à `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.furbulous: debug
```
