---
title: Mettre en place une surveillance centralisée avec Prometheus et Grafana pour infrastructure cloud hybride
date: 2026-07-07
author: Nicolas BODAINE
tags:
  - monitoring
  - prometheus
  - grafana
  - observabilité
  - cloud
  - infrastructure
difficulty: intermédiaire
os: Ubuntu 24.04 | Windows Server 2025
status: publié
---

<!-- ============================================================ -->
<!-- ⚠️ RAPPEL IMPORTANT :                                          -->
<!-- L'article a été ajouté dans docs/cloud/index.md               -->
<!-- ============================================================ -->

# Surveillance centralisée avec Prometheus et Grafana

!!! abstract "Résumé"
    Tutoriel pas-à-pas pour mettre en place une solution de monitoring open-source sur une infrastructure cloud hybride (AWS, Azure, ou Google Cloud). Installation de Prometheus, configuration de collecteurs, intégration avec Grafana et création de dashboards pour visualiser les métriques.

|| Propriété | Valeur |
||-----------|--------|
|| Difficulté | Intermédiaire |
|| OS / Environnement | Ubuntu 24.04 / Windows Server 2025 |
|| Dernière mise à jour | 2026-07-07 |

## Contexte

Dans une infrastructure cloud hybride, il est crucial de disposer d'une vue unifiée sur l'état de tous les systèmes (VMs, conteneurs, services, bases de données, etc.). Les outils de monitoring permettent de :

- Détecter les anomalies et les problèmes avant qu'ils n'affectent les utilisateurs
- Visualiser les performances et la charge système en temps réel
- Générer des alertes automatiques pour les incidents critiques
- Historiser les données pour des analyses rétrospectives

Prometheus et Grafana forment une stack de monitoring populaire et puissante :
- **Prometheus** est un système de collecte et d'alerte de métriques open-source
- **Grafana** est une plateforme de visualisation de données avec de nombreux dashboards intégrés

Cette stack s'intègre bien avec les environnements cloud (AWS, Azure, GCP) grâce à des exporters standard.

## Prérequis

### Matériel requis

- Une ou plusieurs machines virtuelles (VM) pour héberger Prometheus, Grafana et les exporters
- Accès root ou utilisateur avec droits sudo
- Ports ouverts : 9090 (Prometheus), 3000 (Grafana)
- Au moins 2 Go de RAM par serveur de monitoring

### Logiciels requis

- **Prometheus** : collecteur de métriques
- **Grafana** : visualisation de données
- **Node Exporter** : expose les métriques système (CPU, RAM, disque, réseau)
- **cAdvisor** : expose les métriques des conteneurs (Docker, Kubernetes)
- **NGINX Exporter** (optionnel) : expose les métriques de performance NGINX

### Connexion cloud

- Accès à votre instance principale (AWS EC2, Azure VM, ou GCP Compute Engine)
- Ouverture des ports nécessaires dans les règles de sécurité (security groups / firewall)
- CLI installée (AWS CLI, Azure CLI, ou gcloud)

## Procédure

### Étape 1 : Installer Node Exporter sur chaque serveur

Node Exporter fournit des métriques système de base pour chaque machine.

```bash
# Installer les dépendances
sudo apt update
sudo apt install -y wget curl

# Télécharger Node Exporter
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz

# Extraire et installer
tar xvfz node_exporter-1.8.2.linux-amd64.tar.gz
sudo mv node_exporter-1.8.2.linux-amd64/node_exporter /usr/local/bin/

# Créer un utilisateur système pour Node Exporter
sudo useradd --no-create-home --shell /bin/false node_exporter

# Configurer les droits
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter

# Créer un service systemd
sudo tee /etc/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
Group=node_exporter
ExecStart=/usr/local/bin/node_exporter \
  --collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)

[Install]
WantedBy=multi-user.target
EOF

# Activer et démarrer Node Exporter
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter

# Vérifier le statut
sudo systemctl status node_exporter --no-pager
```

Vérifiez que le port 9100 est accessible depuis le serveur Prometheus :

```bash
curl http://localhost:9100/metrics | head -20
```

### Étape 2 : Installer Prometheus

Prometheus collecte les métriques depuis les exporters configurés.

