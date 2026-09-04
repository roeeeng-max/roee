from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, default="כללי")
    person = Column(String, default="משותף")  # רועי / ניקול / משותף
    source_file = Column(String)
    created_at = Column(DateTime, default=func.now())

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    monthly_limit = Column(Float, nullable=False)
    month = Column(String, nullable=False)  # YYYY-MM

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String)
    rows_imported = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=func.now())


class VaultConfig(Base):
    """שורה יחידה - הגדרות הכספת המוצפנת (סיסמת-על להצפנת פרטי ההתחברות לבנקים)."""
    __tablename__ = "vault_config"

    id = Column(Integer, primary_key=True)
    salt = Column(String, nullable=False)      # hex
    verifier = Column(String, nullable=False)  # ciphertext של ערך ידוע, לאימות הסיסמה


class BankConnection(Base):
    """חיבור לגוף פיננסי - בנק/כרטיס אשראי (scraped, אוטומטי) או בית השקעות/ביטוח (manual)."""
    __tablename__ = "bank_connections"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(String, nullable=False)   # למשל "hapoalim" / "phoenix"
    display_name = Column(String, nullable=False)
    kind = Column(String, nullable=False)              # "scraped" | "manual"
    category = Column(String)                          # bank / credit_card / investment_house / insurance_pension / other
    person = Column(String, default="משותף")
    encrypted_credentials = Column(String)              # מוצפן עם מפתח הכספת, ריק בחיבור ידני
    last_balance = Column(Float)
    last_synced_at = Column(DateTime)
    status = Column(String, default="never")            # never | ok | error | locked
    last_error = Column(String)
    created_at = Column(DateTime, default=func.now())


class BalanceSnapshot(Base):
    """היסטוריית יתרות לכל חיבור (לצורך מעקב/גרף)."""
    __tablename__ = "balance_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, nullable=False, index=True)
    balance = Column(Float, nullable=False)
    captured_at = Column(DateTime, default=func.now())


class NetWorthSnapshot(Base):
    """יתרת הון כוללת יומית (סכום כל החיבורים), שורה אחת ליום."""
    __tablename__ = "networth_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    day = Column(String, nullable=False, unique=True)  # YYYY-MM-DD
    total = Column(Float, nullable=False)
    captured_at = Column(DateTime, default=func.now())
