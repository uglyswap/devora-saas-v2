"""
Bundle Optimizer Agent - Performance Squad

Cet agent est responsable de:
- Implémenter le code splitting et lazy loading
- Configurer le tree shaking pour éliminer le dead code
- Optimiser les assets (images, fonts, SVG)
- Réduire le bundle size avec compression et minification
- Analyser et optimiser les dépendances npm
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import os

# Import BaseAgent from orchestration core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../core'))
from base_agent import BaseAgent, AgentConfig


class BundleOptimizerAgent(BaseAgent):
    """
    Agent Bundle Optimizer pour la réduction et l'optimisation des bundles.

    Spécialisations:
        - Code splitting stratégique
        - Tree shaking et dead code elimination
        - Asset optimization (images, fonts, SVG)
        - Dependency analysis et alternatives légères
    """

    def __init__(self, config: AgentConfig):
        """
        Initialise l'agent Bundle Optimizer.

        Args:
            config: Configuration de l'agent incluant API key et modèle LLM
        """
        super().__init__(config)

        self.bundle_size_targets = {
            "main_bundle": 100 * 1024,      # 100KB gzipped
            "vendor_bundle": 150 * 1024,    # 150KB gzipped
            "route_chunk": 50 * 1024,       # 50KB gzipped per route
            "total_js": 250 * 1024,         # 250KB gzipped total
            "total_css": 50 * 1024,         # 50KB gzipped
            "critical_css": 14 * 1024,      # 14KB inline
        }

        self.image_formats = ["WebP", "AVIF", "JPEG XL", "JPEG", "PNG", "SVG"]
        self.compression_algorithms = ["Brotli", "Gzip", "Zstd"]

    def validate_input(self, input_data: Any) -> bool:
        """
        Valide les données d'entrée pour l'optimisation de bundle.

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
            "code_splitting",
            "tree_shaking",
            "asset_optimization",
            "dependency_analysis",
            "compression_config",
            "bundle_analysis"
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
        Exécute une tâche d'optimisation de bundle.

        Args:
            input_data: Dictionnaire avec les clés:
                - task_type: Type d'optimisation
                - context: Code ou configuration à optimiser
                - bundle_stats: Statistiques du bundle actuel (optionnel)
                - bundler: "webpack" | "vite" | "rollup" | "esbuild" (optionnel)
                - framework: "react" | "vue" | "svelte" | "angular" (optionnel)
            **kwargs: Paramètres supplémentaires

        Returns:
            Dictionnaire avec optimisations et configurations
        """
        task_type = input_data["task_type"]
        context = input_data["context"]
        bundle_stats = input_data.get("bundle_stats", {})
        bundler = input_data.get("bundler", "webpack")
        framework = input_data.get("framework", "react")

        self.logger.info(f"Exécution de l'optimisation: {task_type}")

        # Construire le prompt selon le type de tâche
        if task_type == "code_splitting":
            prompt = self._build_code_splitting_prompt(context, bundler, framework)
        elif task_type == "tree_shaking":
            prompt = self._build_tree_shaking_prompt(context, bundler)
        elif task_type == "asset_optimization":
            prompt = self._build_asset_optimization_prompt(context)
        elif task_type == "dependency_analysis":
            prompt = self._build_dependency_analysis_prompt(context, bundle_stats)
        elif task_type == "compression_config":
            prompt = self._build_compression_config_prompt(bundler)
        elif task_type == "bundle_analysis":
            prompt = self._build_bundle_analysis_prompt(bundle_stats, bundler)
        else:
            raise ValueError(f"Type de tâche non supporté: {task_type}")

        # System message pour guider l'agent
        system_message = """Tu es un Bundle Optimizer expert spécialisé en optimisation de bundles web.

Tes domaines d'expertise:
- Code splitting stratégique (route-based, component-based, vendor splitting)
- Tree shaking et dead code elimination (sideEffects, ESM, CommonJS)
- Asset optimization (images, fonts, SVG, videos)
- Webpack, Vite, Rollup, esbuild, Parcel configuration
- Compression (Brotli, Gzip, Zstd)
- Lazy loading et dynamic imports
- Dependency analysis (bundle-phobia, bundlephobia.com)
- CDN strategies et module preloading
- Critical CSS extraction et inlining

