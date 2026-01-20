# Architecture

## Couches

- core/
  - json_parser.py
  - schema.py
- renderer/
  - windev_renderer.py
- config/
  - windev_rules.yaml
- cli.py
- gui.py

## Principe clé

Le moteur est indépendant du style.
Le style est 100% piloté par le YAML.
