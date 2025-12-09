# Data Processing Agreement (DPA)
## Devora - Enterprise Customers

**Version:** 1.0
**Last Updated:** December 9, 2025
**Effective Date:** Upon Execution

---

## PARTIES

**Data Controller ("Customer"):**
- Company Name: ___________________________
- Address: ___________________________
- Contact: ___________________________
- Email: ___________________________

**Data Processor ("Devora"):**
- Company Name: Devora SAS
- Address: Paris, France
- Contact: Data Protection Officer
- Email: dpo@devora.io

---

## SCOPE OF PROCESSING

**Purpose:** AI code generation, project storage, user authentication, billing, customer support

**Types of Personal Data:**
- Identity Data (name, email, username)
- Account Data (password encrypted, profile photo)
- Usage Data (prompts, generated code, projects)
- Billing Data (billing address, VAT ID)

---

## SECURITY MEASURES

- **Encryption:** TLS 1.3 (in transit), AES-256 (at rest)
- **Access Controls:** RBAC, 2FA for admins
- **Infrastructure:** Vercel (SOC 2), Supabase (ISO 27001)
- **Audits:** Annual penetration testing

---

## SUB-PROCESSORS

| Sub-processor | Purpose | Location |
|---------------|---------|----------|
| Supabase | Database hosting | EU (Germany) |
| Stripe | Payment processing | US (SCC signed) |
| OpenAI | AI code generation | US (DPA signed) |
| Vercel | Hosting, CDN | US (SCC signed) |
| Resend | Email delivery | US (DPA signed) |
| PostHog | Analytics (self-hosted) | EU |

---

## DATA SUBJECT RIGHTS

Self-service tools available at Settings > Privacy:
- Export My Data (Access, Portability)
- Edit Profile (Rectification)
- Delete My Account (Erasure)

**Response Time:** 7 business days

---

## DATA BREACH NOTIFICATION

Devora will notify Customer within **72 hours** of becoming aware of a Personal Data breach.

---

## SIGNATURES

**CUSTOMER:** ___________________________

**DEVORA SAS:** ___________________________

---

**For questions, contact dpo@devora.io.**

**Devora SAS - GDPR-compliant by design.**
