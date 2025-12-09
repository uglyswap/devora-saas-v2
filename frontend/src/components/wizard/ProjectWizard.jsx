/**
 * DEVORA PROJECT WIZARD - Ultimate UX Experience
 *
 * Wizard d'onboarding guidé en 4 étapes pour créer une app en 2 minutes
 * Inspiré par les meilleures pratiques de Lovable, Bolt et Vercel
 *
 * @version 5.0.0
 */

import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles, ArrowRight, ArrowLeft, Check, Rocket, Code2,
  Palette, Zap, ShoppingCart, Users, BarChart3, MessageSquare,
  Calendar, FileText, Globe, Layout, CreditCard, Brain,
  Wand2, Play, ChevronRight, Star, Clock, Shield
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { cn } from '../../lib/utils';

// ============================================
// CONFIGURATION & DATA
// ============================================

const STEPS = [
  { id: 'idea', title: 'Votre Idée', icon: Sparkles },
  { id: 'template', title: 'Template', icon: Layout },
  { id: 'style', title: 'Style', icon: Palette },
  { id: 'features', title: 'Features', icon: Zap },
];

const TEMPLATES = [
  {
    id: 'saas-starter',
    name: 'SaaS Starter',
    description: 'Landing, Auth, Dashboard, Billing',
    icon: Rocket,
    gradient: 'from-emerald-500 to-teal-500',
    popular: true,
    features: ['Landing page', 'Auth Google/Email', 'Dashboard', 'Stripe Billing', 'Admin panel'],
    tech: ['Next.js 14', 'TypeScript', 'Tailwind', 'Supabase', 'Stripe'],
    estimatedTime: '~2 min'
  },
  {
    id: 'ai-saas',
    name: 'AI SaaS Platform',
    description: 'Credits, OpenAI, Génération',
    icon: Brain,
    gradient: 'from-violet-500 to-purple-600',
    popular: true,
    features: ['Système de crédits', 'Intégration OpenAI', 'Historique', 'Plans tarifaires'],
    tech: ['Next.js 14', 'OpenAI SDK', 'Stripe', 'PostgreSQL'],
    estimatedTime: '~3 min'
  },
  {
    id: 'ecommerce',
    name: 'E-Commerce',
    description: 'Catalogue, Panier, Checkout',
    icon: ShoppingCart,
    gradient: 'from-orange-500 to-pink-500',
    features: ['Catalogue produits', 'Panier', 'Checkout Stripe', 'Admin produits'],
    tech: ['Next.js 14', 'Stripe', 'Supabase Storage'],
    estimatedTime: '~3 min'
  },
  {
    id: 'crm',
    name: 'CRM Dashboard',
    description: 'Contacts, Pipeline, Analytics',
    icon: Users,
    gradient: 'from-blue-500 to-cyan-500',
    features: ['Gestion contacts', 'Pipeline deals', 'Rapports', 'Équipes'],
    tech: ['Next.js 14', 'Recharts', 'PostgreSQL'],
    estimatedTime: '~2 min'
  },
  {
    id: 'analytics',
    name: 'Analytics Dashboard',
    description: 'KPIs, Graphiques, Temps réel',
    icon: BarChart3,
    gradient: 'from-green-500 to-emerald-500',
    features: ['Graphiques interactifs', 'KPIs temps réel', 'Export CSV', 'Filtres avancés'],
    tech: ['Next.js 14', 'Recharts', 'WebSocket'],
    estimatedTime: '~2 min'
  },
  {
    id: 'landing',
    name: 'Landing Page Pro',
    description: 'Hero, Features, Pricing, CTA',
    icon: Layout,
    gradient: 'from-pink-500 to-rose-500',
    features: ['Hero section', 'Features grid', 'Pricing table', 'Testimonials', 'CTA sections'],
    tech: ['Next.js 14', 'Tailwind', 'Framer Motion'],
    estimatedTime: '~1 min'
  },
  {
    id: 'chat',
    name: 'Chat Application',
    description: 'Messages, Channels, Temps réel',
    icon: MessageSquare,
    gradient: 'from-purple-500 to-violet-500',
    features: ['Messages temps réel', 'Channels', 'Fichiers', 'Notifications'],
    tech: ['Next.js 14', 'Supabase Realtime', 'WebSocket'],
    estimatedTime: '~3 min'
  },
  {
    id: 'booking',
    name: 'Booking System',
    description: 'Calendrier, Réservations, Paiements',
    icon: Calendar,
    gradient: 'from-red-500 to-rose-500',
    features: ['Calendrier', 'Réservations', 'Paiements', 'Rappels email'],
    tech: ['Next.js 14', 'react-big-calendar', 'Stripe'],
    estimatedTime: '~3 min'
  },
  {
    id: 'custom',
    name: 'Projet Custom',
    description: 'Décrivez exactement ce que vous voulez',
    icon: Wand2,
    gradient: 'from-gray-600 to-gray-800',
    features: ['100% personnalisé', 'Basé sur votre description', 'Architecture sur mesure'],
    tech: ['Stack adaptée à vos besoins'],
    estimatedTime: '~2-5 min'
  }
];

