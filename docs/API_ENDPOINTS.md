# Furbulous Cat API - Endpoints complets

Documentation extraite du code décompilé de l'application Android.

## Base URL
```
https://app.api.fr.furbulouspet.com:1443
```

## Authentication
Tous les endpoints nécessitent les headers suivants :
- `appid`: a0baae0630f444b0811ea3c2eb212179
- `platform`: ios (ou android)
- `ts`: timestamp Unix
- `sign`: MD5(appid + path + timestamp) en lowercase
- `authorization`: token (sauf pour /auth/login)

---

## 🔐 Authentication (LoginService)

### POST /app/v1/auth/login
Authentification avec email/password
```json
{
  "account": "email@example.com",
  "password": "password",
  "account_type": 1,
  "iso": "DE",
  "area": "EU",
  "clientid": "65l32f6ql1qehx6",
  "brand": "HomeAssistant",
  "client_token": "",
  "AppVersion": "HomeAssistant_1.0.0"
}
```

### POST /app/v1/auth/register
Enregistrement d'un nouveau compte

### POST /app/v1/auth/autoLogin
Connexion automatique

### POST /app/v1/auth/sendVerifyCode
Envoi d'un code de vérification

### POST /app/v1/auth/checkVerifyCode
Vérification du code

### POST /app/v1/auth/verifyCodeLogin
Connexion avec code de vérification

### POST /app/v1/auth/forgetPwdLogin
Récupération de mot de passe

### POST /app/v1/auth/resetPwdLogin
Réinitialisation du mot de passe

---

## 📱 Devices (DeviceService)

### GET /app/v1/device/list
Liste de tous les devices de l'utilisateur
```
Response: Array de DeviceBindInfoRes
```

### GET /app/v1/device/info
Informations détaillées d'un device
```
Query params: ?iotid=<device_id>
Response: DeviceInfo {last_ip, device_name, mac, software, hardware}
```

### GET /app/v1/device/nickname
Récupère le surnom du device
```
Query params: ?iotid=<device_id>
Response: {name: "Device Name"}
```

### GET /app/v1/device/data/petData
Données d'activité du chat (historique)
```
Query params: ?iotid=<device_id>&day=<1-30>&type=<0>
Response: {
  counts: [{value, stime}],    // Nombre d'utilisations
  duration: [{value, stime, PetId}],  // Durée en minutes
  weight: [{value, stime, PetId}]     // Poids en grammes
}
```

### POST /app/v2/device/bind
Association d'un nouveau device

### POST /app/v1/device/bindShared
Association d'un device partagé

### PUT /app/v1/device/updateNickname
Mise à jour du surnom du device
```json
{
  "iotid": "device_id",
  "nickname": "New Name"
}
```

### PUT /app/v1/device/updateLocation
Mise à jour de la localisation du device

### PUT /app/v1/device/disturb
Activation/désactivation du mode Ne pas déranger

### PUT /app/v1/device/reset
Réinitialisation du device

### DELETE /app/v1/device/unbind
Déliaison d'un device (avec body)

### DELETE /app/v1/device/unbindShared
Déliaison d'un device partagé

### DELETE /app/v1/device/forceUnbind
Déliaison forcée d'un device

### GET /app/v1/product/category/list
Liste des catégories de produits

### POST /app/v1/device/awss/cipher/get
Obtention du cipher pour configuration WiFi

---

## ⚙️ Device Properties (AWSService)

