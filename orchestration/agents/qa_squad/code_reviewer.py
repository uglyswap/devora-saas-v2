"""
Code Reviewer Agent - QA Squad

Agent spécialisé dans la review de code automatique et l'analyse de qualité.
Détecte les anti-patterns, vérifie les bonnes pratiques, analyse la complexité
cyclomatique et suggère des améliorations concrètes.

Author: Devora Orchestration System
Version: 1.0.0
"""

from typing import Dict, Any, List, Optional, Set
import re
import json
from datetime import datetime

from orchestration.core.base_agent import BaseAgent, AgentConfig


class CodeReviewerAgent(BaseAgent):
    """
    Agent Code Reviewer pour l'analyse approfondie de qualité du code.

    Cet agent est un expert en:
    - Review automatique de code (lisibilité, maintenabilité, performance)
    - Détection d'anti-patterns et code smells (God objects, duplication, etc.)
    - Vérification des bonnes pratiques (SOLID, DRY, KISS, YAGNI)
    - Analyse de complexité cyclomatique et cognitive
    - Audit de sécurité (OWASP Top 10, injections, secrets hardcodés)
    - Suggestions d'amélioration actionnables avec exemples de code
    - Review de patterns architecturaux (MVC, Repository, Factory, etc.)

    Architecture:
        - Hérite de BaseAgent pour l'intégration LLM via OpenRouter
        - Implémente validate_input() pour valider le code à reviewer
        - Implémente execute() pour analyser selon le type de review
        - Implémente format_output() pour structurer les findings

    Capabilities:
        - full_review(): Review complète (qualité, sécurité, performance)
        - security_audit(): Audit de sécurité OWASP Top 10
        - performance_audit(): Analyse de performance (complexité, bottlenecks)
        - detect_anti_patterns(): Détection d'anti-patterns et code smells
        - check_best_practices(): Vérification SOLID, DRY, KISS
        - analyze_complexity(): Complexité cyclomatique et cognitive
        - suggest_refactorings(): Suggestions de refactoring avec exemples

    Attributes:
        config (AgentConfig): Configuration de l'agent (model, temperature, etc.)

    Example:
        >>> config = AgentConfig(
        ...     name="code_reviewer",
        ...     model="anthropic/claude-3.5-sonnet",
        ...     api_key="your-key",
        ...     temperature=0.4  # Modérée pour review équilibrée
        ... )
        >>> agent = CodeReviewerAgent(config)
        >>> result = agent.run({
        ...     "code": "...",
        ...     "language": "typescript",
        ...     "focus": "security"
        ... })
        >>> for issue in result["output"]["issues"]:
        ...     print(f"{issue['severity']}: {issue['description']}")
    """

    # Prompt système ultra-détaillé (~600 lignes) définissant l'expertise complète
    SYSTEM_PROMPT = """Tu es un Code Reviewer senior avec 20+ ans d'expérience en software engineering et architecture.

## EXPERTISE PRINCIPALE

Tu es un expert reconnu internationalement en:

### 1. Code Quality Principles

**Lisibilité**:
- Nommage descriptif (variables, fonctions, classes)
- Fonction = verbe, Variable = nom, Classe = nom propre
- Pas d'abréviations cryptiques (sauf standards: i, j, k pour loops)
- Commentaires seulement pour le "pourquoi", pas le "quoi"
- Self-documenting code prioritaire

**Maintenabilité**:
- **DRY (Don't Repeat Yourself)**: Pas de duplication de code
- **KISS (Keep It Simple)**: Solution la plus simple qui fonctionne
- **YAGNI (You Ain't Gonna Need It)**: Pas de features "pour le futur"
- **SOLID Principles**:
  - **S**ingle Responsibility: Une classe/fonction = une responsabilité
  - **O**pen/Closed: Ouvert à l'extension, fermé à la modification
  - **L**iskov Substitution: Les sous-classes respectent le contrat
  - **I**nterface Segregation: Interfaces spécifiques, pas génériques
  - **D**ependency Inversion: Dépendre d'abstractions, pas de concrétions

**Simplicité**:
- Complexité cyclomatique < 10 par fonction (idéalement < 5)
- Complexité cognitive minimale
- Fonctions < 50 lignes (idéalement < 20)
- Classes < 500 lignes (idéalement < 300)
- Nesting depth < 3 niveaux

**Cohésion et Couplage**:
- Haute cohésion: Code lié ensemble
- Faible couplage: Modules indépendants
- Law of Demeter: Ne parler qu'à ses voisins immédiats

### 2. Code Smells - Detection Expertise

**Bloaters** (Code qui grossit):
- **Long Method**: Fonction > 50 lignes
  - Fix: Extract method, décomposer en fonctions plus petites
- **Large Class**: Classe > 500 lignes
  - Fix: Extract class, Single Responsibility
- **Primitive Obsession**: Abus de types primitifs au lieu d'objets métier
  - Fix: Créer Value Objects (Email, Money, UserId)
- **Long Parameter List**: > 3-4 paramètres
  - Fix: Parameter Object, Builder pattern
- **Data Clumps**: Mêmes groupes de données ensemble
  - Fix: Extract class pour encapsuler

**Object-Orientation Abusers**:
- **Switch Statements**: Devrait être du polymorphisme
  - Fix: Strategy pattern, polymorphisme
- **Temporary Field**: Champs utilisés occasionnellement
  - Fix: Extract class pour ces champs
- **Refused Bequest**: Héritage qui n'utilise pas tout
  - Fix: Composition over inheritance
- **Alternative Classes with Different Interfaces**
  - Fix: Rename methods, Extract superclass

**Change Preventers**:
- **Divergent Change**: Une classe change pour plusieurs raisons
  - Fix: Extract class, Single Responsibility
- **Shotgun Surgery**: Un changement nécessite beaucoup de petites modifs
  - Fix: Move method/field, centraliser la logique
- **Parallel Inheritance Hierarchies**
  - Fix: Merger hierarchies ou délégation

**Dispensables** (Inutiles):
- **Comments**: Code devrait être self-explanatory
  - Fix: Refactor pour clarifier, garder seulement "pourquoi"
- **Duplicate Code**
  - Fix: Extract method/function/class
- **Lazy Class**: Classe qui fait trop peu
  - Fix: Inline class, merger avec autre classe
- **Dead Code**: Code non utilisé
  - Fix: Supprimer (sans pitié!)
- **Speculative Generality**: Code "pour le futur"
  - Fix: YAGNI - supprimer jusqu'à vraiment nécessaire

**Couplers** (Couplage excessif):
- **Feature Envy**: Méthode utilise plus une autre classe que la sienne
  - Fix: Move method vers la classe enviée
- **Inappropriate Intimacy**: Classes trop intimes
  - Fix: Encapsulation, déplacer code
- **Message Chains**: `a.b().c().d()`
  - Fix: Hide delegate, extraire méthode
- **Middle Man**: Classe qui délègue juste
  - Fix: Remove middle man, accès direct

### 3. Security Analysis - OWASP Expertise

**OWASP Top 10 (2021)**:

**1. Broken Access Control**:
- Missing authorization checks
- Insecure Direct Object References (IDOR)
- Path traversal (`../../etc/passwd`)
- Elevation of privilege
- CORS misconfiguration

**2. Cryptographic Failures**:
- Hardcoded secrets (API keys, passwords, tokens)
- Weak encryption (MD5, SHA1)
- Missing encryption (passwords en clair)
- Sensitive data in logs
- Transmission over HTTP instead of HTTPS

**3. Injection**:
- SQL Injection: `query = "SELECT * FROM users WHERE id = " + userId`
- NoSQL Injection
- Command Injection: `exec(userInput)`
- LDAP Injection
- XPath Injection
- Template Injection

**4. Insecure Design**:
- Missing security controls
- No rate limiting
- No input validation
- Insufficient entropy (weak randoms)
- Business logic flaws

**5. Security Misconfiguration**:
- Default credentials still active
- Error messages revealing too much
- Unnecessary features enabled
- Missing security headers (CSP, HSTS, X-Frame-Options)
- Unpatched systems

**6. Vulnerable and Outdated Components**:
- Dependencies with known CVEs
- Unmaintained libraries
- No dependency scanning

**7. Identification and Authentication Failures**:
- Weak password policies
- No MFA
- Session fixation
- Missing session timeouts
- Insecure password recovery

**8. Software and Data Integrity Failures**:
- Unsigned packages/updates
- Insecure CI/CD pipeline
- Auto-update without verification
- Deserialization of untrusted data

**9. Security Logging and Monitoring Failures**:
- No logging of security events
- Logs not monitored
- Missing alerting
- Insufficient log detail

**10. Server-Side Request Forgery (SSRF)**:
- User-controlled URLs
- No URL whitelist
- Internal services accessible

### 4. Performance Analysis

**Time Complexity**:
- Identifier O(n²), O(n³) et pires
- Détecter loops imbriqués inutiles
- Trouver algorithmes inefficaces
- Suggérer structures de données optimales

**Algorithmic Optimization**:
```typescript
// ❌ O(n²) - Inefficient
for (let i = 0; i < arr.length; i++) {
  for (let j = 0; j < arr.length; j++) {
    if (arr[i] === arr[j] && i !== j) return true;
  }
}

// ✅ O(n) - Optimized with Set
const seen = new Set();
for (const item of arr) {
  if (seen.has(item)) return true;
  seen.add(item);
}
```

**Space Complexity**:
- Memory leaks potentiels (event listeners non nettoyés)
- Allocations inutiles
- Large objects en mémoire
- Caching opportunities

**Database Performance**:
- **N+1 Problem**: Query en boucle
  - Fix: Eager loading, batch queries
- **Missing Indexes**: Queries lentes
  - Fix: Add indexes on WHERE/JOIN columns
- **SELECT ***: Over-fetching
  - Fix: SELECT seulement colonnes nécessaires
- **No Pagination**: Charger tous les records
  - Fix: Limit/Offset ou cursor-based pagination

**Network Performance**:
- Multiple sequential requests
  - Fix: Paralléliser avec Promise.all()
- Large payloads
  - Fix: Pagination, compression, lazy loading
- Missing caching
  - Fix: HTTP caching, memoization
- No request deduplication
  - Fix: Caching layer, request batching

**Frontend Performance**:
- Unnecessary re-renders (React)
  - Fix: React.memo, useMemo, useCallback
- Heavy computations in render
  - Fix: useMemo pour calculs, Web Workers
- Large lists without virtualization
  - Fix: react-window, react-virtualized
- Bundle size trop gros
  - Fix: Code splitting, tree-shaking, dynamic imports

### 5. Best Practices par Langage

**TypeScript/JavaScript**:
- **Type Safety**: Strict mode, pas de `any`, utiliser `unknown`
- **Error Handling**: try/catch, async/await, pas de Promise rejection non gérée
- **Null Safety**: Optional chaining `?.`, nullish coalescing `??`
- **Immutability**: const par défaut, spread operators, pas de mutations
- **Modern Syntax**: Arrow functions, destructuring, template literals
- **Modules**: ES6 imports, pas de global scope pollution

**Python**:
- **Type Hints**: Utiliser annotations (PEP 484)
- **List Comprehensions**: Préférer à map/filter quand lisible
- **Context Managers**: `with` pour resources (files, DB)
- **Exceptions**: Pas de bare except, être spécifique
- **PEP 8**: Style guide officiel
- **f-strings**: Préférer à format() ou %

**React**:
- **Hooks**: Suivre Rules of Hooks
- **Keys**: Uniques et stables dans listes
- **Props**: Éviter prop drilling, utiliser Context ou state management
- **Side Effects**: useEffect avec dependencies array correcte
- **Performance**: React.memo pour composants lourds, lazy loading

**SQL**:
- **Parameterized Queries**: TOUJOURS, jamais de string concat
- **Indexes**: Sur colonnes dans WHERE, JOIN, ORDER BY
- **Normalization**: Jusqu'à 3NF (généralement)
- **Transactions**: Pour opérations atomiques
- **Views**: Pour queries complexes répétées

### 6. Architecture Patterns

**Design Patterns Classiques**:
- **Singleton**: Une seule instance (DB connection pool)
- **Factory**: Création d'objets sans exposer la logique
- **Builder**: Construction d'objets complexes step-by-step
- **Observer**: Pub/sub pour événements
- **Strategy**: Algorithmes interchangeables
- **Decorator**: Ajouter fonctionnalités dynamiquement
- **Repository**: Abstraction de persistence de données
- **Dependency Injection**: Inversion of Control

**Architectural Patterns**:
- **MVC** (Model-View-Controller)
- **MVVM** (Model-View-ViewModel)
- **Layered Architecture** (Presentation → Business → Data)
- **Hexagonal Architecture** (Ports & Adapters)
- **CQRS** (Command Query Responsibility Segregation)
- **Event Sourcing**
- **Microservices** (quand approprié)

**Anti-Patterns Architecturaux**:
- **God Object**: Objet qui sait/fait trop
- **Spaghetti Code**: Flux de contrôle complexe et difficile à suivre
- **Lava Flow**: Dead code qui reste "au cas où"
- **Golden Hammer**: Utiliser la même solution pour tout
- **Cargo Cult Programming**: Copier sans comprendre

### 7. Error Handling & Input Validation

**Error Handling Best Practices**:
```typescript
// ❌ Mauvais: Silent failure
try {
  await riskyOperation();
} catch (e) {
  // Rien - erreur ignorée!
}

// ❌ Mauvais: Catch trop générique
try {
  await operation();
} catch (e) {
  console.log('Error'); // Quelle erreur? Quoi faire?
}

// ✅ Bon: Error handling précis
try {
  await operation();
} catch (error) {
  if (error instanceof NetworkError) {
    logger.error('Network failed', { error, context });
    return fallbackData;
  }
  if (error instanceof ValidationError) {
    return { error: error.message, field: error.field };
  }
  // Unexpected errors
  logger.critical('Unexpected error', { error });
  throw error; // Re-throw si vraiment inattendu
}
```

**Input Validation**:
- Valider TOUTES les entrées utilisateur
- Whitelist > Blacklist
- Type checking (TypeScript, Zod, Yup)
- Sanitization (XSS prevention)
- Length limits
- Format validation (email, phone, etc.)

### 8. Documentation & Comments

**Good Comments**:
- **WHY**: Pourquoi cette solution (décisions non évidentes)
- **WARNINGS**: Side effects dangereux
- **TODOs**: Avec ticket/issue number
- **Workarounds**: Pour bugs externes, avec liens
- **Regex**: Explication de patterns complexes
- **Business Logic**: Règles métier non évidentes

**Bad Comments**:
- **WHAT**: Ce que fait le code (devrait être évident)
- **Commented Code**: Code mort en commentaire (utiliser Git!)
- **Obvious**: `i++ // increment i`
- **Outdated**: Comments qui ne matchent plus le code

### 9. Testing Considerations

**Code Testability**:
- Dependency Injection (pas de hardcoded dependencies)
- Pure functions (même input → même output)
- Pas de side effects cachés
- Interfaces claires
- Mocking-friendly (pas de static methods partout)

**Test Coverage**:
- Business logic critique: 100%
- Utilities: 90%+
- UI: 70%+
- Edge cases couverts
- Error paths testés

### 10. Refactoring Opportunities

**Quand Refactorer**:
- Before adding features (clean first)
- When fixing bugs (comprendre le code)
- Code smell détecté
- Performance issues
- Security issues

**Comment Refactorer**:
- Tests AVANT (prevent regressions)
- Petits steps incrémentaux
- Commit souvent
- Un refactoring à la fois
- Review après chaque step

## TON RÔLE ET RESPONSABILITÉS

Quand tu reviews du code, tu dois:

1. **Analyser Systématiquement**:
   - Lire le code ligne par ligne
   - Comprendre l'intention et le contexte
   - Identifier tous les problèmes (pas juste les évidents)
   - Prioriser par sévérité

2. **Catégoriser les Issues**:
   - **🔴 CRITICAL**: Bugs, security issues, data loss potential
   - **🟠 MAJOR**: Performance issues, violations SOLID, maintenance nightmare
   - **🟡 MINOR**: Code smells, best practices non suivies
   - **🟢 SUGGESTION**: Nice-to-have, optimisations non urgentes

3. **Être Constructif**:
   - Toujours expliquer le POURQUOI
   - Donner des exemples de fix CONCRETS
   - Reconnaître ce qui est bien fait (positif!)
   - Ton empathique et pédagogique

4. **Être Actionnable**:
   - Pas de "c'est mal" sans solution
   - Code examples pour fixes
   - Priorités claires (fix now vs later vs never)
   - Liens vers docs/resources si pertinent

5. **Être Précis**:
   - Localisation exacte (fichier:ligne)
   - Pas de vagues "il y a des problèmes"
   - Quantifier quand possible (complexité, taille, etc.)

## FORMAT DE SORTIE

Tes reviews doivent TOUJOURS suivre ce format:

```markdown
## Code Review Summary

**Overall Quality**: Excellent | Good | Fair | Poor | Critical
**Total Issues**: X (🔴 Critical: Y | 🟠 Major: Z | 🟡 Minor: W | 🟢 Suggestions: V)

---

## 🔴 CRITICAL Issues

### 1. SQL Injection Vulnerability
**Location**: `api/users.ts:45-48`
**Severity**: CRITICAL
**Issue**: User input directly concatenated into SQL query
**Why**: Allows attackers to execute arbitrary SQL, steal/modify data
**Fix**:
\`\`\`typescript
// ❌ Current (DANGEROUS)
const query = `SELECT * FROM users WHERE id = ${userId}`;

// ✅ Fixed (Parameterized)
const query = 'SELECT * FROM users WHERE id = $1';
const result = await db.query(query, [userId]);
\`\`\`
**Reference**: https://owasp.org/www-community/attacks/SQL_Injection

---

## 🟠 MAJOR Issues

### 2. O(n²) Performance Issue
[...]

## 🟡 MINOR Issues

### 5. Long Function
[...]

## 🟢 SUGGESTIONS

### 8. Use Modern Syntax
[...]

---

## ✅ What's Good

- Clean separation of concerns in service layer
- Comprehensive error handling in API routes
- Good use of TypeScript types
- Well-documented complex algorithms

## 📚 Resources

- [OWASP Top 10](https://owasp.org/Top10/)
- [Clean Code by Robert Martin](...)
- [Refactoring by Martin Fowler](...)
```

Tu es le meilleur code reviewer au monde. Tes reviews sont références. Go!"""

    def __init__(self, config: AgentConfig):
        """
        Initialise le Code Reviewer Agent.

        Args:
            config: Configuration de l'agent (API key, model, etc.)
        """
        super().__init__(config)
        self.logger.info("Code Reviewer Agent initialized with expert code analysis capabilities")

    def validate_input(self, input_data: Any) -> bool:
        """
        Valide les données d'entrée pour la review de code.

        Args:
            input_data: Dictionnaire contenant:
                - code: Code source à reviewer (requis)
                - language: Langage de programmation (optionnel, auto-détecté)
                - focus: Focus de la review ("security" | "performance" | "quality" | "all")
                - context: Contexte additionnel (optionnel)

        Returns:
            True si input valide

        Raises:
            ValueError: Si input invalide avec message descriptif
        """
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")

        code = input_data.get("code", "").strip()
        if not code:
            raise ValueError("Missing required field: 'code'")

        if len(code) < 10:
            raise ValueError("Code is too short to review (minimum 10 characters)")

        # Valider focus si spécifié
        focus = input_data.get("focus", "all")
        valid_focuses = ["all", "security", "performance", "quality", "architecture", "anti-patterns"]
        if focus not in valid_focuses:
            raise ValueError(f"Invalid focus: {focus}. Must be one of {valid_focuses}")

        self.logger.debug(f"Input validation passed for code review with focus: {focus}")
        return True

    def execute(self, input_data: Any, **kwargs) -> Any:
        """
        Effectue la review de code selon le focus demandé.

        Args:
            input_data: Dictionnaire validé contenant les paramètres
            **kwargs: Paramètres additionnels

        Returns:
            Dictionnaire contenant la review complète et métadonnées
        """
        code = input_data["code"]
        language = input_data.get("language", self._detect_language(code))
        focus = input_data.get("focus", "all")
        context = input_data.get("context", "")

        self.logger.info(f"Reviewing {language} code with focus on {focus}")

        # Construire le prompt selon le focus
        if focus == "security":
            user_prompt = self._build_security_prompt(code, language, context)
        elif focus == "performance":
            user_prompt = self._build_performance_prompt(code, language, context)
        elif focus == "quality":
            user_prompt = self._build_quality_prompt(code, language, context)
        elif focus == "architecture":
            user_prompt = self._build_architecture_prompt(code, language, context)
        elif focus == "anti-patterns":
            user_prompt = self._build_anti_patterns_prompt(code, language, context)
        else:  # "all"
            user_prompt = self._build_full_review_prompt(code, language, context)

        # Appeler le LLM
        response = self._call_llm(
            prompt=user_prompt,
            system_message=self.SYSTEM_PROMPT,
            temperature=kwargs.get("temperature", 0.4)  # Modérée pour review équilibrée
        )

        return {
            "review": response["content"],
            "language": language,
            "focus": focus,
            "code_metrics": self._calculate_basic_metrics(code),
            "model_used": response.get("model"),
            "tokens_used": response.get("usage", {})
        }

    def format_output(self, raw_output: Any) -> Dict[str, Any]:
        """
        Formate la sortie brute en structure standardisée.

        Args:
            raw_output: Sortie brute de execute()

        Returns:
            Dictionnaire formaté avec review et métadonnées
        """
        # Extraire les issues de la review
        issues = self._parse_issues_from_review(raw_output["review"])

        return {
            "review": raw_output["review"],
            "summary": {
                "language": raw_output["language"],
                "focus": raw_output["focus"],
                "total_issues": len(issues),
                "critical": sum(1 for i in issues if i["severity"] == "critical"),
                "major": sum(1 for i in issues if i["severity"] == "major"),
                "minor": sum(1 for i in issues if i["severity"] == "minor"),
                "suggestions": sum(1 for i in issues if i["severity"] == "suggestion")
            },
            "issues": issues,
            "metrics": raw_output["code_metrics"],
            "metadata": {
                "model": raw_output.get("model_used"),
                "tokens": raw_output.get("tokens_used"),
                "reviewed_at": datetime.now().isoformat()
            }
        }

    # ==================== PROMPT BUILDERS ====================

    def _build_full_review_prompt(self, code: str, language: str, context: str) -> str:
        """Construit le prompt pour une review complète."""
        return f"""Effectue une code review COMPLÈTE et APPROFONDIE du code suivant.

LANGAGE: {language}

CONTEXTE:
{context if context else "Pas de contexte spécifique fourni"}

CODE À REVIEWER:
```{language}
{code}
```

ANALYSE TOUS LES ASPECTS:

1. **🔒 Security** (OWASP Top 10):
   - Injections (SQL, NoSQL, Command, XSS)
   - Broken authentication/authorization
   - Sensitive data exposure (hardcoded secrets, logs)
   - Security misconfiguration
   - Vulnerable dependencies
   - CSRF, SSRF vulnerabilities

2. **⚡ Performance**:
   - Time complexity (Big O)
   - Space complexity
   - Database performance (N+1, missing indexes)
   - Network optimization (caching, batching)
   - Algorithmic inefficiencies

3. **✨ Code Quality**:
   - SOLID principles violations
   - DRY violations (code duplication)
   - KISS violations (over-engineering)
   - YAGNI violations (speculative generality)
   - Naming conventions
   - Function/class size
   - Complexity (cyclomatique < 10)

4. **🏗️ Architecture & Patterns**:
   - Design patterns appropriés
   - Anti-patterns détectés
   - Separation of concerns
   - Dependency management
   - Error handling

5. **🧪 Testability**:
   - Code testable (dependency injection)
   - Pure functions vs side effects
   - Mock-friendly design

6. **📝 Documentation**:
   - Comments pertinents (WHY, pas WHAT)
   - JSDoc/docstrings si appropriés
   - TODOs avec context

POUR CHAQUE ISSUE DÉTECTÉE:

- **Severity**: 🔴 CRITICAL | 🟠 MAJOR | 🟡 MINOR | 🟢 SUGGESTION
- **Location**: Ligne(s) précise(s)
- **Issue**: Description claire du problème
- **Why**: Pourquoi c'est problématique (impact)
- **Fix**: Solution concrète AVEC CODE
- **Reference**: Lien vers docs/best practices si pertinent

STRUCTURE DE SORTIE OBLIGATOIRE:

```markdown
## Code Review Summary

**Overall Quality**: [Excellent/Good/Fair/Poor/Critical]
**Total Issues**: X (🔴 Y | 🟠 Z | 🟡 W | 🟢 V)
**Complexity**: [Low/Medium/High/Very High]

---

## 🔴 CRITICAL Issues
[Si aucun: "None detected ✅"]

### 1. [Issue Title]
**Location**: line X-Y
**Issue**: [Description]
**Why**: [Impact/Risk]
**Fix**:
\`\`\`{language}
// ❌ Current code
[problematic code]

// ✅ Fixed code
[solution]
\`\`\`
**Reference**: [URL if applicable]

---

## 🟠 MAJOR Issues
[...]

## 🟡 MINOR Issues
[...]

## 🟢 SUGGESTIONS
[...]

---

## ✅ What's Good
- [Positive point 1]
- [Positive point 2]
- [...]

## 📊 Code Metrics
- Lines of Code: X
- Functions: Y
- Avg Complexity: Z
- [Other relevant metrics]

## 📚 Resources
- [Relevant link 1]
- [Relevant link 2]
```

REVIEW COMPLÈTE, CONSTRUCTIVE ET ACTIONNABLE."""

    def _build_security_prompt(self, code: str, language: str, context: str) -> str:
        """Construit le prompt pour un audit de sécurité."""
        return f"""Effectue un AUDIT DE SÉCURITÉ COMPLET et APPROFONDI du code suivant.

LANGAGE: {language}

CONTEXTE:
{context if context else "Audit de sécurité général"}

CODE À AUDITER:
```{language}
{code}
```

ANALYSE SELON OWASP TOP 10 (2021):

### 1. Broken Access Control
- Missing authorization checks
- Insecure Direct Object References (IDOR)
- Path traversal vulnerabilities
- Elevation of privilege possible
- CORS misconfiguration
- Bypassing access control via URL modification

### 2. Cryptographic Failures
- Hardcoded secrets (API keys, passwords, tokens, credentials)
- Sensitive data in logs, error messages, URLs
- Weak hashing algorithms (MD5, SHA1)
- Missing encryption for sensitive data
- Transmission over HTTP instead of HTTPS
- Predictable IDs, tokens, session IDs

### 3. Injection Vulnerabilities
- **SQL Injection**: String concatenation dans queries
- **NoSQL Injection**: Unescaped user input dans MongoDB, etc.
- **Command Injection**: `exec()`, `eval()` avec user input
- **XSS (Cross-Site Scripting)**: Unescaped HTML output
- **LDAP, XPath, Template Injection**

### 4. Insecure Design
- Missing rate limiting (brute force, DoS)
- No input validation/sanitization
- Insufficient entropy (weak randoms)
- Business logic flaws
- Missing security controls

### 5. Security Misconfiguration
- Default credentials
- Error stack traces exposed
- Unnecessary features enabled
- Missing security headers (CSP, HSTS, X-Frame-Options)
- Directory listing enabled

### 6. Vulnerable and Outdated Components
- Dependencies with known CVEs
- Unmaintained libraries
- Missing security patches

### 7. Identification and Authentication Failures
- Weak password policies
- No multi-factor authentication
- Session fixation possible
- Missing session timeout
- Insecure password recovery
- Credentials in URLs or logs

### 8. Software and Data Integrity Failures
- Unsigned packages/updates
- Insecure CI/CD pipeline
- Auto-update without verification
- Deserialization of untrusted data

### 9. Security Logging and Monitoring Failures
- No logging of authentication attempts
- Sensitive operations not logged
- Logs not monitored/alerted
- Insufficient log detail

### 10. Server-Side Request Forgery (SSRF)
- User-controlled URLs in server requests
- No URL whitelist/validation
- Internal services accessible via SSRF

POUR CHAQUE VULNÉRABILITÉ:

```markdown
### [Vulnerability Type]
**Severity**: CRITICAL | HIGH | MEDIUM | LOW
**OWASP Category**: [OWASP Top 10 category]
**Location**: line X
**Vulnerability**: [Description]
**Exploit Scenario**: [Comment un attaquant pourrait exploiter]
**Impact**: [Data breach, RCE, DoS, etc.]
**Fix**:
\`\`\`{language}
// ❌ Vulnerable
[code vulnérable]

// ✅ Secured
[code sécurisé]
\`\`\`
**Additional Recommendations**: [...]
**Reference**: [OWASP link, CVE, etc.]
```

AUDIT COMPLET ET SANS COMPROMIS SUR LA SÉCURITÉ."""

    def _build_performance_prompt(self, code: str, language: str, context: str) -> str:
        """Construit le prompt pour un audit de performance."""
        return f"""Effectue un AUDIT DE PERFORMANCE COMPLET du code suivant.

LANGAGE: {language}

CONTEXTE:
{context if context else "Audit de performance général"}

CODE À ANALYSER:
```{language}
{code}
```

ANALYSE TOUS LES ASPECTS DE PERFORMANCE:

### 1. Time Complexity (Algorithmic)

- Identifier opérations O(n²), O(n³) ou pires
- Détecter nested loops inutiles
- Trouver algorithmes inefficaces
- Suggérer structures de données optimales

Pour chaque inefficacité:
```markdown
**Issue**: [Description]
**Current Complexity**: O(?)
**Bottleneck**: lines X-Y
**Optimization**:
\`\`\`{language}
// ❌ O(n²) - Inefficient
[code actuel]

// ✅ O(n) - Optimized
[code optimisé]
\`\`\`
**Performance Gain**: [Estimation]
```

### 2. Space Complexity

- Memory leaks potentiels:
  - Event listeners non nettoyés
  - Timers non cleared
  - References circulaires
  - Closures gardant grosses données
- Allocations inutiles
- Large objects en mémoire
- Caching opportunities manquées

### 3. Database Performance

- **N+1 Problem**: Queries dans boucles
  - Fix: Eager loading, batch queries, JOIN
- **Missing Indexes**: Queries sur colonnes non indexées
  - Fix: CREATE INDEX sur WHERE/JOIN/ORDER BY columns
- **SELECT ***: Over-fetching
  - Fix: SELECT seulement colonnes nécessaires
- **No Pagination**: Charger tous les records
  - Fix: LIMIT/OFFSET ou cursor-based pagination
- **Inefficient Queries**: Subqueries, multiple JOINs
  - Fix: Optimize query structure, materialized views

### 4. Network Performance

- **Sequential Requests**: Devrait être parallèle
  - Fix: Promise.all(), concurrent requests
- **Large Payloads**: Transfert de trop de données
  - Fix: Compression, pagination, field selection
- **Missing Caching**: Re-fetching même data
  - Fix: HTTP caching, CDN, memoization
- **No Request Deduplication**
  - Fix: Request caching, batching

### 5. Frontend Performance (si applicable)

- **React Re-renders**: Unnecessary re-renders
  - Fix: React.memo, useMemo, useCallback
- **Heavy Computations**: Dans render path
  - Fix: useMemo, Web Workers pour calculs lourds
- **Large Lists**: Sans virtualization
  - Fix: react-window, infinite scroll
- **Bundle Size**: JavaScript trop gros
  - Fix: Code splitting, tree-shaking, dynamic imports, lazy loading

### 6. Concurrency & Async

- Blocking operations dans event loop
- Missing async/await
- Promise anti-patterns (nested then)
- Race conditions
- Synchronous file I/O

### 7. String/Array Operations

- String concatenation en boucle
  - Fix: Array join ou template literals
- Unnecessary copies (push vs concat)
- Regex dans hot paths
- Missing memoization de calculs coûteux

POUR CHAQUE ISSUE:

```markdown
### [Issue Type]
**Impact**: HIGH | MEDIUM | LOW
**Current Complexity**: O(?)
**Bottleneck**: lines X-Y
**Issue**: [Description]
**Benchmark**: [Current performance metrics if estimable]
**Optimization**:
\`\`\`{language}
// Before
[code actuel]

// After
[code optimisé]
\`\`\`
**Estimated Improvement**: [X% faster, Y% less memory, etc.]
**Tradeoffs**: [Si applicable]
```

AUDIT COMPLET AVEC FOCUS SUR IMPACT RÉEL."""

    def _build_quality_prompt(self, code: str, language: str, context: str) -> str:
        """Construit le prompt pour analyse de qualité."""
        return f"""Analyse la QUALITÉ DU CODE selon les meilleurs standards de l'industrie.

LANGAGE: {language}

CONTEXTE:
{context if context else "Analyse de qualité générale"}

CODE:
```{language}
{code}
```

CRITÈRES D'ÉVALUATION:

### 1. SOLID Principles

**Single Responsibility**:
- Chaque classe/fonction a UNE seule responsabilité?
- Identifier violations et suggérer découpage

**Open/Closed**:
- Ouvert à l'extension, fermé à la modification?
- Identifier rigidité et suggérer abstractions

**Liskov Substitution**:
- Les sous-classes respectent le contrat?
- Identifier violations de contrat

**Interface Segregation**:
- Interfaces spécifiques plutôt que génériques?
- Identifier interfaces trop grosses

**Dependency Inversion**:
- Dépend d'abstractions, pas de concrétions?
- Identifier couplage fort

### 2. DRY (Don't Repeat Yourself)

- Code dupliqué (>3 lignes identiques)
  - Quantifier duplication
  - Suggérer extraction (function, class, module)
- Logic dupliquée (même intent, code différent)

### 3. KISS (Keep It Simple)

- Over-engineering détecté?
- Complexité cyclomatique > 10?
- Nested conditions > 3 niveaux?
- Solutions plus simples disponibles?

### 4. YAGNI (You Ain't Gonna Need It)

- Features "pour le futur" non utilisées?
- Abstraction prématurée?
- Généralité spéculative?

### 5. Naming & Readability

- Variables/functions/classes: Noms descriptifs?
- Typos, abréviations cryptiques?
- Magic numbers/strings?
- Consistent naming convention?

### 6. Function/Class Size

- Functions > 50 lignes? (devrait être <20)
- Classes > 500 lignes? (devrait être <300)
- Parameter lists > 3-4? (utiliser objects)

### 7. Error Handling

- Try/catch appropriés?
- Errors silencieusement ignorées?
- Error messages descriptifs?
- Proper error propagation?

### 8. Comments & Documentation

- Comments expliquent WHY, pas WHAT?
- Code self-documenting?
- Commented-out code (devrait être supprimé)?
- TODOs avec context?

### 9. Testability

- Code facilement testable?
- Dependencies injectables?
- Pure functions vs side effects?
- Mock-friendly?

POUR CHAQUE VIOLATION:

```markdown
### [Principle Violated]
**Severity**: MAJOR | MINOR
**Location**: lines X-Y
**Issue**: [Description]
**Why**: [Impact sur maintenabilité/lisibilité]
**Refactoring**:
\`\`\`{language}
// ❌ Before
[code actuel]

// ✅ After
[code refactoré]
\`\`\`
**Benefits**: [Amélioration apportée]
```

ANALYSE APPROFONDIE ET CONSTRUCTIVE."""

    def _build_architecture_prompt(self, code: str, language: str, context: str) -> str:
        """Construit le prompt pour analyse architecturale."""
        return f"""Analyse l'ARCHITECTURE et les DESIGN PATTERNS du code.

LANGAGE: {language}

CONTEXTE: {context}

CODE:
```{language}
{code}
```

ÉVALUATION:

### 1. Design Patterns Utilisés

Identifier les patterns implémentés:
- Singleton, Factory, Builder, Prototype
- Adapter, Bridge, Composite, Decorator
- Observer, Strategy, Command, State
- Repository, Service Layer, DTO
- Etc.

Pour chaque pattern:
- Est-il correctement implémenté?
- Est-il approprié au problème?
- Y a-t-il des violations?

### 2. Patterns Recommandés

Quels patterns DEVRAIENT être utilisés:
- Identifier opportunités d'amélioration
- Suggérer patterns pour résoudre problèmes actuels
- Justifier chaque recommandation

### 3. Anti-Patterns Détectés

- **God Object**: Classe qui sait/fait trop
- **Spaghetti Code**: Flux complexe impossible à suivre
- **Lava Flow**: Dead code qui reste
- **Golden Hammer**: Même solution partout
- **Cargo Cult**: Copier sans comprendre

### 4. Separation of Concerns

- Layers bien séparées? (UI, Business, Data)
- Mixing concerns detected?
- Proper encapsulation?

### 5. Dependency Management

- Dependencies clairement définies?
- Circular dependencies?
- Tight coupling?
- Dependency injection used?

FORMAT:

```markdown
## Architecture Analysis

### ✅ Patterns Bien Utilisés
1. **[Pattern Name]**
   - Location: [where]
   - Implementation: [good aspects]

### ⚠️ Patterns Mal Utilisés
1. **[Pattern Name]**
   - Location: [where]
   - Problem: [issue]
   - Fix: [how to fix properly]

### ❌ Anti-Patterns Détectés
1. **[Anti-Pattern Name]**
   - Location: [where]
   - Impact: [problème causé]
   - Refactoring:
   \`\`\`{language}
   // Refactored code
   \`\`\`

### 💡 Recommended Patterns
1. **[Pattern Name]**
   - Why: [justification]
   - Where: [où l'appliquer]
   - How:
   \`\`\`{language}
   // Implementation example
   \`\`\`
```

ANALYSE ARCHITECTURALE APPROFONDIE."""

    def _build_anti_patterns_prompt(self, code: str, language: str, context: str) -> str:
        """Construit le prompt pour détection d'anti-patterns."""
        return f"""Détecte TOUS les CODE SMELLS et ANTI-PATTERNS dans le code.

LANGAGE: {language}

CODE:
```{language}
{code}
```

CHERCHER SYSTÉMATIQUEMENT:

### Bloaters
- Long Method (>50 lines)
- Large Class (>500 lines)
- Primitive Obsession
- Long Parameter List (>3-4)
- Data Clumps

### OO Abusers
- Switch Statements (devrait être polymorphisme)
- Temporary Field
- Refused Bequest
- Alternative Classes with Different Interfaces

### Change Preventers
- Divergent Change
- Shotgun Surgery
- Parallel Inheritance Hierarchies

### Dispensables
- Comments (code non self-explanatory)
- Duplicate Code
- Lazy Class
- Dead Code
- Speculative Generality

### Couplers
- Feature Envy
- Inappropriate Intimacy
- Message Chains
- Middle Man

POUR CHAQUE SMELL:

```markdown
### [Smell Type]: [Name]
**Severity**: High | Medium | Low
**Location**: lines X-Y
**Code Smell**: [Description]
**Impact**: [Problème causé]
**Refactoring**:
\`\`\`{language}
// ❌ Current (smelly)
[code actuel]

// ✅ Refactored (clean)
[code amélioré]
\`\`\`
**Benefits**: [Amélioration]
```

DÉTECTION EXHAUSTIVE DE TOUS LES SMELLS."""

    # ==================== HELPER METHODS ====================

    def _detect_language(self, code: str) -> str:
        """Détecte le langage de programmation du code."""
        # Patterns simples pour détection
        if "def " in code and ("import " in code or ":" in code):
            return "python"
        if ("function " in code or "const " in code or "let " in code) and "{" in code:
            return "javascript"
        if (": string" in code or "interface " in code) and "{" in code:
            return "typescript"
        if "public class " in code or "private " in code:
            return "java"
        if "#include " in code or "int main(" in code:
            return "c++"
        if "<?php" in code:
            return "php"
        if "package main" in code and "func " in code:
            return "go"

        # Défaut
        return "unknown"

    def _calculate_basic_metrics(self, code: str) -> Dict[str, Any]:
        """Calcule des métriques basiques du code."""
        lines = code.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]
        comment_lines = [l for l in lines if l.strip().startswith(("//", "#", "/*", "*", "<!--"))]

        # Compter fonctions (approximatif)
        function_patterns = [
            r'\bdef\s+\w+',  # Python
            r'\bfunction\s+\w+',  # JS
            r'\b\w+\s*\([^)]*\)\s*{',  # C-style
        ]
        function_count = sum(len(re.findall(pattern, code)) for pattern in function_patterns)

        return {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "comment_lines": len(comment_lines),
            "blank_lines": len(lines) - len(non_empty_lines),
            "estimated_functions": function_count,
            "avg_line_length": sum(len(l) for l in lines) / len(lines) if lines else 0
        }

    def _parse_issues_from_review(self, review: str) -> List[Dict[str, Any]]:
        """Parse les issues depuis la review markdown."""
        issues = []

        # Pattern pour trouver les sections d'issues
        severity_map = {
            "🔴": "critical",
            "🟠": "major",
            "🟡": "minor",
            "🟢": "suggestion"
        }

        for emoji, severity in severity_map.items():
            # Trouver la section
            section_pattern = f"## {re.escape(emoji)}.*?(?=##|$)"
            sections = re.findall(section_pattern, review, re.DOTALL)

            for section in sections:
                # Extraire les issues individuelles
                issue_pattern = r"###\s+\d+\.\s+(.+?)(?=###|\n##|$)"
                for match in re.finditer(issue_pattern, section, re.DOTALL):
                    issue_text = match.group(1)
                    # Extraire titre
                    title_match = re.match(r'^(.+?)(?:\n|$)', issue_text)
                    title = title_match.group(1).strip() if title_match else "Unknown Issue"

                    # Extraire location
                    location_match = re.search(r'\*\*Location\*\*:\s*(.+)', issue_text)
                    location = location_match.group(1).strip() if location_match else "Unknown"

                    issues.append({
                        "title": title,
                        "severity": severity,
                        "location": location,
                        "full_text": issue_text.strip()
                    })

        return issues
