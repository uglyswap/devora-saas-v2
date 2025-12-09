"""
Compliance Officer Agent - Business Squad

Cet agent est responsable de:
- Vérifier la conformité GDPR, CCPA, LGPD
- Générer les politiques de confidentialité et CGU
- Auditer les pratiques de données et sécurité
- Assurer la conformité légale et réglementaire
"""

import sys
import os
from typing import Dict, Any, List, Set
from datetime import datetime

# Ajouter le chemin du backend pour importer BaseAgent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../backend'))

from agents.base_agent import BaseAgent


class ComplianceOfficerAgent(BaseAgent):
    """
    Agent Compliance Officer pour la conformité légale et réglementaire.

    Attributes:
        name (str): Nom de l'agent
        api_key (str): Clé API pour le LLM
        model (str): Modèle LLM à utiliser
        regulations (Set[str]): Réglementations applicables
    """

    def __init__(
        self,
        api_key: str,
        model: str = "openai/gpt-4o",
        regulations: List[str] = None
    ):
        super().__init__(name="ComplianceOfficer", api_key=api_key, model=model)
        self.regulations = set(regulations or ["GDPR", "CCPA"])
        self.system_prompt = f"""Tu es un Compliance Officer expert en protection des données et réglementation tech.

Ton expertise:
- **GDPR** (EU): Règlement général sur la protection des données
- **CCPA/CPRA** (California): California Consumer Privacy Act
- **LGPD** (Brazil): Lei Geral de Proteção de Dados
- **PIPEDA** (Canada): Personal Information Protection and Electronic Documents Act
- **Privacy Shield / SCCs**: Transferts internationaux de données
- **Cookie Law / ePrivacy Directive**: Consentement cookies
- **SOC 2**: Security, Availability, Processing Integrity, Confidentiality, Privacy
- **ISO 27001**: Management de la sécurité de l'information
- **PCI DSS**: Payment Card Industry Data Security Standard

Réglementations actives pour ce projet: {', '.join(self.regulations)}

Principes fondamentaux:
- **Privacy by Design**: Intégrer la protection dès la conception
- **Data Minimization**: Collecter seulement ce qui est nécessaire
- **Transparency**: Informer clairement les utilisateurs
- **User Rights**: Respecter droits d'accès, rectification, suppression
- **Security**: Mesures techniques et organisationnelles appropriées
- **Accountability**: Documenter la conformité

Format de sortie:
- Checklist actionnable
- Références aux articles de loi pertinents
- Risques identifiés avec niveau de criticité
- Recommandations prioritaires"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute une tâche de compliance.

        Args:
            task (Dict[str, Any]): Tâche à exécuter avec les clés:
                - task_type: "audit" | "policy" | "data_mapping" | "consent" | "rights" | "dpia"
                - context: Contexte du produit/système
                - data_types: Types de données collectées
                - jurisdictions: Juridictions applicables
                - current_practices: Pratiques actuelles (pour audit)

        Returns:
            Dict[str, Any]: Résultat avec les clés:
                - status: "success" | "error"
                - output: Analyse et recommandations
                - risk_level: "low" | "medium" | "high" | "critical"
                - action_items: Liste des actions requises
        """
        task_type = task.get("task_type", "audit")
        context = task.get("context", "")
        data_types = task.get("data_types", [])
        jurisdictions = task.get("jurisdictions", list(self.regulations))
        current_practices = task.get("current_practices", "")

        # Construire le prompt selon le type de tâche
        if task_type == "audit":
            user_prompt = self._build_audit_prompt(context, data_types, jurisdictions, current_practices)
        elif task_type == "policy":
            user_prompt = self._build_policy_prompt(context, data_types, jurisdictions)
        elif task_type == "data_mapping":
            user_prompt = self._build_data_mapping_prompt(context, data_types)
        elif task_type == "consent":
            user_prompt = self._build_consent_prompt(context, data_types)
        elif task_type == "rights":
            user_prompt = self._build_rights_prompt(context, jurisdictions)
        elif task_type == "dpia":
            user_prompt = self._build_dpia_prompt(context, data_types)
        else:
            return {
                "status": "error",
                "output": f"Type de tâche inconnu: {task_type}",
                "risk_level": "unknown",
                "action_items": []
            }

        # Appeler le LLM
        response = await self.call_llm(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=self.system_prompt
        )

        # Ajouter à la mémoire
        self.add_to_memory("user", user_prompt)
        self.add_to_memory("assistant", response)

        # Extraire le niveau de risque de la réponse
        risk_level = self._extract_risk_level(response)

        return {
            "status": "success",
            "output": response,
            "risk_level": risk_level,
            "metadata": {
                "task_type": task_type,
                "timestamp": datetime.utcnow().isoformat(),
                "jurisdictions": jurisdictions
            }
        }

    def _build_audit_prompt(self, context: str, data_types: List[str], jurisdictions: List[str], practices: str) -> str:
        """Construit le prompt pour un audit de conformité."""
        data_list = ", ".join(data_types) if data_types else "Non spécifié"
        juris_list = ", ".join(jurisdictions)

        return f"""Effectue un audit complet de conformité pour:

CONTEXTE PRODUIT/SYSTÈME:
{context}

TYPES DE DONNÉES COLLECTÉES:
{data_list}

JURIDICTIONS APPLICABLES:
{juris_list}

PRATIQUES ACTUELLES:
{practices if practices else "Aucune information sur les pratiques actuelles"}

**AUDIT CHECKLIST:**

**1. GDPR COMPLIANCE (si applicable)**

□ **Lawful Basis (Article 6)**
- Consentement obtenu de manière valide?
- Intérêt légitime documenté?
- Base légale claire pour chaque traitement?

□ **Data Subject Rights (Articles 12-23)**
- Droit d'accès implémenté? (export données)
- Droit de rectification?
- Droit à l'effacement ("right to be forgotten")?
- Droit à la portabilité?
- Droit d'opposition?
- Processus pour répondre sous 30 jours?

□ **Privacy by Design (Article 25)**
- Protection des données dès la conception?
- Pseudonymisation/encryption en place?
- Data minimization respectée?

□ **Data Transfers (Articles 44-50)**
- Transferts hors UE documentés?
- SCCs (Standard Contractual Clauses) signées?
- Adéquacy decision vérifiée?

□ **DPO & Records (Articles 30, 37-39)**
- DPO désigné si requis?
- Registre des traitements maintenu?
- Documentation des mesures de sécurité?

□ **Breach Notification (Articles 33-34)**
- Processus pour détecter les breaches?
- Notification CNIL sous 72h?
- Communication aux personnes concernées?

**2. CCPA/CPRA COMPLIANCE (si applicable)**

□ **Consumer Rights**
- Right to Know implémenté?
- Right to Delete?
- Right to Opt-Out (vente de données)?
- Right to Non-Discrimination?

□ **Notice Requirements**
- Privacy Policy accessible?
- "Do Not Sell My Personal Information" lien?
- Notice at collection?

□ **Service Providers**
- Contrats avec vendors conformes?
- Certifications des sous-traitants?

**3. COOKIES & CONSENT**

□ Cookie banner conforme?
□ Consentement avant dépôt de cookies non essentiels?
□ Granularité du consentement (accepter/refuser par catégorie)?
□ Cookie policy à jour?

**4. SECURITY MEASURES**

□ Encryption at rest et in transit?
□ Access controls (RBAC)?
□ Logging et monitoring?
□ Incident response plan?
□ Penetration testing régulier?

**5. VENDOR MANAGEMENT**

□ Liste des sous-traitants documentée?
□ DPAs (Data Processing Agreements) signés?
□ Due diligence des vendors?

**SCORING:**
- ✅ Conforme: 0 points de risque
- ⚠️ Partiellement conforme: 1 point
- ❌ Non conforme: 3 points
- 🚨 Violation critique: 5 points

**TOTAL SCORE & RISK LEVEL:**
- 0-5 points: LOW RISK
- 6-15 points: MEDIUM RISK
- 16-30 points: HIGH RISK
- 30+ points: CRITICAL RISK

**TOP 5 ACTIONS PRIORITAIRES:**
Liste les actions les plus urgentes avec deadline suggérée."""

    def _build_policy_prompt(self, context: str, data_types: List[str], jurisdictions: List[str]) -> str:
        """Construit le prompt pour générer une politique de confidentialité."""
        data_list = ", ".join(data_types) if data_types else "Non spécifié"
        juris_list = ", ".join(jurisdictions)

        return f"""Génère une Privacy Policy (Politique de Confidentialité) conforme pour:

CONTEXTE:
{context}

DONNÉES COLLECTÉES:
{data_list}

JURIDICTIONS:
{juris_list}

**STRUCTURE DE LA PRIVACY POLICY:**

**1. Introduction**
- Qui sommes-nous?
- Engagement envers la confidentialité
- Dernière mise à jour

**2. Informations Collectées**
Pour chaque type de donnée:
- Quelle donnée?
- Pourquoi collectée? (finalité)
- Base légale (GDPR: consentement, intérêt légitime, etc.)

Catégories:
- Données d'identification (nom, email, etc.)
- Données techniques (IP, user agent, cookies)
- Données d'utilisation (logs, analytics)
- Données de paiement (si applicable)

**3. Utilisation des Données**
- Fournir le service
- Améliorer le produit
- Communications marketing (avec opt-out)
- Support client
- Conformité légale

**4. Partage des Données**
- Sous-traitants (liste ou catégories)
- Transferts internationaux (SCCs si hors UE)
- Obligations légales
- Pas de vente (sauf si business model)

**5. Vos Droits**

**GDPR (UE):**
- Droit d'accès
- Droit de rectification
- Droit à l'effacement
- Droit à la portabilité
- Droit d'opposition
- Droit de limitation du traitement
- Comment exercer ces droits? (email, formulaire)

**CCPA (California):**
- Right to Know
- Right to Delete
- Right to Opt-Out
- Right to Non-Discrimination

**6. Sécurité des Données**
- Mesures techniques (encryption, firewalls)
- Mesures organisationnelles (access controls, training)
- Retention period (combien de temps gardées?)

**7. Cookies**
- Types de cookies utilisés
- Finalité de chaque type
- Comment gérer les cookies?
- Lien vers Cookie Policy détaillée

**8. Modifications**
- Comment notifiés des changements?
- Dernière date de mise à jour

**9. Contact**
- Email du DPO ou Data Privacy contact
- Adresse postale (si requis)
- Autorité de contrôle (CNIL pour France, ICO pour UK, etc.)

**FORMAT:**
- Langage clair et accessible (pas juste du legal jargon)
- Sections numérotées pour navigation facile
- Liens vers ressources externes (autorités de contrôle)
- Disponible en plusieurs langues si service international"""

    def _build_data_mapping_prompt(self, context: str, data_types: List[str]) -> str:
        """Construit le prompt pour mapper les flux de données."""
        data_list = ", ".join(data_types) if data_types else "Non spécifié"

        return f"""Crée une Data Mapping (cartographie des données) pour:

CONTEXTE:
{context}

DONNÉES IDENTIFIÉES:
{data_list}

**DATA FLOW MAPPING:**

Pour chaque type de donnée, documente:

| Donnée | Source | Finalité | Base légale | Stockage | Durée rétention | Partage | Transferts intl. |
|--------|--------|----------|-------------|----------|-----------------|---------|------------------|
| Email | Formulaire inscription | Authentification | Contrat | DB EU | Durée du compte + 1 an | Mailchimp (ESP) | Non |
| ... | ... | ... | ... | ... | ... | ... | ... |

**CATÉGORIES DE DONNÉES:**

**1. Personal Data (PII - Personally Identifiable Information)**
- Nom, prénom
- Email
- Téléphone
- Adresse
- Date de naissance
- → Risque: ÉLEVÉ | Mesures spéciales requises

**2. Special Category Data (Sensitive - GDPR Article 9)**
- Origine ethnique
- Opinions politiques
- Données de santé
- Données biométriques
- → Risque: CRITIQUE | Consentement explicite requis + mesures renforcées

**3. Technical Data**
- IP address
- Cookies
- Device ID
- User agent
- → Risque: MOYEN | Pseudonymisation recommandée

**4. Usage Data**
- Pages visitées
- Features utilisées
- Timestamps
- → Risque: BAS | Aggregation recommandée

**5. Payment Data**
- Numéro de carte (si stocké - déconseillé)
- Billing address
- Transaction history
- → Risque: ÉLEVÉ | PCI DSS compliance requis

**SYSTÈMES & THIRD PARTIES:**

Liste tous les systèmes qui traitent des données:
- **Production DB** (Supabase): Stockage principal
- **Analytics** (Google Analytics, Mixpanel): Tracking anonymisé
- **Email** (SendGrid, Mailchimp): Communications
- **Payment** (Stripe): Traitement paiements
- **Support** (Intercom, Zendesk): Support client
- **Hosting** (AWS, Vercel): Infrastructure

Pour chaque:
- DPA signé? (Data Processing Agreement)
- Localisation des serveurs?
- Certifications (SOC 2, ISO 27001)?

**DATA LIFECYCLE:**

Collection → Storage → Processing → Sharing → Deletion

1. **Collection**: Comment collectées?
2. **Storage**: Où? Combien de temps?
3. **Processing**: Quelles opérations?
4. **Sharing**: Avec qui? Pourquoi?
5. **Deletion**: Après combien de temps? Processus?

**RECOMMENDATIONS:**
- Données à supprimer (non nécessaires)
- Pseudonymisation/anonymisation à implémenter
- Encryption manquante
- Durées de rétention à définir"""

    def _build_consent_prompt(self, context: str, data_types: List[str]) -> str:
        """Construit le prompt pour le mécanisme de consentement."""
        data_list = ", ".join(data_types) if data_types else "Non spécifié"

        return f"""Définis un mécanisme de consentement conforme pour:

CONTEXTE:
{context}

DONNÉES NÉCESSITANT CONSENTEMENT:
{data_list}

**CONSENT MANAGEMENT:**

**1. Cookie Consent Banner**

**Design du banner:**
- Apparaît avant tout dépôt de cookie non essentiel
- Options claires: "Tout accepter" | "Tout refuser" | "Personnaliser"
- Pas de pre-ticked boxes (GDPR violation)
- Accessible (WCAG compliant)

**Catégories de cookies:**
```
□ Strictement nécessaires (toujours actifs - pas de consentement requis)
  - Session cookies
  - Security tokens
  - Load balancing

□ Fonctionnels (consentement requis)
  - Préférences utilisateur
  - Language selection

□ Analytics (consentement requis)
  - Google Analytics
  - Mixpanel
  - Hotjar

□ Marketing (consentement requis)
  - Facebook Pixel
  - Google Ads
  - Retargeting
```

**Implementation:**
```javascript
// Pseudo-code
if (!hasConsent('analytics')) {{
  // Ne pas charger GA
}}

if (userAcceptsAnalytics()) {{
  loadGoogleAnalytics();
  saveConsent('analytics', true, expiryDate);
}}
```

**2. Email Marketing Consent**

**À l'inscription:**
```
□ J'accepte de recevoir des emails marketing
  (Case à cocher, non pré-cochée)

  "Vous pouvez vous désabonner à tout moment via le lien
   dans chaque email."
```

**Double opt-in recommandé:**
1. User s'inscrit
2. Email de confirmation envoyé
3. User clique pour confirmer
4. Consentement validé

**3. Data Processing Consent (GDPR)**

Pour certaines activités:
```
"En créant un compte, vous acceptez notre Privacy Policy
 et nos Terms of Service."

[Lien Privacy Policy] [Lien ToS]
```

**Consent doit être:**
- ✅ **Freely given**: Pas de bundled consent (ne pas conditionner service à consentement non nécessaire)
- ✅ **Specific**: Par finalité (ne pas demander consentement générique)
- ✅ **Informed**: User comprend ce à quoi il consent
- ✅ **Unambiguous**: Action claire (clic, case cochée)
- ✅ **Withdrawable**: Aussi facile de retirer que de donner

**4. Consent Records**

Documenter dans la DB:
```sql
CREATE TABLE consent_records (
  user_id UUID,
  consent_type VARCHAR(50), -- 'marketing', 'analytics', 'cookies'
  granted BOOLEAN,
  timestamp TIMESTAMPTZ,
  ip_address INET,
  user_agent TEXT,
  consent_version VARCHAR(10) -- version de la privacy policy
);
```

**5. Consent Refresh**

Quand refresh le consentement?
- Changement majeur de Privacy Policy
- Nouvelles finalités de traitement
- Nouvelles third parties
- Tous les 12-24 mois (bonne pratique)

**6. UI/UX pour gérer le consentement**

**Dans les settings utilisateur:**
```
Préférences de confidentialité
├── Cookies
│   ├── Strictement nécessaires [Always On]
│   ├── Analytics [Toggle]
│   └── Marketing [Toggle]
├── Emails
│   ├── Notifications produit [Toggle]
│   ├── Marketing [Toggle]
│   └── Newsletter [Toggle]
└── Partage de données
    └── Amélioration du produit [Toggle]
```

**IMPLEMENTATION CHECKLIST:**
□ Cookie banner implémenté avec consentement granulaire
□ Scripts tiers chargés uniquement après consentement
□ Consentement email avec double opt-in
□ Records de consentement stockés
□ Interface pour retirer/modifier le consentement
□ Respect du consentement à travers tous les systèmes"""

    def _build_rights_prompt(self, context: str, jurisdictions: List[str]) -> str:
        """Construit le prompt pour implémenter les droits des utilisateurs."""
        juris_list = ", ".join(jurisdictions)

        return f"""Implémente les droits des utilisateurs (Data Subject Rights) pour:

CONTEXTE:
{context}

JURIDICTIONS:
{juris_list}

**DATA SUBJECT RIGHTS IMPLEMENTATION:**

**1. Right to Access (Droit d'accès)**

User peut demander:
- Quelles données sont collectées?
- Comment utilisées?
- Avec qui partagées?
- Combien de temps conservées?

**Implementation:**
- Formulaire dans les settings: "Télécharger mes données"
- Générer export JSON/CSV de toutes les données user
- Délai: Maximum 30 jours (GDPR)
- Format: Machine-readable

**Exemple d'export:**
```json
{
  "user_profile": {
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-01"
  },
  "usage_data": [...],
  "consent_records": [...],
  "payment_history": [...]
}
```

**2. Right to Rectification (Droit de rectification)**

User peut corriger données incorrectes.

**Implementation:**
- Interface pour modifier profil
- Vérification email si changement d'email
- Log des modifications (audit trail)

**3. Right to Erasure / "Right to be Forgotten" (Droit à l'effacement)**

User peut demander suppression de ses données.

**Implementation:**
```
Settings → Supprimer mon compte
  ↓
Confirmation (avec avertissement des conséquences)
  ↓
Soft delete (anonymisation) vs Hard delete
  ↓
Confirmation par email
  ↓
Données supprimées sous 30 jours
```

**Exceptions** (données conservées):
- Obligations légales (comptabilité: 10 ans)
- Litiges en cours
- Consentement spécifique pour conservation

**Pseudonymisation alternative:**
- Anonymiser au lieu de supprimer
- Remplacer PII par UUID
- Garder usage data anonymisé pour analytics

**4. Right to Data Portability (Droit à la portabilité)**

User peut récupérer données dans format réutilisable.

**Implementation:**
- Export en JSON (machine-readable)
- Export en CSV (human-readable)
- Inclure toutes les données fournies par le user

**5. Right to Object (Droit d'opposition)**

User peut s'opposer à certains traitements.

**Implementation:**
- Opt-out marketing emails (unsubscribe)
- Opt-out analytics/tracking
- Opt-out profiling

**6. Right to Restriction (Droit à la limitation)**

User peut demander limitation du traitement (pause).

**Use cases:**
- Contestation de l'exactitude des données
- Traitement illicite mais user ne veut pas effacement
- Opposition au traitement

**Implementation:**
- Flag `processing_restricted` dans la DB
- Bloquer traitements non essentiels

**PROCESS WORKFLOW:**

**Request received** (email, formulaire)
  ↓
**Verify identity** (authentification, preuve d'identité si sensible)
  ↓
**Assess request** (quel droit? exceptions applicables?)
  ↓
**Execute** (accès, rectification, effacement, etc.)
  ↓
**Respond** (< 30 jours, confirmation + détails)
  ↓
**Log** (traçabilité pour audit)

**AUTOMATION:**

Automatiser quand possible:
- Accès: Self-service export
- Rectification: Self-service edit
- Effacement: Self-service delete avec confirmation

Requérir intervention manuelle pour:
- Cas complexes
- Litiges
- Vérification d'identité douteuse

**SLA (Service Level Agreement):**
- Réponse initiale: 48-72h
- Exécution complète: < 30 jours (GDPR max)
- Target interne: 7-14 jours

**TEAM RESPONSIBLE:**
- DPO ou Privacy contact
- Support team (first line)
- Engineering (pour exécution technique)

**METRICS TO TRACK:**
- Nombre de requests par type
- Temps de réponse moyen
- % automatisées vs manuelles
- Satisfaction utilisateur"""

    def _build_dpia_prompt(self, context: str, data_types: List[str]) -> str:
        """Construit le prompt pour une DPIA (Data Protection Impact Assessment)."""
        data_list = ", ".join(data_types) if data_types else "Non spécifié"

        return f"""Effectue une DPIA (Data Protection Impact Assessment) pour:

CONTEXTE:
{context}

DONNÉES TRAITÉES:
{data_list}

**DPIA (GDPR Article 35):**

Une DPIA est **obligatoire** si:
- Traitement automatisé avec effets juridiques (scoring, profiling)
- Traitement à grande échelle de données sensibles (Article 9)
- Surveillance systématique à grande échelle
- Technologies nouvelles avec risques élevés

**DPIA FRAMEWORK:**

**1. Description du Traitement**
- Nature du traitement
- Finalité
- Volume de données
- Nombre de personnes concernées
- Durée de conservation
- Qui a accès?

**2. Necessity & Proportionality**
- Le traitement est-il nécessaire?
- Existe-t-il des alternatives moins intrusives?
- Les données collectées sont-elles minimales?
- La durée de conservation est-elle justifiée?

**3. Risks pour les Personnes**

Pour chaque risque, évaluer:
- **Likelihood** (Probabilité): Low / Medium / High
- **Severity** (Gravité): Low / Medium / High
- **Risk Level** = Likelihood × Severity

**Risques types:**

**Risque 1: Data Breach (Violation de données)**
- Likelihood: ?
- Severity: ?
- Impact: Exposition de données personnelles, usurpation d'identité
- Mesures existantes: Encryption, access controls, monitoring
- Mesures additionnelles nécessaires: ?

**Risque 2: Unauthorized Access (Accès non autorisé)**
- Likelihood: ?
- Severity: ?
- Impact: Accès par employés non autorisés ou tiers
- Mesures: RBAC, audit logs, 2FA
- Gaps: ?

**Risque 3: Function Creep (Dérive de finalité)**
- Likelihood: ?
- Severity: ?
- Impact: Données utilisées pour autre finalité que prévue
- Mesures: Policies claires, training, audits réguliers

**Risque 4: Re-identification (Dé-anonymisation)**
- Likelihood: ?
- Severity: ?
- Impact: Données "anonymes" peuvent être ré-identifiées
- Mesures: K-anonymity, differential privacy

**Risque 5: Vendor Risk (Sous-traitants)**
- Likelihood: ?
- Severity: ?
- Impact: Breach chez un vendor
- Mesures: DPAs, vendor assessments, SOC 2 requirements

**Risque 6: Transfer Risk (Transferts internationaux)**
- Likelihood: ?
- Severity: ?
- Impact: Données transférées vers juridictions sans protection adéquate
- Mesures: SCCs, adequacy decisions, data localization

**4. Mitigation Measures (Mesures de mitigation)**

Pour chaque risque HIGH ou CRITICAL:
- Quelle mesure technique/organisationnelle?
- Coût estimated?
- Timeline d'implémentation?
- Risque résiduel après mitigation?

**5. Consultation**

- DPO consulté? (obligatoire si désigné)
- Data subjects consultés? (recommandé si risque élevé)
- Autorité de contrôle consultée? (si risque résiduel élevé après mitigation)

**6. Approval & Review**

- Qui approuve la DPIA? (DPO, Legal, Management)
- Date d'approbation
- Prochaine revue (recommandé: annuelle ou si changement majeur)

**DPIA CONCLUSION:**

**Risk Matrix:**
```
         Likelihood
         Low    Med    High
Severity
High    [MED]  [HIGH] [CRIT]
Med     [LOW]  [MED]  [HIGH]
Low     [LOW]  [LOW]  [MED]
```

**Overall Risk Assessment:** LOW / MEDIUM / HIGH / CRITICAL

**Decision:**
□ Proceed with processing (risques acceptables)
□ Proceed with additional measures (mitigation requise)
□ Do not proceed (risques trop élevés)
□ Consult supervisory authority (CNIL, ICO, etc.)

**Action Plan:**
1. [Action prioritaire 1] - Deadline: [date]
2. [Action 2] - Deadline: [date]
...

**DOCUMENTATION:**
- Sauvegarder la DPIA complète
- Mettre à jour si changements
- Disponible pour audit par autorité de contrôle"""

    def _extract_risk_level(self, response: str) -> str:
        """Extrait le niveau de risque de la réponse."""
        response_lower = response.lower()
        if "critical" in response_lower or "critique" in response_lower:
            return "critical"
        elif "high" in response_lower or "élevé" in response_lower or "haut" in response_lower:
            return "high"
        elif "medium" in response_lower or "moyen" in response_lower:
            return "medium"
        else:
            return "low"

    async def audit_compliance(
        self,
        product_context: str,
        data_types: List[str],
        jurisdictions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Méthode helper pour auditer la conformité.

        Args:
            product_context (str): Description du produit
            data_types (List[str]): Types de données collectées
            jurisdictions (List[str]): Juridictions applicables

        Returns:
            Dict: Résultat de l'audit avec niveau de risque
        """
        return await self.execute({
            "task_type": "audit",
            "context": product_context,
            "data_types": data_types,
            "jurisdictions": jurisdictions or list(self.regulations)
        })

    async def generate_privacy_policy(
        self,
        product_context: str,
        data_types: List[str],
        jurisdictions: List[str] = None
    ) -> str:
        """
        Méthode helper pour générer une privacy policy.

        Args:
            product_context (str): Description du produit
            data_types (List[str]): Types de données collectées
            jurisdictions (List[str]): Juridictions applicables

        Returns:
            str: Privacy policy complète
        """
        result = await self.execute({
            "task_type": "policy",
            "context": product_context,
            "data_types": data_types,
            "jurisdictions": jurisdictions or list(self.regulations)
        })
        return result["output"]

    async def map_data_flows(self, product_context: str, data_types: List[str]) -> str:
        """
        Méthode helper pour mapper les flux de données.

        Args:
            product_context (str): Description du système
            data_types (List[str]): Types de données

        Returns:
            str: Cartographie des données
        """
        result = await self.execute({
            "task_type": "data_mapping",
            "context": product_context,
            "data_types": data_types
        })
        return result["output"]

    async def design_consent_mechanism(self, product_context: str, data_types: List[str]) -> str:
        """
        Méthode helper pour designer le mécanisme de consentement.

        Args:
            product_context (str): Description du produit
            data_types (List[str]): Données nécessitant consentement

        Returns:
            str: Spécifications du consent management
        """
        result = await self.execute({
            "task_type": "consent",
            "context": product_context,
            "data_types": data_types
        })
        return result["output"]

    async def implement_user_rights(self, product_context: str, jurisdictions: List[str] = None) -> str:
        """
        Méthode helper pour implémenter les droits utilisateurs.

        Args:
            product_context (str): Description du produit
            jurisdictions (List[str]): Juridictions applicables

        Returns:
            str: Guide d'implémentation des droits
        """
        result = await self.execute({
            "task_type": "rights",
            "context": product_context,
            "jurisdictions": jurisdictions or list(self.regulations)
        })
        return result["output"]

    async def conduct_dpia(self, product_context: str, data_types: List[str]) -> Dict[str, Any]:
        """
        Méthode helper pour conduire une DPIA.

        Args:
            product_context (str): Description du traitement
            data_types (List[str]): Types de données traitées

        Returns:
            Dict: DPIA complète avec niveau de risque
        """
        return await self.execute({
            "task_type": "dpia",
            "context": product_context,
            "data_types": data_types
        })

    def add_regulation(self, regulation: str):
        """Ajoute une réglementation au scope."""
        self.regulations.add(regulation.upper())

    def remove_regulation(self, regulation: str):
        """Retire une réglementation du scope."""
        self.regulations.discard(regulation.upper())