### GET /app/v1/device/properties/get
**ENDPOINT PRINCIPAL** - Récupère toutes les propriétés du device
```
Query params: ?iotid=<device_id>
Response: {
  "ConnectType": {value: "online", time: timestamp},
  "catWeight": {value: 7763, time: timestamp},  // Poids en grammes
  "excreteTimesEveryday": {value: 1, time: timestamp},
  "excreteTimerEveryday": {value: 35, time: timestamp},  // Minutes
  "workstatus": {value: 0, time: timestamp},
  "errorReportEvent": {value: 32, time: timestamp},
  "catLitterType": {value: 0, time: timestamp},
  "FullAutoModeSwitch": {value: 1, time: timestamp},
  "childLockOnOff": {value: 0, time: timestamp},
  "masterSleepOnOff": {value: 0, time: timestamp},
  "DisplaySwitch": {value: 0, time: timestamp},
  "unitSwitch": {value: 0, time: timestamp},
  "completionStatus": {value: 1, time: timestamp},
  "handMode": {value: 1, time: timestamp},
  "sleepTimeStart": {value: 0, time: timestamp},
  "sleepTimeStop": {value: 0, time: timestamp},
  "catBathroomTimeStart": {value: 96, time: timestamp},
  "catBathroomTimeStop": {value: 97, time: timestamp},
  "catCleanOnOff": {value: 1, time: timestamp},
  "timingShoveledShit": {value: "110001000A000100", time: timestamp},
  "mcuversion": {value: "uvw-212", time: timestamp},
  "wifivertion": {value: 132, time: timestamp},
  "trdversion": {value: "0.0.1", time: timestamp},
  "otastatus": {value: 0, time: timestamp},
  "LocalTime": {value: 17504513, time: timestamp}
}
```

### POST /app/v1/device/properties/set
Définit une ou plusieurs propriétés du device
```json
{
  "iotid": "device_id",
  "properties": {
    "propertyName": value
  }
}
```

### GET /app/v1/device/status
Statut du device (online/offline)

### GET /app/v1/device/ota
Vérification des mises à jour OTA
```
Query params: ?iotid=<device_id>
Response: OtaInfo
```

### POST /app/v1/device/ota
Lancement d'une mise à jour OTA

---

## 🐱 Pets (PetService)

### GET /app/v1/pet/list
Liste de tous les animaux de l'utilisateur

### GET /app/v1/pet/info
Informations détaillées d'un animal
```
Query params: ?petid=<pet_id>
```

### POST /app/v1/pet/create
Création d'un nouveau profil d'animal

### PUT /app/v1/pet/update
Mise à jour des informations d'un animal

### GET /app/v1/pet/remind/allMatter
Tous les rappels/notifications pour les animaux

### GET /app/v1/pet/remind/matter
Récupération d'un rappel spécifique

### POST /app/v1/pet/remind/matter
Création d'un rappel

### PUT /app/v1/pet/remind/matter
Mise à jour d'un rappel

### PUT /app/v1/pet/remind/expire
Marquage d'un rappel comme expiré

### GET /app/v1/pet/remind/remind
Liste des rappels actifs

---

## 👤 User (UserService)

### GET /app/v1/user/info
Informations du compte utilisateur

### PUT /app/v1/user/updateInfo
Mise à jour des informations utilisateur

### GET /app/v1/user/logout
Déconnexion

### DELETE /app/v1/user/delete
Suppression du compte

### GET /app/v1/user/getIdentityid
Récupération de l'Identity ID (AWS Cognito)

### PUT /app/v1/user/syncIdentityid
Synchronisation de l'Identity ID

### PUT /app/v1/user/updateAppLanguageTag
Mise à jour de la langue de l'application

### GET /app/v1/user/stat
Statistiques utilisateur

### GET /app/v1/user/pushRecord
Historique des notifications push

### GET /app/v1/user/pushRecord/unread
Notifications push non lues

### GET /app/v1/user/devicePushRecord
Notifications push spécifiques aux devices

### POST /app/v1/user/devicePushRecord/read
Marquer les notifications comme lues

### GET /app/v1/user/devicePushRecord/unread
Notifications device non lues

### GET /app/v1/user/deviceShareRecordList
Liste des partages de devices

---

## 🔗 Device Sharing (AWSService)

### POST /app/v1/device/aws/bind
Liaison AWS du device

### POST /app/v1/device/aws/batch/share
Partage en masse de devices

