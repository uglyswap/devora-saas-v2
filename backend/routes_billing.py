from fastapi import APIRouter, HTTPException, Depends, Request, status
from motor.motor_asyncio import AsyncIOMotorClient
from models import SubscriptionPlan, Invoice
from auth import get_current_user
from stripe_service import StripeService, StripeNotConfiguredError
from config_service import ConfigService
from email_service import EmailService
from datetime import datetime, timezone
import logging
import json
import stripe
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/billing', tags=['billing'])

# MongoDB connection with centralized config
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]

# Initialize services
stripe_service = StripeService(db)
config_service = ConfigService(db)
email_service = EmailService(db)

@router.get('/plans', response_model=SubscriptionPlan)
async def get_subscription_plans():
    """Get available subscription plans"""
    # Récupère le prix depuis la config système
    billing_settings = await config_service.get_billing_settings()
    return SubscriptionPlan(price=billing_settings["price"])

@router.post('/create-checkout-session')
async def create_checkout_session(current_user: dict = Depends(get_current_user)):
    """Create a Stripe checkout session

    Returns:
        dict: Session ID and checkout URL

    Raises:
        HTTPException 400: Already subscribed
        HTTPException 404: User not found
        HTTPException 503: Stripe not configured or unavailable
    """
    user = await db.users.find_one({'id': current_user['user_id']}, {'_id': 0})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Utilisateur non trouvé'
        )

    # Check if user already has active subscription
    if user.get('subscription_status') == 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Vous avez déjà un abonnement actif'
        )

    try:
        stripe_customer_id = user.get('stripe_customer_id')
        if not stripe_customer_id:
            # Create Stripe customer if doesn't exist
            stripe_customer_id = await stripe_service.create_customer(
                email=user['email'],
                name=user.get('full_name')
            )
            await db.users.update_one(
                {'id': user['id']},
                {'$set': {'stripe_customer_id': stripe_customer_id}}
            )

        # Get trial days from config
        billing_settings = await config_service.get_billing_settings()

        # Create checkout session
        session = await stripe_service.create_checkout_session(
            customer_id=stripe_customer_id,
            success_url=f"{settings.FRONTEND_URL}/billing/success",
            cancel_url=f"{settings.FRONTEND_URL}/billing/cancel",
            user_id=user['id'],
            trial_days=billing_settings["free_trial_days"]
        )

        return session

    except StripeNotConfiguredError as e:
        logger.error(f"Stripe not configured: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le système de paiement est temporairement indisponible. Veuillez réessayer plus tard."
        )
    except stripe.error.CardError as e:
        logger.error(f"Card error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Votre carte a été refusée. Veuillez vérifier vos informations de paiement."
        )
    except stripe.error.RateLimitError:
        logger.error("Stripe rate limit exceeded")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de requêtes. Veuillez patienter quelques instants."
        )
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Invalid Stripe request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requête de paiement invalide. Contactez le support si le problème persiste."
        )
    except stripe.error.AuthenticationError:
        logger.error("Stripe authentication failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erreur de configuration du système de paiement. Contactez l'administrateur."
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Une erreur est survenue avec le système de paiement. Veuillez réessayer."
        )

@router.post('/create-portal-session')
async def create_portal_session(current_user: dict = Depends(get_current_user)):
    """Create a Stripe customer portal session

    Returns:
        dict: Portal URL

    Raises:
        HTTPException 404: No billing info
        HTTPException 503: Stripe unavailable
    """
    user = await db.users.find_one({'id': current_user['user_id']}, {'_id': 0})

    if not user or not user.get('stripe_customer_id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Aucune information de facturation trouvée'
        )

    try:
        portal_url = await stripe_service.create_portal_session(
            customer_id=user['stripe_customer_id'],
            return_url=f"{settings.FRONTEND_URL}/billing"
        )
        return {'url': portal_url}

    except StripeNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le système de paiement est temporairement indisponible."
        )
    except stripe.error.StripeError as e:
        logger.error(f"Stripe portal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible d'accéder au portail de gestion. Veuillez réessayer."
        )

@router.get('/invoices')
async def get_invoices(current_user: dict = Depends(get_current_user)):
    """Get user invoices"""
    user = await db.users.find_one({'id': current_user['user_id']}, {'_id': 0})
    
    if not user or not user.get('stripe_customer_id'):
        return []
    
    invoices = await stripe_service.list_invoices(user['stripe_customer_id'])
    return invoices

