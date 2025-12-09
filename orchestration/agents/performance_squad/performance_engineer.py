"""
Performance Engineer Agent - Performance Squad

Cet agent est responsable de:
- Analyser les Core Web Vitals (LCP, FID, CLS, TTFB)
- Profiler le runtime JavaScript et identifier les bottlenecks
- Optimiser le rendering React (React DevTools Profiler)
- Détecter les memory leaks et optimiser la garbage collection
- Auditer les performances avec Lighthouse et WebPageTest
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import os

# Import BaseAgent from orchestration core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../core'))
from base_agent import BaseAgent, AgentConfig


class PerformanceEngineerAgent(BaseAgent):
    """
    Agent Performance Engineer pour l'analyse et l'optimisation des performances web.

    Spécialisations:
        - Core Web Vitals analysis
        - JavaScript runtime profiling
        - React rendering optimization
        - Performance budgets et monitoring
    """

    def __init__(self, config: AgentConfig):
        """
        Initialise l'agent Performance Engineer.

        Args:
            config: Configuration de l'agent incluant API key et modèle LLM
        """
        super().__init__(config)

        self.performance_thresholds = {
            "lcp": {"good": 2.5, "needs_improvement": 4.0},  # seconds
            "fid": {"good": 100, "needs_improvement": 300},  # milliseconds
            "cls": {"good": 0.1, "needs_improvement": 0.25},  # score
            "ttfb": {"good": 800, "needs_improvement": 1800},  # milliseconds
            "fcp": {"good": 1.8, "needs_improvement": 3.0},  # seconds
            "tti": {"good": 3.8, "needs_improvement": 7.3},  # seconds
        }

    def validate_input(self, input_data: Any) -> bool:
        """
        Valide les données d'entrée pour l'analyse de performance.

        Args:
            input_data: Dictionnaire contenant task_type et context

        Returns:
            True si les données sont valides

        Raises:
            ValueError: Si les données sont invalides ou incomplètes
        """
        if not isinstance(input_data, dict):
            raise ValueError("input_data doit être un dictionnaire")

        task_type = input_data.get("task_type")
        valid_task_types = [
            "core_web_vitals",
            "js_profiling",
            "react_optimization",
            "lighthouse_audit",
            "performance_budget",
            "bottleneck_analysis"
        ]

        if task_type not in valid_task_types:
            raise ValueError(
                f"task_type doit être l'un de: {', '.join(valid_task_types)}"
            )

        if "context" not in input_data:
            raise ValueError("Le champ 'context' est requis")

        return True

    def execute(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Exécute une tâche d'analyse de performance.

        Args:
            input_data: Dictionnaire avec les clés:
                - task_type: Type d'analyse ("core_web_vitals" | "js_profiling" | ...)
                - context: Données de performance ou code à analyser
                - url: URL du site (optionnel)
                - metrics: Métriques collectées (optionnel)
                - lighthouse_report: Rapport Lighthouse JSON (optionnel)
            **kwargs: Paramètres supplémentaires

        Returns:
            Dictionnaire avec l'analyse et les recommandations
        """
        task_type = input_data["task_type"]
        context = input_data["context"]
        url = input_data.get("url", "")
        metrics = input_data.get("metrics", {})
        lighthouse_report = input_data.get("lighthouse_report", {})

        self.logger.info(f"Exécution de l'analyse: {task_type}")

        # Construire le prompt selon le type de tâche
        if task_type == "core_web_vitals":
            prompt = self._build_core_web_vitals_prompt(context, url, metrics)
        elif task_type == "js_profiling":
            prompt = self._build_js_profiling_prompt(context)
        elif task_type == "react_optimization":
            prompt = self._build_react_optimization_prompt(context)
        elif task_type == "lighthouse_audit":
            prompt = self._build_lighthouse_audit_prompt(lighthouse_report, url)
        elif task_type == "performance_budget":
            prompt = self._build_performance_budget_prompt(context, url)
        elif task_type == "bottleneck_analysis":
            prompt = self._build_bottleneck_analysis_prompt(context, metrics)
        else:
            raise ValueError(f"Type de tâche non supporté: {task_type}")

        # System message pour guider l'agent
        system_message = """Tu es un Performance Engineer expert avec 10+ ans d'expérience en optimisation web.

Tes domaines d'expertise:
- Core Web Vitals (LCP, FID, CLS, TTFB, FCP, TTI)
- JavaScript performance profiling (V8, DevTools)
- React performance optimization (React DevTools Profiler, useMemo, useCallback)
- Lighthouse audits et WebPageTest analysis
- Performance budgets et monitoring (SpeedCurve, Calibre)
- Network optimization (HTTP/2, HTTP/3, compression, caching)
- Image optimization (lazy loading, WebP, AVIF, responsive images)
- Code splitting et lazy loading (Webpack, Vite, Rollup)
- Memory leaks detection et garbage collection optimization

Principes de performance:
- Measure first: toujours baser les optimisations sur des métriques réelles
- User-centric: optimiser pour l'expérience utilisateur perçue
- Progressive enhancement: garantir une expérience de base rapide
- Performance budgets: définir des limites strictes et les monitorer
- Continuous monitoring: surveiller les régressions en production

Format de sortie:
- Analyse détaillée avec métriques et seuils
- Recommandations priorisées par impact (P0/P1/P2)
- Code examples concrets et actionnables
- Métriques avant/après estimées
- Markdown structuré avec sections numérotées"""

        # Appeler le LLM
        response = self._call_llm(prompt, system_message=system_message)

        return {
            "task_type": task_type,
            "analysis": response["content"],
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_analyzed": bool(metrics),
            "llm_usage": response["usage"]
        }

    def format_output(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate la sortie de l'analyse de performance.

        Args:
            raw_output: Sortie brute de l'exécution

        Returns:
            Dictionnaire formaté avec analyse et recommandations
        """
        return {
            "performance_analysis": {
                "task_type": raw_output["task_type"],
                "analysis": raw_output["analysis"],
                "url": raw_output["url"],
                "timestamp": raw_output["timestamp"]
            },
            "metadata": {
                "metrics_included": raw_output["metrics_analyzed"],
                "llm_model": raw_output["llm_usage"].get("model"),
                "tokens_used": raw_output["llm_usage"].get("total_tokens", 0)
            }
        }

    def _build_core_web_vitals_prompt(
        self,
        context: str,
        url: str,
        metrics: Dict[str, float]
    ) -> str:
        """Construit le prompt pour analyser les Core Web Vitals."""
        metrics_section = ""
        if metrics:
            metrics_section = "\n\nMÉTRIQUES MESURÉES:\n"
            for metric, value in metrics.items():
                threshold = self.performance_thresholds.get(metric.lower(), {})
                status = "❌ Poor"
                if threshold:
                    if value <= threshold["good"]:
                        status = "✅ Good"
                    elif value <= threshold["needs_improvement"]:
                        status = "⚠️ Needs Improvement"
                metrics_section += f"- {metric.upper()}: {value} {status}\n"

        return f"""Analyse les Core Web Vitals suivants:

URL: {url if url else "Non spécifiée"}

CONTEXTE:
{context}
{metrics_section}

Fournis une analyse détaillée incluant:

1. **État actuel des Core Web Vitals**
   - LCP (Largest Contentful Paint): Évalue le chargement
   - FID (First Input Delay): Évalue l'interactivité
   - CLS (Cumulative Layout Shift): Évalue la stabilité visuelle
   - TTFB (Time to First Byte): Évalue la réponse serveur
   - FCP (First Contentful Paint): Première peinture
   - TTI (Time to Interactive): Temps jusqu'à interactivité

2. **Diagnostic des problèmes**
   - Identifier les métriques hors des seuils
   - Expliquer les causes racines (render-blocking, large images, etc.)
   - Quantifier l'impact sur l'expérience utilisateur

3. **Recommandations priorisées**
   Pour chaque métrique problématique:
   - **P0 (Critical)**: Impact élevé, effort faible
   - **P1 (Important)**: Impact élevé, effort moyen
   - **P2 (Nice-to-have)**: Améliorations incrémentales

4. **Plan d'action**
   - Quick wins (< 1 jour)
   - Medium-term improvements (1-5 jours)
   - Long-term optimizations (> 5 jours)

5. **Estimation d'impact**
   - Amélioration estimée par métrique
   - Impact sur le score Lighthouse global
   - Impact business estimé (conversion, bounce rate)

Seuils de référence:
- Good: LCP < 2.5s, FID < 100ms, CLS < 0.1
- Needs Improvement: LCP < 4.0s, FID < 300ms, CLS < 0.25
- Poor: Au-delà des seuils ci-dessus"""

    def _build_js_profiling_prompt(self, context: str) -> str:
        """Construit le prompt pour le profiling JavaScript."""
        return f"""Analyse le profiling JavaScript suivant et identifie les bottlenecks:

CODE/PROFILING DATA:
{context}

Fournis une analyse détaillée:

1. **Détection des bottlenecks**
   - Long tasks (> 50ms) qui bloquent le main thread
   - Fonctions appelées trop fréquemment
   - Allocations mémoire excessives
   - Event listeners inefficaces

2. **Analyse du call stack**
   - Identifier les fonctions les plus coûteuses
   - Mesurer le temps d'exécution relatif
   - Détecter les récursions inefficaces

3. **Optimisations recommandées**
   - Debouncing/throttling pour les events
   - Lazy loading pour le code non-critique
   - Web Workers pour les tâches lourdes
   - Optimisation des algorithmes (complexité O(n))

4. **Code examples**
   Avant/après pour chaque optimisation avec:
   - Code original problématique
   - Code optimisé
   - Gain de performance estimé
   - Trade-offs éventuels

5. **Outils de monitoring**
   - Chrome DevTools Performance tab
   - React DevTools Profiler
   - Performance markers API
   - User Timing API pour mesurer en production"""

    def _build_react_optimization_prompt(self, context: str) -> str:
        """Construit le prompt pour l'optimisation React."""
        return f"""Optimise les performances de ce code React:

CODE REACT:
{context}

Analyse les aspects suivants:

1. **Rendering optimization**
   - Identifier les re-renders inutiles
   - Utilisation de React.memo, useMemo, useCallback
   - Optimisation des listes (key prop, virtualization)
   - Code splitting avec React.lazy et Suspense

2. **State management**
   - Éviter les states trop larges
   - Optimiser le context API (split contexts)
   - useReducer pour la logique complexe
   - Éviter les inline objects/functions dans JSX

3. **Component architecture**
   - Composition vs inheritance
   - Smart vs Presentational components
   - Lazy loading des components lourds
   - Windowing pour les longues listes (react-window)

4. **Performance patterns**
   - Debouncing des inputs
   - Optimistic UI updates
   - Suspense pour le data fetching
   - Preloading des routes critiques

5. **Code refactoré**
   Fournis le code optimisé avec:
   - Annotations expliquant chaque optimisation
   - Mesures avant/après (re-renders, bundle size)
   - Trade-offs et edge cases à considérer

6. **React DevTools Profiler**
   - Comment mesurer l'impact
   - Métriques à surveiller (commit duration, render count)
   - Flame graph analysis"""

    def _build_lighthouse_audit_prompt(
        self,
        lighthouse_report: Dict[str, Any],
        url: str
    ) -> str:
        """Construit le prompt pour analyser un rapport Lighthouse."""
        report_summary = "Non fourni - analyse générique"
        if lighthouse_report:
            report_summary = f"""
Scores:
- Performance: {lighthouse_report.get('performance', 'N/A')}
- Accessibility: {lighthouse_report.get('accessibility', 'N/A')}
- Best Practices: {lighthouse_report.get('best-practices', 'N/A')}
- SEO: {lighthouse_report.get('seo', 'N/A')}

Opportunities: {len(lighthouse_report.get('opportunities', []))} identifiées
Diagnostics: {len(lighthouse_report.get('diagnostics', []))} identifiés"""

        return f"""Analyse ce rapport Lighthouse et fournis un plan d'action:

URL: {url if url else "Non spécifiée"}

RAPPORT LIGHTHOUSE:
{report_summary}

Fournis:

1. **Résumé exécutif**
   - État global de la performance
   - Points critiques à adresser immédiatement
   - Score cible et timeline

2. **Analyse par catégorie**

   **Performance (0-100)**
   - Opportunities principales (render-blocking, unused code)
   - Diagnostics critiques
   - Métriques hors seuils

   **Accessibility (0-100)**
   - Violations WCAG détectées
   - Impact sur les utilisateurs
   - Fixes rapides vs long-terme

   **Best Practices (0-100)**
   - Vulnérabilités de sécurité
   - APIs dépréciées
   - Console errors

   **SEO (0-100)**
   - Problèmes de crawlabilité
   - Meta tags manquants
   - Mobile-friendliness

3. **Plan d'action priorisé**
   Pour chaque catégorie, liste les actions par priorité:
   - P0: Bloquant, doit être fixé avant prod
   - P1: Important, impacte significativement le score
   - P2: Nice-to-have, amélioration incrémentale

4. **Estimated impact**
   - Gain de score par action
   - Effort estimé (heures/jours)
   - ROI (impact/effort)

5. **Monitoring post-fix**
   - Lighthouse CI pour les checks automatiques
   - Métriques à surveiller en production
   - Seuils d'alerte à configurer"""

    def _build_performance_budget_prompt(self, context: str, url: str) -> str:
        """Construit le prompt pour définir un performance budget."""
        return f"""Définis un performance budget pour cette application:

URL: {url if url else "Non spécifiée"}

CONTEXTE:
{context}

Crée un performance budget complet:

1. **Budget par catégorie**

   **JavaScript**
   - Total bundle size: < 200KB (gzipped)
   - Main bundle: < 80KB
   - Vendor bundle: < 120KB
   - Per-route chunks: < 50KB

   **CSS**
   - Total CSS: < 50KB (gzipped)
   - Critical CSS inline: < 14KB
   - Font files: < 100KB total

   **Images**
   - Total images (above-the-fold): < 200KB
   - Hero image: < 50KB (WebP/AVIF)
   - Thumbnails: < 10KB each

   **Fonts**
   - Web fonts: max 2 families, 4 weights
   - Font files: < 100KB total
   - FOUT/FOIT strategy

2. **Timing budgets**
   - TTFB: < 600ms
   - FCP: < 1.5s
   - LCP: < 2.0s
   - TTI: < 3.0s
   - Total page load: < 5s (3G)

3. **Request budgets**
   - Total requests: < 50
   - Critical path requests: < 10
   - Third-party requests: < 5

4. **Implementation strategy**
   - Webpack Bundle Analyzer configuration
   - Lighthouse CI thresholds
   - Performance budgets in package.json
   - CI/CD gates (fail build if budget exceeded)

5. **Monitoring & alerting**
   - Real User Monitoring (RUM) setup
   - SpeedCurve/Calibre budgets
   - Slack/email alerts on violations
   - Weekly performance reports

6. **Tools & automation**
```json
// package.json performance budgets
{{
  "performance": {{
    "maxSize": "200KB",
    "maxRequests": 50,
    "budgets": [
      {{"resourceType": "script", "budget": 200}},
      {{"resourceType": "style", "budget": 50}},
      {{"resourceType": "image", "budget": 200}}
    ]
  }}
}}
```"""

    def _build_bottleneck_analysis_prompt(
        self,
        context: str,
        metrics: Dict[str, Any]
    ) -> str:
        """Construit le prompt pour analyser les bottlenecks."""
        metrics_info = ""
        if metrics:
            metrics_info = f"\n\nMÉTRIQUES DISPONIBLES:\n{metrics}\n"

        return f"""Identifie et résous les bottlenecks de performance:

CONTEXTE:
{context}
{metrics_info}

Analyse systématique:

1. **Identification des bottlenecks**

   **Network layer**
   - Slow TTFB (serveur lent, cold start)
   - Trop de requests (manque de bundling)
   - Large payloads (pas de compression)
   - Blocking resources (CSS/JS non-defer)

   **Rendering layer**
   - Render-blocking resources
   - Large DOM size (> 1500 nodes)
   - CSS/JS parsing time élevé
   - Layout thrashing (forced reflow)

   **JavaScript layer**
   - Long tasks (> 50ms)
   - Main thread busy
   - Heavy computations
   - Memory leaks

   **Resource layer**
   - Unoptimized images (large, wrong format)
   - Missing lazy loading
   - Fonts loading strategy
   - Third-party scripts

2. **Diagnostic approfondi**
   Pour chaque bottleneck:
   - Root cause analysis
   - Impact quantifié (ms saved)
   - Outils de mesure (DevTools, Lighthouse)

3. **Solutions priorisées**
   - Quick wins (< 1h): low-hanging fruits
   - Medium-term (1-3j): refactoring nécessaire
   - Long-term (> 3j): architecture changes

4. **Implementation roadmap**
   Semaine 1: [Quick wins]
   Semaine 2-3: [Medium improvements]
   Semaine 4+: [Long-term optimizations]

5. **Success metrics**
   - Métriques cibles après optimisation
   - Tests de régression à mettre en place
   - Monitoring continu (alertes)"""

    # Helper methods pour usage simplifié
    def analyze_core_web_vitals(
        self,
        url: str,
        metrics: Dict[str, float],
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyse les Core Web Vitals d'une page.

        Args:
            url: URL de la page analysée
            metrics: Métriques mesurées (lcp, fid, cls, ttfb, etc.)
            context: Contexte additionnel sur la page

        Returns:
            Analyse complète et recommandations
        """
        return self.run({
            "task_type": "core_web_vitals",
            "url": url,
            "metrics": metrics,
            "context": context or f"Analyse des Core Web Vitals pour {url}"
        })

    def profile_javascript(self, code_or_profiling_data: str) -> Dict[str, Any]:
        """
        Profile du code JavaScript et identifie les bottlenecks.

        Args:
            code_or_profiling_data: Code source ou données de profiling

        Returns:
            Analyse des performances et optimisations recommandées
        """
        return self.run({
            "task_type": "js_profiling",
            "context": code_or_profiling_data
        })

    def optimize_react(self, react_code: str) -> Dict[str, Any]:
        """
        Optimise un composant React.

        Args:
            react_code: Code source React à optimiser

        Returns:
            Code optimisé et explications
        """
        return self.run({
            "task_type": "react_optimization",
            "context": react_code
        })

    def audit_lighthouse(
        self,
        lighthouse_report: Dict[str, Any],
        url: str
    ) -> Dict[str, Any]:
        """
        Analyse un rapport Lighthouse.

        Args:
            lighthouse_report: Rapport Lighthouse au format JSON
            url: URL auditée

        Returns:
            Plan d'action détaillé
        """
        return self.run({
            "task_type": "lighthouse_audit",
            "lighthouse_report": lighthouse_report,
            "url": url,
            "context": "Analyse du rapport Lighthouse"
        })
