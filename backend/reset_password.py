"""Reset password for a user"""
import asyncio
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_password_hash
from config import settings
from datetime import datetime, timezone

async def reset_password(email: str, new_password: str):
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]

    hashed = get_password_hash(new_password)

    result = await db.users.update_one(
        {'email': email},
        {'$set': {'hashed_password': hashed, 'updated_at': datetime.now(timezone.utc).isoformat()}}
    )

    if result.modified_count > 0:
        print(f'Mot de passe reinitialise pour {email}!')
        print(f'Nouveau mot de passe: {new_password}')
    else:
        print(f'Utilisateur {email} non trouve')

    client.close()

if __name__ == "__main__":
    email = "test@devora.com"
    password = "Test123!"

    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]

    asyncio.run(reset_password(email, password))
