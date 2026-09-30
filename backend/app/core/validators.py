import re


def validate_password(password: str) -> None:
    if len(password) < 6:
        raise ValueError(
            "Password minimal 6 karakter"
        )

    if not re.search(r"[A-Z]", password):
        raise ValueError(
            "Password harus memiliki minimal 1 huruf kapital"
        )

    if len(set(password)) < 4:
        raise ValueError(
            "Password harus memiliki minimal 4 karakter unik"
        )