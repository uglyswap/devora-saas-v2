// ==========================================
// CRACO CONFIG - OPTIMIZED FOR PERFORMANCE
// ==========================================
// Agent: Bundle Optimizer
// Objectif: Réduire bundle de 2MB à 559KB (-73%)
// ==========================================

const path = require("path");
const webpack = require("webpack");
const TerserPlugin = require("terser-webpack-plugin");
const CompressionPlugin = require("compression-webpack-plugin");
const { BundleAnalyzerPlugin } = require("webpack-bundle-analyzer");
require("dotenv").config();

// Environment variable overrides
const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === "true",
  enableVisualEdits: process.env.REACT_APP_ENABLE_VISUAL_EDITS === "true",
  enableHealthCheck: process.env.ENABLE_HEALTH_CHECK === "true",
  analyzeBunle: process.env.ANALYZE === "true",
  isProd: process.env.NODE_ENV === "production",
};

// Conditionally load visual editing modules only if enabled
let babelMetadataPlugin;
let setupDevServer;

if (config.enableVisualEdits) {
  babelMetadataPlugin = require("./plugins/visual-edits/babel-metadata-plugin");
  setupDevServer = require("./plugins/visual-edits/dev-server-setup");
}

// Conditionally load health check modules only if enabled
let WebpackHealthPlugin;
let setupHealthEndpoints;
let healthPluginInstance;

if (config.enableHealthCheck) {
  WebpackHealthPlugin = require("./plugins/health-check/webpack-health-plugin");
  setupHealthEndpoints = require("./plugins/health-check/health-endpoints");
  healthPluginInstance = new WebpackHealthPlugin();
}

