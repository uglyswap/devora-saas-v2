"""
Script pour creer ou promouvoir un utilisateur administrateur
Usage:
  python create_admin.py                    # Creer admin par defaut
  python create_admin.py user@email.com     # Promouvoir un utilisateur existant en admin
"""
import asyncio
import sys
import io

# Fix Windows encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_password_hash
from config import settings
import uuid
from datetime import datetime, timezone

async def promote_to_admin(email: str):
    """Promeut un utilisateur existant en admin"""
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]

    user = await db.users.find_one({"email": email}, {"_id": 0})

    if not user:
        print(f"Utilisateur non trouve: {email}")
        print("   Verifiez que l'email est correct.")
        client.close()
        return False

    if user.get('is_admin'):
        print(f"{email} est deja admin!")
    else:
        await db.users.update_one(
            {"email": email},
            {"$set": {
                "is_admin": True,
                "subscription_status": "active",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        print(f"{email} est maintenant SuperAdmin!")
        print(f"   Reconnectez-vous pour voir le menu Admin.")

    client.close()
    return True

async def create_admin_user():
    """Cree un utilisateur admin dans la base de donnees"""

    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]

    admin_email = "admin@devora.fun"
    admin_password = "Admin123!"

    existing_admin = await db.users.find_one({"email": admin_email}, {"_id": 0})

    if existing_admin:
        print(f"Admin user already exists: {admin_email}")
        print(f"   ID: {existing_admin['id']}")
        print(f"   Is Admin: {existing_admin.get('is_admin', False)}")

        if not existing_admin.get('is_admin'):
            await db.users.update_one(
                {"email": admin_email},
                {"$set": {"is_admin": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            print(f"   Updated to admin status")
    else:
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": admin_email,
            "hashed_password": get_password_hash(admin_password),
            "full_name": "Admin Devora",
            "is_active": True,
            "is_admin": True,
            "stripe_customer_id": None,
            "subscription_status": "active",
            "subscription_id": None,
            "current_period_end": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        await db.users.insert_one(admin_user)
        print(f"Admin user created successfully!")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   IMPORTANT: Changez ce mot de passe apres la premiere connexion!")

    client.close()

async def list_users():
    """Liste tous les utilisateurs"""
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]

    users = await db.users.find({}, {"_id": 0, "email": 1, "full_name": 1, "is_admin": 1, "subscription_status": 1}).to_list(100)

    print("\nUtilisateurs enregistres:")
    print("-" * 60)
    for user in users:
        admin_badge = "[ADMIN]" if user.get('is_admin') else "      "
        status = user.get('subscription_status', 'none')
        name = user.get('full_name', 'N/A')
        print(f"{admin_badge} {user['email']:<35} | {status:<10} | {name}")
    print("-" * 60)
    print(f"Total: {len(users)} utilisateurs")

    client.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--list":
            print("Listing users...")
            asyncio.run(list_users())
        elif "@" in arg:
            print(f"Promoting {arg} to admin...")
            asyncio.run(promote_to_admin(arg))
        else:
            print("Usage:")
            print("  python create_admin.py                    # Creer admin par defaut")
            print("  python create_admin.py user@email.com     # Promouvoir utilisateur")
            print("  python create_admin.py --list             # Lister tous les utilisateurs")
    else:
        print("Creating default admin user...")
        asyncio.run(create_admin_user())

    print("\nDone!")