### POST /app/v1/device/aws/share/agree
Acceptation d'un partage

### DELETE /app/v1/device/aws/unbind
Suppression de la liaison AWS

### POST /app/v1/device/aws/bind/code
Génération d'un code de liaison

### POST /app/v1/device/aws/ble/encryption/random
Génération d'une clé aléatoire pour BLE

### POST /app/v1/device/aws/ble/encryption/verify
Vérification de l'encryption BLE

---

## 📦 Products (ProductService)

### GET /app/v1/goods/list
Liste des produits/accessoires disponibles

### GET /app/v1/product/guide
Guide d'utilisation des produits

### GET /app/v1/product/link
Liens liés aux produits

### GET /app/v1/product/instruction
Instructions des produits

### PUT /app/v1/device/prop/name
Mise à jour du nom d'une propriété

### GET /app/v1/device/linkage/cond
Conditions de liaison entre devices

---

## 💬 Support & Feedback (QuestionService)

### GET /app/v1/help/faqList
Liste des FAQ

### GET /app/v1/help/appConf
Configuration de l'aide dans l'app

### GET /app/v1/feedback/list
Liste des tickets de support

### GET /app/v1/feedback/msgList
Messages d'un ticket

### POST /app/v1/feedback/submit
Création d'un nouveau ticket

### POST /app/v1/feedback/sendMsg
Envoi d'un message dans un ticket

### PUT /app/v1/feedback/append
Ajout d'informations à un ticket

### PUT /app/v1/feedback/solve
Marquage d'un ticket comme résolu

### GET /app/v1/feedback/unread
Tickets non lus

---

## 🔄 Updates (UpdateService)

### GET /app/v1/help/upgradeInfo
Informations de mise à jour (v1)

### GET /app/v2/help/upgradeInfo
Informations de mise à jour (v2)

### GET /app/v1/help/docList
Liste des documents

### GET /app/v1/help/voice
Commandes vocales

### GET /app/v1/panel/upgradeInfo
Infos de mise à jour du panneau

### GET /app/v1/panel/h5/upgradeInfo
Infos de mise à jour H5

---

## ☁️ Cloud Storage (OssService)

### GET /app/v1/oss/stsToken
Token STS pour accès au stockage OSS

### POST /app/v1/oss/uploadImage
Upload d'une image

### POST /app/v1/oss/uploadLog
Upload des logs

---

## 🔧 Configuration (ConfigService)

### GET /app/v1/config/launch
Configuration au lancement de l'app

---

## 📊 Valeurs des propriétés

### workstatus (État de fonctionnement)
- `0`: Idle (en attente)
- `1`: Working (en fonctionnement)
- `2`: Cleaning (nettoyage)
- `3`: Error (erreur)

### catLitterType (Type de litière)
- `0`: Bentonite (bentonite)
- `1`: Tofu (tofu)
- `2`: Mixed (mixte)

### errorReportEvent (Codes d'erreur)
- `32`: Aucune erreur
- Autres codes: voir documentation device

### unitSwitch (Unités)
- `0`: Métrique (kg, cm)
- `1`: Impérial (lb, inch)

### Switches (On/Off)
- `0`: Off/Désactivé
- `1`: On/Activé

Pour:
- `FullAutoModeSwitch`: Mode auto complet
- `childLockOnOff`: Verrouillage enfant
- `masterSleepOnOff`: Mode sommeil principal
- `DisplaySwitch`: Affichage LED
- `catCleanOnOff`: Nettoyage automatique

### catWeight
Valeur en grammes. Ex: 7763 = 7.763 kg

### excreteTimerEveryday
Durée totale d'utilisation en minutes pour la journée

### Times (Heures)
Format: Minutes depuis minuit
- `sleepTimeStart`: Début mode sommeil (ex: 0 = 00:00)
- `sleepTimeStop`: Fin mode sommeil
- `catBathroomTimeStart`: Début période utilisation
- `catBathroomTimeStop`: Fin période utilisation
