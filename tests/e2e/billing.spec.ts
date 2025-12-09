import { test, expect, Page } from '@playwright/test';

/**
 * Tests E2E pour le flux de facturation Stripe
 * Couvre: Subscription, Payment, Upgrade/Downgrade, Billing portal
 */

async function loginAsUser(page: Page) {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'test@devora.test');
  await page.fill('input[name="password"]', 'TestPassword123!');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard');
}

test.describe('Stripe Billing Flow', () => {
  test.describe('Subscription Plans', () => {
    test('should display available subscription plans', async ({ page }) => {
      await page.goto('/billing');

      // Should show plan options
      await expect(page.locator('[data-testid="plan-starter"]')).toBeVisible();
      await expect(page.locator('[data-testid="plan-pro"]')).toBeVisible();
      await expect(page.locator('[data-testid="plan-enterprise"]')).toBeVisible();
    });

    test('should show plan features and pricing', async ({ page }) => {
      await page.goto('/billing');

      // Starter plan
      const starterPlan = page.locator('[data-testid="plan-starter"]');
      await expect(starterPlan.locator('text=/€/i')).toBeVisible();
      await expect(starterPlan.locator('text=/projets/i')).toBeVisible();

      // Pro plan
      const proPlan = page.locator('[data-testid="plan-pro"]');
      await expect(proPlan.locator('text=/€/i')).toBeVisible();
      await expect(proPlan.locator('text=/illimité/i')).toBeVisible();
    });

    test('should highlight recommended plan', async ({ page }) => {
      await page.goto('/billing');

      // Pro plan should be highlighted as recommended
      const proPlan = page.locator('[data-testid="plan-pro"]');
      await expect(proPlan.locator('text=/recommandé/i')).toBeVisible();
    });

    test('should toggle between monthly and yearly billing', async ({ page }) => {
      await page.goto('/billing');

      // Default to monthly
      await expect(page.locator('[data-testid="price-monthly"]')).toBeVisible();

      // Switch to yearly
      await page.click('[data-testid="toggle-yearly"]');

      await expect(page.locator('[data-testid="price-yearly"]')).toBeVisible();
      await expect(page.locator('text=/économisez/i')).toBeVisible(); // Savings badge
    });
  });

  test.describe('Checkout Process', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsUser(page);
    });

    test('should redirect to Stripe Checkout for new subscription', async ({ page }) => {
      await page.goto('/billing');

      // Click subscribe on Pro plan
      await page.click('[data-testid="plan-pro"] button:has-text("S\'abonner")');

      // Should redirect to Stripe Checkout
      await page.waitForURL(/checkout\.stripe\.com/);

      // Verify Stripe Checkout page elements
      await expect(page.locator('text=/devora/i')).toBeVisible();
      await expect(page.locator('text=/carte/i')).toBeVisible();
    });

    test('should complete checkout with test card', async ({ page }) => {
      await page.goto('/billing');
      await page.click('[data-testid="plan-pro"] button:has-text("S\'abonner")');

      // Wait for Stripe Checkout
      await page.waitForURL(/checkout\.stripe\.com/);

      // Fill Stripe test card details
      const cardNumberFrame = page.frameLocator('iframe[name*="cardNumber"]');
      await cardNumberFrame.locator('input').fill('4242424242424242');

      const expiryFrame = page.frameLocator('iframe[name*="cardExpiry"]');
      await expiryFrame.locator('input').fill('12/34');

      const cvcFrame = page.frameLocator('iframe[name*="cardCvc"]');
      await cvcFrame.locator('input').fill('123');

      // Fill billing details
      await page.fill('input[name="billingName"]', 'Test User');
      await page.fill('input[name="email"]', 'test@devora.test');

      // Submit payment
      await page.click('button[type="submit"]');

      // Should redirect back to success page
      await page.waitForURL(/success|dashboard/);
      await expect(page.locator('text=/abonnement.*activé/i')).toBeVisible({ timeout: 10000 });
    });

    test('should handle declined card gracefully', async ({ page }) => {
      await page.goto('/billing');
      await page.click('[data-testid="plan-pro"] button:has-text("S\'abonner")');
      await page.waitForURL(/checkout\.stripe\.com/);

      // Use declined test card
      const cardNumberFrame = page.frameLocator('iframe[name*="cardNumber"]');
      await cardNumberFrame.locator('input').fill('4000000000000002');

      const expiryFrame = page.frameLocator('iframe[name*="cardExpiry"]');
      await expiryFrame.locator('input').fill('12/34');

      const cvcFrame = page.frameLocator('iframe[name*="cardCvc"]');
      await cvcFrame.locator('input').fill('123');

      await page.fill('input[name="billingName"]', 'Test User');
      await page.click('button[type="submit"]');

      // Should show error
      await expect(page.locator('text=/carte.*refusée/i')).toBeVisible();
    });

    test('should allow canceling checkout', async ({ page }) => {
      await page.goto('/billing');
      await page.click('[data-testid="plan-pro"] button:has-text("S\'abonner")');
      await page.waitForURL(/checkout\.stripe\.com/);

      // Go back
      await page.goBack();

      // Should be back on billing page
      expect(page.url()).toContain('/billing');
    });
  });

  test.describe('Active Subscription Management', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsUser(page);
      // Assume user has active subscription
    });

    test('should display current subscription details', async ({ page }) => {
      await page.goto('/billing');

      // Should show active plan
      await expect(page.locator('[data-testid="current-plan"]')).toBeVisible();
      await expect(page.locator('text=/plan actuel/i')).toBeVisible();

      // Show next billing date
      await expect(page.locator('text=/prochain.*paiement/i')).toBeVisible();

      // Show amount
      await expect(page.locator('[data-testid="subscription-amount"]')).toBeVisible();
    });

    test('should show subscription status badge', async ({ page }) => {
      await page.goto('/billing');

      // Active badge
      const statusBadge = page.locator('[data-testid="subscription-status"]');
      await expect(statusBadge).toBeVisible();
      await expect(statusBadge).toHaveText(/actif/i);
    });

    test('should display payment method', async ({ page }) => {
      await page.goto('/billing');

      // Card details (last 4 digits)
      await expect(page.locator('text=/•••• \\d{4}/i')).toBeVisible();

      // Card brand
      await expect(page.locator('[data-testid="card-brand"]')).toBeVisible();
    });
  });

  test.describe('Plan Upgrade/Downgrade', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsUser(page);
    });

    test('should upgrade to higher plan', async ({ page }) => {
      await page.goto('/billing');

      // Assume currently on Starter plan
      // Click upgrade to Pro
      await page.click('[data-testid="plan-pro"] button:has-text("Passer à Pro")');

      // Should show upgrade confirmation
      await expect(page.locator('text=/confirmer.*mise à niveau/i')).toBeVisible();

      // Show prorated amount
      await expect(page.locator('text=/prorata/i')).toBeVisible();
      await expect(page.locator('[data-testid="prorated-amount"]')).toBeVisible();

      // Confirm upgrade
      await page.click('button:has-text("Confirmer")');

      await expect(page.locator('text=/plan.*mis à niveau/i')).toBeVisible({ timeout: 10000 });
    });

    test('should downgrade to lower plan', async ({ page }) => {
      await page.goto('/billing');

      // Assume currently on Pro plan
      // Click downgrade to Starter
      await page.click('[data-testid="plan-starter"] button:has-text("Rétrograder")');

      // Should show downgrade warning
      await expect(page.locator('text=/limitation.*fonctionnalités/i')).toBeVisible();

      // Show effective date (end of current period)
      await expect(page.locator('text=/fin.*période/i')).toBeVisible();

      // Confirm downgrade
      await page.click('button:has-text("Confirmer")');

      await expect(page.locator('text=/rétrogradation.*planifiée/i')).toBeVisible();
    });

    test('should prevent downgrade if usage exceeds lower plan limits', async ({ page }) => {
      await page.goto('/billing');

      // Try to downgrade but have too many projects
      await page.click('[data-testid="plan-starter"] button:has-text("Rétrograder")');

      // Should show error about exceeding limits
      await expect(page.locator('text=/limite.*projets.*dépassée/i')).toBeVisible();

      // Downgrade button should be disabled or warning shown
      const confirmButton = page.locator('button:has-text("Confirmer")');
      await expect(confirmButton).toBeDisabled();
    });
  });

  test.describe('Stripe Customer Portal', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsUser(page);
    });

    test('should open Stripe customer portal', async ({ page }) => {
      await page.goto('/billing');

      // Click manage billing
      await page.click('button:has-text("Gérer l\'abonnement")');

      // Should redirect to Stripe portal
      await page.waitForURL(/billing\.stripe\.com/);

      // Verify portal page
      await expect(page.locator('text=/abonnement/i')).toBeVisible();
      await expect(page.locator('text=/méthode de paiement/i')).toBeVisible();
    });

    test('should allow updating payment method in portal', async ({ page }) => {
      await page.goto('/billing');
      await page.click('button:has-text("Gérer l\'abonnement")');
      await page.waitForURL(/billing\.stripe\.com/);

      // Update payment method
      await page.click('text=/mettre à jour.*carte/i');

      // Should show card form
      await expect(page.locator('iframe[name*="cardNumber"]')).toBeVisible();
    });

    test('should allow viewing invoices in portal', async ({ page }) => {
      await page.goto('/billing');
      await page.click('button:has-text("Gérer l\'abonnement")');
      await page.waitForURL(/billing\.stripe\.com/);

      // View invoices
      await page.click('text=/factures/i');

      // Should show invoice list
      await expect(page.locator('[data-testid="invoice-list"]')).toBeVisible();
    });
  });

  test.describe('Subscription Cancellation', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsUser(page);
    });

    test('should cancel subscription', async ({ page }) => {
      await page.goto('/billing');

      // Click cancel subscription
      await page.click('button:has-text("Annuler l\'abonnement")');

      // Should show cancellation confirmation
      await expect(page.locator('text=/êtes-vous sûr/i')).toBeVisible();

      // Show what happens on cancellation
      await expect(page.locator('text=/fin.*période/i')).toBeVisible();

      // Confirm cancellation
      await page.click('button:has-text("Confirmer l\'annulation")');

      await expect(page.locator('text=/abonnement.*annulé/i')).toBeVisible();
    });

    test('should show feedback form on cancellation', async ({ page }) => {
      await page.goto('/billing');

      await page.click('button:has-text("Annuler l\'abonnement")');

      // Should ask for cancellation reason
      await expect(page.locator('text=/pourquoi.*annulez/i')).toBeVisible();

      // Select reason
      await page.click('input[value="too-expensive"]');
      await page.fill('textarea[name="feedback"]', 'Too expensive for my needs');

      await page.click('button:has-text("Confirmer l\'annulation")');

      await expect(page.locator('text=/merci.*retour/i')).toBeVisible();
    });

    test('should allow reactivating canceled subscription', async ({ page }) => {
      await page.goto('/billing');

      // Assume subscription is canceled but still active until period end
      await expect(page.locator('text=/annulé.*expire/i')).toBeVisible();

      // Reactivate
      await page.click('button:has-text("Réactiver")');

      await expect(page.locator('text=/abonnement.*réactivé/i')).toBeVisible();
    });
  });

  test.describe('Invoice and Payment History', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsUser(page);
    });

    test('should display invoice history', async ({ page }) => {
      await page.goto('/billing');

      // View invoices
      await page.click('text=/historique.*factures/i');

      // Should show list of invoices
      await expect(page.locator('[data-testid="invoice-item"]')).toBeVisible();

      // Each invoice should show date, amount, status
      const firstInvoice = page.locator('[data-testid="invoice-item"]').first();
      await expect(firstInvoice.locator('text=/€/i')).toBeVisible();
      await expect(firstInvoice.locator('text=/payé|paid/i')).toBeVisible();
    });

    test('should download invoice PDF', async ({ page }) => {
      await page.goto('/billing');
      await page.click('text=/historique.*factures/i');

      // Download first invoice
      const downloadPromise = page.waitForEvent('download');
      await page.click('[data-testid="download-invoice"]');
      const download = await downloadPromise;

      // Verify download
      expect(download.suggestedFilename()).toMatch(/\.pdf$/);
    });

    test('should filter invoices by status', async ({ page }) => {
      await page.goto('/billing');
      await page.click('text=/historique.*factures/i');

      // Filter by paid
      await page.click('[data-filter="paid"]');

      // All visible invoices should be paid
      const invoices = page.locator('[data-testid="invoice-item"]');
      const count = await invoices.count();

      for (let i = 0; i < count; i++) {
        await expect(invoices.nth(i).locator('text=/payé/i')).toBeVisible();
      }
    });
  });

  test.describe('Free Trial', () => {
    test('should start free trial without payment', async ({ page }) => {
      await loginAsUser(page);
      await page.goto('/billing');

      // Start trial
      await page.click('button:has-text("Essai gratuit")');

      // Should not ask for payment method
      await expect(page.locator('text=/essai.*activé/i')).toBeVisible();

      // Show trial end date
      await expect(page.locator('[data-testid="trial-end-date"]')).toBeVisible();
    });

    test('should show trial countdown', async ({ page }) => {
      await loginAsUser(page);
      await page.goto('/billing');

      // Assume user is on trial
      await expect(page.locator('text=/\\d+ jours? restants?/i')).toBeVisible();
    });

    test('should prompt to upgrade before trial ends', async ({ page }) => {
      await loginAsUser(page);
      await page.goto('/billing');

      // If trial is ending soon
      await expect(page.locator('text=/essai.*expire.*bientôt/i')).toBeVisible();

      await expect(page.locator('button:has-text("Passer à un plan payant")')).toBeVisible();
    });
  });

  test.describe('Promo Codes and Discounts', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsUser(page);
    });

    test('should apply promo code at checkout', async ({ page }) => {
      await page.goto('/billing');
      await page.click('[data-testid="plan-pro"] button:has-text("S\'abonner")');
      await page.waitForURL(/checkout\.stripe\.com/);

      // Enter promo code
      await page.click('text=/code promo/i');
      await page.fill('input[name="promoCode"]', 'DEVORA50');
      await page.click('button:has-text("Appliquer")');

      // Should show discount
      await expect(page.locator('text=/50.*%/i')).toBeVisible();

      // Price should be reduced
      await expect(page.locator('[data-testid="discounted-price"]')).toBeVisible();
    });

    test('should show error for invalid promo code', async ({ page }) => {
      await page.goto('/billing');
      await page.click('[data-testid="plan-pro"] button:has-text("S\'abonner")');
      await page.waitForURL(/checkout\.stripe\.com/);

      await page.click('text=/code promo/i');
      await page.fill('input[name="promoCode"]', 'INVALID');
      await page.click('button:has-text("Appliquer")');

      await expect(page.locator('text=/code.*invalide/i')).toBeVisible();
    });
  });

  test.describe('Failed Payments and Retry', () => {
    test.beforeEach(async ({ page }) => {
      await loginAsUser(page);
    });

    test('should notify user of failed payment', async ({ page }) => {
      await page.goto('/billing');

      // Simulate failed payment notification
      await expect(page.locator('[data-testid="payment-failed-banner"]')).toBeVisible();

      await expect(page.locator('text=/échec.*paiement/i')).toBeVisible();
    });

    test('should allow updating payment method after failure', async ({ page }) => {
      await page.goto('/billing');

      // Click retry payment
      await page.click('button:has-text("Mettre à jour la carte")');

      // Should redirect to update payment method
      await page.waitForURL(/billing\.stripe\.com/);
    });
  });
});
