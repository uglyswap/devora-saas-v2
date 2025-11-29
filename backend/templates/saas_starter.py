"""SaaS Starter Template - Complete full-stack SaaS application.

Features:
- Authentication (Supabase Auth)
- Billing (Stripe subscriptions)
- Dashboard
- Settings
- Landing page
- User profiles
"""

SAAS_STARTER_TEMPLATE = {
    "name": "SaaS Starter",
    "description": "Complete SaaS application with auth, billing, and dashboard",
    "version": "1.0.0",
    
    "stack": {
        "frontend": ["next.js", "react", "tailwind", "shadcn/ui"],
        "backend": ["next.js-api-routes", "server-actions"],
        "database": ["supabase", "postgresql"],
        "auth": ["supabase-auth"],
        "payments": ["stripe"]
    },
    
    "features": [
        {
            "name": "authentication",
            "description": "Email/password and OAuth authentication",
            "pages": ["/login", "/register", "/forgot-password"],
            "components": ["LoginForm", "RegisterForm", "AuthProvider"]
        },
        {
            "name": "billing",
            "description": "Stripe subscription management",
            "pages": ["/pricing", "/settings/billing"],
            "components": ["PricingTable", "BillingPortal", "SubscriptionStatus"]
        },
        {
            "name": "dashboard",
            "description": "User dashboard with metrics",
            "pages": ["/dashboard"],
            "components": ["DashboardLayout", "MetricsCard", "RecentActivity"]
        },
        {
            "name": "settings",
            "description": "User settings and preferences",
            "pages": ["/settings", "/settings/profile", "/settings/billing"],
            "components": ["SettingsLayout", "ProfileForm", "NotificationSettings"]
        },
        {
            "name": "landing",
            "description": "Marketing landing page",
            "pages": ["/"],
            "components": ["Hero", "Features", "Testimonials", "CTA", "Footer"]
        }
    ],
    
    "data_models": [
        {
            "name": "users",
            "description": "Extended user profiles",
            "fields": [
                "id uuid primary key references auth.users",
                "email text unique not null",
                "full_name text",
                "avatar_url text",
                "created_at timestamp with time zone default now()",
                "updated_at timestamp with time zone default now()"
            ]
        },
        {
            "name": "subscriptions",
            "description": "Stripe subscription data",
            "fields": [
                "id uuid primary key default gen_random_uuid()",
                "user_id uuid references users(id) unique",
                "stripe_customer_id text unique",
                "stripe_subscription_id text unique",
                "status text default 'inactive'",
                "plan text default 'free'",
                "current_period_end timestamp with time zone"
            ]
        }
    ],
    
    "api_routes": [
        {
            "path": "/api/auth/callback",
            "methods": ["GET"],
            "description": "Supabase auth callback"
        },
        {
            "path": "/api/user",
            "methods": ["GET", "PUT"],
            "description": "User profile CRUD"
        },
        {
            "path": "/api/stripe/webhook",
            "methods": ["POST"],
            "description": "Stripe webhook handler"
        },
        {
            "path": "/api/stripe/checkout",
            "methods": ["POST"],
            "description": "Create Stripe checkout session"
        },
        {
            "path": "/api/stripe/portal",
            "methods": ["POST"],
            "description": "Create Stripe customer portal"
        }
    ],
    
    "file_structure": {
        "app": {
            "(auth)": {
                "login": ["page.tsx"],
                "register": ["page.tsx"],
                "forgot-password": ["page.tsx"],
                "layout.tsx": True
            },
            "(dashboard)": {
                "dashboard": ["page.tsx"],
                "settings": {
                    "page.tsx": True,
                    "profile": ["page.tsx"],
                    "billing": ["page.tsx"]
                },
                "layout.tsx": True
            },
            "api": {
                "auth": {
                    "callback": ["route.ts"]
                },
                "user": ["route.ts"],
                "stripe": {
                    "webhook": ["route.ts"],
                    "checkout": ["route.ts"],
                    "portal": ["route.ts"]
                }
            },
            "layout.tsx": True,
            "page.tsx": True,
            "globals.css": True
        },
        "components": {
            "ui": ["button.tsx", "input.tsx", "card.tsx", "dialog.tsx"],
            "auth": ["login-form.tsx", "register-form.tsx"],
            "dashboard": ["sidebar.tsx", "header.tsx", "metrics-card.tsx"],
            "landing": ["hero.tsx", "features.tsx", "pricing.tsx", "footer.tsx"],
            "billing": ["pricing-table.tsx", "subscription-status.tsx"]
        },
        "lib": {
            "supabase": ["client.ts", "server.ts", "middleware.ts"],
            "stripe.ts": True,
            "utils.ts": True
        },
        "types": ["index.ts", "database.ts"]
    },
    
    "base_files": [
        {
            "path": "middleware.ts",
            "description": "Next.js middleware for auth protection",
            "content": '''import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({
            request,
          })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  const {
    data: { user },
  } = await supabase.auth.getUser()

  // Protected routes
  if (
    !user &&
    (request.nextUrl.pathname.startsWith('/dashboard') ||
      request.nextUrl.pathname.startsWith('/settings'))
  ) {
    const url = request.nextUrl.clone()
    url.pathname = '/login'
    return NextResponse.redirect(url)
  }

  return supabaseResponse
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
'''
        },
        {
            "path": "lib/supabase/client.ts",
            "description": "Supabase browser client",
            "content": '''import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
'''
        },
        {
            "path": "lib/supabase/server.ts",
            "description": "Supabase server client",
            "content": '''import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export function createClient() {
  const cookieStore = cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // The `setAll` method was called from a Server Component.
          }
        },
      },
    }
  )
}
'''
        },
        {
            "path": "lib/stripe.ts",
            "description": "Stripe client setup",
            "content": '''import Stripe from 'stripe'

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
  typescript: true,
})
'''
        },
        {
            "path": "lib/utils.ts",
            "description": "Utility functions",
            "content": '''import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: Date | string) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(date))
}

export function absoluteUrl(path: string) {
  return `${process.env.NEXT_PUBLIC_APP_URL}${path}`
}
'''
        }
    ]
}
