from app.db.database import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.models.company import Company
from app.models.application import Application
from app.core.security import hash_password

ROLES = ["USER", "PM_IT", "STAFF_IT", "ADMIN"]

DEMO_USERS = [
    {"name": "Demo User", "username": "user", "email": "user@test.com", "password": "123456", "role": "USER"},
    {"name": "Demo PM IT", "username": "pm", "email": "pm@test.com", "password": "123456", "role": "PM_IT"},
    {"name": "Demo Staff IT", "username": "staff", "email": "staff@test.com", "password": "123456", "role": "STAFF_IT"},
    {"name": "Demo Admin", "username": "admin", "email": "admin@test.com", "password": "123456", "role": "ADMIN"},
]

# Aplikasi dikelompokkan di bawah company-nya
DEMO_COMPANIES = [
    {
        "name": "Amazink People Group",
        "applications": [
            {"name": "HRIS", "description": "Sistem informasi sumber daya manusia"},
            {"name": "Payroll", "description": "Aplikasi penggajian"},
        ],
    },
    {
        "name": "Mitra Teknologi",
        "applications": [
            {"name": "Portal Pelanggan", "description": "Portal layanan pelanggan"},
            {"name": "Inventory", "description": "Manajemen stok barang"},
        ],
    },
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
                # isi username untuk akun lama yang belum punya
                if not exists.username:
                    exists.username = u["username"]
                continue
            db.add(User(
                name=u["name"],
                username=u["username"],
                email=u["email"],
                password_hash=hash_password(u["password"]),
                role_id=role_map[u["role"]].id,
            ))
        db.commit()

        for c in DEMO_COMPANIES:
            company = db.query(Company).filter(Company.name == c["name"]).first()
            if not company:
                company = Company(name=c["name"])
                db.add(company)
                db.commit()
                db.refresh(company)

            for a in c["applications"]:
                app_exists = (
                    db.query(Application)
                    .filter(Application.company_id == company.id, Application.name == a["name"])
                    .first()
                )
                if app_exists:
                    continue
                db.add(Application(
                    company_id=company.id,
                    name=a["name"],
                    description=a["description"],
                ))
            db.commit()

        print("Seed selesai (atau sudah ada sebelumnya).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()