```bash
# Télécharger Prometheus
cd /opt
sudo wget https://github.com/prometheus/prometheus/releases/download/v2.55.1/prometheus-2.55.1.linux-amd64.tar.gz

# Extraire
sudo tar xvfz prometheus-2.55.1.linux-amd64.tar.gz
sudo mv prometheus-2.55.1.linux-amd64 prometheus

# Créer un utilisateur système
sudo useradd --no-create-home --shell /bin/false prometheus

# Créer les répertoires de données et de logs
sudo mkdir -p /var/lib/prometheus /var/log/prometheus
sudo chown -R prometheus:prometheus /var/lib/prometheus /var/log/prometheus

# Configurer les droits sur l'exécutable
sudo chown -R prometheus:prometheus /opt/prometheus

# Créer la configuration Prometheus
sudo tee /etc/prometheus/prometheus.yml <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
EOF

# Créer un service systemd
sudo tee /etc/systemd/system/prometheus.service <<EOF
[Unit]
Description=Prometheus
After=network.target

[Service]
User=prometheus
Group=prometheus
ExecStart=/opt/prometheus/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus \
  --storage.tsdb.retention.time=30d \
  --web.console.libraries=/opt/prometheus/console_libraries \
  --web.console.templates=/opt/prometheus/consoles \
  --web.listen-address=0.0.0.0:9090

[Install]
WantedBy=multi-user.target
EOF

# Activer et démarrer Prometheus
sudo systemctl daemon-reload
sudo systemctl enable prometheus
sudo systemctl start prometheus

# Vérifier le statut
sudo systemctl status prometheus --no-pager
```

### Étape 3 : Accéder à l'interface Prometheus

Prometheus est accessible sur `http://<IP_DU_SERVEUR>:9090`.

Vérifiez que les targets sont UP :

1. Connectez-vous à l'interface Prometheus
2. Cliquez sur **Status** → **Targets**
3. Vous devriez voir deux targets UP :
   - `prometheus` (localhost:9090)
   - `node_exporter` (localhost:9100)

### Étape 4 : Installer Grafana

Grafana permet de visualiser les métriques collectées par Prometheus.

```bash
# Installer les dépendances
sudo apt install -y software-properties-common apt-transport-https software-properties-common

# Ajouter le repository Grafana
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"

# Importer la clé GPG
wget -q -O - https://packages.grafana.com/gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/grafana-archive-keyring.gpg

# Configurer le repository
echo "deb [signed-by=/usr/share/keyrings/grafana-archive-keyring.gpg] https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Mettre à jour et installer Grafana
sudo apt update
sudo apt install -y grafana

# Activer et démarrer Grafana
sudo systemctl daemon-reload
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

# Vérifier le statut
sudo systemctl status grafana-server --no-pager
```

### Étape 5 : Configurer la source de données Prometheus dans Grafana

1. Connectez-vous à Grafana sur `http://<IP_DU_SERVEUR>:3000`
   - Par défaut : utilisateur `admin`, mot de passe `admin`
   - Changez immédiatement le mot de passe

