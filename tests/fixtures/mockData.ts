/**
 * Fixtures et mock data pour les tests
 */

export const mockUser = {
  id: 'user-123',
  email: 'test@devora.test',
  name: 'Test User',
  role: 'user',
  subscriptionStatus: 'active',
  subscriptionPlan: 'pro',
  createdAt: '2024-01-01T00:00:00.000Z',
};

export const mockAdminUser = {
  id: 'admin-123',
  email: 'admin@devora.test',
  name: 'Admin User',
  role: 'admin',
  subscriptionStatus: 'active',
  subscriptionPlan: 'enterprise',
  createdAt: '2024-01-01T00:00:00.000Z',
};

export const mockProject = {
  id: 'project-123',
  userId: 'user-123',
  name: 'Test Project',
  description: 'A test project',
  code: {
    'index.html': '<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hello World</h1></body></html>',
    'styles.css': 'body { margin: 0; padding: 0; }',
    'script.js': 'console.log("Hello from test");',
  },
  template: 'blank',
  createdAt: '2024-01-15T10:00:00.000Z',
  updatedAt: '2024-01-15T12:00:00.000Z',
};

export const mockProjects = [
  mockProject,
  {
    id: 'project-456',
    userId: 'user-123',
    name: 'Second Project',
    description: 'Another test project',
    code: {
      'index.html': '<h1>Project 2</h1>',
    },
    template: 'landing-page',
    createdAt: '2024-01-16T10:00:00.000Z',
    updatedAt: '2024-01-16T10:00:00.000Z',
  },
];

export const mockSubscription = {
  id: 'sub-123',
  userId: 'user-123',
  status: 'active',
  plan: 'pro',
  currentPeriodStart: '2024-01-01T00:00:00.000Z',
  currentPeriodEnd: '2024-02-01T00:00:00.000Z',
  cancelAtPeriodEnd: false,
  trialEnd: null,
  amount: 2900, // in cents
  currency: 'eur',
  interval: 'month',
};

export const mockInvoices = [
  {
    id: 'inv-123',
    userId: 'user-123',
    subscriptionId: 'sub-123',
    amount: 2900,
    currency: 'eur',
    status: 'paid',
    paidAt: '2024-01-01T00:00:00.000Z',
    invoicePdf: 'https://stripe.com/invoices/inv-123.pdf',
    createdAt: '2024-01-01T00:00:00.000Z',
  },
  {
    id: 'inv-456',
    userId: 'user-123',
    subscriptionId: 'sub-123',
    amount: 2900,
    currency: 'eur',
    status: 'paid',
    paidAt: '2024-02-01T00:00:00.000Z',
    invoicePdf: 'https://stripe.com/invoices/inv-456.pdf',
    createdAt: '2024-02-01T00:00:00.000Z',
  },
];

export const mockDeployment = {
  id: 'deploy-123',
  projectId: 'project-123',
  userId: 'user-123',
  platform: 'vercel',
  status: 'deployed',
  url: 'https://test-project-abc123.vercel.app',
  deploymentUrl: 'https://vercel.com/deployments/deploy-123',
  branch: 'main',
  commitHash: 'abc123def456',
  commitMessage: 'Initial deployment',
  buildLogs: 'Building project...\nBuild successful!',
  createdAt: '2024-01-15T14:00:00.000Z',
  completedAt: '2024-01-15T14:05:00.000Z',
};

export const mockGitHubRepo = {
  id: 'repo-123',
  name: 'test-project',
  fullName: 'testuser/test-project',
  owner: 'testuser',
  htmlUrl: 'https://github.com/testuser/test-project',
  private: false,
  createdAt: '2024-01-15T13:00:00.000Z',
};

export const mockAIGeneration = {
  id: 'gen-123',
  projectId: 'project-123',
  userId: 'user-123',
  prompt: 'Create a modern landing page with hero section',
  generatedCode: {
    'index.html': '<!DOCTYPE html><html>...</html>',
    'styles.css': 'body { ... }',
  },
  model: 'gpt-4',
  tokensUsed: 1500,
  status: 'completed',
  createdAt: '2024-01-15T11:00:00.000Z',
  completedAt: '2024-01-15T11:00:15.000Z',
};

