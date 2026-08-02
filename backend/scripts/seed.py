from app.db.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password

db = SessionLocal()

users = [
    {
        "name": "Demo User",
        "email": "user@test.com",
        "password": "123456",
        "role": "USER",
    },
    {
        "name": "Demo PM",
        "email": "pm@test.com",
        "password": "123456",
        "role": "PM_IT",
    },
    {
        "name": "Demo Staff",
        "email": "staff@test.com",
        "password": "123456",
        "role": "STAFF_IT",
    },
]

try:
    for item in users:
        # Cek apakah user sudah ada
        existing = db.query(User).filter(User.email == item["email"]).first()
        if existing:
            continue

        # Cari role berdasarkan nama
        role = db.query(Role).filter(Role.name == item["role"]).first()

        if role is None:
            print(f"Role {item['role']} tidak ditemukan.")
            continue

        user = User(
            name=item["name"],
            email=item["email"],
            password_hash=hash_password(item["password"]),
            role_id=role.id,
        )

        db.add(user)

    db.commit()
    print(" Users seeded successfully!")

except Exception as e:
    db.rollback()
    print(e)

finally:
    db.close()