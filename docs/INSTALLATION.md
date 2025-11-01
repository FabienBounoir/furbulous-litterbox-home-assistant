# Installation Guide - Furbulous Cat Integration

## Méthode 1 : Installation via HACS (Recommandée)

### Prérequis
- HACS installé sur votre Home Assistant
- Accès à votre instance Home Assistant

### Étapes

1. **Ouvrez HACS**
   - Allez dans HACS depuis le menu de Home Assistant

2. **Ajoutez ce dépôt personnalisé**
   - Cliquez sur les trois points en haut à droite
   - Sélectionnez "Custom repositories"
   - Ajoutez l'URL de ce dépôt : `https://github.com/fabienbounoir/furbulous-litterbox-home-assistant`
   - Catégorie : "Integration"
   - Cliquez sur "Add"

3. **Installez l'intégration**
   - Recherchez "Furbulous Cat" dans HACS
   - Cliquez sur "Download"
   - Redémarrez Home Assistant

4. **Configurez l'intégration**
   - Allez dans **Paramètres** > **Appareils et services**
   - Cliquez sur **+ Ajouter une intégration**
   - Recherchez "Furbulous Cat"
   - Entrez vos identifiants Furbulous Cat

## Méthode 2 : Installation manuelle

### Prérequis
- Accès SSH ou accès aux fichiers de votre Home Assistant
- Connaissance de l'emplacement du dossier `config`

### Étapes

1. **Téléchargez l'intégration**
   ```bash
   cd ~
   git clone https://github.com/fabienbounoir/furbulous-litterbox-home-assistant.git
   ```

2. **Copiez les fichiers**
   ```bash
   # Créez le dossier custom_components s'il n'existe pas
   mkdir -p /config/custom_components
   
   # Copiez l'intégration
   cp -r furbulous-litterbox-home-assistant/custom_components/furbulous /config/custom_components/
   ```

3. **Vérifiez l'installation**
   ```bash
   ls -la /config/custom_components/furbulous/
   ```
   
   Vous devriez voir :
   - `__init__.py`
   - `config_flow.py`
   - `const.py`
   - `device.py`
   - `furbulous_api.py`
   - `manifest.json`
   - `sensor.py`
   - `strings.json`

4. **Redémarrez Home Assistant**
   - Allez dans **Paramètres** > **Système**
   - Cliquez sur **Redémarrer**

5. **Configurez l'intégration**
   - Allez dans **Paramètres** > **Appareils et services**
   - Cliquez sur **+ Ajouter une intégration**
   - Recherchez "Furbulous Cat"
   - Entrez vos identifiants

## Configuration

### Identifiants requis

- **Email** : Votre adresse email Furbulous Cat
- **Mot de passe** : Votre mot de passe Furbulous Cat
- **Type de compte** : 1 (par défaut)

### Vérification

Après la configuration, vous devriez voir :

1. **Un nouvel appareil** dans Appareils et services
2. **Plusieurs capteurs** pour chaque litière :
   - `sensor.furbulous_box_etat`
   - `sensor.furbulous_box_connexion`
   - `sensor.furbulous_box_derniere_activite`
3. **Un capteur de statut général** :
   - `sensor.furbulous_cat_status`

## Dépannage

### L'intégration n'apparaît pas

1. Vérifiez que les fichiers sont dans le bon dossier :
   ```bash
   ls /config/custom_components/furbulous/
   ```

2. Vérifiez les logs :
   - Allez dans **Paramètres** > **Système** > **Logs**
   - Recherchez "furbulous"

3. Redémarrez Home Assistant complètement

### Erreur d'authentification

1. Vérifiez vos identifiants
2. Essayez de vous connecter à l'application mobile Furbulous Cat
3. Vérifiez que votre compte est actif

### Les capteurs n'apparaissent pas

1. Attendez 5 minutes (première mise à jour)
2. Vérifiez les logs :
   ```yaml
   logger:
     default: info
     logs:
       custom_components.furbulous: debug
   ```
3. Rechargez l'intégration :
   - Paramètres > Appareils et services
   - Cliquez sur les trois points de Furbulous Cat
   - Cliquez sur "Recharger"

### Tester l'API manuellement

Utilisez le script de test fourni :

```bash
cd /path/to/furbulous-litterbox-home-assistant
python3 test_api.py votre.email@example.com votre_mot_de_passe
```

Ce script testera :
- ✅ L'authentification
- ✅ La récupération de la liste des appareils

## Support

Si vous rencontrez des problèmes :

1. **Vérifiez les logs** avec le mode debug activé
2. **Ouvrez une issue** sur GitHub avec :
   - Version de Home Assistant
   - Logs d'erreur
   - Description du problème
3. **Consultez la documentation** dans `API_DOCUMENTATION.md`

## Mise à jour

### Via HACS
1. Ouvrez HACS
2. Recherchez "Furbulous Cat"
3. Cliquez sur "Update" si disponible
4. Redémarrez Home Assistant

### Manuelle
1. Téléchargez la nouvelle version
2. Remplacez les fichiers dans `/config/custom_components/furbulous/`
3. Redémarrez Home Assistant

## Désinstallation

1. **Supprimez l'intégration**
   - Paramètres > Appareils et services
   - Cliquez sur les trois points de Furbulous Cat
   - Cliquez sur "Supprimer"

2. **Supprimez les fichiers** (optionnel)
   ```bash
   rm -rf /config/custom_components/furbulous/
   ```

3. **Redémarrez Home Assistant**
