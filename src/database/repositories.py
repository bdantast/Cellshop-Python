from typing import List, Optional, Tuple, Any
from datetime import datetime, date
from sqlite3 import Row
import bcrypt

from src.database.connection import get_connection, init_database
from src.models import (
    User, UserRole, Brand, Category, Supplier, Customer, Product,
    Purchase, PurchaseItem, PurchaseStatus, Sale, SaleItem, SaleStatus, PaymentStatus,
    Payment, PaymentMethod, StockMovement, StockMovementType, Setting
)


class BaseRepository:
    def __init__(self):
        init_database()


class UserRepository(BaseRepository):
    def create(self, user: User) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO users (username, password_hash, full_name, role, is_active)
                   VALUES (?, ?, ?, ?, ?)""",
                (user.username, user.password_hash, user.full_name, user.role.value, user.is_active)
            )
            return cursor.lastrowid

    def get_by_id(self, user_id: int) -> Optional[User]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def get_by_username(self, username: str) -> Optional[User]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None

    def get_all(self, active_only: bool = True) -> List[User]:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM users"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY full_name"
            cursor.execute(query)
            return [self._row_to_user(row) for row in cursor.fetchall()]

    def update(self, user: User) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE users SET full_name = ?, role = ?, is_active = ?
                   WHERE id = ?""",
                (user.full_name, user.role.value, user.is_active, user.id)
            )
            return cursor.rowcount > 0

    def update_password(self, user_id: int, new_password_hash: str) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_password_hash, user_id)
            )
            return cursor.rowcount > 0

    def update_last_login(self, user_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            return cursor.rowcount > 0

    def delete(self, user_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
            return cursor.rowcount > 0

    def verify_password(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _row_to_user(self, row: Row) -> User:
        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            full_name=row["full_name"],
            role=UserRole(row["role"]),
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            last_login=datetime.fromisoformat(row["last_login"]) if row["last_login"] else None
        )


class BrandRepository(BaseRepository):
    def create(self, brand: Brand) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO brands (name, logo_path) VALUES (?, ?)",
                          (brand.name, brand.logo_path))
            return cursor.lastrowid

    def get_by_id(self, brand_id: int) -> Optional[Brand]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM brands WHERE id = ?", (brand_id,))
            row = cursor.fetchone()
            return self._row_to_brand(row) if row else None

    def get_all(self, active_only: bool = True) -> List[Brand]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM brands ORDER BY name")
            return [self._row_to_brand(row) for row in cursor.fetchall()]

    def update(self, brand: Brand) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE brands SET name = ?, logo_path = ? WHERE id = ?",
                          (brand.name, brand.logo_path, brand.id))
            return cursor.rowcount > 0

    def delete(self, brand_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM brands WHERE id = ?", (brand_id,))
            return cursor.rowcount > 0

    def _row_to_brand(self, row: Row) -> Brand:
        return Brand(
            id=row["id"],
            name=row["name"],
            logo_path=row["logo_path"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
        )


class CategoryRepository(BaseRepository):
    def create(self, category: Category) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
                          (category.name, category.description))
            return cursor.lastrowid

    def get_by_id(self, category_id: int) -> Optional[Category]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()
            return self._row_to_category(row) if row else None

    def get_all(self) -> List[Category]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name")
            return [self._row_to_category(row) for row in cursor.fetchall()]

    def update(self, category: Category) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE categories SET name = ?, description = ? WHERE id = ?",
                          (category.name, category.description, category.id))
            return cursor.rowcount > 0

    def delete(self, category_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0

    def _row_to_category(self, row: Row) -> Category:
        return Category(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
        )


class SupplierRepository(BaseRepository):
    def create(self, supplier: Supplier) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO suppliers (name, contact_name, phone, email, address, cnpj, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (supplier.name, supplier.contact_name, supplier.phone, supplier.email,
                 supplier.address, supplier.cnpj, supplier.is_active)
            )
            return cursor.lastrowid

    def get_by_id(self, supplier_id: int) -> Optional[Supplier]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
            row = cursor.fetchone()
            return self._row_to_supplier(row) if row else None

    def get_all(self, active_only: bool = True) -> List[Supplier]:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM suppliers"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY name"
            cursor.execute(query)
            return [self._row_to_supplier(row) for row in cursor.fetchall()]

    def search(self, term: str) -> List[Supplier]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM suppliers 
                   WHERE name LIKE ? OR contact_name LIKE ? OR cnpj LIKE ?
                   ORDER BY name""",
                (f"%{term}%", f"%{term}%", f"%{term}%")
            )
            return [self._row_to_supplier(row) for row in cursor.fetchall()]

    def update(self, supplier: Supplier) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE suppliers SET name = ?, contact_name = ?, phone = ?, email = ?,
                   address = ?, cnpj = ?, is_active = ? WHERE id = ?""",
                (supplier.name, supplier.contact_name, supplier.phone, supplier.email,
                 supplier.address, supplier.cnpj, supplier.is_active, supplier.id)
            )
            return cursor.rowcount > 0

    def delete(self, supplier_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE suppliers SET is_active = 0 WHERE id = ?", (supplier_id,))
            return cursor.rowcount > 0

    def _row_to_supplier(self, row: Row) -> Supplier:
        return Supplier(
            id=row["id"],
            name=row["name"],
            contact_name=row["contact_name"],
            phone=row["phone"],
            email=row["email"],
            address=row["address"],
            cnpj=row["cnpj"],
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
        )


class CustomerRepository(BaseRepository):
    def create(self, customer: Customer) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO customers (name, phone, email, cpf_cnpj, address, city, state, zip_code, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (customer.name, customer.phone, customer.email, customer.cpf_cnpj,
                 customer.address, customer.city, customer.state, customer.zip_code, customer.notes)
            )
            return cursor.lastrowid

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            return self._row_to_customer(row) if row else None

    def get_all(self) -> List[Customer]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers ORDER BY name")
            return [self._row_to_customer(row) for row in cursor.fetchall()]

    def search(self, term: str) -> List[Customer]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM customers 
                   WHERE name LIKE ? OR phone LIKE ? OR cpf_cnpj LIKE ? OR email LIKE ?
                   ORDER BY name""",
                (f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%")
            )
            return [self._row_to_customer(row) for row in cursor.fetchall()]

    def update(self, customer: Customer) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE customers SET name = ?, phone = ?, email = ?, cpf_cnpj = ?,
                   address = ?, city = ?, state = ?, zip_code = ?, notes = ? WHERE id = ?""",
                (customer.name, customer.phone, customer.email, customer.cpf_cnpj,
                 customer.address, customer.city, customer.state, customer.zip_code,
                 customer.notes, customer.id)
            )
            return cursor.rowcount > 0

    def delete(self, customer_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            return cursor.rowcount > 0

    def _row_to_customer(self, row: Row) -> Customer:
        return Customer(
            id=row["id"],
            name=row["name"],
            phone=row["phone"],
            email=row["email"],
            cpf_cnpj=row["cpf_cnpj"],
            address=row["address"],
            city=row["city"],
            state=row["state"],
            zip_code=row["zip_code"],
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
        )


class ProductRepository(BaseRepository):
    def create(self, product: Product) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO products (sku, name, brand_id, category_id, model, color,
                   storage_gb, ram_gb, screen_inches, battery_mah, description,
                   cost_price, sale_price, min_stock, current_stock, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (product.sku, product.name, product.brand_id, product.category_id,
                 product.model, product.color, product.storage_gb, product.ram_gb,
                 product.screen_inches, product.battery_mah, product.description,
                 product.cost_price, product.sale_price, product.min_stock,
                 product.current_stock, product.is_active)
            )
            return cursor.lastrowid

    def get_by_id(self, product_id: int) -> Optional[Product]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT p.*, b.name as brand_name, c.name as category_name,
                   (SELECT image_path FROM product_images WHERE product_id = p.id AND is_primary = 1 LIMIT 1) as primary_image
                   FROM products p
                   JOIN brands b ON p.brand_id = b.id
                   JOIN categories c ON p.category_id = c.id
                   WHERE p.id = ?""",
                (product_id,)
            )
            row = cursor.fetchone()
            return self._row_to_product(row) if row else None

    def get_by_sku(self, sku: str) -> Optional[Product]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT p.*, b.name as brand_name, c.name as category_name,
                   (SELECT image_path FROM product_images WHERE product_id = p.id AND is_primary = 1 LIMIT 1) as primary_image
                   FROM products p
                   JOIN brands b ON p.brand_id = b.id
                   JOIN categories c ON p.category_id = c.id
                   WHERE p.sku = ?""",
                (sku,)
            )
            row = cursor.fetchone()
            return self._row_to_product(row) if row else None

    def get_all(self, active_only: bool = True, include_relations: bool = True) -> List[Product]:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """SELECT p.*, b.name as brand_name, c.name as category_name,
                       (SELECT image_path FROM product_images WHERE product_id = p.id AND is_primary = 1 LIMIT 1) as primary_image
                       FROM products p
                       JOIN brands b ON p.brand_id = b.id
                       JOIN categories c ON p.category_id = c.id"""
            if active_only:
                query += " WHERE p.is_active = 1"
            query += " ORDER BY p.name"
            cursor.execute(query)
            return [self._row_to_product(row) for row in cursor.fetchall()]

    def search(self, term: str, active_only: bool = True) -> List[Product]:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """SELECT p.*, b.name as brand_name, c.name as category_name,
                       (SELECT image_path FROM product_images WHERE product_id = p.id AND is_primary = 1 LIMIT 1) as primary_image
                       FROM products p
                       JOIN brands b ON p.brand_id = b.id
                       JOIN categories c ON p.category_id = c.id"""
            conditions = []
            if active_only:
                conditions.append("p.is_active = 1")
            conditions.append("(p.name LIKE ? OR p.sku LIKE ? OR p.model LIKE ? OR b.name LIKE ?)")
            query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY p.name"
            cursor.execute(query, (f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%"))
            return [self._row_to_product(row) for row in cursor.fetchall()]

    def get_low_stock(self) -> List[Product]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT p.*, b.name as brand_name, c.name as category_name,
                   (SELECT image_path FROM product_images WHERE product_id = p.id AND is_primary = 1 LIMIT 1) as primary_image
                   FROM products p
                   JOIN brands b ON p.brand_id = b.id
                   JOIN categories c ON p.category_id = c.id
                   WHERE p.is_active = 1 AND p.current_stock <= p.min_stock
                   ORDER BY p.current_stock ASC"""
            )
            return [self._row_to_product(row) for row in cursor.fetchall()]

    def update(self, product: Product) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE products SET sku = ?, name = ?, brand_id = ?, category_id = ?,
                   model = ?, color = ?, storage_gb = ?, ram_gb = ?, screen_inches = ?,
                   battery_mah = ?, description = ?, cost_price = ?, sale_price = ?,
                   min_stock = ?, current_stock = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (product.sku, product.name, product.brand_id, product.category_id,
                 product.model, product.color, product.storage_gb, product.ram_gb,
                 product.screen_inches, product.battery_mah, product.description,
                 product.cost_price, product.sale_price, product.min_stock,
                 product.current_stock, product.is_active, product.id)
            )
            return cursor.rowcount > 0

    def update_stock(self, product_id: int, quantity: int, movement_type: StockMovementType) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            if movement_type == StockMovementType.IN:
                cursor.execute(
                    "UPDATE products SET current_stock = current_stock + ? WHERE id = ?",
                    (quantity, product_id)
                )
            elif movement_type == StockMovementType.OUT:
                cursor.execute(
                    "UPDATE products SET current_stock = current_stock - ? WHERE id = ? AND current_stock >= ?",
                    (quantity, product_id, quantity)
                )
            elif movement_type == StockMovementType.ADJUSTMENT:
                cursor.execute(
                    "UPDATE products SET current_stock = ? WHERE id = ?",
                    (quantity, product_id)
                )
            return cursor.rowcount > 0

    def delete(self, product_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))
            return cursor.rowcount > 0

    def _row_to_product(self, row: Row) -> Product:
        return Product(
            id=row["id"],
            sku=row["sku"],
            name=row["name"],
            brand_id=row["brand_id"],
            category_id=row["category_id"],
            model=row["model"],
            color=row["color"],
            storage_gb=row["storage_gb"],
            ram_gb=row["ram_gb"],
            screen_inches=row["screen_inches"],
            battery_mah=row["battery_mah"],
            description=row["description"],
            cost_price=row["cost_price"],
            sale_price=row["sale_price"],
            min_stock=row["min_stock"],
            current_stock=row["current_stock"],
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            brand_name=row["brand_name"],
            category_name=row["category_name"],
            primary_image=row["primary_image"]
        )


class PurchaseRepository(BaseRepository):
    def create(self, purchase: Purchase) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO purchases (supplier_id, user_id, invoice_number, invoice_date,
                   subtotal, discount, tax, total, status, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (purchase.supplier_id, purchase.user_id, purchase.invoice_number,
                 purchase.invoice_date.isoformat() if purchase.invoice_date else None,
                 purchase.subtotal, purchase.discount, purchase.tax, purchase.total,
                 purchase.status.value, purchase.notes)
            )
            purchase_id = cursor.lastrowid
            for item in purchase.items:
                cursor.execute(
                    """INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_cost, total)
                       VALUES (?, ?, ?, ?, ?)""",
                    (purchase_id, item.product_id, item.quantity, item.unit_cost, item.total)
                )
            return purchase_id

    def get_by_id(self, purchase_id: int) -> Optional[Purchase]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT p.*, s.name as supplier_name, u.full_name as user_name
                   FROM purchases p
                   JOIN suppliers s ON p.supplier_id = s.id
                   JOIN users u ON p.user_id = u.id
                   WHERE p.id = ?""",
                (purchase_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            purchase = self._row_to_purchase(row)
            purchase.items = self._get_items(purchase_id)
            return purchase

    def get_all(self, status: Optional[PurchaseStatus] = None,
                start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Purchase]:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """SELECT p.*, s.name as supplier_name, u.full_name as user_name
                       FROM purchases p
                       JOIN suppliers s ON p.supplier_id = s.id
                       JOIN users u ON p.user_id = u.id"""
            conditions = []
            params = []
            if status:
                conditions.append("p.status = ?")
                params.append(status.value)
            if start_date:
                conditions.append("date(p.created_at) >= ?")
                params.append(start_date.isoformat())
            if end_date:
                conditions.append("date(p.created_at) <= ?")
                params.append(end_date.isoformat())
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY p.created_at DESC"
            cursor.execute(query, params)
            purchases = [self._row_to_purchase(row) for row in cursor.fetchall()]
            for p in purchases:
                p.items = self._get_items(p.id)
            return purchases

    def update_status(self, purchase_id: int, status: PurchaseStatus) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE purchases SET status = ? WHERE id = ?", (status.value, purchase_id))
            return cursor.rowcount > 0

    def receive_purchase(self, purchase_id: int, user_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM purchase_items WHERE purchase_id = ?", (purchase_id,))
            items = cursor.fetchall()
            for item in items:
                cursor.execute(
                    "UPDATE products SET current_stock = current_stock + ? WHERE id = ?",
                    (item["quantity"], item["product_id"])
                )
                cursor.execute(
                    """INSERT INTO stock_movements (product_id, movement_type, quantity,
                       reference_type, reference_id, user_id, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (item["product_id"], StockMovementType.IN.value, item["quantity"],
                     "purchase", purchase_id, user_id, f"Recebimento da compra #{purchase_id}")
                )
            cursor.execute(
                "UPDATE purchases SET status = ? WHERE id = ?",
                (PurchaseStatus.RECEIVED.value, purchase_id)
            )
            return True

    def _get_items(self, purchase_id: int) -> List[PurchaseItem]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT pi.*, p.name as product_name, p.sku as product_sku
                   FROM purchase_items pi
                   JOIN products p ON pi.product_id = p.id
                   WHERE pi.purchase_id = ?""",
                (purchase_id,)
            )
            return [PurchaseItem(
                id=row["id"],
                purchase_id=row["purchase_id"],
                product_id=row["product_id"],
                quantity=row["quantity"],
                unit_cost=row["unit_cost"],
                total=row["total"],
                product_name=row["product_name"],
                product_sku=row["product_sku"]
            ) for row in cursor.fetchall()]

    def _row_to_purchase(self, row: Row) -> Purchase:
        return Purchase(
            id=row["id"],
            supplier_id=row["supplier_id"],
            user_id=row["user_id"],
            invoice_number=row["invoice_number"],
            invoice_date=datetime.fromisoformat(row["invoice_date"]) if row["invoice_date"] else None,
            subtotal=row["subtotal"],
            discount=row["discount"],
            tax=row["tax"],
            total=row["total"],
            status=PurchaseStatus(row["status"]),
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            supplier_name=row["supplier_name"],
            user_name=row["user_name"]
        )


class SaleRepository(BaseRepository):
    def create(self, sale: Sale) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO sales (customer_id, user_id, sale_number, subtotal, discount,
                   tax, total, payment_status, sale_status, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sale.customer_id, sale.user_id, sale.sale_number, sale.subtotal,
                 sale.discount, sale.tax, sale.total, sale.payment_status.value,
                 sale.sale_status.value, sale.notes)
            )
            sale_id = cursor.lastrowid
            for item in sale.items:
                cursor.execute(
                    """INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, discount, total)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (sale_id, item.product_id, item.quantity, item.unit_price,
                     item.discount, item.total)
                )
                cursor.execute(
                    "UPDATE products SET current_stock = current_stock - ? WHERE id = ?",
                    (item.quantity, item.product_id)
                )
                cursor.execute(
                    """INSERT INTO stock_movements (product_id, movement_type, quantity,
                       reference_type, reference_id, user_id, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (item.product_id, StockMovementType.OUT.value, item.quantity,
                     "sale", sale_id, sale.user_id, f"Venda #{sale.sale_number}")
                )
            for payment in sale.payments:
                cursor.execute(
                    """INSERT INTO payments (sale_id, payment_method, amount, installments,
                       card_brand, card_last4, transaction_id, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (sale_id, payment.payment_method.value, payment.amount, payment.installments,
                     payment.card_brand, payment.card_last4, payment.transaction_id,
                     payment.status.value)
                )
            return sale_id

    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT s.*, c.name as customer_name, u.full_name as user_name
                   FROM sales s
                   LEFT JOIN customers c ON s.customer_id = c.id
                   JOIN users u ON s.user_id = u.id
                   WHERE s.id = ?""",
                (sale_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            sale = self._row_to_sale(row)
            sale.items = self._get_items(sale_id)
            sale.payments = self._get_payments(sale_id)
            return sale

    def get_all(self, status: Optional[SaleStatus] = None,
                payment_status: Optional[PaymentStatus] = None,
                start_date: Optional[date] = None, end_date: Optional[date] = None,
                customer_id: Optional[int] = None) -> List[Sale]:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """SELECT s.*, c.name as customer_name, u.full_name as user_name
                       FROM sales s
                       LEFT JOIN customers c ON s.customer_id = c.id
                       JOIN users u ON s.user_id = u.id"""
            conditions = []
            params = []
            if status:
                conditions.append("s.sale_status = ?")
                params.append(status.value)
            if payment_status:
                conditions.append("s.payment_status = ?")
                params.append(payment_status.value)
            if start_date:
                conditions.append("date(s.created_at) >= ?")
                params.append(start_date.isoformat())
            if end_date:
                conditions.append("date(s.created_at) <= ?")
                params.append(end_date.isoformat())
            if customer_id:
                conditions.append("s.customer_id = ?")
                params.append(customer_id)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY s.created_at DESC"
            cursor.execute(query, params)
            sales = [self._row_to_sale(row) for row in cursor.fetchall()]
            for s in sales:
                s.items = self._get_items(s.id)
                s.payments = self._get_payments(s.id)
            return sales

    def get_open_sales(self) -> List[Sale]:
        return self.get_all(status=SaleStatus.OPEN)

    def update_status(self, sale_id: int, status: SaleStatus) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            completed_at = datetime.now().isoformat() if status == SaleStatus.COMPLETED else None
            cursor.execute(
                "UPDATE sales SET sale_status = ?, completed_at = ? WHERE id = ?",
                (status.value, completed_at, sale_id)
            )
            return cursor.rowcount > 0

    def update_payment_status(self, sale_id: int, status: PaymentStatus) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sales SET payment_status = ? WHERE id = ?",
                (status.value, sale_id)
            )
            return cursor.rowcount > 0

    def add_payment(self, payment: Payment) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO payments (sale_id, payment_method, amount, installments,
                   card_brand, card_last4, transaction_id, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (payment.sale_id, payment.payment_method.value, payment.amount,
                 payment.installments, payment.card_brand, payment.card_last4,
                 payment.transaction_id, payment.status.value)
            )
            return cursor.lastrowid

    def _get_items(self, sale_id: int) -> List[SaleItem]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT si.*, p.name as product_name, p.sku as product_sku
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   WHERE si.sale_id = ?""",
                (sale_id,)
            )
            return [SaleItem(
                id=row["id"],
                sale_id=row["sale_id"],
                product_id=row["product_id"],
                quantity=row["quantity"],
                unit_price=row["unit_price"],
                discount=row["discount"],
                total=row["total"],
                product_name=row["product_name"],
                product_sku=row["product_sku"]
            ) for row in cursor.fetchall()]

    def _get_payments(self, sale_id: int) -> List[Payment]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM payments WHERE sale_id = ?", (sale_id,))
            return [Payment(
                id=row["id"],
                sale_id=row["sale_id"],
                payment_method=PaymentMethod(row["payment_method"]),
                amount=row["amount"],
                installments=row["installments"],
                card_brand=row["card_brand"],
                card_last4=row["card_last4"],
                transaction_id=row["transaction_id"],
                status=PaymentStatus(row["status"]),
                received_at=datetime.fromisoformat(row["received_at"]) if row["received_at"] else None
            ) for row in cursor.fetchall()]

    def _row_to_sale(self, row: Row) -> Sale:
        return Sale(
            id=row["id"],
            customer_id=row["customer_id"],
            user_id=row["user_id"],
            sale_number=row["sale_number"],
            subtotal=row["subtotal"],
            discount=row["discount"],
            tax=row["tax"],
            total=row["total"],
            payment_status=PaymentStatus(row["payment_status"]),
            sale_status=SaleStatus(row["sale_status"]),
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            customer_name=row["customer_name"] or "Consumidor Final",
            user_name=row["user_name"]
        )


class StockMovementRepository(BaseRepository):
    def create(self, movement: StockMovement) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO stock_movements (product_id, movement_type, quantity,
                   reference_type, reference_id, user_id, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (movement.product_id, movement.movement_type.value, movement.quantity,
                 movement.reference_type, movement.reference_id, movement.user_id, movement.notes)
            )
            return cursor.lastrowid

    def get_by_product(self, product_id: int, limit: int = 50) -> List[StockMovement]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT sm.*, p.name as product_name, p.sku as product_sku, u.full_name as user_name
                   FROM stock_movements sm
                   JOIN products p ON sm.product_id = p.id
                   JOIN users u ON sm.user_id = u.id
                   WHERE sm.product_id = ?
                   ORDER BY sm.created_at DESC LIMIT ?""",
                (product_id, limit)
            )
            return [self._row_to_movement(row) for row in cursor.fetchall()]

    def get_all(self, start_date: Optional[date] = None, end_date: Optional[date] = None,
                movement_type: Optional[StockMovementType] = None) -> List[StockMovement]:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = """SELECT sm.*, p.name as product_name, p.sku as product_sku, u.full_name as user_name
                       FROM stock_movements sm
                       JOIN products p ON sm.product_id = p.id
                       JOIN users u ON sm.user_id = u.id"""
            conditions = []
            params = []
            if start_date:
                conditions.append("date(sm.created_at) >= ?")
                params.append(start_date.isoformat())
            if end_date:
                conditions.append("date(sm.created_at) <= ?")
                params.append(end_date.isoformat())
            if movement_type:
                conditions.append("sm.movement_type = ?")
                params.append(movement_type.value)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY sm.created_at DESC"
            cursor.execute(query, params)
            return [self._row_to_movement(row) for row in cursor.fetchall()]

    def _row_to_movement(self, row: Row) -> StockMovement:
        return StockMovement(
            id=row["id"],
            product_id=row["product_id"],
            movement_type=StockMovementType(row["movement_type"]),
            quantity=row["quantity"],
            reference_type=row["reference_type"],
            reference_id=row["reference_id"],
            user_id=row["user_id"],
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            product_name=row["product_name"],
            product_sku=row["product_sku"],
            user_name=row["user_name"]
        )


class SettingRepository(BaseRepository):
    def get(self, key: str, default: str = "") -> str:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set(self, key: str, value: str, description: str = "") -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value, description) VALUES (?, ?, ?)",
                (key, value, description)
            )
            return cursor.rowcount > 0

    def get_all(self) -> List[Setting]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings ORDER BY key")
            return [Setting(key=row["key"], value=row["value"], description=row["description"])
                    for row in cursor.fetchall()]