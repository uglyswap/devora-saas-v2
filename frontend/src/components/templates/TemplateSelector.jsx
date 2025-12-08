import React, { useState } from "react";
import { Sparkles, ShoppingCart, Users, BarChart3, MessageSquare, Calendar, FileText, Palette, Rocket, Check, ArrowRight } from "lucide-react";
import { Button } from "../ui/button";

const SAAS_TEMPLATES = [
  {
    id: "ecommerce",
    name: "E-Commerce Pro",
    description: "Boutique complete avec panier, paiements Stripe et gestion produits",
    icon: ShoppingCart,
    color: "from-orange-500 to-pink-500",
    tags: ["Next.js", "Stripe", "Supabase"],
    features: ["Catalogue produits", "Panier", "Checkout Stripe", "Dashboard admin"]
  },
  {
    id: "crm",
    name: "CRM Dashboard",
    description: "Gestion clients, pipeline de ventes et analytics",
    icon: Users,
    color: "from-blue-500 to-cyan-500",
    tags: ["React", "Charts", "Auth"],
    features: ["Gestion contacts", "Pipeline deals", "Rapports", "Equipes"]
  },
  {
    id: "analytics",
    name: "Analytics Platform",
    description: "Dashboard analytics avec graphiques et KPIs en temps reel",
    icon: BarChart3,
    color: "from-green-500 to-emerald-500",
    tags: ["Recharts", "Real-time", "API"],
    features: ["Graphiques", "KPIs", "Export CSV", "Alertes"]
  },
  {
    id: "chat",
    name: "Chat App",
    description: "Application de messagerie temps reel avec channels",
    icon: MessageSquare,
    color: "from-purple-500 to-violet-500",
    tags: ["WebSocket", "Supabase", "Auth"],
    features: ["Messages temps reel", "Channels", "Fichiers", "Notifications"]
  },
  {
    id: "booking",
    name: "Booking System",
    description: "Systeme de reservation avec calendrier et paiements",
    icon: Calendar,
    color: "from-red-500 to-rose-500",
    tags: ["Calendar", "Stripe", "Email"],
    features: ["Calendrier", "Reservations", "Paiements", "Rappels email"]
  },
  {
    id: "blog",
    name: "Blog CMS",
    description: "Plateforme de blog avec editeur riche et SEO",
    icon: FileText,
    color: "from-yellow-500 to-amber-500",
    tags: ["MDX", "SEO", "Auth"],
    features: ["Editeur WYSIWYG", "Categories", "SEO", "Commentaires"]
  }
];

const TemplateSelector = ({ onSelect }) => {
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [hoveredTemplate, setHoveredTemplate] = useState(null);

  const handleSelect = (template) => {
    setSelectedTemplate(template.id);
    if (onSelect) onSelect(template);
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-xl">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Templates SaaS</h2>
          <p className="text-gray-400 text-sm">Commencez avec un template professionnel</p>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {SAAS_TEMPLATES.map(template => {
          const Icon = template.icon;
          const isSelected = selectedTemplate === template.id;
          const isHovered = hoveredTemplate === template.id;
          
          return (
            <div
              key={template.id}
              onMouseEnter={() => setHoveredTemplate(template.id)}
              onMouseLeave={() => setHoveredTemplate(null)}
              onClick={() => handleSelect(template)}
              className={"relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-300 " + 
                (isSelected 
                  ? "border-white bg-white/10" 
                  : "border-gray-700 hover:border-gray-500 bg-gray-800/50")}
            >
              {isSelected && (
                <div className="absolute top-2 right-2">
                  <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                </div>
              )}
              
              <div className={"w-12 h-12 rounded-xl bg-gradient-to-r flex items-center justify-center mb-3 " + template.color}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              
              <h3 className="font-bold text-white mb-1">{template.name}</h3>
              <p className="text-xs text-gray-400 mb-3 line-clamp-2">{template.description}</p>
              
              <div className="flex flex-wrap gap-1">
                {template.tags.map(tag => (
                  <span key={tag} className="px-2 py-0.5 bg-gray-700 text-gray-300 rounded text-xs">{tag}</span>
                ))}
              </div>

              {(isHovered || isSelected) && (
                <div className="mt-3 pt-3 border-t border-gray-700">
                  <div className="text-xs text-gray-400 space-y-1">
                    {template.features.map(feature => (
                      <div key={feature} className="flex items-center gap-1">
                        <Check className="w-3 h-3 text-green-500" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {selectedTemplate && (
        <div className="mt-6 flex items-center justify-between p-4 bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-xl">
          <div className="flex items-center gap-3">
            <Rocket className="w-5 h-5 text-blue-400" />
            <span className="text-white">Template selectionne: <strong>{SAAS_TEMPLATES.find(t => t.id === selectedTemplate)?.name}</strong></span>
          </div>
          <Button className="bg-gradient-to-r from-blue-600 to-purple-600">
            Utiliser ce template <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default TemplateSelector;