const STYLES = [
  { id: 'minimal', name: 'Minimal', description: 'Épuré et professionnel', colors: ['#f5f5f5', '#333333', '#000000'] },
  { id: 'modern', name: 'Moderne', description: 'Design contemporain', colors: ['#0f172a', '#3b82f6', '#10b981'] },
  { id: 'colorful', name: 'Coloré', description: 'Vibrant et énergique', colors: ['#7c3aed', '#ec4899', '#f59e0b'] },
  { id: 'corporate', name: 'Corporate', description: 'Sobre et institutionnel', colors: ['#1e3a5f', '#ffffff', '#64748b'] },
  { id: 'dark', name: 'Dark Mode', description: 'Thème sombre élégant', colors: ['#0a0a0b', '#10b981', '#6366f1'] },
  { id: 'glass', name: 'Glassmorphism', description: 'Effets de verre modernes', colors: ['rgba(255,255,255,0.1)', '#3b82f6', '#a855f7'] },
];

const FEATURE_OPTIONS = [
  { id: 'auth', name: 'Authentification', icon: Shield, description: 'Login, Register, OAuth' },
  { id: 'billing', name: 'Paiements Stripe', icon: CreditCard, description: 'Abonnements, Checkout' },
  { id: 'dashboard', name: 'Dashboard', icon: BarChart3, description: 'Analytics, KPIs' },
  { id: 'api', name: 'API REST', icon: Code2, description: 'Endpoints documentés' },
  { id: 'realtime', name: 'Temps réel', icon: Zap, description: 'WebSocket, Live updates' },
  { id: 'ai', name: 'Intégration IA', icon: Brain, description: 'OpenAI, Claude, Gemini' },
  { id: 'storage', name: 'File Storage', icon: FileText, description: 'Upload, CDN' },
  { id: 'i18n', name: 'Multi-langue', icon: Globe, description: 'FR, EN, ES...' },
];

// ============================================
// STEP COMPONENTS
// ============================================

