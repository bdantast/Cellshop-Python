from typing import List, Optional
from datetime import date
from src.database.repositories import (
    ProductRepository, BrandRepository, CategoryRepository,
    PurchaseRepository, SaleRepository, SupplierRepository,
    CustomerRepository, StockMovementRepository
)
from src.models import (
    Product, Brand, Category, Purchase, PurchaseItem, PurchaseStatus,
    Sale, SaleItem, SaleStatus, Payment, PaymentStatus, PaymentMethod,
    Supplier, Customer, StockMovement, StockMovementType
)


class ProductController:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.brand_repo = BrandRepository()
        self.category_repo = CategoryRepository()

    def create_product(self, product: Product) -> tuple[bool, str, Optional[int]]:
        if not product.sku:
            return False, "SKU é obrigatório", None
        if not product.name:
            return False, "Nome é obrigatório", None
        if self.product_repo.get_by_sku(product.sku):
            return False, "SKU já cadastrado", None
        if product.sale_price < 0:
            return False, "Preço de venda não pode ser negativo", None
        if product.cost_price < 0:
            return False, "Preço de custo não pode ser negativo", None
        
        product_id = self.product_repo.create(product)
        return True, "Produto criado com sucesso", product_id

    def update_product(self, product: Product) -> tuple[bool, str]:
        if not product.name:
            return False, "Nome é obrigatório"
        existing = self.product_repo.get_by_sku(product.sku)
        if existing and existing.id != product.id:
            return False, "SKU já cadastrado para outro produto"
        
        if self.product_repo.update(product):
            return True, "Produto atualizado com sucesso"
        return False, "Erro ao atualizar produto"

    def delete_product(self, product_id: int) -> tuple[bool, str]:
        if self.product_repo.delete(product_id):
            return True, "Produto desativado com sucesso"
        return False, "Erro ao desativar produto"

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.product_repo.get_by_id(product_id)

    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        return self.product_repo.get_by_sku(sku)

    def list_products(self, active_only: bool = True) -> List[Product]:
        return self.product_repo.get_all(active_only=active_only)

    def search_products(self, term: str, active_only: bool = True) -> List[Product]:
        return self.product_repo.search(term, active_only=active_only)

    def get_low_stock_products(self) -> List[Product]:
        return self.product_repo.get_low_stock()

    def adjust_stock(self, product_id: int, new_quantity: int, user_id: int, notes: str = "") -> tuple[bool, str]:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return False, "Produto não encontrado"
        
        old_quantity = product.current_stock
        if new_quantity < 0:
            return False, "Quantidade não pode ser negativa"
        
        if self.product_repo.update_stock(product_id, new_quantity, StockMovementType.ADJUSTMENT):
            movement = StockMovement(
                product_id=product_id,
                movement_type=StockMovementType.ADJUSTMENT,
                quantity=new_quantity - old_quantity,
                reference_type="adjustment",
                user_id=user_id,
                notes=notes or f"Ajuste de estoque: {old_quantity} -> {new_quantity}"
            )
            StockMovementRepository().create(movement)
            return True, "Estoque ajustado com sucesso"
        return False, "Erro ao ajustar estoque"

    def list_brands(self) -> List[Brand]:
        return self.brand_repo.get_all()

    def create_brand(self, name: str) -> tuple[bool, str, Optional[int]]:
        if not name.strip():
            return False, "Nome da marca é obrigatório", None
        brand = Brand(name=name.strip())
        brand_id = self.brand_repo.create(brand)
        return True, "Marca criada com sucesso", brand_id

    def list_categories(self) -> List[Category]:
        return self.category_repo.get_all()

    def create_category(self, name: str, description: str = "") -> tuple[bool, str, Optional[int]]:
        if not name.strip():
            return False, "Nome da categoria é obrigatório", None
        category = Category(name=name.strip(), description=description)
        category_id = self.category_repo.create(category)
        return True, "Categoria criada com sucesso", category_id


