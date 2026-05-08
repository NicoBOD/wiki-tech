---
title: "Sniffnet AppImage — Installation et lancement sur Ubuntu 24.04"
date: 2026-05-07
author: Nicolas BODAINE
tags:
  - sniffnet
  - appimage
  - ubuntu 24.04
  - fuse
  - capabilities
  - réseau
difficulty: avancé
os: Ubuntu 24.04
status: publié
---

# Sniffnet AppImage — Installation et lancement sur Ubuntu 24.04

!!! abstract "Résumé"
    L'installation de Sniffnet via AppImage sur Ubuntu 24.04 rencontre **trois problèmes distincts**,
    chacun indépendant du précédent : échec d'intégration AppImageLauncher (compression zstd),
    échec du runtime FUSE embarqué (squashfuse 0.5.2 bugué), et absence de permissions réseau
    (`libcap error`). Cette fiche documente les trois correctifs à appliquer dans l'ordre.

| Propriété | Valeur |
|-----------|--------|
| Difficulté | Avancé |
| OS / Environnement | Ubuntu 24.04 Desktop — GNOME |
| Application | Sniffnet 1.5.0 (AppImage) |
| Dernière mise à jour | 2026-05-07 |

## Contexte

Sniffnet est un outil de surveillance réseau distribué en AppImage. Sur Ubuntu 24.04, trois
couches posent problème :

1. **AppImageLauncher** ne peut pas lire le squashfs interne (compression zstd non supportée)
2. **Le runtime FUSE embarqué** dans l'AppImage plante au montage (bug squashfuse 0.5.2 statique)
3. **Le binaire** n'a pas les droits d'ouvrir des sockets bruts sans root

## Prérequis

- AppImageLauncher installé (`dpkg -l appimagelauncher`)
- L'AppImage `Sniffnet_LinuxAppImage_amd64.AppImage` téléchargée dans `~/Downloads/`
- Accès `sudo`

---

## Problème 1 — AppImageLauncher refuse d'intégrer l'AppImage

### Symptôme

Après avoir déplacé l'AppImage dans `~/Applications/`, aucun raccourci n'apparaît dans le
lanceur GNOME. Les journaux montrent :

```bash
journalctl --user --no-pager -n 30 | grep -i appimage
```

```
appimagelauncherd: Squashfs image uses (null) compression, this version supports only xz, zlib.
appimagelauncherd: ERROR: appimage_shall_not_be_integrated : sqfs_open_image error
appimagelauncherd: WARNING: AppImage shall not be integrated, skipping
```

### Cause

AppImageLauncher 2.2.0 est la seule version disponible. Elle a été compilée pour Ubuntu 18.04
(Bionic) et son `libappimage.so` interne embarque un squashfuse trop ancien qui ne reconnaît
**que xz et zlib**. Sniffnet utilise **zstd** (compression ID 6). Le PPA officiel n'existe
pas pour Ubuntu 24.04 Noble (erreur 404).

### Correctif

Remplacer la bibliothèque bundlée d'AppImageLauncher par la version native Ubuntu 24.04 :

```bash
# 1. Installer les dépendances
sudo apt-get install -y libappimage1.0abi1t64 libsquashfuse0 patchelf

# 2. Créer une copie avec le bon soname
sudo cp /usr/lib/x86_64-linux-gnu/libappimage.so.1.0.3.abi1 /tmp/libappimage-noble.so
sudo patchelf --set-soname libappimage.so.1.0 /tmp/libappimage-noble.so

# 3. Sauvegarder l'ancienne bibliothèque et installer la nouvelle
sudo cp /usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0.3 \
        /usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0.3.backup-bionic
sudo cp /tmp/libappimage-noble.so \
        /usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0
rm /tmp/libappimage-noble.so

# 4. Redémarrer le daemon
systemctl --user restart appimagelauncherd
```

### Vérification

```bash
journalctl --user --no-pager -n 20 --since "1 minute ago" | grep -i appimage
```

!!! success "Résultat attendu"
    ```
    appimagelauncherd: AppImage is not integrated yet, integrating
    appimagelauncherd: Extracting usr/share/icons/hicolor/256x256/apps/sniffnet.png to ...
    appimagelauncherd: Done
    ```

Le raccourci Sniffnet est maintenant visible dans le lanceur GNOME, mais l'application ne se
lance pas encore — voir Problème 2.

---

## Problème 2 — L'AppImage ne se lance pas (runtime FUSE embarqué défaillant)

### Symptôme

Cliquer sur l'icône Sniffnet ou lancer l'AppImage depuis un terminal ne produit rien :

```bash
~/Applications/Sniffnet_LinuxAppImage_amd64_*.AppImage
```