Outils maîtrisés:
- Webpack Bundle Analyzer
- source-map-explorer
- Vite bundle visualizer
- webpack-bundle-buddy
- Lighthouse bundle analysis
- ImageOptim, Squoosh, Sharp
- SVGO pour SVG optimization

Principes d'optimisation:
- Target: < 250KB JS total (gzipped) pour le premier chargement
- Critical path: minimiser les blocking resources
- Progressive loading: charger le strict nécessaire d'abord
- Cache optimization: vendor bundles stables, app bundles dynamiques
- Format moderne: ESM, WebP/AVIF, Brotli

Format de sortie:
- Configuration complète et prête à l'emploi
- Code examples avec before/after
- Commandes npm/scripts à exécuter
- Impact estimé (KB saved, % reduction)
- Markdown structuré avec code blocks syntaxés"""

        # Appeler le LLM
        response = self._call_llm(prompt, system_message=system_message)

        return {
            "task_type": task_type,
            "optimization": response["content"],
            "bundler": bundler,
            "framework": framework,
            "timestamp": datetime.utcnow().isoformat(),
            "bundle_stats_provided": bool(bundle_stats),
            "llm_usage": response["usage"]
        }

    def format_output(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate la sortie de l'optimisation de bundle.

        Args:
            raw_output: Sortie brute de l'exécution

        Returns:
            Dictionnaire formaté avec optimisations
        """
        return {
            "bundle_optimization": {
                "task_type": raw_output["task_type"],
                "recommendations": raw_output["optimization"],
                "bundler": raw_output["bundler"],
                "framework": raw_output["framework"],
                "timestamp": raw_output["timestamp"]
            },
            "metadata": {
                "bundle_stats_analyzed": raw_output["bundle_stats_provided"],
                "llm_model": raw_output["llm_usage"].get("model"),
                "tokens_used": raw_output["llm_usage"].get("total_tokens", 0)
            }
        }

    def _build_code_splitting_prompt(
        self,
        context: str,
        bundler: str,
        framework: str
    ) -> str:
        """Construit le prompt pour le code splitting."""
        return f"""Implémente une stratégie de code splitting optimale pour cette application {framework}:

BUNDLER: {bundler}
FRAMEWORK: {framework}

CONTEXTE/CODE:
{context}

Fournis une stratégie complète de code splitting:

1. **Route-based splitting**
   - Configuration pour lazy load les routes
   - React.lazy + Suspense (React)
   - defineAsyncComponent (Vue)
   - Gestion des loading states et error boundaries

   Exemple React:
   ```jsx
   const Dashboard = lazy(() => import('./pages/Dashboard'));

   <Suspense fallback={{<LoadingSpinner />}}>
     <Routes>
       <Route path="/dashboard" element={{<Dashboard />}} />
     </Routes>
   </Suspense>
   ```

2. **Component-based splitting**
   - Identifier les composants lourds (charts, editors, maps)
   - Lazy loading conditionnel (modals, tabs)
   - Intersection Observer pour le lazy loading

3. **Vendor splitting**
   - Séparer React/Vue du code app
   - Common chunks configuration
   - Long-term caching strategy

   Webpack config:
   ```js
   optimization: {{
     splitChunks: {{
       chunks: 'all',
       cacheGroups: {{
         vendor: {{
           test: /[\\/]node_modules[\\/]/,
           name: 'vendor',
           priority: 10
         }},
         common: {{
           minChunks: 2,
           priority: 5,
           reuseExistingChunk: true
         }}
       }}
     }}
   }}
   ```

4. **Dynamic imports**
   - Magic comments pour chunk naming
   - Preload/prefetch strategies
   - webpackChunkName, webpackPrefetch

5. **Configuration {bundler}**
   - Configuration complète pour {bundler}
   - Build scripts package.json
   - Analyse avec bundle visualizer

6. **Mesures d'impact**
   - Taille avant/après par chunk
   - Initial load time estimation
   - Cache hit rate optimization

Fournis du code prêt à l'emploi avec instructions step-by-step."""

    def _build_tree_shaking_prompt(self, context: str, bundler: str) -> str:
        """Construit le prompt pour le tree shaking."""
        return f"""Configure le tree shaking optimal pour éliminer le dead code:

BUNDLER: {bundler}

PACKAGE.JSON / CODE:
{context}

Optimise le tree shaking:

1. **Package.json configuration**
   ```json
   {{
     "sideEffects": false,
     // ou
     "sideEffects": [
       "*.css",
       "*.scss",
       "./src/polyfills.js"
     ]
   }}
   ```

2. **Import optimization**
   ❌ Mauvais:
   ```js
   import _ from 'lodash';  // Import tout lodash
   import {{ Button }} from '@mui/material';  // Import tout MUI
   ```

   ✅ Bon:
   ```js
   import debounce from 'lodash/debounce';  // Import 1 fonction
   import Button from '@mui/material/Button';  // Import 1 composant
   ```

3. **ESM vs CommonJS**
   - Forcer ESM dans les dépendances
   - Vérifier les packages qui ne supportent pas le tree shaking
   - Alternatives légères (lodash-es vs lodash, date-fns vs moment)

4. **Bundler configuration**

   **Webpack:**
   ```js
   module.exports = {{
     mode: 'production',
     optimization: {{
       usedExports: true,
       minimize: true,
       sideEffects: true
     }}
   }};
   ```

   **Vite:**
   ```js
   export default {{
     build: {{
       rollupOptions: {{
         output: {{
           manualChunks: (id) => {{
             if (id.includes('node_modules')) {{
               return 'vendor';
             }}
           }}
         }}
       }}
     }}
   }};
   ```

5. **Dead code detection**
   - ESLint rules pour imports inutilisés
   - Outils: depcheck, npm-check, unimported
   - CI checks pour prévenir les regressions

6. **Library alternatives**
   Suggère des alternatives légères:
   - moment.js (232KB) → date-fns (12KB) ou day.js (2KB)
   - lodash (71KB) → lodash-es (tree-shakable)
   - axios (13KB) → ky (4KB) ou native fetch

7. **Impact measurement**
   - Analyse before/after avec bundle analyzer
   - KB saved par optimisation
   - Liste des dead code détectés"""

    def _build_asset_optimization_prompt(self, context: str) -> str:
        """Construit le prompt pour l'optimisation des assets."""
        return f"""Optimise les assets (images, fonts, SVG) de cette application:

ASSETS / CONFIGURATION:
{context}

Plan d'optimisation complet:

1. **Image optimization**

   **Format selection:**
   - Hero images: AVIF (fallback WebP, fallback JPEG)
   - Photos: WebP (fallback JPEG)
   - Illustrations: SVG (ou PNG si complexe)
   - Icons: SVG sprite ou icon font

   **Responsive images:**
   ```html
   <picture>
     <source srcset="hero.avif" type="image/avif">
     <source srcset="hero.webp" type="image/webp">
     <img src="hero.jpg" alt="Hero" loading="lazy"
          srcset="hero-320.jpg 320w,
                  hero-640.jpg 640w,
                  hero-1024.jpg 1024w"
          sizes="(max-width: 640px) 100vw, 50vw">
   </picture>
   ```

   **Lazy loading:**
   - Native `loading="lazy"` attribute
   - Intersection Observer pour custom loading
   - Blur-up technique (LQIP - Low Quality Image Placeholder)

2. **Font optimization**

   **Font loading strategy:**
   ```css
   @font-face {{
     font-family: 'Inter';
     src: url('/fonts/inter-var.woff2') format('woff2');
     font-weight: 100 900;
     font-display: swap; /* ou optional */
   }}
   ```

   **Subsetting:**
   - Limiter aux glyphes utilisés (latin uniquement)
   - Variable fonts pour réduire les variants
   - Outils: glyphhanger, subfont

   **Preloading:**
   ```html
   <link rel="preload" href="/fonts/inter-var.woff2"
         as="font" type="font/woff2" crossorigin>
   ```

3. **SVG optimization**

   **SVGO configuration:**
   ```js
   // svgo.config.js
   module.exports = {{
     plugins: [
       'removeDoctype',
       'removeComments',
       'removeMetadata',
       'removeXMLProcInst',
       'removeEditorsNSData',
       'cleanupIDs',
       'minifyStyles',
       'convertStyleToAttrs'
     ]
   }};
   ```

   **SVG sprites:**
   ```html
   <!-- sprite.svg -->
   <svg style="display: none">
     <symbol id="icon-home" viewBox="0 0 24 24">...</symbol>
     <symbol id="icon-user" viewBox="0 0 24 24">...</symbol>
   </svg>

   <!-- Usage -->
   <svg><use href="#icon-home" /></svg>
   ```

4. **Build pipeline**

   **Image optimization tools:**
   - imagemin + imagemin-webp + imagemin-avif
   - sharp pour le resizing dynamique
   - Squoosh CLI pour batch processing

   **Webpack config:**
   ```js
   module.exports = {{
     module: {{
       rules: [
         {{
           test: /\\.(png|jpg|jpeg)$/,
           type: 'asset/resource',
           use: [
             {{
               loader: 'image-webpack-loader',
               options: {{
                 mozjpeg: {{ progressive: true, quality: 80 }},
                 optipng: {{ enabled: false }},
                 pngquant: {{ quality: [0.8, 0.9], speed: 4 }},
                 webp: {{ quality: 85 }}
               }}
             }}
           ]
         }}
       ]
     }}
   }};
   ```

5. **CDN & caching**
   - CloudFront / Cloudflare Images
   - Automatic format conversion (AVIF/WebP)
   - Responsive image variants
   - Cache headers (1 year pour assets avec hash)

6. **Metrics & targets**
   - Images above-the-fold: < 200KB total
   - Hero image: < 50KB (WebP/AVIF)
   - Fonts: < 100KB total (WOFF2)
   - SVG icons: < 10KB (sprite)
   - Total assets budget: < 500KB initial load"""

    def _build_dependency_analysis_prompt(
        self,
        context: str,
        bundle_stats: Dict[str, Any]
    ) -> str:
        """Construit le prompt pour l'analyse des dépendances."""
        stats_info = ""
        if bundle_stats:
            stats_info = f"\n\nBUNDLE STATS:\n{bundle_stats}\n"

        return f"""Analyse les dépendances npm et suggère des optimisations:

PACKAGE.JSON / DEPENDENCIES:
{context}
{stats_info}

Analyse approfondie:

1. **Dependency audit**
   - Identifier les packages les plus lourds
   - Vérifier les doublons (multiple versions)
   - Détecter les dépendances inutilisées

   Outils:
   ```bash
   npx bundle-phobia [package-name]  # Taille du package
   npx depcheck                       # Dépendances inutilisées
   npm ls [package]                   # Arbre de dépendances
   npm dedupe                         # Dédupliquer les versions
   ```

2. **Heavy dependencies alternatives**

   Analyse chaque dépendance et suggère des alternatives:

   | Package | Taille | Alternative | Taille Alt | Gain |
   |---------|--------|-------------|------------|------|
   | moment | 232KB | date-fns | 12KB | -220KB |
   | lodash | 71KB | lodash-es | tree-shakable | ~50KB |
   | axios | 13KB | ky / fetch | 4KB / 0KB | -9KB |
   | chart.js | 230KB | recharts | 180KB | -50KB |

3. **Peer dependencies conflicts**
   - Identifier les conflits de versions
   - Résolutions dans package.json (npm/yarn)
   - Migration path si breaking changes

4. **Tree-shakable alternatives**
   - Packages qui supportent ESM
   - Imports granulaires possibles
   - Side-effects free packages

5. **CDN externalization**
   Externaliser les libs stables:
   ```js
   // webpack.config.js
   externals: {{
     'react': 'React',
     'react-dom': 'ReactDOM'
   }}
   ```

   ```html
   <!-- index.html -->
   <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
   ```

6. **Code replacement strategies**
   Pour chaque dépendance à remplacer:
   - Impact assessment (breaking changes)
   - Migration guide step-by-step
   - Codemods si disponibles
   - Tests de régression

7. **Bundle size targets**
   - node_modules total: évaluer si raisonnable
   - Dependencies dans le bundle final
   - Stratégie de lazy loading pour les grosses libs

8. **Action plan**
   Priorisation:
   - P0: Quick wins (< 1h, > 50KB saved)
   - P1: Medium effort (1-3h, > 20KB saved)
   - P2: Refactoring (> 3h, architectural)"""

    def _build_compression_config_prompt(self, bundler: str) -> str:
        """Construit le prompt pour la configuration de compression."""
        return f"""Configure la compression optimale pour {bundler}:

Fournis une configuration complète:

1. **Brotli compression** (meilleure compression)

   **Webpack:**
   ```js
   const CompressionPlugin = require('compression-webpack-plugin');
   const zlib = require('zlib');

   module.exports = {{
     plugins: [
       new CompressionPlugin({{
         filename: '[path][base].br',
         algorithm: 'brotliCompress',
         test: /\\.(js|css|html|svg)$/,
         compressionOptions: {{
           params: {{
             [zlib.constants.BROTLI_PARAM_QUALITY]: 11
           }}
         }},
         threshold: 10240,  // 10KB minimum
         minRatio: 0.8,
         deleteOriginalAssets: false
       }})
     ]
   }};
   ```

   **Vite:**
   ```js
   import viteCompression from 'vite-plugin-compression';

   export default {{
     plugins: [
       viteCompression({{
         algorithm: 'brotliCompress',
         ext: '.br',
         threshold: 10240
       }})
     ]
   }};
   ```

2. **Gzip fallback** (support navigateurs anciens)

   ```js
   new CompressionPlugin({{
     filename: '[path][base].gz',
     algorithm: 'gzip',
     test: /\\.(js|css|html|svg)$/,
     threshold: 10240,
     minRatio: 0.8
   }})
   ```

3. **Server configuration**

   **Nginx:**
   ```nginx
   server {{
     gzip on;
     gzip_vary on;
     gzip_types text/plain text/css application/json application/javascript text/xml;

     # Brotli (module ngx_brotli requis)
     brotli on;
     brotli_types text/plain text/css application/json application/javascript text/xml;
     brotli_comp_level 6;

     location ~* \\.br$ {{
       add_header Content-Encoding br;
       add_header Vary Accept-Encoding;
     }}
   }}
   ```

   **Express.js:**
   ```js
   const compression = require('compression');
   const express = require('express');
   const app = express();

   app.use(compression({{
     level: 6,
     threshold: 10 * 1024,  // 10KB
     filter: (req, res) => {{
       if (req.headers['x-no-compression']) {{
         return false;
       }}
       return compression.filter(req, res);
     }}
   }}));
   ```

   **Next.js:**
   ```js
   // next.config.js
   module.exports = {{
     compress: true,  // Gzip par défaut

     async headers() {{
       return [
         {{
           source: '/:path*\\.br',
           headers: [
             {{ key: 'Content-Encoding', value: 'br' }},
             {{ key: 'Content-Type', value: 'application/javascript' }}
           ]
         }}
       ];
     }}
   }};
   ```

4. **Build scripts**
   ```json
   {{
     "scripts": {{
       "build": "{bundler} build",
       "build:compress": "{bundler} build && npm run compress",
       "compress": "node scripts/compress.js",
       "analyze": "{bundler}-bundle-analyzer build/stats.json"
     }}
   }}
   ```

5. **Compression ratios attendus**
   - JavaScript: 70-80% reduction (Brotli 11)
   - CSS: 75-85% reduction
   - HTML: 60-70% reduction
   - JSON: 80-90% reduction

6. **Vérification**
   ```bash
   # Tester la compression
   curl -H "Accept-Encoding: br" -I https://example.com/main.js

   # Comparer les tailles
   du -h build/main.js
   du -h build/main.js.br
   du -h build/main.js.gz
   ```"""

    def _build_bundle_analysis_prompt(
        self,
        bundle_stats: Dict[str, Any],
        bundler: str
    ) -> str:
        """Construit le prompt pour l'analyse de bundle."""
        return f"""Analyse ce bundle et fournis des recommandations d'optimisation:

BUNDLER: {bundler}
BUNDLE STATS: {bundle_stats if bundle_stats else "Non fournis - analyse générique"}

Analyse complète:

1. **Bundle composition**
   - Identifier les chunks les plus lourds
   - Ratio app code vs vendor code
   - Duplicate packages (même lib, versions différentes)
   - Unused code potentiel

2. **Optimization opportunities**

   **Code splitting:**
   - Routes qui devraient être split
   - Composants lourds à lazy load
   - Vendor chunks à optimiser

   **Tree shaking:**
   - Packages qui ne sont pas tree-shakable
   - Imports non optimaux (import * from)
   - Dead code à éliminer

   **Dependencies:**
   - Top 10 packages les plus lourds
   - Alternatives plus légères
   - Packages inutilisés à supprimer

3. **Performance impact**
   - Download time (3G/4G/WiFi)
   - Parse + compile time estimation
   - Impact sur FCP, TTI, LCP

4. **Actionable recommendations**
   Priorisées par ROI:
   - P0: > 50KB saved, < 1h effort
   - P1: > 20KB saved, < 3h effort
   - P2: > 10KB saved, any effort

5. **Implementation guide**
   Pour chaque recommandation:
   - Step-by-step instructions
   - Code examples
   - Expected impact (KB saved)
   - Verification method

6. **Bundle analyzer setup**
   ```bash
   # Webpack
   npm install --save-dev webpack-bundle-analyzer
   npx webpack-bundle-analyzer build/stats.json

   # Vite
   npm install --save-dev rollup-plugin-visualizer
   npm run build -- --mode analyze

   # Next.js
   npm install --save-dev @next/bundle-analyzer
   ```

7. **Targets & budgets**
   Définir des budgets par route:
   ```json
   {{
     "/": {{ "initial": "150KB", "total": "300KB" }},
     "/dashboard": {{ "initial": "200KB", "total": "500KB" }},
     "/admin": {{ "initial": "250KB", "total": "600KB" }}
   }}
   ```"""

    # Helper methods pour usage simplifié
    def optimize_code_splitting(
        self,
        code: str,
        bundler: str = "webpack",
        framework: str = "react"
    ) -> Dict[str, Any]:
        """
        Génère une stratégie de code splitting.

        Args:
            code: Code source ou routing configuration
            bundler: Bundler utilisé
            framework: Framework utilisé

        Returns:
            Stratégie et configuration de code splitting
        """
        return self.run({
            "task_type": "code_splitting",
            "context": code,
            "bundler": bundler,
            "framework": framework
        })

    def configure_tree_shaking(
        self,
        package_json: str,
        bundler: str = "webpack"
    ) -> Dict[str, Any]:
        """
        Configure le tree shaking optimal.

        Args:
            package_json: Contenu du package.json
            bundler: Bundler utilisé

        Returns:
            Configuration de tree shaking
        """
        return self.run({
            "task_type": "tree_shaking",
            "context": package_json,
            "bundler": bundler
        })

    def optimize_assets(self, assets_config: str) -> Dict[str, Any]:
        """
        Optimise les assets (images, fonts, SVG).

        Args:
            assets_config: Configuration ou liste des assets

        Returns:
            Plan d'optimisation des assets
        """
        return self.run({
            "task_type": "asset_optimization",
            "context": assets_config
        })

    def analyze_dependencies(
        self,
        package_json: str,
        bundle_stats: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyse les dépendances npm.

        Args:
            package_json: Contenu du package.json
            bundle_stats: Statistiques du bundle (optionnel)

        Returns:
            Analyse des dépendances et alternatives
        """
        return self.run({
            "task_type": "dependency_analysis",
            "context": package_json,
            "bundle_stats": bundle_stats or {}
        })
