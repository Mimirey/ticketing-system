from app.db.database import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password

ROLES = ["USER", "PM_IT", "STAFF_IT"]

DEMO_USERS = [
    {"name": "Demo User", "email": "user@test.com", "password": "password123", "role": "USER"},
    {"name": "Demo PM IT", "email": "pmit@test.com", "password": "password123", "role": "PM_IT"},
    {"name": "Demo Staff IT", "email": "staff@test.com", "password": "password123", "role": "STAFF_IT"},
]

def seed():
    db = SessionLocal()
    try:
        role_map = {}
        for role_name in ROLES:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name)
                db.add(role)
                db.commit()
                db.refresh(role)
            role_map[role_name] = role

        for u in DEMO_USERS:
            exists = db.query(User).filter(User.email == u["email"]).first()
            if exists:
                continue
            db.add(User(
                name=u["name"],
                email=u["email"],
                password_hash=hash_password(u["password"]),
                role_id=role_map[u["role"]].id,
            ))
        db.commit()
        print("Seed selesai (atau sudah ada sebelumnya).")
    finally:
        db.close()

if __name__ == "__main__":
    seed()