---
title: "AppImageLauncher — Échec d'intégration sur Ubuntu 24.04 (compression zstd)"
date: 2026-05-07
author: Nicolas BODAINE
tags:
  - appimage
  - appimagelauncher
  - squashfs
  - zstd
  - ubuntu 24.04
  - libappimage
difficulty: avancé
os: Ubuntu 24.04
status: publié
---

# AppImageLauncher — Échec d'intégration sur Ubuntu 24.04 (compression zstd)

!!! abstract "Résumé"
    AppImageLauncher 2.2.0 (seule version disponible, compilée pour Ubuntu 18.04) ne supporte pas
    la compression **zstd** utilisée par les AppImages modernes. Sur Ubuntu 24.04, le daemon échoue
    silencieusement et aucun raccourci système n'est créé. Cette fiche couvre le diagnostic complet
    et la correction sans désinstaller AppImageLauncher.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Avancé |
| OS / Environnement | Ubuntu 24.04 Desktop |
| Dernière mise à jour | 2026-05-07 |

## Contexte

AppImageLauncher s'intègre au système via un hook `binfmt_misc` : tout clic sur un fichier `.AppImage`
est intercepté par `/usr/bin/AppImageLauncher`, qui extrait les métadonnées (icônes, `.desktop`) du
squashfs interne pour créer un raccourci dans le lanceur GNOME.

Le PPA officiel (`ppa:appimagelauncher-team/stable`) **n'existe pas pour Ubuntu 24.04 Noble** :
seul le paquet compilé pour Ubuntu 18.04 Bionic (version 2.2.0) est installable. Sa bibliothèque
interne `libappimage.so` embarque une version ancienne de squashfuse qui ne reconnaît que les
compressions **xz** et **zlib**. Les AppImages récentes (Sniffnet, etc.) utilisent **zstd**, ce qui
provoque l'échec.

## Problème

!!! failure "Message d'erreur dans les journaux système"
    ```
    appimagelauncherd: Squashfs image uses (null) compression, this version supports only xz, zlib.
    appimagelauncherd: ERROR: appimage_shall_not_be_integrated : sqfs_open_image error: /home/user/Applications/MonApp.AppImage
    appimagelauncherd: WARNING: AppImage shall not be integrated, skipping
    ```

Le daemon intègre normalement l'AppImage dans `~/Applications/` mais supprime ensuite les fichiers
de bureau générés et aucun raccourci n'est créé dans le lanceur GNOME.

## Diagnostic

### 1. Confirmer l'erreur dans les journaux

```bash
journalctl --user --no-pager -n 50 | grep -i "appimage\|squashfs\|compression"
```

### 2. Vérifier la version installée et le PPA

```bash
dpkg -l appimagelauncher
# Version attendue : 2.2.0-travis995~0f91801+bionic  ← compilée pour Ubuntu 18.04
```

```bash
# Vérifier que le PPA n'existe pas pour noble
cat /etc/apt/sources.list.d/appimagelauncher-team-ubuntu-stable-noble.sources 2>/dev/null \
  | grep "Enabled"
# Enabled: no  →  le PPA est configuré mais désactivé (ou renvoie 404 si activé)
```

### 3. Identifier la compression de l'AppImage problématique

```bash
python3 -c "
import struct
with open('/chemin/vers/MonApp.AppImage', 'rb') as f:
    data = f.read(1100000)
# Chercher tous les superblocks squashfs (magic 'hsqs')
import re
for m in re.finditer(b'hsqs', data):
    pos = m.start()
    inodes, mtime, bsize, frags = struct.unpack_from('<IIII', data, pos + 4)
    comp = struct.unpack_from('<H', data, pos + 20)[0]
    comps = {0:'none', 1:'gzip', 2:'lzma', 3:'lzo', 4:'xz', 5:'lz4', 6:'zstd'}
    print(f'Offset 0x{pos:x}: {inodes} inodes, compression={comp} ({comps.get(comp,\"?\")})' )
"
```

!!! tip "Interpréter le résultat"
    Plusieurs occurrences de `hsqs` peuvent apparaître — seule celle avec un nombre d'inodes
    cohérent (> 1) correspond au vrai superblock. `compression=6` confirme du **zstd**.

### 4. Confirmer que la bibliothèque bundlée est le coupable

```bash
strings /usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0 \
  | grep -i "supports only"
# Résultat : "this version supports only"  →  ancienne bibliothèque sans zstd
```

## Solution

La correction remplace uniquement la bibliothèque interne d'AppImageLauncher par la version
native Ubuntu 24.04 (`libappimage1.0abi1t64`), qui utilise le `libsquashfuse0` système
supportant zstd, lz4, xz, lzo et zlib.

### Étape 1 : Installer les dépendances système

