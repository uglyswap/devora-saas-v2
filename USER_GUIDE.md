# 📖 Guide Utilisateur Devora SaaS V2

## Bienvenue sur Devora

Devora est un générateur de code intelligent basé sur l'IA. Décrivez votre projet en langage naturel et obtenez une application complète en quelques minutes.

## Démarrage Rapide

### 1. Créer un compte

1. Allez sur [devora.app](https://devora.app)
2. Cliquez sur "Commencer gratuitement"
3. Entrez votre email et créez un mot de passe
4. Confirmez votre email

### 2. Souscrire à un plan

Devora propose deux plans:

| Plan | Prix | Générations/mois |
|------|------|------------------|
| **Pro Monthly** | €29/mois | Illimité |
| **Pro Yearly** | €290/an | Illimité (2 mois gratuits) |

### 3. Créer votre premier projet

1. Accédez au Dashboard
2. Cliquez sur "Nouveau Projet"
3. Décrivez votre application:

```
Crée une application SaaS de gestion de tâches avec:
- Authentification utilisateur
- Dashboard avec statistiques
- Liste de tâches avec drag & drop
- Filtres par statut et priorité
- Mode sombre
```

4. Cliquez sur "Générer"

## L'Éditeur

### Interface

```
┌─────────────────────────────────────────────────────────┐
│  [Logo]  Nom Projet  [Fichiers ▼]  [Actions ▼]  [User]  │
├─────────────────┬───────────────────────────────────────┤
│                 │                                       │
│    CHAT IA      │           ÉDITEUR CODE               │
│                 │                                       │
│  [Votre msg]    │   // fichier.tsx                     │
│  [Réponse IA]   │   export default function...         │
│                 │                                       │
│  [Input____]    │                                       │
│                 │                                       │
├─────────────────┴───────────────────────────────────────┤
│                    PREVIEW LIVE                          │
└─────────────────────────────────────────────────────────┘
```

### Barre de Fichiers

- Cliquez sur un fichier pour l'ouvrir dans l'éditeur
- Les fichiers sont organisés par type:
  - `.tsx/.jsx` - Composants React
  - `.ts/.js` - Logique JavaScript
  - `.css` - Styles
  - `.sql` - Schémas base de données

### Modes de Génération

| Mode | Description | Utilisation |
|------|-------------|-------------|
| **Simple** | HTML/CSS/JS basique | Sites statiques, landing pages |
| **Agentic** | Multi-agents coordination | Applications web complexes |
| **Full-Stack** | Next.js 14+ complet | SaaS, E-commerce, Dashboards |

#### Activer le mode Full-Stack

1. Dans l'éditeur, activez le toggle "Mode Agentic"
2. Sélectionnez "Full-Stack" dans le dropdown
3. Décrivez votre application complète

## Fonctionnalités

### Conversation Continue

L'IA garde le contexte de votre conversation. Vous pouvez:

```
Vous: Ajoute un formulaire de contact
IA: [Génère le formulaire]

Vous: Ajoute la validation avec Zod
IA: [Ajoute la validation au formulaire existant]

Vous: Change la couleur du bouton en bleu
IA: [Modifie le style]
```

### Effacer la Conversation

Pour repartir de zéro:
1. Cliquez sur l'icône "🗑️" à côté du chat
2. Confirmez l'effacement

### Télécharger le Projet

1. Cliquez sur "Actions" → "Télécharger ZIP"
2. Tous vos fichiers sont empaquetés
3. Décompressez et `npm install && npm run dev`

### Exporter vers GitHub

1. Cliquez sur "Actions" → "Push GitHub"
2. Entrez le nom du repository
3. Le code est pushé sur votre compte GitHub
4. Un lien vers le repo apparaît dans le dashboard

### Déployer sur Vercel

1. Assurez-vous d'avoir exporté vers GitHub d'abord
2. Cliquez sur "Actions" → "Déployer Vercel"
3. Votre app est live en quelques secondes!
4. Le lien de déploiement apparaît dans le dashboard

## Templates Disponibles

### SaaS Starter

Application SaaS complète avec:
- ✅ Authentification (Supabase Auth)
- ✅ Billing (Stripe subscriptions)
- ✅ Dashboard utilisateur
- ✅ Settings & profil
- ✅ Landing page marketing

### E-commerce

Boutique en ligne avec:
- ✅ Catalogue produits
- ✅ Panier d'achat
- ✅ Checkout Stripe
- ✅ Gestion commandes

### Blog/CMS

Plateforme de contenu avec:
- ✅ Articles MDX
- ✅ Catégories & tags
- ✅ Commentaires
- ✅ SEO optimisé

### Dashboard

Tableau de bord avec:
- ✅ Graphiques (Recharts)
- ✅ Tables de données
- ✅ Filtres & recherche
- ✅ Export données

## Bonnes Pratiques

### Prompts Efficaces

❌ **Trop vague:**
```
Crée un site web
```

✅ **Spécifique:**
```
Crée une landing page pour une app de fitness avec:
- Hero section avec CTA
- 3 features avec icônes
- Section témoignages (3 avis)
- Pricing avec 2 plans
- Footer avec liens réseaux sociaux
- Palette de couleurs: bleu et blanc
- Style moderne et épuré
```

### Itérations

Procédez par étapes:

1. **Structure de base**
   ```
   Crée la structure de base d'un dashboard admin
   ```

2. **Ajout de fonctionnalités**
   ```
   Ajoute un graphique de revenus mensuels
   ```

3. **Refinement**
   ```
   Améliore le responsive pour mobile
   ```

### Personnalisation

Vous pouvez toujours:
- Modifier le code généré manuellement
- Demander des changements spécifiques à l'IA
- Combiner génération IA et code custom

## FAQ

### Le code généré m'appartient-il?

Oui, 100%. Vous avez tous les droits sur le code généré.

### Puis-je utiliser le code en production?

Oui, le code est prêt pour la production. Il suit les meilleures pratiques et utilise des technologies modernes.

### Comment fonctionne le mode Full-Stack?

Le mode Full-Stack utilise plusieurs agents IA spécialisés:
1. **Architect**: Analyse vos besoins et conçoit l'architecture
2. **Frontend**: Génère l'interface utilisateur
3. **Backend**: Crée les API et la logique serveur
4. **Database**: Conçoit les schémas de base de données

### Le contexte est-il sauvegardé?

Oui, votre historique de conversation est sauvegardé avec le projet. Vous pouvez reprendre où vous en étiez.

### Comment effacer l'historique?

Cliquez sur l'icône poubelle dans le chat pour effacer l'historique et repartir de zéro.

## Support

- 📧 Email: support@devora.app
- 💬 Discord: [discord.gg/devora](https://discord.gg/devora)
- 📖 Documentation: [docs.devora.app](https://docs.devora.app)