const webpackConfig = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      // Alias pour réduire les imports longs
      '@components': path.resolve(__dirname, 'src/components'),
      '@pages': path.resolve(__dirname, 'src/pages'),
      '@utils': path.resolve(__dirname, 'src/utils'),
      '@hooks': path.resolve(__dirname, 'src/hooks'),
      '@contexts': path.resolve(__dirname, 'src/contexts'),
    },

    configure: (webpackConfig, { env, paths }) => {
      const isProd = env === "production";

      // ==========================================
      // 1. CODE SPLITTING - Optimisation du découpage
      // ==========================================
      webpackConfig.optimization = {
        ...webpackConfig.optimization,

        // Activer le splitting
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            // Vendors séparés par taille
            defaultVendors: false, // Désactiver le groupe par défaut

            // 1. React core (toujours nécessaire)
            react: {
              test: /[\\/]node_modules[\\/](react|react-dom|react-router-dom)[\\/]/,
              name: 'react-core',
              priority: 40,
              reuseExistingChunk: true,
            },

            // 2. Radix UI (gros mais utilisé partout)
            radix: {
              test: /[\\/]node_modules[\\/]@radix-ui[\\/]/,
              name: 'radix-ui',
              priority: 30,
              reuseExistingChunk: true,
            },

            // 3. Monaco Editor (très gros - lazy load)
            monaco: {
              test: /[\\/]node_modules[\\/](@monaco-editor|monaco-editor)[\\/]/,
              name: 'monaco-editor',
              priority: 35,
              reuseExistingChunk: true,
            },

            // 4. CodeMirror (éditeur alternatif)
            codemirror: {
              test: /[\\/]node_modules[\\/](@codemirror|codemirror)[\\/]/,
              name: 'codemirror',
              priority: 35,
              reuseExistingChunk: true,
            },

            // 5. Autres vendors (tout le reste)
            vendors: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              priority: 20,
              reuseExistingChunk: true,
              minSize: 30000, // Au moins 30KB pour créer un chunk
            },

            // 6. Code commun utilisé plusieurs fois
            common: {
              minChunks: 2,
              priority: 10,
              reuseExistingChunk: true,
              name: 'common',
            },
          },

          // Configuration globale
          maxInitialRequests: 25, // Max de chunks chargés en parallèle
          maxAsyncRequests: 25,
          minSize: 20000, // Taille minimum d'un chunk (20KB)
          maxSize: 244000, // Taille max recommandée (244KB)
        },

        // Runtime dans un chunk séparé
        runtimeChunk: {
          name: 'runtime',
        },

        // Minification agressive en production
        minimize: isProd,
        minimizer: isProd
          ? [
              new TerserPlugin({
                terserOptions: {
                  parse: {
                    ecma: 8,
                  },
                  compress: {
                    ecma: 5,
                    warnings: false,
                    comparisons: false,
                    inline: 2,
                    drop_console: true, // Supprimer console.log en prod
                    drop_debugger: true,
                    pure_funcs: ['console.log', 'console.info'], // Supprimer ces fonctions
                  },
                  mangle: {
                    safari10: true,
                  },
                  output: {
                    ecma: 5,
                    comments: false,
                    ascii_only: true,
                  },
                },
                parallel: true,
                extractComments: false,
              }),
            ]
          : [],

        // Eviter les duplications
        usedExports: true,
        sideEffects: true,
      };

      // ==========================================
      // 2. TREE SHAKING - Supprimer le code inutilisé
      // ==========================================
      if (isProd) {
        // Mode production uniquement pour tree shaking
        webpackConfig.mode = 'production';

        // Désactiver le module concatenation si problèmes
        // webpackConfig.optimization.concatenateModules = false;
      }

      // ==========================================
      // 3. PLUGINS D'OPTIMISATION
      // ==========================================
      const optimizationPlugins = [];

      // Compression Gzip
      if (isProd) {
        optimizationPlugins.push(
          new CompressionPlugin({
            filename: '[path][base].gz',
            algorithm: 'gzip',
            test: /\.(js|css|html|svg)$/,
            threshold: 10240, // Seulement fichiers > 10KB
            minRatio: 0.8,
          })
        );

        // Compression Brotli (meilleure que gzip)
        optimizationPlugins.push(
          new CompressionPlugin({
            filename: '[path][base].br',
            algorithm: 'brotliCompress',
            test: /\.(js|css|html|svg)$/,
            compressionOptions: {
              level: 11,
            },
            threshold: 10240,
            minRatio: 0.8,
          })
        );
      }

      // Bundle Analyzer (optionnel - via ANALYZE=true)
      if (config.analyzeBunle) {
        optimizationPlugins.push(
          new BundleAnalyzerPlugin({
            analyzerMode: 'static',
            reportFilename: 'bundle-report.html',
            openAnalyzer: true,
          })
        );
      }

      // Définir les variables d'environnement
      optimizationPlugins.push(
        new webpack.DefinePlugin({
          'process.env.NODE_ENV': JSON.stringify(env),
          __DEV__: env !== 'production',
        })
      );

      // Ignore moment.js locales (économie de ~200KB)
      optimizationPlugins.push(
        new webpack.IgnorePlugin({
          resourceRegExp: /^\.\/locale$/,
          contextRegExp: /moment$/,
        })
      );

      webpackConfig.plugins = [...webpackConfig.plugins, ...optimizationPlugins];

      // ==========================================
      // 4. MODULE RULES - Optimiser le chargement
      // ==========================================

      // Optimiser les images
      const imageRule = {
        test: /\.(png|jpe?g|gif|svg|webp)$/i,
        type: 'asset',
        parser: {
          dataUrlCondition: {
            maxSize: 8192, // Images < 8KB en base64
          },
        },
        generator: {
          filename: 'static/media/[name].[hash:8][ext]',
        },
      };

      webpackConfig.module.rules.push(imageRule);

      // ==========================================
      // 5. RESOLVE - Optimiser la résolution
      // ==========================================
      webpackConfig.resolve = {
        ...webpackConfig.resolve,
        extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
        // Modules à chercher
        modules: ['node_modules', path.resolve(__dirname, 'src')],
        // Aliases déjà définis plus haut
        alias: {
          ...webpackConfig.resolve.alias,
          // Remplacer les gros packages par des alternatives légères
          // 'lodash': 'lodash-es', // Version ES modules pour tree shaking
        },
      };

      // ==========================================
      // 6. CACHE - Accélérer les builds
      // ==========================================
      webpackConfig.cache = {
        type: 'filesystem',
        cacheDirectory: path.resolve(__dirname, '.webpack-cache'),
        buildDependencies: {
          config: [__filename],
        },
      };

      // ==========================================
      // 7. PERFORMANCE HINTS
      // ==========================================
      webpackConfig.performance = {
        hints: isProd ? 'warning' : false,
        maxEntrypointSize: 512000, // 500KB max pour entry
        maxAssetSize: 512000, // 500KB max pour assets individuels
      };

      // ==========================================
      // 8. HOT RELOAD (DEV ONLY)
      // ==========================================
      if (config.disableHotReload) {
        webpackConfig.plugins = webpackConfig.plugins.filter(
          (plugin) => plugin.constructor.name !== 'HotModuleReplacementPlugin'
        );
        webpackConfig.watch = false;
        webpackConfig.watchOptions = {
          ignored: /.*/,
        };
      } else {
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/public/**',
          ],
        };
      }

      // ==========================================
      // 9. HEALTH CHECK PLUGIN
      // ==========================================
      if (config.enableHealthCheck && healthPluginInstance) {
        webpackConfig.plugins.push(healthPluginInstance);
      }

      console.log('✅ Webpack optimized configuration loaded');
      console.log('📦 Mode:', env);
      console.log('🔧 Code splitting: enabled');
      console.log('🌳 Tree shaking:', isProd ? 'enabled' : 'disabled (dev only)');
      console.log('📊 Bundle analyzer:', config.analyzeBunle ? 'enabled' : 'disabled');

      return webpackConfig;
    },
  },
};

// ==========================================
// 10. BABEL CONFIGURATION
// ==========================================
const babelPlugins = [];

// Visual edits plugin
if (config.enableVisualEdits && babelMetadataPlugin) {
  babelPlugins.push(babelMetadataPlugin);
}

// Optimizations babel
babelPlugins.push(
  // Transform runtime pour réduire la duplication
  [
    '@babel/plugin-transform-runtime',
    {
      corejs: false,
      helpers: true,
      regenerator: true,
      useESModules: true,
    },
  ]
);

webpackConfig.babel = {
  plugins: babelPlugins,
  presets: [
    [
      '@babel/preset-env',
      {
        modules: false, // Ne pas transformer les modules ES6 (pour tree shaking)
        useBuiltIns: 'usage',
        corejs: 3,
      },
    ],
    '@babel/preset-react',
  ],
};

// ==========================================
// 11. DEV SERVER
// ==========================================
if (config.enableVisualEdits || config.enableHealthCheck) {
  webpackConfig.devServer = (devServerConfig) => {
    // Apply visual edits dev server setup if enabled
    if (config.enableVisualEdits && setupDevServer) {
      devServerConfig = setupDevServer(devServerConfig);
    }

    // Add health check endpoints if enabled
    if (config.enableHealthCheck && setupHealthEndpoints && healthPluginInstance) {
      const originalSetupMiddlewares = devServerConfig.setupMiddlewares;

      devServerConfig.setupMiddlewares = (middlewares, devServer) => {
        if (originalSetupMiddlewares) {
          middlewares = originalSetupMiddlewares(middlewares, devServer);
        }

        setupHealthEndpoints(devServer, healthPluginInstance);

        return middlewares;
      };
    }

    return devServerConfig;
  };
}

module.exports = webpackConfig;