```bash
sudo apt-get install -y libappimage1.0abi1t64 libsquashfuse0 patchelf
```

!!! info "Ce que chaque paquet apporte"
    - `libappimage1.0abi1t64` : version native noble de libappimage (utilise squashfuse système)
    - `libsquashfuse0` : squashfuse 0.5.0 compilé avec support zstd, lz4, xz, lzo, zlib
    - `patchelf` : outil pour modifier le soname d'une bibliothèque ELF

### Étape 2 : Créer une version patchée avec le bon soname

AppImageLauncher cherche une bibliothèque nommée `libappimage.so.1.0`, mais la version système
s'appelle `libappimage.so.1.0abi1`. Il faut corriger ce soname :

```bash
# Copier la bibliothèque système
sudo cp /usr/lib/x86_64-linux-gnu/libappimage.so.1.0.3.abi1 /tmp/libappimage-noble.so

# Changer le soname pour correspondre à ce qu'attend AppImageLauncher
sudo patchelf --set-soname libappimage.so.1.0 /tmp/libappimage-noble.so

# Vérifier
readelf -d /tmp/libappimage-noble.so | grep SONAME
# SONAME : [libappimage.so.1.0]  ← correct
```

### Étape 3 : Sauvegarder l'ancienne bibliothèque et installer la nouvelle

```bash
# Sauvegarder l'ancienne (8 Mo — tout est bundlé dedans)
sudo cp /usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0.3 \
        /usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0.3.backup-bionic

# Remplacer (le .so.1.0 est un symlink vers .so.1.0.3, cp suit le symlink)
sudo cp /tmp/libappimage-noble.so \
        /usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0

# Nettoyer
rm /tmp/libappimage-noble.so
```

### Étape 4 : Redémarrer le daemon

```bash
systemctl --user restart appimagelauncherd
```

## Vérification

### Tester la bibliothèque directement

```bash
python3 -c "
import ctypes
lib = ctypes.CDLL('/usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0')
appimage = '/chemin/vers/MonApp.AppImage'
result = lib.appimage_shall_not_be_integrated(appimage.encode())
print(f'shall_not_be_integrated = {result}')
# 0 = OK (intégration autorisée)  /  -1 = erreur (compression non supportée)
result2 = lib.appimage_get_type(appimage.encode())
print(f'type = {result2}')
# 2 = AppImage Type 2 (correct)
"
```

!!! success "Résultat attendu"
    ```
    shall_not_be_integrated = 0
    type = 2
    ```

### Vérifier l'intégration dans les journaux

```bash
journalctl --user --no-pager -n 40 --since "1 minute ago" | grep -i appimage
```

!!! success "Résultat attendu"
    ```
    appimagelauncherd: AppImage is not integrated yet, integrating
    appimagelauncherd: Extracting usr/share/icons/hicolor/256x256/apps/...
    appimagelauncherd: Done
    ```

### Vérifier le raccourci créé

```bash
ls ~/.local/share/applications/ | grep -i appimagekit
cat ~/.local/share/applications/appimagekit_*-MonApp.desktop
```

## Restauration (si nécessaire)

Pour revenir à l'ancienne bibliothèque bundlée :

```bash
sudo cp /usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0.3.backup-bionic \
        /usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0.3
systemctl --user restart appimagelauncherd
```

## Glossaire

AppImage Type 2
:   Format d'application portable Linux qui embarque un système de fichiers squashfs à la suite d'un binaire ELF. Le runtime est extrait ou monté via FUSE à l'exécution.

binfmt_misc
:   Mécanisme du noyau Linux qui associe un interpréteur à un type de fichier binaire selon sa signature magique. AppImageLauncher l'utilise pour intercepter tout fichier `.AppImage` cliqué.

squashfuse
:   Bibliothèque permettant de monter un système de fichiers squashfs en espace utilisateur (FUSE). Sa version détermine les algorithmes de compression supportés.

soname
:   Identifiant de version d'une bibliothèque partagée Linux, embarqué dans le binaire ELF. Le chargeur dynamique (`ld.so`) vérifie ce nom lors du chargement.

zstd
:   Algorithme de compression rapide (Zstandard, Meta 2016). Compression ID 6 dans le format squashfs. Non supporté par squashfuse < 0.4.x.

## Ressources

- [AppImageLauncher GitHub](https://github.com/TheAssassin/AppImageLauncher) — Projet (dernière release : 2.2.0, novembre 2022)
- [squashfuse GitHub](https://github.com/vasi/squashfuse) — Source de squashfuse avec changelog des compressions supportées
- [AppImage Specification — Type 2](https://github.com/AppImage/AppImageSpec/blob/master/draft.md) — Format officiel AppImage Type 2
