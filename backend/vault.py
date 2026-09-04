# "כספת" - הצפנה מקומית של פרטי ההתחברות לבנקים.
#
# מפתח ההצפנה נגזר מסיסמת-על (master password) שהמשתמש בוחר, ולעולם לא
# נשמר בדיסק - רק ה-salt וה-verifier (לאימות שהסיסמה נכונה) נשמרים ב-DB.
# המפתח בפועל מוחזק בזיכרון בלבד לאורך חיי התהליך (מאז שנפתחה הכספת ועד
# לסגירת השרת/לחיצה על "נעל"), כך שהסנכרון האוטומטי ברקע יכול לפעול כל
# עוד השרת רץ בלי להקליד סיסמה בכל פעם, אבל לאחר הפעלה מחדש של השרת יש
# לפתוח את הכספת מחדש כדי שהסנכרון האוטומטי יוכל להמשיך.
import base64
import json
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from sqlalchemy.orm import Session

from models import VaultConfig

_session_key: bytes | None = None


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
    raw = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(raw)


def is_setup(db: Session) -> bool:
    return db.query(VaultConfig).first() is not None


def is_unlocked() -> bool:
    return _session_key is not None


def setup_vault(db: Session, password: str) -> None:
    global _session_key
    if is_setup(db):
        raise ValueError("הכספת כבר הוגדרה")
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    verifier = Fernet(key).encrypt(b"vault-check").decode("utf-8")
    db.add(VaultConfig(salt=salt.hex(), verifier=verifier))
    db.commit()
    _session_key = key


def unlock_vault(db: Session, password: str) -> None:
    global _session_key
    cfg = db.query(VaultConfig).first()
    if not cfg:
        raise ValueError("הכספת לא הוגדרה עדיין")
    key = _derive_key(password, bytes.fromhex(cfg.salt))
    try:
        Fernet(key).decrypt(cfg.verifier.encode("utf-8"))
    except InvalidToken:
        raise ValueError("סיסמה שגויה")
    _session_key = key


def lock_vault() -> None:
    global _session_key
    _session_key = None


def encrypt_credentials(creds: dict) -> str:
    if _session_key is None:
        raise ValueError("הכספת נעולה")
    return Fernet(_session_key).encrypt(json.dumps(creds).encode("utf-8")).decode("utf-8")


def decrypt_credentials(ciphertext: str) -> dict:
    if _session_key is None:
        raise ValueError("הכספת נעולה")
    plain = Fernet(_session_key).decrypt(ciphertext.encode("utf-8"))
    return json.loads(plain.decode("utf-8"))
