"""Check user and Stripe config"""
import asyncio
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

async def check():
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]

    # Check user
    user = await db.users.find_one({'email': 'test@devora.com'}, {'_id': 0})
    print('=== USER test@devora.com ===')
    if user:
        print(f"Stripe Customer ID: {user.get('stripe_customer_id', 'NON CONFIGURE')}")
        print(f"Subscription Status: {user.get('subscription_status', 'AUCUN')}")
        print(f"Is Admin: {user.get('is_admin', False)}")
    else:
        print('User not found')

    # Check system config
    config = await db.system_config.find_one({'key': 'stripe'}, {'_id': 0})
    print('')
    print('=== STRIPE CONFIG ===')
    if config and config.get('value'):
        val = config['value']
        sk = val.get('secret_key', '')
        print(f"Secret Key: {'CONFIGURE (' + sk[:20] + '...)' if sk else 'NON CONFIGURE'}")
        print(f"Test Mode: {val.get('test_mode', True)}")
    else:
        print('Stripe non configure dans system_config')

    client.close()

if __name__ == "__main__":
    asyncio.run(check())