@router.post('/webhook')
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = await stripe_service.verify_webhook_signature(payload, sig_header)
    except ValueError as e:
        logger.error(f'Webhook error: {str(e)}')
        raise HTTPException(status_code=400, detail=str(e))
    
    # Handle different event types
    event_type = event['type']
    data = event['data']['object']
    
    logger.info(f'Received webhook: {event_type}')
    
    if event_type == 'customer.subscription.created':
        # New subscription created
        subscription_id = data['id']
        customer_id = data['customer']
        status_value = data['status']
        current_period_end = datetime.fromtimestamp(data['current_period_end'], tz=timezone.utc)
        
        await db.users.update_one(
            {'stripe_customer_id': customer_id},
            {'$set': {
                'subscription_id': subscription_id,
                'subscription_status': status_value,
                'current_period_end': current_period_end.isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
        logger.info(f'Subscription created: {subscription_id}')
    
    elif event_type == 'customer.subscription.updated':
        # Subscription updated
        subscription_id = data['id']
        status_value = data['status']
        current_period_end = datetime.fromtimestamp(data['current_period_end'], tz=timezone.utc)
        
        await db.users.update_one(
            {'subscription_id': subscription_id},
            {'$set': {
                'subscription_status': status_value,
                'current_period_end': current_period_end.isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
        logger.info(f'Subscription updated: {subscription_id} - Status: {status_value}')
    
    elif event_type == 'customer.subscription.deleted':
        # Subscription canceled
        subscription_id = data['id']
        
        await db.users.update_one(
            {'subscription_id': subscription_id},
            {'$set': {
                'subscription_status': 'canceled',
                'updated_at': datetime.now(timezone.utc).isoformat()
            }}
        )
        logger.info(f'Subscription canceled: {subscription_id}')
    
    elif event_type == 'invoice.paid':
        # Invoice paid successfully
        invoice_id = data['id']
        customer_id = data['customer']
        amount = data['amount_paid'] / 100
        currency = data['currency']
        invoice_pdf = data.get('invoice_pdf')
        
        # Save invoice to database
        user = await db.users.find_one({'stripe_customer_id': customer_id}, {'_id': 0})
        if user:
            invoice = Invoice(
                user_id=user['id'],
                stripe_invoice_id=invoice_id,
                amount=amount,
                currency=currency,
                status='paid',
                invoice_pdf=invoice_pdf
            )
            invoice_dict = invoice.model_dump()
            invoice_dict['created_at'] = invoice_dict['created_at'].isoformat()
            await db.invoices.insert_one(invoice_dict)
            logger.info(f'Invoice paid: {invoice_id} - Amount: {amount} {currency}')
            
            # Send invoice email
            try:
                period_start = datetime.fromtimestamp(data['period_start'])
                period_end = datetime.fromtimestamp(data['period_end'])
                period = f"{period_start.strftime('%d/%m/%Y')} - {period_end.strftime('%d/%m/%Y')}"
                
                html = EmailService.get_invoice_email(
                    user.get('full_name', user['email'].split('@')[0]),
                    amount,
                    invoice_pdf or '#',
                    period
                )
                await email_service.send_email(
                    to=user['email'],
                    subject=f'Votre facture Devora - {amount:.2f}€',
                    html=html
                )
            except Exception as e:
                logger.error(f'Failed to send invoice email: {str(e)}')
    
    elif event_type == 'invoice.payment_failed':
        # Invoice payment failed
        subscription_id = data.get('subscription')
        customer_id = data['customer']
        amount = data['amount_due'] / 100
        
        if subscription_id:
            await db.users.update_one(
                {'subscription_id': subscription_id},
                {'$set': {
                    'subscription_status': 'past_due',
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }}
            )
            logger.warning(f'Payment failed for subscription: {subscription_id}')
            
            # Send payment failed email
            try:
                user = await db.users.find_one({'stripe_customer_id': customer_id}, {'_id': 0})
                if user:
                    html = EmailService.get_payment_failed_email(
                        user.get('full_name', user['email'].split('@')[0]),
                        amount
                    )
                    await email_service.send_email(
                        to=user['email'],
                        subject='⚠️ Échec de paiement - Devora',
                        html=html
                    )
            except Exception as e:
                logger.error(f'Failed to send payment failed email: {str(e)}')
    
    return {'status': 'success'}