```
fuse: memory allocation failed
squashfuse 0.5.2 (c) 2012 Dave Vasilevsky
(null) options:
    -o offset=N   offset N bytes into ARCHIVE to mount
    ...
Can't open squashfs image: Bad address
Cannot mount AppImage, please check your FUSE setup.
execv error: No such file or directory
```

### Cause

L'AppImage embarque son propre squashfuse (v0.5.2, compilé statiquement). Ce runtime échoue
à initialiser une session FUSE sur Ubuntu 24.04 avec le noyau actuel. Il s'agit d'un bug de
compatibilité propre à cette version du runtime statique — le squashfuse système (v0.5.0)
monte exactement le même squashfs sans problème.

!!! info "Confirmation rapide"
    ```bash
    # Vérifier que le squashfs lui-même est lisible par le système
    mkdir -p /tmp/test-mount
    squashfuse -o offset=$(~/Applications/Sniffnet_*.AppImage --appimage-offset) \
               ~/Applications/Sniffnet_*.AppImage /tmp/test-mount && echo "OK"
    ls /tmp/test-mount/    # doit afficher AppRun, sniffnet.desktop, usr/
    fusermount3 -u /tmp/test-mount
    ```

### Correctif

Extraire le contenu de l'AppImage de façon permanente avec `unsquashfs` (qui supporte zstd)
et créer un wrapper de lancement :

```bash
# 1. Identifier l'offset du squashfs
OFFSET=$(~/Applications/Sniffnet_*.AppImage --appimage-offset)
echo "Offset squashfs : $OFFSET"   # doit afficher 944632

# 2. Extraire vers ~/.local/share/sniffnet/
mkdir -p ~/.local/share/sniffnet
sudo unsquashfs -offset "$OFFSET" -no-progress \
  -dest ~/.local/share/sniffnet \
  ~/Applications/Sniffnet_*.AppImage

# 3. Corriger l'ownership (unsquashfs tourne en root)
sudo chown -R "$USER:$USER" ~/.local/share/sniffnet

# 4. Créer le wrapper de lancement
mkdir -p ~/.local/bin
cat > ~/.local/bin/sniffnet << 'EOF'
#!/bin/bash
APPDIR="$HOME/.local/share/sniffnet"
APPIMAGE=$(echo "$HOME"/Applications/Sniffnet_*.AppImage | head -1)
exec "$APPDIR/AppRun" "$@"
EOF
chmod +x ~/.local/bin/sniffnet

# 5. Corriger le desktop entry créé par AppImageLauncher
DESKTOP=$(ls ~/.local/share/applications/appimagekit_*-Sniffnet.desktop 2>/dev/null | head -1)
if [ -n "$DESKTOP" ]; then
    sed -i \
        -e "s|^Name=.*|Name=Sniffnet|" \
        -e "s|^Exec=.*AppImage.*|Exec=$HOME/.local/bin/sniffnet|" \
        -e "s|^TryExec=.*AppImage.*|TryExec=$HOME/.local/bin/sniffnet|" \
        "$DESKTOP"
    update-desktop-database ~/.local/share/applications/
    echo "Desktop entry mis à jour : $DESKTOP"
fi
```

### Vérification

```bash
~/.local/bin/sniffnet --version
# → sniffnet 1.5.0
```

L'application s'ouvre mais affiche une erreur réseau — voir Problème 3.

---

## Problème 3 — Erreur `libcap error: socket: Operation not permitted`

### Symptôme

Sniffnet se lance mais quelle que soit l'interface sélectionnée, la capture échoue :

```
libcap error: socket: Operation not permitted
```

### Cause

Sniffnet doit ouvrir des **sockets bruts** (raw sockets) pour capturer le trafic réseau. Par
défaut, cette opération est réservée à root. Le binaire n'a aucune capability Linux lui
permettant de le faire sans élévation de privilèges.

### Correctif

Accorder les capabilities réseau directement au binaire via `setcap` — sans passer par `sudo`
pour lancer toute l'application :

```bash
sudo setcap cap_net_raw,cap_net_admin=eip ~/.local/share/sniffnet/usr/bin/sniffnet
```

### Vérification

```bash
# Vérifier les capabilities
getcap ~/.local/share/sniffnet/usr/bin/sniffnet
# → /home/user/.local/share/sniffnet/usr/bin/sniffnet cap_net_admin,cap_net_raw=eip

# Lancer et vérifier l'absence d'erreur réseau
~/.local/bin/sniffnet
```

!!! success "Résultat attendu"
    Sniffnet s'ouvre, la liste des interfaces réseau s'affiche et la capture démarre sans erreur.

---

## En cas de mise à jour de Sniffnet

Lorsqu'une nouvelle version de l'AppImage est disponible, les trois correctifs doivent être
réappliqués car AppImageLauncher remplacera l'AppImage dans `~/Applications/` et l'extraction
précédente sera obsolète.

