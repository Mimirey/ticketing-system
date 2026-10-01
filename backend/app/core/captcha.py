import random
import string
import time

CAPTCHA_EXPIRE_SECONDS = 300

captcha_store = {}
def generate_captcha():
    captcha_id = "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=32
        )
    )
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    answer = num1 + num2
    captcha_store[captcha_id] = {
        "answer": answer,
        "expires_at": time.time() + CAPTCHA_EXPIRE_SECONDS,
    }
    return captcha_id, f"{num1} + {num2} = ?"


def verify_captcha(
    captcha_id: str,
    answer: int
) -> bool:
    captcha = captcha_store.get(captcha_id)
    if not captcha:
        return False
    if time.time() > captcha["expires_at"]:
        captcha_store.pop(captcha_id, None)
        return False
    if captcha["answer"] != answer:
        return False
    captcha_store.pop(captcha_id, None)

    return True