# JSON → WinDev — Roadmap de développement

Ce document définit le **plan de développement complet** du projet **json2windev**.
Il sert de référence pour suivre l’avancement, cadrer les étapes, et éviter toute dérive fonctionnelle.

---

## 🎯 Objectif global

Développer un outil Python capable de :

- analyser un JSON arbitraire,
- en inférer une structure logique,
- générer un code **WinDev conforme aux normes Mecasystems / Emil Frey**,
- via des règles **100 % externalisées en YAML**.

L’outil doit être :

- fiable,
- prédictible,
- maintenable,
- utilisable en CLI et GUI.

---

## 🧱 Phase 0 — Cadrage (VALIDÉE ✅)

### Livrables

- [x] Besoin fonctionnel formalisé
- [x] Stack technique validée
- [x] Architecture définie
- [x] Arborescence projet créée
- [x] Règles WinDev figées (`windev_rules.yaml`)

### Résultat

➡️ Aucun flou fonctionnel ou technique restant  
➡️ Le moteur peut être développé sans hypothèse implicite

---

## 🧠 Phase 1 — Modèle de schéma interne (CORE)

### Phase 1 — Objectif

Créer une représentation interne **agnostique WinDev** du JSON.

### Phase 1 — Tâches

- [ ] Définir la classe `SchemaNode`
  - kinds : object, array, string, number, boolean, null
- [ ] Implémenter le parsing JSON → SchemaNode
- [ ] Implémenter la fusion de types
  - null + type → variant
  - tableau hétérogène → variant
- [ ] Gérer les tableaux vides

### Phase 1 — Fichiers concernés

```bash
src/json2windev/core/schema.py
src/json2windev/core/infer.py
src/json2windev/core/merge.py
```

### Phase 1 — Tests

- [ ] JSON simple
- [ ] JSON imbriqué
- [ ] Tableaux homogènes / hétérogènes
- [ ] null

---

## 🎨 Phase 2 — Chargement et validation des règles YAML

### Phase 2 — Objectif

Garantir que le moteur ne tourne **jamais** avec des règles invalides.

### Phase 2 — Tâches

- [ ] Charger `windev_rules.yaml`
- [ ] Valider les clés obligatoires
- [ ] Valider la cohérence interne (types, chaînes, placeholders)
- [ ] Exposer un objet `Rules` typé

### Phase 2 — Fichiers concernés

```bash
src/json2windev/rules/loader.py
src/json2windev/rules/models.py
```

### Phase 2 — Tests

- [ ] YAML valide
- [ ] YAML incomplet
- [ ] YAML mal formé

---

## 🧾 Phase 3 — Renderer WinDev

### Phase 3 — Objectif

Transformer le schéma interne en **code WinDev strictement conforme**.

### Phase 3 — Tâches

- [ ] Ordonnancement des structures (children → parents)
- [ ] Génération des structures ST*
- [ ] Génération des types scalaires
- [ ] Gestion des tableaux
- [ ] Gestion des mots réservés WinDev
- [ ] Génération de la variable finale (`Resultat`)

### Phase 3 — Fichiers concernés

```bash
src/json2windev/renderers/base.py
src/json2windev/renderers/windev.py
```

### Phase 3 — Tests

- [ ] Exemple Glossary (référence figée)
- [ ] Comparaison ligne à ligne (golden file)

---

## 🖥️ Phase 4 — Interface CLI

### Phase 4 — Objectif

Permettre l’utilisation simple de l’outil en ligne de commande.

### Phase 4 — Commande cible

```bash
json2windev input.json --rules config/windev_rules.yaml
```

### Phase 4 — Tâches

- [ ] Parsing des arguments
- [ ] Gestion des erreurs utilisateur
- [ ] Lecture JSON depuis fichier ou stdin
- [ ] Sortie stdout / fichier

### Phase 4 — Fichiers concernés

```bash
src/json2windev/app/cli.py
```

---

## 🪟 Phase 5 — Interface GUI (Tkinter)

### Phase 5 — Objectif

Permettre une utilisation sans terminal.

### Phase 5 — Fonctionnalités

- Zone texte JSON
- Bouton Générer
- Zone résultat
- Bouton Copier / Exporter

### Phase 5 — Fichiers concernés

```bash
src/json2windev/app/gui_tk.py
```

---

## 🧪 Phase 6 — Tests et verrouillage

### Phase 6 — Objectif

Empêcher toute régression fonctionnelle.

### Phase 6 — Tâches

- [ ] Tests unitaires core
- [ ] Tests renderer (golden files)
- [ ] Tests CLI
- [ ] Validation cross-platform

### Phase 6 — Dossier

```bash
tests/
```

---

## 📦 Phase 7 — Packaging & distribution

### Phase 7 — Objectif

Faciliter l’adoption de l’outil.

### Phase 7 — Options

- [ ] Installation via `pip -e .`
- [ ] Binaire Windows via PyInstaller
- [ ] Documentation utilisateur

### Phase 7 — Fichiers

```bash
scripts/build_exe.ps1
README.md (public)
```

---

## 🔮 Phase 8 — Évolutions futures (hors scope initial)

- Support d’autres langages (DTO C#, TypeScript…)
- Génération Markdown / documentation
- Mode “strict” vs “permissif”
- Intégration CI

---

## ✅ Règle d’or du projet

> **Le moteur n’implémente jamais une règle WinDev.**  
> **Il applique uniquement ce qui est décrit dans le YAML.**

Toute évolution passe par :

1. Mise à jour du YAML
2. Mise à jour de la roadmap
3. Implémentation

---

📌 Ce document fait foi pour toute la durée du projet.
