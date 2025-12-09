# Description

## Type de Changement
<!-- Cochez la case appropriée -->
- [ ] 🐛 Bug fix (changement non-breaking qui corrige un problème)
- [ ] ✨ New feature (changement non-breaking qui ajoute une fonctionnalité)
- [ ] 💥 Breaking change (correction ou feature qui causerait un dysfonctionnement des fonctionnalités existantes)
- [ ] 📝 Documentation update
- [ ] 🎨 Style/UI update (pas de changement de logique)
- [ ] ♻️ Refactoring (pas de changement fonctionnel)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Tests addition/update

## Résumé
<!-- Décrivez clairement ce que fait cette PR en 2-3 phrases -->


## Motivation et Contexte
<!-- Pourquoi ce changement est-il nécessaire? Quel problème résout-il? -->
<!-- Lien vers l'issue GitHub si applicable: Closes #123 -->


## Changements Techniques
<!-- Listez les principaux changements techniques -->
-
-
-

## Screenshots / Vidéos
<!-- Si applicable, ajoutez des screenshots ou vidéos pour les changements UI -->

**Avant:**

**Après:**

---

# Checklist Qualité

## Tests
- [ ] J'ai ajouté des tests qui prouvent que ma correction est efficace ou que ma feature fonctionne
- [ ] Les tests unitaires existants passent localement (`npm test`)
- [ ] Les tests E2E passent localement (si applicable)
- [ ] Coverage ≥ 80% pour le code ajouté

## Code Quality
- [ ] Mon code suit les conventions du projet
- [ ] J'ai effectué une auto-review de mon code
- [ ] J'ai commenté le code dans les zones difficiles à comprendre
- [ ] Pas de console.log() oubliés
- [ ] Pas de code commenté (sauf si justifié)
- [ ] ESLint passe sans erreurs (`npm run lint`)
- [ ] TypeScript compile sans erreurs (`npm run typecheck`)

## Documentation
- [ ] J'ai mis à jour la documentation (si nécessaire)
- [ ] J'ai mis à jour le README (si nécessaire)
- [ ] J'ai documenté les nouvelles fonctions/composants complexes

## Sécurité
- [ ] Pas de secrets/clés API exposés
- [ ] Validation de tous les inputs utilisateur
- [ ] Protection contre XSS/injection
- [ ] Authentification/autorisation vérifiée

## Performance
- [ ] Pas de boucles O(n²) évitables
- [ ] Mémoïsation appropriée (useMemo, useCallback)
- [ ] Images optimisées (si ajout d'images)
- [ ] Bundle size vérifié (pas d'augmentation >20%)

## Accessibilité
- [ ] Alt text sur les images
- [ ] Labels sur les inputs
- [ ] Navigation au clavier fonctionnelle
- [ ] Contraste suffisant

---

# Impact Analysis

## Fichiers Critiques Modifiés
<!-- Listez les fichiers qui pourraient avoir un impact important -->
- [ ] Aucun fichier critique modifié
- [ ] Fichiers critiques: (listez-les)

## Breaking Changes
<!-- Si breaking change, listez ce qui casse et comment migrer -->
- [ ] Aucun breaking change
- [ ] Breaking changes: (détaillez)

## Dépendances
<!-- Nouvelles dépendances ajoutées? -->
- [ ] Aucune nouvelle dépendance
- [ ] Nouvelles dépendances:
  - Package: `xxx` - Raison: ...

## Impact Base de Données
- [ ] Aucune migration nécessaire
- [ ] Migrations à appliquer: (listez)

---

# Testing Instructions

## Comment Tester
<!-- Instructions détaillées pour tester cette PR -->
1.
2.
3.

## Test Data / Setup
<!-- Si des données de test spécifiques sont nécessaires -->


## Environnements Testés
- [ ] Développement local
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Mobile (responsive)

---

# Déploiement

## Pré-requis Déploiement
<!-- Changements de configuration, variables d'environnement, etc. -->
- [ ] Aucun pré-requis
- [ ] Variables d'env à ajouter:
- [ ] Autres pré-requis:

## Rollback Plan
<!-- Comment revenir en arrière si problème en prod? -->


---

# Review Focus Areas
<!-- Guidez les reviewers sur quoi concentrer leur attention -->

**Merci de porter une attention particulière à:**
-
-

**Zones de code où j'ai des doutes:**
-

---

# Related Issues / PRs
<!-- Liens vers issues ou PRs liées -->
- Closes #
- Related to #
- Depends on #

---

# Notes Additionnelles
<!-- Toute information supplémentaire pour les reviewers -->

