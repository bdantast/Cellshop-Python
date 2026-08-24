from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SELLER = "seller"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD_DEBIT = "card_debit"
    CARD_CREDIT = "card_credit"
    PIX = "pix"
    BANK_TRANSFER = "bank_transfer"
    INSTALLMENT = "installment"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class SaleStatus(str, Enum):
    OPEN = "open"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class PurchaseStatus(str, Enum):
    PENDING = "pending"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class StockMovementType(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"
    RETURN = "return"


@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    full_name: str = ""
    role: UserRole = UserRole.SELLER
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


@dataclass
class Brand:
    id: Optional[int] = None
    name: str = ""
    logo_path: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Category:
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Supplier:
    id: Optional[int] = None
    name: str = ""
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    cnpj: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


@dataclass
class Customer:
    id: Optional[int] = None
    name: str = ""
    phone: Optional[str] = None
    email: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Product:
    id: Optional[int] = None
    sku: str = ""
    name: str = ""
    brand_id: int = 0
    category_id: int = 0
    model: Optional[str] = None
    color: Optional[str] = None
    storage_gb: Optional[int] = None
    ram_gb: Optional[int] = None
    screen_inches: Optional[float] = None
    battery_mah: Optional[int] = None
    description: Optional[str] = None
    cost_price: float = 0.0
    sale_price: float = 0.0
    min_stock: int = 5
    current_stock: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    brand_name: str = ""
    category_name: str = ""
    primary_image: Optional[str] = None


@dataclass
class Purchase:
    id: Optional[int] = None
    supplier_id: int = 0
    user_id: int = 0
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    subtotal: float = 0.0
    discount: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    status: PurchaseStatus = PurchaseStatus.PENDING
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    supplier_name: str = ""
    user_name: str = ""
    items: List['PurchaseItem'] = field(default_factory=list)


@dataclass
class PurchaseItem:
    id: Optional[int] = None
    purchase_id: int = 0
    product_id: int = 0
    quantity: int = 0
    unit_cost: float = 0.0
    total: float = 0.0
    
    product_name: str = ""
    product_sku: str = ""


@dataclass
class Sale:
    id: Optional[int] = None
    customer_id: Optional[int] = None
    user_id: int = 0
    sale_number: str = ""
    subtotal: float = 0.0
    discount: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    payment_status: PaymentStatus = PaymentStatus.PENDING
    sale_status: SaleStatus = SaleStatus.OPEN
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    customer_name: str = ""
    user_name: str = ""
    items: List['SaleItem'] = field(default_factory=list)
    payments: List['Payment'] = field(default_factory=list)


@dataclass
class SaleItem:
    id: Optional[int] = None
    sale_id: int = 0
    product_id: int = 0
    quantity: int = 0
    unit_price: float = 0.0
    discount: float = 0.0
    total: float = 0.0
    
    product_name: str = ""
    product_sku: str = ""


@dataclass
class Payment:
    id: Optional[int] = None
    sale_id: int = 0
    payment_method: PaymentMethod = PaymentMethod.CASH
    amount: float = 0.0
    installments: int = 1
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    transaction_id: Optional[str] = None
    status: PaymentStatus = PaymentStatus.COMPLETED
    received_at: Optional[datetime] = None


@dataclass
class StockMovement:
    id: Optional[int] = None
    product_id: int = 0
    movement_type: StockMovementType = StockMovementType.IN
    quantity: int = 0
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    user_id: int = 0
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    product_name: str = ""
    product_sku: str = ""
    user_name: str = ""


@dataclass
class Setting:
    key: str = ""
    value: str = ""
    description: Optional[str] = None