const StepIdea = ({ data, onChange }) => {
  const [charCount, setCharCount] = useState(data.idea?.length || 0);

  const suggestions = [
    "Une app de gestion de tâches avec collaboration temps réel",
    "Un SaaS de facturation pour freelances avec Stripe",
    "Un dashboard analytics pour e-commerce",
    "Une plateforme de cours en ligne avec paiements"
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">Décrivez votre projet</h2>
        <p className="text-gray-400">En quelques mots, qu'est-ce que vous voulez créer ?</p>
      </div>

      <div className="relative">
        <Textarea
          value={data.idea || ''}
          onChange={(e) => {
            onChange({ idea: e.target.value });
            setCharCount(e.target.value.length);
          }}
          placeholder="Ex: Une application SaaS pour gérer les abonnements de mes clients avec un dashboard analytics..."
          className="min-h-[150px] bg-white/5 border-white/10 text-lg p-4 resize-none"
          maxLength={500}
        />
        <span className="absolute bottom-3 right-3 text-sm text-gray-500">
          {charCount}/500
        </span>
      </div>

      <div className="space-y-3">
        <p className="text-sm text-gray-400">Suggestions rapides :</p>
        <div className="flex flex-wrap gap-2">
          {suggestions.map((suggestion, idx) => (
            <button
              key={idx}
              onClick={() => {
                onChange({ idea: suggestion });
                setCharCount(suggestion.length);
              }}
              className="px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 transition-colors text-left"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

const StepTemplate = ({ data, onChange }) => {
  const [hoveredTemplate, setHoveredTemplate] = useState(null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">Choisissez un template</h2>
        <p className="text-gray-400">Sélectionnez une base pour votre projet</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {TEMPLATES.map((template) => {
          const Icon = template.icon;
          const isSelected = data.template === template.id;
          const isHovered = hoveredTemplate === template.id;

          return (
            <motion.div
              key={template.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onMouseEnter={() => setHoveredTemplate(template.id)}
              onMouseLeave={() => setHoveredTemplate(null)}
              onClick={() => onChange({ template: template.id, templateData: template })}
              className={cn(
                "relative p-5 rounded-xl cursor-pointer transition-all duration-300 border-2",
                isSelected
                  ? "border-emerald-500 bg-emerald-500/10"
                  : "border-white/10 bg-white/5 hover:border-white/30"
              )}
            >
              {template.popular && (
                <div className="absolute -top-2 -right-2 px-2 py-0.5 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full text-xs font-bold flex items-center gap-1">
                  <Star className="w-3 h-3" /> Popular
                </div>
              )}

              {isSelected && (
                <div className="absolute top-3 right-3">
                  <div className="w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                </div>
              )}

              <div className={cn(
                "w-12 h-12 rounded-xl flex items-center justify-center mb-4 bg-gradient-to-br",
                template.gradient
              )}>
                <Icon className="w-6 h-6 text-white" />
              </div>

              <h3 className="font-bold text-lg mb-1">{template.name}</h3>
              <p className="text-sm text-gray-400 mb-3">{template.description}</p>

              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                <span>{template.estimatedTime}</span>
              </div>

              <AnimatePresence>
                {(isHovered || isSelected) && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-4 pt-4 border-t border-white/10"
                  >
                    <div className="space-y-2">
                      {template.features.slice(0, 4).map((feature, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-sm text-gray-300">
                          <Check className="w-3 h-3 text-emerald-400" />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-1 mt-3">
                      {template.tech.slice(0, 3).map((tech, idx) => (
                        <span key={idx} className="px-2 py-0.5 bg-white/10 rounded text-xs">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

const StepStyle = ({ data, onChange }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">Choisissez un style</h2>
        <p className="text-gray-400">Définissez l'apparence de votre application</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {STYLES.map((style) => {
          const isSelected = data.style === style.id;

          return (
            <motion.div
              key={style.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onChange({ style: style.id, styleData: style })}
              className={cn(
                "relative p-5 rounded-xl cursor-pointer transition-all duration-300 border-2",
                isSelected
                  ? "border-emerald-500 bg-emerald-500/10"
                  : "border-white/10 bg-white/5 hover:border-white/30"
              )}
            >
              {isSelected && (
                <div className="absolute top-3 right-3">
                  <div className="w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                </div>
              )}

              {/* Color Preview */}
              <div className="flex gap-2 mb-4">
                {style.colors.map((color, idx) => (
                  <div
                    key={idx}
                    className="w-8 h-8 rounded-lg border border-white/20"
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>

              <h3 className="font-bold text-lg mb-1">{style.name}</h3>
              <p className="text-sm text-gray-400">{style.description}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Custom Colors Option */}
      <div className="mt-6 p-4 bg-white/5 border border-white/10 rounded-xl">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium">Couleurs personnalisées</h4>
            <p className="text-sm text-gray-400">Définissez vos propres couleurs</p>
          </div>
          <div className="flex gap-2">
            <input
              type="color"
              value={data.customColors?.primary || '#10b981'}
              onChange={(e) => onChange({ customColors: { ...data.customColors, primary: e.target.value } })}
              className="w-10 h-10 rounded cursor-pointer"
            />
            <input
              type="color"
              value={data.customColors?.secondary || '#3b82f6'}
              onChange={(e) => onChange({ customColors: { ...data.customColors, secondary: e.target.value } })}
              className="w-10 h-10 rounded cursor-pointer"
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

const StepFeatures = ({ data, onChange }) => {
  const selectedFeatures = data.features || [];

  const toggleFeature = (featureId) => {
    const newFeatures = selectedFeatures.includes(featureId)
      ? selectedFeatures.filter(f => f !== featureId)
      : [...selectedFeatures, featureId];
    onChange({ features: newFeatures });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">Sélectionnez les fonctionnalités</h2>
        <p className="text-gray-400">Choisissez ce que vous voulez inclure</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {FEATURE_OPTIONS.map((feature) => {
          const Icon = feature.icon;
          const isSelected = selectedFeatures.includes(feature.id);

          return (
            <motion.div
              key={feature.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => toggleFeature(feature.id)}
              className={cn(
                "relative p-4 rounded-xl cursor-pointer transition-all duration-300 border-2 text-center",
                isSelected
                  ? "border-emerald-500 bg-emerald-500/10"
                  : "border-white/10 bg-white/5 hover:border-white/30"
              )}
            >
              {isSelected && (
                <div className="absolute top-2 right-2">
                  <div className="w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center">
                    <Check className="w-3 h-3 text-white" />
                  </div>
                </div>
              )}

              <div className={cn(
                "w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-3",
                isSelected ? "bg-emerald-500/20 text-emerald-400" : "bg-white/10 text-gray-400"
              )}>
                <Icon className="w-5 h-5" />
              </div>

              <h3 className="font-medium text-sm mb-1">{feature.name}</h3>
              <p className="text-xs text-gray-500">{feature.description}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Additional Requirements */}
      <div className="mt-6 p-4 bg-white/5 border border-white/10 rounded-xl">
        <h4 className="font-medium mb-3">Exigences additionnelles (optionnel)</h4>
        <Textarea
          value={data.additionalRequirements || ''}
          onChange={(e) => onChange({ additionalRequirements: e.target.value })}
          placeholder="Ajoutez des détails spécifiques, des intégrations particulières, des contraintes..."
          className="bg-white/5 border-white/10 resize-none"
          rows={3}
        />
      </div>

      {/* Summary */}
      <div className="mt-6 p-4 bg-gradient-to-r from-emerald-500/10 to-blue-500/10 border border-emerald-500/20 rounded-xl">
        <h4 className="font-medium mb-2 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          Résumé de votre projet
        </h4>
        <div className="text-sm text-gray-300 space-y-1">
          <p><strong>Template:</strong> {data.templateData?.name || 'Non sélectionné'}</p>
          <p><strong>Style:</strong> {data.styleData?.name || 'Non sélectionné'}</p>
          <p><strong>Features:</strong> {selectedFeatures.length > 0 ? selectedFeatures.map(f => FEATURE_OPTIONS.find(fo => fo.id === f)?.name).join(', ') : 'Aucune'}</p>
        </div>
      </div>
    </motion.div>
  );
};

// ============================================
// MAIN WIZARD COMPONENT
// ============================================

const ProjectWizard = ({ onComplete, onCancel }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [wizardData, setWizardData] = useState({
    idea: '',
    template: null,
    templateData: null,
    style: 'modern',
    styleData: STYLES[1],
    features: ['auth', 'dashboard'],
    customColors: {},
    additionalRequirements: ''
  });
  const [isGenerating, setIsGenerating] = useState(false);

  const updateData = useCallback((newData) => {
    setWizardData(prev => ({ ...prev, ...newData }));
  }, []);

  const canProceed = useCallback(() => {
    switch (currentStep) {
      case 0: return wizardData.idea?.length >= 10;
      case 1: return wizardData.template !== null;
      case 2: return wizardData.style !== null;
      case 3: return true;
      default: return false;
    }
  }, [currentStep, wizardData]);

  const nextStep = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      handleGenerate();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);

    // Build the complete prompt from wizard data
    const prompt = buildPromptFromWizard(wizardData);

    // Call the onComplete callback with the wizard data and prompt
    if (onComplete) {
      await onComplete({
        ...wizardData,
        generatedPrompt: prompt
      });
    }

    setIsGenerating(false);
  };

  const buildPromptFromWizard = (data) => {
    const template = data.templateData;
    const style = data.styleData;
    const features = data.features
      .map(f => FEATURE_OPTIONS.find(fo => fo.id === f)?.name)
      .filter(Boolean);

    let prompt = `Crée une application ${template?.name || 'custom'} avec les caractéristiques suivantes:\n\n`;

    prompt += `**Description:** ${data.idea}\n\n`;

    if (template) {
      prompt += `**Template de base:** ${template.name}\n`;
      prompt += `**Stack technique:** ${template.tech.join(', ')}\n\n`;
    }

    prompt += `**Style visuel:** ${style?.name || 'Moderne'} - ${style?.description || ''}\n`;

    if (data.customColors?.primary) {
      prompt += `**Couleur principale:** ${data.customColors.primary}\n`;
    }

    if (features.length > 0) {
      prompt += `\n**Fonctionnalités requises:**\n`;
      features.forEach(f => {
        prompt += `- ${f}\n`;
      });
    }

    if (data.additionalRequirements) {
      prompt += `\n**Exigences additionnelles:**\n${data.additionalRequirements}\n`;
    }

    prompt += `\nGénère un projet complet et fonctionnel avec:
- Architecture propre et maintenable
- Code TypeScript avec typage strict
- Composants réutilisables
- Design responsive
- Best practices de sécurité`;

    return prompt;
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return <StepIdea data={wizardData} onChange={updateData} />;
      case 1:
        return <StepTemplate data={wizardData} onChange={updateData} />;
      case 2:
        return <StepStyle data={wizardData} onChange={updateData} />;
      case 3:
        return <StepFeatures data={wizardData} onChange={updateData} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0b] via-[#111113] to-[#0a0a0b] py-8 px-4">
      {/* Progress Bar */}
      <div className="max-w-4xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-4">
          {STEPS.map((step, idx) => {
            const Icon = step.icon;
            const isActive = idx === currentStep;
            const isCompleted = idx < currentStep;

            return (
              <React.Fragment key={step.id}>
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      "w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300",
                      isActive
                        ? "bg-gradient-to-r from-emerald-500 to-blue-500 text-white"
                        : isCompleted
                        ? "bg-emerald-500 text-white"
                        : "bg-white/10 text-gray-400"
                    )}
                  >
                    {isCompleted ? (
                      <Check className="w-5 h-5" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>
                  <span className={cn(
                    "text-sm mt-2",
                    isActive ? "text-white font-medium" : "text-gray-500"
                  )}>
                    {step.title}
                  </span>
                </div>
                {idx < STEPS.length - 1 && (
                  <div className={cn(
                    "flex-1 h-1 mx-4 rounded-full transition-all duration-300",
                    idx < currentStep ? "bg-emerald-500" : "bg-white/10"
                  )} />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Step Content */}
      <div className="max-w-4xl mx-auto">
        <AnimatePresence mode="wait">
          {renderStep()}
        </AnimatePresence>
      </div>

      {/* Navigation Buttons */}
      <div className="max-w-4xl mx-auto mt-8 flex justify-between">
        <div>
          {currentStep > 0 ? (
            <Button
              variant="outline"
              onClick={prevStep}
              className="border-white/10 text-gray-300 hover:bg-white/5"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Retour
            </Button>
          ) : (
            <Button
              variant="ghost"
              onClick={onCancel}
              className="text-gray-400 hover:text-white"
            >
              Annuler
            </Button>
          )}
        </div>

        <Button
          onClick={nextStep}
          disabled={!canProceed() || isGenerating}
          className={cn(
            "px-8",
            currentStep === STEPS.length - 1
              ? "bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600"
              : "bg-emerald-500 hover:bg-emerald-600"
          )}
        >
          {isGenerating ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="mr-2"
              >
                <Sparkles className="w-4 h-4" />
              </motion.div>
              Génération en cours...
            </>
          ) : currentStep === STEPS.length - 1 ? (
            <>
              <Rocket className="w-4 h-4 mr-2" />
              Générer mon projet
            </>
          ) : (
            <>
              Continuer
              <ArrowRight className="w-4 h-4 ml-2" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
};

export default ProjectWizard;
