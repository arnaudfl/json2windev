# JSON → WinDev structures

## Summary

- Structures: **1**
- Fields: **0**
- Arrays: **0**
- Variant fields: **0**
- Max depth: **0**

## Rules snapshot

- Prefixes enabled: **True**
- Serialize enabled: **True**

### Prefixes

| Kind | Prefix |
|---|---|
| string | `s` |
| int | `n` |
| real | `r` |
| boolean | `b` |
| array | `tab` |
| structure | `st` |
| variant | `v` |

### Type mapping

| JSON kind | WinDev type |
|---|---|
| string | `une chaîne` |
| int | `un entier` |
| real | `un réel` |
| boolean | `un booléen` |
| null / heterogeneous | `un Variant` |

### Array rules

- Empty array: `un tableau de Variant`
- Array of strings: `un tableau de chaînes`
- Generic: `un tableau de {item}`

## Notes

- Fields are generated using WinDev prefixes (if enabled) but keep JSON compatibility via `<serialize="jsonKey">`.
- `null` values and heterogeneous types are mapped to `Variant`.
- Empty arrays are mapped according to `array.empty` in the rules.

## Structure dependencies

This section shows which WinDev structures reference other structures.

- `STResult`


## Table of contents

- [STResult](#stresult)

## Structures

### STResult

| JSON key | WinDev field | WinDev type | Serialize |
|---|---|---|---|

## Generated WinDev code

```wlanguage
STResult est une structure
FIN

Resultat est un STResult
```