export const mockPlans = [
  {
    id: 'plan-starter',
    name: 'Starter',
    price: 900, // €9
    currency: 'eur',
    interval: 'month',
    features: [
      '5 projets',
      '10 générations IA par mois',
      'Support email',
      'Export ZIP',
    ],
    limits: {
      projects: 5,
      aiGenerations: 10,
      storage: 100, // MB
    },
  },
  {
    id: 'plan-pro',
    name: 'Pro',
    price: 2900, // €29
    currency: 'eur',
    interval: 'month',
    features: [
      'Projets illimités',
      'Générations IA illimitées',
      'Déploiement automatique',
      'Support prioritaire',
      'Domaines personnalisés',
    ],
    limits: {
      projects: -1, // unlimited
      aiGenerations: -1,
      storage: 1000, // MB
    },
    recommended: true,
  },
  {
    id: 'plan-enterprise',
    name: 'Enterprise',
    price: 9900, // €99
    currency: 'eur',
    interval: 'month',
    features: [
      'Tout du plan Pro',
      'Équipes multiples',
      'SSO / SAML',
      'Support dédié 24/7',
      'SLA garantie',
      'Audit logs',
    ],
    limits: {
      projects: -1,
      aiGenerations: -1,
      storage: -1,
      teamMembers: 50,
    },
  },
];

export const mockTemplates = [
  {
    id: 'template-blank',
    name: 'Blank',
    description: 'Start from scratch',
    thumbnail: '/templates/blank.png',
    code: {
      'index.html': '<!DOCTYPE html><html><head></head><body></body></html>',
    },
  },
  {
    id: 'template-landing',
    name: 'Landing Page',
    description: 'Modern landing page template',
    thumbnail: '/templates/landing.png',
    code: {
      'index.html': '<!DOCTYPE html>...',
      'styles.css': '/* Landing page styles */',
    },
  },
  {
    id: 'template-dashboard',
    name: 'Dashboard',
    description: 'Admin dashboard template',
    thumbnail: '/templates/dashboard.png',
    code: {
      'index.html': '<!DOCTYPE html>...',
      'styles.css': '/* Dashboard styles */',
      'script.js': '// Dashboard logic',
    },
  },
];

export const mockAuthTokens = {
  accessToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsImVtYWlsIjoidGVzdEBkZXZvcmEudGVzdCIsImlhdCI6MTYxNjIzOTAyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
  refreshToken: 'refresh-token-abc123',
};

export const mockErrorResponses = {
  unauthorized: {
    status: 401,
    data: {
      error: 'Unauthorized',
      message: 'Invalid or expired token',
    },
  },
  forbidden: {
    status: 403,
    data: {
      error: 'Forbidden',
      message: 'You do not have permission to access this resource',
    },
  },
  notFound: {
    status: 404,
    data: {
      error: 'Not Found',
      message: 'The requested resource was not found',
    },
  },
  validationError: {
    status: 400,
    data: {
      error: 'Validation Error',
      message: 'Invalid input',
      fields: {
        email: 'Invalid email format',
        password: 'Password must be at least 8 characters',
      },
    },
  },
  serverError: {
    status: 500,
    data: {
      error: 'Internal Server Error',
      message: 'An unexpected error occurred',
    },
  },
};

export const mockWebhookEvents = {
  subscriptionCreated: {
    type: 'customer.subscription.created',
    data: {
      object: {
        id: 'sub-123',
        customer: 'cus-123',
        status: 'active',
        items: {
          data: [
            {
              price: {
                id: 'price-pro',
                product: 'prod-pro',
              },
            },
          ],
        },
      },
    },
  },
  paymentSucceeded: {
    type: 'invoice.payment_succeeded',
    data: {
      object: {
        id: 'in-123',
        customer: 'cus-123',
        subscription: 'sub-123',
        amount_paid: 2900,
        status: 'paid',
      },
    },
  },
  subscriptionCanceled: {
    type: 'customer.subscription.deleted',
    data: {
      object: {
        id: 'sub-123',
        customer: 'cus-123',
        status: 'canceled',
      },
    },
  },
};
