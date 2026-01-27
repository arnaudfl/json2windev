# json2windev

**json2windev** est un outil en ligne de commande écrit en Python qui permet de :

- convertir un JSON en structures **WinDev**
- générer une **documentation Markdown** riche (structures, dépendances, Mermaid, etc.)
- gérer des JSON réels et "sales" (clés invalides, collisions, tableaux hétérogènes, null, etc.)
- traiter **un fichier ou un dossier entier** (mode batch)

Le projet est pensé pour un usage **professionnel**, prédictible et testable.

---

## Prérequis

- Python **3.10+** (recommandé : 3.11)
- Git
- Windows, Linux ou macOS

---

## Installation

### Cloner le dépôt

```bash
git clone https://github.com/arnaudfl/json2windev.git
cd json2windev
```

### Créer un environnement virtuel (recommandé)

```bash
python -m venv .venv
```

### Activer l’environnement virtuel (⚠️ à faire à chaque nouvelle session)

> ⚠️ **Important**  
> L’environnement virtuel doit être activé **avant toute commande**
> (`pytest`, `python -m json2windev`, etc.).

#### Windows (CMD / PowerShell)

```bash
.venv\Scripts\activate.bat
```

#### Windows (PowerShell – si erreur de droits)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

Une fois activé, l’invite doit afficher :

```text
(.venv)
```

### Installer le projet en mode editable

```bash
python -m pip install -e .
```

---

## Utilisation

### Convertir un fichier JSON (WinDev)

```bash
python -m json2windev example.json
```

➡️ Sortie par défaut : **terminal** (format WinDev, `.txt`).

### Générer la documentation Markdown

```bash
python -m json2windev example.json --format markdown
```

---

## Mode batch (dossier)

Traiter tous les fichiers `.json` d’un dossier.

### WinDev (sortie `.txt`)

```bash
python -m json2windev input_dir --output-dir out --format windev --continue-on-error
```

### Markdown (sortie `.md`)

```bash
python -m json2windev input_dir --output-dir out --format markdown --continue-on-error
```

Structure générée :

```txt
out/
├─ file1.txt
├─ file2.txt
└─ subdir/
   └─ file3.txt
```

---

## Options CLI

| Option | Description |
| ------ | ------------- |
| `--format` | `windev` (défaut) ou `markdown` |
| `--output` | Écrit la sortie dans un fichier |
| `--output-dir` | Dossier de sortie (mode batch) |
| `--continue-on-error` | Continue le batch même si un fichier échoue |
| `--pretty` | Pretty-print du JSON et sortie |
| `--validate-only` | Valide le JSON + schéma puis quitte |
| `--rules` | Chemin vers le fichier `windev_rules.yaml` |

---

## Règles WinDev

Les règles de génération sont définies dans :

```txt
config/windev_rules.yaml
```

Elles contrôlent :

- préfixes (`s`, `n`, `tab`, `st`, etc.)
- types WinDev
- mots réservés
- règles sur les tableaux
- gestion de `<serialize="jsonKey">`

---

## Robustesse / Hardening

Le moteur gère :

- clés invalides (`-`, `.`, `@`, chiffre en premier, clé vide)
- collisions déterministes (`sField`, `sField2`, `sField3`)
- tableaux hétérogènes
- `null` et unions de types
- tableaux vides

➡️ **Le JSON d’entrée n’est jamais modifié**  
La compatibilité est assurée via `<serialize="clé originale">`.

---

## Tests

### Lancer tous les tests

> ⚠️ Assurez-vous que l’environnement virtuel est bien activé (`(.venv)` visible)

```bash
pytest -q
```

Les tests couvrent :

- inférence de schéma
- génération WinDev
- génération Markdown
- hardening JSON réel
- mode batch CLI

---

## Structure du projet

```txt
src/json2windev/
├─ app/            # CLI
├─ core/           # parsing, inférence
├─ renderers/      # WinDev / Markdown
├─ rules/          # chargement YAML
├─ utils/          # helpers (naming, dedupe)
tests/
config/
docs/
```

---

## Licence

Projet personnel – usage libre.
