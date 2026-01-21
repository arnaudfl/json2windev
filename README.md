# json2windev

**json2windev** est un outil Python permettant de générer automatiquement des **structures WinDev**
à partir d’un fichier **JSON**, en respectant strictement les conventions de nommage et de typage
internes (préfixes, structures `ST*`, attributs `<serialize="">`, etc.).

Le projet est pensé pour les développeurs **WinDev / WebDev** travaillant avec des API,
webservices ou flux JSON, et souhaitant éviter toute génération manuelle fastidieuse.

---

## 🎯 Objectif

- Convertir un JSON arbitraire en structures WinDev exploitables
- Garantir une compatibilité parfaite avec le JSON d’origine
- Respecter les normes WinDev (préfixes, typage, sérialisation)
- Centraliser les règles de génération dans un fichier **YAML**
- Fournir une utilisation **CLI** (et GUI à terme)

---

## ✨ Fonctionnalités clés

- Inférence automatique du schéma JSON
- Génération de structures `ST*`
- Préfixes WinDev automatiques (`s`, `n`, `b`, `tab`, `st`, …)
- Génération des attributs `<serialize="cléJson">`
- Gestion des :
  - tableaux (`un tableau de …`)
  - tableaux de chaînes
  - tableaux hétérogènes → `Variant`
  - valeurs `null` → `Variant`
- Ordre de génération : **sous-structures → structures parentes**
- Variable finale :

  ```text
  Resultat est un STResult
  ```

---

## 📁 Structure du projet

```text
json2windev/
├─ config/
│  └─ windev_rules.yaml
├─ docs/
│  └─ examples/
├─ src/
│  └─ json2windev/
│     ├─ core/
│     ├─ renderers/
│     ├─ rules/
│     ├─ utils/
│     └─ app/
├─ tests/
└─ pyproject.toml
```

---

## ⚙️ Installation

### Prérequis

- Python **3.11+**
- Git

### Cloner le dépôt

```bash
git clone https://github.com/arnaudfl/json2windev.git
cd json2windev
```

### (Option recommandé) Créer un environnement virtuel

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux / macOS
```

### Installer les dépendances

```bash
pip install -e .
```

---

## ▶️ Utilisation

### En ligne de commande (CLI)

À partir d’un fichier JSON :

```bash
python -m json2windev docs/examples/glossary.json
```

Depuis l’entrée standard :

```bash
cat docs/examples/glossary.json | python -m json2windev
```

Rediriger la sortie vers un fichier :

```bash
python -m json2windev input.json -o output.txt
```

Utiliser un fichier de règles personnalisé :

```bash
python -m json2windev input.json --rules config/windev_rules.yaml
```

---

## 🧪 Lancer les tests

Les tests permettent de garantir que la génération reste **strictement identique**
(aux exemples de référence) et d’éviter toute régression.

### Installer pytest

```bash
pip install pytest
```

### Lancer tous les tests

```bash
pytest
```

### Lancer un test spécifique

```bash
pytest tests/test_renderer_windev.py
```

Les tests utilisent une approche **golden file** :

- JSON d’entrée connu
- sortie WinDev attendue
- comparaison ligne à ligne

---

## 🔧 Configuration (règles WinDev)

Toutes les règles de génération sont centralisées dans :

```text
config/windev_rules.yaml
```

Ce fichier définit :

- les préfixes de variables (`s`, `n`, `b`, `tab`, `st`, …)
- les types WinDev
- la gestion des tableaux et du `null`
- l’ajout automatique de `<serialize="">`
- l’ordre de génération

👉 **Le moteur n’implémente aucune règle WinDev en dur**.  
Toute évolution passe par une modification du YAML.

---

## 🗺️ Roadmap

Le plan de développement détaillé est disponible dans :

```text
ROADMAP.md
```

---

## 📌 Philosophie du projet

> Le moteur infère des faits.  
> Le YAML décide du style.  
> Le rendu est prévisible et conforme.

---

## 📄 Licence

MIT