class PurchaseController:
    def __init__(self):
        self.purchase_repo = PurchaseRepository()
        self.supplier_repo = SupplierRepository()
        self.product_repo = ProductRepository()

    def create_purchase(self, purchase: Purchase) -> tuple[bool, str, Optional[int]]:
        if not purchase.supplier_id:
            return False, "Fornecedor é obrigatório", None
        if not purchase.items:
            return False, "Adicione pelo menos um item", None
        
        for item in purchase.items:
            if item.quantity <= 0:
                return False, "Quantidade deve ser maior que zero", None
            if item.unit_cost < 0:
                return False, "Custo unitário não pode ser negativo", None
        
        purchase_id = self.purchase_repo.create(purchase)
        return True, "Compra criada com sucesso", purchase_id

    def receive_purchase(self, purchase_id: int, user_id: int) -> tuple[bool, str]:
        purchase = self.purchase_repo.get_by_id(purchase_id)
        if not purchase:
            return False, "Compra não encontrada"
        if purchase.status == PurchaseStatus.RECEIVED:
            return False, "Compra já recebida"
        if purchase.status == PurchaseStatus.CANCELLED:
            return False, "Compra cancelada não pode ser recebida"
        
        self.purchase_repo.receive_purchase(purchase_id, user_id)
        return True, "Compra recebida e estoque atualizado"

    def cancel_purchase(self, purchase_id: int) -> tuple[bool, str]:
        purchase = self.purchase_repo.get_by_id(purchase_id)
        if not purchase:
            return False, "Compra não encontrada"
        if purchase.status == PurchaseStatus.RECEIVED:
            return False, "Compra já recebida não pode ser cancelada"
        
        if self.purchase_repo.update_status(purchase_id, PurchaseStatus.CANCELLED):
            return True, "Compra cancelada com sucesso"
        return False, "Erro ao cancelar compra"

    def get_purchase(self, purchase_id: int) -> Optional[Purchase]:
        return self.purchase_repo.get_by_id(purchase_id)

    def list_purchases(self, status: Optional[PurchaseStatus] = None,
                       start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Purchase]:
        return self.purchase_repo.get_all(status, start_date, end_date)

    def list_suppliers(self, active_only: bool = True) -> List[Supplier]:
        return self.supplier_repo.get_all(active_only)

    def search_suppliers(self, term: str) -> List[Supplier]:
        return self.supplier_repo.search(term)

    def create_supplier(self, supplier: Supplier) -> tuple[bool, str, Optional[int]]:
        if not supplier.name:
            return False, "Nome do fornecedor é obrigatório", None
        supplier_id = self.supplier_repo.create(supplier)
        return True, "Fornecedor criado com sucesso", supplier_id


