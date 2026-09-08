from api.database import SessionLocal, engine
from api.models import MemberInfo, Base
from api.security import get_password_hash

def seed_users():
    print("Rebuilding database tables to apply the latest models...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    
    try:
        print("Seeding database with all 3 access tiers...")

        # 1. THE MASTER USER (God Mode)
        master_user = MemberInfo(
            full_name="System Overlord",
            email="master@gym.com",
            phone_no="000-0000",
            address="The Cloud",
            hashed_password=get_password_hash("master"),
            role="master"
        )

        # 2. THE ADMIN USER (Gym Staff)
        admin_user = MemberInfo(
            full_name="Gym Manager",
            email="admin@gym.com",
            phone_no="555-0000",
            address="123 Admin Way",
            hashed_password=get_password_hash("admin"),
            role="admin"
        )

        # 3. THE REGULAR USER (Gym Member)
        regular_user = MemberInfo(
            full_name="Test Member",
            email="user@gym.com",
            phone_no="555-1111",
            address="456 Member Lane",
            hashed_password=get_password_hash("user"),
            role="user"
        )

        db.add_all([master_user, admin_user, regular_user])
        db.commit()
        
        print("✅ Success! Database seeded.")
        print("Master: master@gym.com | Password: master")
        print("Admin:  admin@gym.com  | Password: admin")
        print("User:   user@gym.com   | Password: user")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()