# DevOps Squad - Architecture

Diagrammes et visualisations de l'architecture du DevOps Squad.

## Vue d'Ensemble du Squad

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEVOPS SQUAD                             │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  Infrastructure  │  │    Security      │  │  Monitoring  │ │
│  │    Engineer      │  │    Engineer      │  │   Engineer   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│           │                     │                     │         │
│           │                     │                     │         │
│           ▼                     ▼                     ▼         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     Base Agent                          │  │
│  │  - LLM Communication (OpenRouter)                       │  │
│  │  - Memory Management                                    │  │
│  │  - Abstract execute() method                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Statistiques Globales

```
Total Code Python:       2,882 lignes
Total Documentation:     37 KB
Agents:                  3
Tasks supportées:        15
Stacks supportés:        6+
Platforms supportées:    5+
```

---

**Navigation:**
- [← Retour à l'index](./INDEX.md)
- [Documentation complète →](./README.md)