class SaleController:
    def __init__(self):
        self.sale_repo = SaleRepository()
        self.customer_repo = CustomerRepository()
        self.product_repo = ProductRepository()

    def create_sale(self, sale: Sale) -> tuple[bool, str, Optional[int]]:
        if not sale.items:
            return False, "Adicione pelo menos um item", None
        
        for item in sale.items:
            product = self.product_repo.get_by_id(item.product_id)
            if not product:
                return False, f"Produto ID {item.product_id} não encontrado", None
            if not product.is_active:
                return False, f"Produto {product.name} está inativo", None
            if product.current_stock < item.quantity:
                return False, f"Estoque insuficiente para {product.name}. Disponível: {product.current_stock}", None
        
        sale_id = self.sale_repo.create(sale)
        self._update_payment_status(sale_id)
        return True, "Venda criada com sucesso", sale_id

    def complete_sale(self, sale_id: int) -> tuple[bool, str]:
        sale = self.sale_repo.get_by_id(sale_id)
        if not sale:
            return False, "Venda não encontrada"
        if sale.sale_status != SaleStatus.OPEN:
            return False, "Venda não está aberta", None
        
        if self.sale_repo.update_status(sale_id, SaleStatus.COMPLETED):
            return True, "Venda finalizada com sucesso"
        return False, "Erro ao finalizar venda"

    def cancel_sale(self, sale_id: int, user_id: int) -> tuple[bool, str]:
        sale = self.sale_repo.get_by_id(sale_id)
        if not sale:
            return False, "Venda não encontrada"
        if sale.sale_status == SaleStatus.CANCELLED:
            return False, "Venda já cancelada"
        if sale.sale_status == SaleStatus.COMPLETED:
            return False, "Venda finalizada não pode ser cancelada diretamente"
        
        with self.sale_repo.__class__.__bases__[0]().get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sale_items WHERE sale_id = ?", (sale_id,))
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
                    (item["product_id"], StockMovementType.RETURN.value, item["quantity"],
                     "sale_return", sale_id, user_id, f"Cancelamento da venda #{sale.sale_number}")
                )
            cursor.execute(
                "UPDATE sales SET sale_status = ?, payment_status = ? WHERE id = ?",
                (SaleStatus.CANCELLED.value, PaymentStatus.REFUNDED.value, sale_id)
            )
        return True, "Venda cancelada e estoque restaurado"

    def add_payment(self, payment: Payment) -> tuple[bool, str]:
        sale = self.sale_repo.get_by_id(payment.sale_id)
        if not sale:
            return False, "Venda não encontrada"
        
        total_paid = sum(p.amount for p in sale.payments) + payment.amount
        if total_paid > sale.total + 0.01:
            return False, f"Valor excede o total da venda. Total: R$ {sale.total:.2f}, Pago: R$ {total_paid:.2f}"
        
        payment_id = self.sale_repo.add_payment(payment)
        self._update_payment_status(payment.sale_id)
        return True, "Pagamento registrado com sucesso"

    def _update_payment_status(self, sale_id: int) -> None:
        sale = self.sale_repo.get_by_id(sale_id)
        if not sale:
            return
        
        total_paid = sum(p.amount for p in sale.payments)
        if total_paid <= 0:
            status = PaymentStatus.PENDING
        elif total_paid >= sale.total - 0.01:
            status = PaymentStatus.PAID
        else:
            status = PaymentStatus.PARTIAL
        
        self.sale_repo.update_payment_status(sale_id, status)

    def get_sale(self, sale_id: int) -> Optional[Sale]:
        return self.sale_repo.get_by_id(sale_id)

    def list_sales(self, status: Optional[SaleStatus] = None,
                   payment_status: Optional[PaymentStatus] = None,
                   start_date: Optional[date] = None, end_date: Optional[date] = None,
                   customer_id: Optional[int] = None) -> List[Sale]:
        return self.sale_repo.get_all(status, payment_status, start_date, end_date, customer_id)

    def get_open_sales(self) -> List[Sale]:
        return self.sale_repo.get_open_sales()

    def list_customers(self) -> List[Customer]:
        return self.customer_repo.get_all()

    def search_customers(self, term: str) -> List[Customer]:
        return self.customer_repo.search(term)

    def create_customer(self, customer: Customer) -> tuple[bool, str, Optional[int]]:
        if not customer.name:
            return False, "Nome do cliente é obrigatório", None
        customer_id = self.customer_repo.create(customer)
        return True, "Cliente criado com sucesso", customer_id

    def get_product_for_sale(self, sku_or_id: str) -> Optional[Product]:
        if sku_or_id.isdigit():
            return self.product_repo.get_by_id(int(sku_or_id))
        return self.product_repo.get_by_sku(sku_or_id)