### Procédure de mise à jour

```bash
# 1. Télécharger la nouvelle AppImage dans ~/Downloads/

# 2. Placer l'AppImage dans ~/Applications/ pour déclencher l'intégration
#    AppImageLauncher va la renommer et créer le desktop entry automatiquement
cp ~/Downloads/Sniffnet_LinuxAppImage_amd64.AppImage ~/Applications/

# 3. Récupérer le nom exact du nouveau fichier
NEW_APPIMAGE=$(ls ~/Applications/Sniffnet_*.AppImage | head -1)
echo "Nouvelle AppImage : $NEW_APPIMAGE"

# 4. Extraire le nouveau squashfs
OFFSET=$("$NEW_APPIMAGE" --appimage-offset)
rm -rf ~/.local/share/sniffnet
mkdir -p ~/.local/share/sniffnet
sudo unsquashfs -offset "$OFFSET" -no-progress \
  -dest ~/.local/share/sniffnet "$NEW_APPIMAGE"
sudo chown -R "$USER:$USER" ~/.local/share/sniffnet

# 5. Réappliquer les capabilities (obligatoire après chaque remplacement du binaire)
sudo setcap cap_net_raw,cap_net_admin=eip ~/.local/share/sniffnet/usr/bin/sniffnet

# 6. Mettre à jour le wrapper
cat > ~/.local/bin/sniffnet << 'EOF'
#!/bin/bash
APPDIR="$HOME/.local/share/sniffnet"
exec "$APPDIR/AppRun" "$@"
EOF
chmod +x ~/.local/bin/sniffnet

# 7. Mettre à jour le desktop entry si AppImageLauncher en a créé un nouveau
DESKTOP=$(ls ~/.local/share/applications/appimagekit_*-Sniffnet.desktop 2>/dev/null | head -1)
if [ -n "$DESKTOP" ]; then
    sed -i \
        -e "s|^Name=.*|Name=Sniffnet|" \
        -e "s|^Exec=.*|Exec=$HOME/.local/bin/sniffnet|" \
        -e "s|^TryExec=.*|TryExec=$HOME/.local/bin/sniffnet|" \
        "$DESKTOP"
    update-desktop-database ~/.local/share/applications/
fi

# 8. Vérification
getcap ~/.local/share/sniffnet/usr/bin/sniffnet
~/.local/bin/sniffnet --version
```

!!! warning "Le setcap est à refaire à chaque mise à jour"
    Les capabilities Linux sont stockées dans les métadonnées du fichier binaire (xattr). Elles
    disparaissent dès que le fichier est remplacé — même si le nom reste identique. Il est donc
    **obligatoire** de relancer le `setcap` après chaque mise à jour de Sniffnet.

!!! tip "Astuce — vérifier la version de la libappimage après une mise à jour système"
    Si Ubuntu met à jour `libappimage1.0abi1t64` ou `libsquashfuse0`, il faudra peut-être
    recréer le correctif du Problème 1 :
    ```bash
    # Vérifier que la bibliothèque patchée est toujours valide
    python3 -c "
    import ctypes
    lib = ctypes.CDLL('/usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0')
    result = lib.appimage_shall_not_be_integrated(
        b'/home/user/Applications/Sniffnet_LinuxAppImage_amd64_*.AppImage')
    print('OK' if result == 0 else 'KO — relancer le correctif Problème 1')
    "
    ```

---

## Récapitulatif des fichiers modifiés

| Fichier | Rôle |
|---------|------|
| `/usr/lib/x86_64-linux-gnu/appimagelauncher/libappimage.so.1.0.3` | Bibliothèque AppImageLauncher remplacée (backup : `.backup-bionic`) |
| `~/.local/share/sniffnet/` | Contenu extrait de l'AppImage (AppRun + binaire + ressources) |
| `~/.local/share/sniffnet/usr/bin/sniffnet` | Binaire Sniffnet avec `cap_net_raw,cap_net_admin=eip` |
| `~/.local/bin/sniffnet` | Wrapper de lancement |
| `~/.local/share/applications/appimagekit_*-Sniffnet.desktop` | Entrée bureau GNOME (Exec → wrapper) |

## Ressources

- [Sniffnet — Install on Linux (wiki officiel)](https://github.com/GyulyVGC/sniffnet/wiki/Install-on-Linux) — Documentation officielle incluant l'option `sudo -E`
- [AppImageLauncher GitHub](https://github.com/TheAssassin/AppImageLauncher) — Projet (abandonné pour Ubuntu 24.04)
- [Linux capabilities — man 7 capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html) — Référence complète des capabilities Linux
- [squashfuse GitHub](https://github.com/vasi/squashfuse) — Source squashfuse, changelog des compressions supportées