2. Cliquez sur **Configuration** (roue dentée) → **Data sources**
3. Cliquez sur **Add data source**
4. Sélectionnez **Prometheus**
5. Configurez :
   - **Name** : `Prometheus`
   - **URL** : `http://localhost:9090` (ou l'IP du serveur Prometheus)
   - **Access** : `Server (default)`
6. Cliquez sur **Save & test**
7. Vous devriez voir un message vert "Data source is working"

### Étape 6 : Installer cAdvisor (optionnel - conteneurs)

Si vous utilisez Docker ou Kubernetes :

```bash
# Télécharger cAdvisor
cd /tmp
wget https://github.com/google/cadvisor/releases/download/v0.49.3/cadvisor-0.49.3-linux-amd64.tar.gz

# Extraire et installer
tar xvfz cadvisor-0.49.3-linux-amd64.tar.gz
sudo mv cadvisor-0.49.3-linux-amd64/cadvisor /usr/local/bin/

# Créer un service systemd
sudo tee /etc/systemd/system/cadvisor.service <<EOF
[Unit]
Description=cAdvisor
After=network.target

[Service]
ExecStart=/usr/local/bin/cadvisor \
  --rootfs=/rootfs \
  --docker=unix:///var/run/docker.sock \
  --docker-only \
  --config=/etc/cadvisor/config.yml

[Install]
WantedBy=multi-user.target
EOF

# Créer un fichier de configuration minimal
sudo mkdir -p /etc/cadvisor
sudo tee /etc/cadvisor/config.yml <<EOF
port: 8080
EOF

# Activer et démarrer cAdvisor
sudo systemctl daemon-reload
sudo systemctl enable cadvisor
sudo systemctl start cadvisor

# Vérifier le statut
sudo systemctl status cadvisor --no-pager
```

Ajoutez cAdvisor à la configuration Prometheus :

```bash
sudo tee -a /etc/prometheus/prometheus.yml <<EOF

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['localhost:8080']
EOF

# Redémarrer Prometheus
sudo systemctl restart prometheus
```

### Étape 7 : Créer un premier dashboard

1. Dans Grafana, cliquez sur **+** → **Create** → **Dashboard**
2. Cliquez sur **Add visualization**
3. Ajoutez un graphique pour visualiser l'utilisation du CPU

   - **Query Editor** (metrics) :
     ```
     rate(node_cpu_seconds_total{mode="user"}[5m]) * 100
     ```

   - **Time range** : `Last 5 minutes`

4. Configurez le graphique :
   - **Title** : `Utilisation CPU par cœur`
   - **Unit** : `percent`

5. Ajoutez une nouvelle visualisation pour la mémoire :

   - **Query Editor** (metrics) :
     ```
     (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
     ```

6. Cliquez sur **Dashboard settings** (roue dentée) → **Settings**
7. **Dashboard name** : `Infrastructure Monitoring`
8. **Tags** : `cloud`, `monitoring`, `infrastructure`
9. Cliquez sur **Apply**

### Étape 8 : Configurer des alertes dans Prometheus

Prometheus peut générer des alertes qui sont envoyées à Grafana ou à un système d'alerte (Alertmanager).

```bash
# Créer un fichier d'alertes
sudo tee /etc/prometheus/alerts.yml <<EOF
groups:
  - name: node_alerts
    interval: 30s
    rules:
      - alert: HighCPUUsage
        expr: rate(node_cpu_seconds_total{mode!="idle"}[5m]) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU à plus de 80% pendant 5 minutes"
          description: "Node {{ $labels.instance }} a une utilisation CPU de {{ $value | humanizePercentage }}"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Mémoire à plus de 90% pendant 5 minutes"
          description: "Node {{ $labels.instance }} a une utilisation mémoire de {{ $value | humanizePercentage }}"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Espace disque faible (< 10%)"
          description: "Node {{ $labels.instance }} sur {{ $labels.mountpoint }} a seulement {{ $value | humanizePercentage }} d'espace disponible"
EOF

# Mettre à jour la configuration Prometheus
sudo tee /etc/prometheus/prometheus.yml <<EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'infra-cloud-hybride'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['localhost:8080']

rule_files:
  - "/etc/prometheus/alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: []
EOF

# Redémarrer Prometheus
sudo systemctl restart prometheus

# Vérifier que les règles sont chargées
curl http://localhost:9090/api/v1/rules
```

### Étape 9 : Intégration avec AWS, Azure ou GCP

#### AWS EC2

Ajoutez chaque instance EC2 comme target :

```bash
sudo tee -a /etc/prometheus/prometheus.yml <<EOF

  - job_name: 'aws_ec2'
    ec2_sd_configs:
      - region: us-east-1
        access_key: ${AWS_ACCESS_KEY_ID}
        secret_key: ${AWS_SECRET_ACCESS_KEY}
        port: 9100
        relabel_configs:
          - source_labels: [__meta_ec2_tag_Name]
            target_label: instance
EOF

# Redémarrer Prometheus
sudo systemctl restart prometheus
```

#### Azure VMs

```bash
sudo tee -a /etc/prometheus/prometheus.yml <<EOF

  - job_name: 'azure_vm'
    azure_sd_configs:
      - subscription_id: ${AZURE_SUBSCRIPTION_ID}
        tenant_id: ${AZURE_TENANT_ID}
        client_id: ${AZURE_CLIENT_ID}
        client_secret: ${AZURE_CLIENT_SECRET}
        port: 9100
        refresh_interval: 60s
        relabel_configs:
          - source_labels: [__meta_azure_vm_name]
            target_label: instance
EOF

# Redémarrer Prometheus
sudo systemctl restart prometheus
```

#### Google Cloud Compute Engine

```bash
sudo tee -a /etc/prometheus/prometheus.yml <<EOF

  - job_name: 'gcp_compute'
    gce_sd_configs:
      - project: ${GCP_PROJECT_ID}
        zone: us-central1-a
        filters:
          - name: labels.instance-purpose
            values:
              - monitoring
        port: 9100
        refresh_interval: 60s
        relabel_configs:
          - source_labels: [__meta_gce_instance_name]
            target_label: instance
EOF

# Redémarrer Prometheus
sudo systemctl restart prometheus
```

## Problème / Solution

### Problème : Les targets ne montrent pas "UP"

**Symptôme** : Dans l'interface Prometheus, les targets sont en **DOWN**.

**Causes possibles** :

1. Le port n'est pas ouvert dans le firewall / security group
2. Le service n'est pas démarré
3. L'adresse IP est incorrecte dans la configuration

**Solution** :

```bash
# Vérifier si le service est en cours d'exécution
sudo systemctl status node_exporter

# Vérifier si le port est écoute
sudo netstat -tlnp | grep 9100

# Vérifier les logs du service
sudo journalctl -u node_exporter -n 50

# Vérifier les logs de Prometheus
sudo journalctl -u prometheus -n 50

# Tester la connexion depuis le serveur Prometheus
curl http://<IP_DU_SERVEUR>:9100/metrics | head
```

### Problème : Les métriques ne s'affichent pas dans Grafana

**Symptôme** : Les requêtes dans Grafana retournent des résultats vides.

**Causes possibles** :

1. La source de données n'est pas bien configurée
2. Les métriques n'existent pas (nom incorrect)
3. La plage de temps est trop courte

**Solution** :

1. Vérifiez que la source de données est testée avec succès dans Grafana
2. Dans l'explorateur de métriques de Grafana, vérifiez que les métriques existent
3. Utilisez une plage de temps plus longue (ex: "Last 1 hour")

## Aide-mémoire

|| Commande / Action | Description |
||-------------------|-------------|
| `systemctl status prometheus` | Vérifier le statut de Prometheus |
| `systemctl restart prometheus` | Redémarrer Prometheus |
| `curl http://localhost:9090/-/healthy` | Vérifier la santé de Prometheus |
| `curl http://localhost:9090/api/v1/targets` | Voir les targets actives |
| `systemctl status grafana-server` | Vérifier le statut de Grafana |
| `curl http://localhost:3000/api/health` | Vérifier la santé de Grafana |
| `docker run -d -p 9100:9100 prom/node-exporter` | Lancer Node Exporter en conteneur |
| `docker run -d -p 8080:8080 google/cadvisor` | Lancer cAdvisor en conteneur |

## Checklist

- [x] Node Exporter installé et démarré sur chaque serveur
- [x] Prometheus installé et configuré
- [x] Prometheus collecte les métriques des exporters
- [x] Grafana installé et accessible
- [x] Source de données Prometheus configurée dans Grafana
- [x] Premier dashboard créé
- [x] Alertes définies dans Prometheus
- [x] Intégration cloud configurée (AWS/Azure/GCP)
- [x] Ports ouverts dans le firewall / security groups
- [x] Vérification des logs et du fonctionnement

## Vérification

Testez les requêtes Prometheus dans l'interface :

```bash
# Utilisation CPU globale
curl -s 'http://localhost:9090/api/v1/query?query=rate(node_cpu_seconds_total{mode!="idle"}[5m]) * 100' | jq '.data.result[] | {instance: .metric.instance, value: .value[1]}'

# Mémoire utilisée
curl -s 'http://localhost:9090/api/v1/query?query=(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100' | jq '.data.result[] | {instance: .metric.instance, value: .value[1]}'

# Espace disque disponible
curl -s 'http://localhost:9090/api/v1/query?query=(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100' | jq '.data.result[] | {mountpoint: .metric.mountpoint, value: .value[1]}'
```

Vérifiez que les alertes sont correctement configurées :

```bash
curl -s 'http://localhost:9090/api/v1/alerts' | jq '.data.alerts[] | {alertname: .labels.alertname, state: .state}'
```

## Ressources

- [Documentation Prometheus](https://prometheus.io/docs/) — Documentation officielle
- [Documentation Grafana](https://grafana.com/docs/) — Documentation officielle
- [Node Exporter Documentation](https://github.com/prometheus/node_exporter) — Documentation de Node Exporter
- [cAdvisor Documentation](https://github.com/google/cadvisor) — Documentation de cAdvisor
- [Prometheus Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) — Guide sur les alertes
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/) — Dashboards partagés
- [AWS Monitoring Best Practices](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/best-practices.html) — Meilleures pratiques AWS
- [Azure Monitor Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/) — Documentation Azure Monitor
- [Google Cloud Operations Suite](https://cloud.google.com/monitoring/docs) — Documentation GCP Monitoring

## Glossaire

- **Prometheus** : Système de collecte et d'alerte de métriques open-source développé par SoundCloud
- **Grafana** : Plateforme de visualisation de données open-source pour le monitoring
- **Node Exporter** : Exporter de métriques système pour Linux, expose les métriques sur le port 9100
- **cAdvisor** : Outil de collecte de métriques pour les conteneurs (Docker, Kubernetes)
- **Exporter** : Composant qui expose des métriques dans le format Prometheus
- **Target** : Une cible de scraping, c'est-à-dire une adresse IP et un port où Prometheus collecte des métriques
- **Scrape** : Action de collecter des métriques depuis une target
- **Dashboard** : Page de visualisation de métriques dans Grafana
- **Time series** : Série temporelle de valeurs, format standard des métriques dans Prometheus
- **Alertmanager** : Composant qui gère l'envoi d'alertes (non configuré dans ce tutoriel)
