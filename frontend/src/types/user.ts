/**
 * User Types
 * Types related to user management, authentication, and subscriptions
 */

/**
 * Subscription status values from Stripe
 */
export type SubscriptionStatus =
  | 'inactive'      // No subscription
  | 'active'        // Active paid subscription
  | 'trialing'      // In trial period
  | 'canceled'      // Subscription canceled but still active until period end
  | 'past_due'      // Payment failed, grace period
  | 'unpaid'        // Payment failed, subscription suspended
  | 'incomplete'    // Initial payment pending
  | 'incomplete_expired'; // Initial payment failed

/**
 * Subscription tier/plan names
 */
export type SubscriptionTier = 'free' | 'starter' | 'pro' | 'enterprise';

/**
 * User role in the system
 */
export type UserRole = 'user' | 'admin' | 'super_admin';

/**
 * Full user entity as stored in the database
 */
export interface User {
  /** Unique user identifier (UUID) */
  id: string;
  /** User email address (unique) */
  email: string;
  /** User's full name */
  full_name?: string;
  /** Profile avatar URL */
  avatar_url?: string;
  /** Whether the account is active */
  is_active: boolean;
  /** Whether the user has admin privileges */
  is_admin: boolean;
  /** User role */
  role?: UserRole;
  /** Current subscription status */
  subscription_status: SubscriptionStatus;
  /** Current subscription tier */
  subscription_tier?: SubscriptionTier;
  /** Stripe customer ID */
  stripe_customer_id?: string;
  /** End of current billing period (ISO 8601) */
  current_period_end?: string;
  /** Account creation timestamp */
  created_at: string;
  /** Last profile update timestamp */
  updated_at?: string;
  /** Last login timestamp */
  last_login_at?: string;
  /** User preferences */
  preferences?: UserPreferences;
}

/**
 * User preferences for UI and behavior customization
 */
export interface UserPreferences {
  /** UI theme preference */
  theme?: 'light' | 'dark' | 'system';
  /** Preferred language/locale */
  locale?: string;
  /** Editor preferences */
  editor?: EditorPreferences;
  /** Notification preferences */
  notifications?: NotificationPreferences;
}

/**
 * Code editor preferences
 */
export interface EditorPreferences {
  /** Font size in pixels */
  fontSize?: number;
  /** Tab size in spaces */
  tabSize?: number;
  /** Use tabs instead of spaces */
  useTabs?: boolean;
  /** Enable word wrap */
  wordWrap?: boolean;
  /** Show line numbers */
  lineNumbers?: boolean;
  /** Enable minimap */
  minimap?: boolean;
  /** Editor theme name */
  theme?: string;
}

/**
 * Notification preferences
 */
export interface NotificationPreferences {
  /** Email notifications enabled */
  email?: boolean;
  /** Browser push notifications enabled */
  push?: boolean;
  /** In-app notifications enabled */
  inApp?: boolean;
  /** Marketing emails enabled */
  marketing?: boolean;
}

/**
 * Authentication state for the application
 */
export interface AuthState {
  /** Currently authenticated user or null */
  user: User | null;
  /** Whether auth state is being loaded */
  loading: boolean;
  /** Authentication error message if any */
  error: string | null;
  /** Whether the user is authenticated */
  isAuthenticated: boolean;
  /** Session expiry timestamp */
  sessionExpiresAt?: string;
}

/**
 * Login credentials
 */
export interface LoginCredentials {
  email: string;
  password: string;
  /** Remember me for extended session */
  rememberMe?: boolean;
}

/**
 * Registration data
 */
export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
  /** Accept terms of service */
  acceptTerms: boolean;
}

/**
 * Password reset request
 */
export interface PasswordResetRequest {
  email: string;
}

/**
 * Password reset confirmation
 */
export interface PasswordResetConfirm {
  token: string;
  newPassword: string;
}

/**
 * Profile update data
 */
export interface ProfileUpdate {
  full_name?: string;
  avatar_url?: string;
  preferences?: Partial<UserPreferences>;
}

/**
 * Change password data
 */
export interface ChangePassword {
  currentPassword: string;
  newPassword: string;
}

/**
 * User session information
 */
export interface UserSession {
  /** Session ID */
  id: string;
  /** Access token */
  access_token: string;
  /** Refresh token */
  refresh_token?: string;
  /** Token type (usually "Bearer") */
  token_type: string;
  /** Seconds until token expires */
  expires_in: number;
  /** Token expiry timestamp */
  expires_at: string;
  /** User data */
  user: User;
}

/**
 * OAuth provider types
 */
export type OAuthProvider = 'google' | 'github' | 'discord';

/**
 * OAuth login request
 */
export interface OAuthLoginRequest {
  provider: OAuthProvider;
  /** Redirect URL after OAuth */
  redirectUrl?: string;
}

/**
 * Usage limits based on subscription
 */
export interface UsageLimits {
  /** Maximum projects allowed */
  maxProjects: number;
  /** Maximum files per project */
  maxFilesPerProject: number;
  /** Maximum generations per month */
  maxGenerationsPerMonth: number;
  /** Current generation count this month */
  currentGenerations: number;
  /** Maximum file size in bytes */
  maxFileSize: number;
  /** Access to premium features */
  premiumFeatures: boolean;
}

/**
 * Subscription tier limits configuration
 */
export const TIER_LIMITS: Record<SubscriptionTier, UsageLimits> = {
  free: {
    maxProjects: 3,
    maxFilesPerProject: 10,
    maxGenerationsPerMonth: 50,
    currentGenerations: 0,
    maxFileSize: 1024 * 1024, // 1MB
    premiumFeatures: false,
  },
  starter: {
    maxProjects: 10,
    maxFilesPerProject: 50,
    maxGenerationsPerMonth: 500,
    currentGenerations: 0,
    maxFileSize: 5 * 1024 * 1024, // 5MB
    premiumFeatures: false,
  },
  pro: {
    maxProjects: 100,
    maxFilesPerProject: 200,
    maxGenerationsPerMonth: 5000,
    currentGenerations: 0,
    maxFileSize: 20 * 1024 * 1024, // 20MB
    premiumFeatures: true,
  },
  enterprise: {
    maxProjects: Infinity,
    maxFilesPerProject: Infinity,
    maxGenerationsPerMonth: Infinity,
    currentGenerations: 0,
    maxFileSize: 100 * 1024 * 1024, // 100MB
    premiumFeatures: true,
  },
};

/**
 * Helper function to check if user has active subscription
 */
export function hasActiveSubscription(user: User): boolean {
  return ['active', 'trialing'].includes(user.subscription_status);
}

/**
 * Helper function to check if user can perform action based on limits
 */
export function canPerformAction(
  user: User,
  limits: UsageLimits,
  action: 'create_project' | 'generate' | 'add_file'
): boolean {
  if (!user.is_active) return false;

  switch (action) {
    case 'generate':
      return limits.currentGenerations < limits.maxGenerationsPerMonth;
    default:
      return true;
  }
}