class ReportController:
    def __init__(self):
        self.sale_repo = SaleRepository()
        self.purchase_repo = PurchaseRepository()
        self.product_repo = ProductRepository()

    def get_dashboard_stats(self) -> dict:
        with self.sale_repo.__class__.__bases__[0]().get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as total, SUM(total) as revenue FROM sales WHERE sale_status = 'completed' AND date(created_at) = date('now')")
            today_sales = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as total, SUM(total) as revenue FROM sales WHERE sale_status = 'completed' AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')")
            month_sales = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as count FROM products WHERE is_active = 1 AND current_stock <= min_stock")
            low_stock = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as count FROM products WHERE is_active = 1")
            total_products = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as count FROM sales WHERE sale_status = 'open'")
            open_sales = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as count FROM purchases WHERE status = 'pending'")
            pending_purchases = cursor.fetchone()
            
            return {
                "today_sales_count": today_sales["total"] or 0,
                "today_sales_revenue": today_sales["revenue"] or 0,
                "month_sales_count": month_sales["total"] or 0,
                "month_sales_revenue": month_sales["revenue"] or 0,
                "low_stock_count": low_stock["count"] or 0,
                "total_products": total_products["count"] or 0,
                "open_sales_count": open_sales["count"] or 0,
                "pending_purchases_count": pending_purchases["count"] or 0,
            }

    def get_sales_report(self, start_date: date, end_date: date) -> dict:
        with self.sale_repo.__class__.__bases__[0]().get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT COUNT(*) as total_sales, SUM(total) as total_revenue,
                          SUM(subtotal) as total_subtotal, SUM(discount) as total_discount,
                          AVG(total) as avg_ticket
                   FROM sales
                   WHERE sale_status = 'completed' AND date(created_at) BETWEEN ? AND ?""",
                (start_date.isoformat(), end_date.isoformat())
            )
            summary = cursor.fetchone()
            
            cursor.execute(
                """SELECT payment_method, COUNT(*) as count, SUM(amount) as total
                   FROM payments p
                   JOIN sales s ON p.sale_id = s.id
                   WHERE s.sale_status = 'completed' AND date(s.created_at) BETWEEN ? AND ?
                   GROUP BY payment_method""",
                (start_date.isoformat(), end_date.isoformat())
            )
            payment_methods = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute(
                """SELECT p.name, SUM(si.quantity) as qty_sold, SUM(si.total) as revenue
                   FROM sale_items si
                   JOIN products p ON si.product_id = p.id
                   JOIN sales s ON si.sale_id = s.id
                   WHERE s.sale_status = 'completed' AND date(s.created_at) BETWEEN ? AND ?
                   GROUP BY p.id ORDER BY qty_sold DESC LIMIT 10""",
                (start_date.isoformat(), end_date.isoformat())
            )
            top_products = [dict(row) for row in cursor.fetchall()]
            
            return {
                "summary": dict(summary) if summary else {},
                "payment_methods": payment_methods,
                "top_products": top_products
            }

    def get_inventory_report(self) -> List[dict]:
        with self.product_repo.__class__.__bases__[0]().get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT p.sku, p.name, b.name as brand, c.name as category,
                          p.current_stock, p.min_stock, p.cost_price, p.sale_price,
                          (p.current_stock * p.cost_price) as stock_value
                   FROM products p
                   JOIN brands b ON p.brand_id = b.id
                   JOIN categories c ON p.category_id = c.id
                   WHERE p.is_active = 1
                   ORDER BY p.current_stock ASC"""
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_financial_summary(self, start_date: date, end_date: date) -> dict:
        with self.sale_repo.__class__.__bases__[0]().get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT SUM(total) as total_sales FROM sales
                   WHERE sale_status = 'completed' AND date(created_at) BETWEEN ? AND ?""",
                (start_date.isoformat(), end_date.isoformat())
            )
            sales = cursor.fetchone()
            
            cursor.execute(
                """SELECT SUM(total) as total_purchases FROM purchases
                   WHERE status = 'received' AND date(created_at) BETWEEN ? AND ?""",
                (start_date.isoformat(), end_date.isoformat())
            )
            purchases = cursor.fetchone()
            
            return {
                "total_sales": sales["total_sales"] or 0,
                "total_purchases": purchases["total_purchases"] or 0,
                "gross_profit": (sales["total_sales"] or 0) - (purchases["total_purchases"] or 0)
            }