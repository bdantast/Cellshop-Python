import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from src.controllers.auth_controller import AuthController
from src.controllers.business_controllers import SaleController
from src.models import Sale, SaleItem, SaleStatus, Payment, PaymentMethod, PaymentStatus, Customer, Product


class SalesView(ctk.CTkFrame):
    def __init__(self, parent, controller: SaleController, auth: AuthController):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.auth = auth
        self.current_sale = None
        self.sale_items = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.setup_ui()
        self.new_sale()
        
    def setup_ui(self):
        toolbar = ctk.CTkFrame(self, height=60, corner_radius=10)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkButton(toolbar, text="➕ Nova Venda", height=40, width=130,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     command=self.new_sale).pack(side="left", padx=15, pady=10)
        
        ctk.CTkButton(toolbar, text="📋 Vendas Abertas", height=40, width=140,
                     command=self.show_open_sales).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(toolbar, text="👥 Clientes", height=40, width=110,
                     command=self.manage_customers).pack(side="left", padx=10, pady=10)
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=3)
        content.grid_columnconfigure(2, weight=2)
        content.grid_rowconfigure(0, weight=1)
        
        left_frame = ctk.CTkFrame(content, corner_radius=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(left_frame, text="🔍 Buscar Produto", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.search_entry = ctk.CTkEntry(left_frame, placeholder_text="SKU, nome, modelo...", height=40,
                                        font=ctk.CTkFont(size=13))
        self.search_entry.grid(row=0, column=0, padx=15, pady=(50, 10), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)
        self.search_entry.focus()
        
        self.results_frame = ctk.CTkScrollableFrame(left_frame, label_text="Resultados")
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        center_frame = ctk.CTkFrame(content, corner_radius=10)
        center_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(1, weight=1)
        
        cart_header = ctk.CTkFrame(center_frame, fg_color="transparent")
        cart_header.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        cart_header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(cart_header, text="🛒 Carrinho", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w")
        
        self.customer_label = ctk.CTkLabel(cart_header, text="Cliente: Consumidor Final", font=ctk.CTkFont(size=12), text_color="gray")
        self.customer_label.grid(row=0, column=1, sticky="e")
        
        ctk.CTkButton(cart_header, text="👤", width=40, height=35, command=self.select_customer).grid(row=0, column=2, padx=5)
        ctk.CTkButton(cart_header, text="➕", width=40, height=35, command=self.add_customer).grid(row=0, column=3, padx=5)
        
        self.cart_frame = ctk.CTkScrollableFrame(center_frame, label_text="Itens")
        self.cart_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.cart_frame.grid_columnconfigure(0, weight=1)
        
        totals_frame = ctk.CTkFrame(center_frame, height=120, fg_color=("gray90", "gray15"), corner_radius=10)
        totals_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        totals_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(totals_frame, text="Subtotal:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=15, pady=8, sticky="w")
        self.subtotal_label = ctk.CTkLabel(totals_frame, text="R$ 0.00", font=ctk.CTkFont(size=14, weight="bold"))
        self.subtotal_label.grid(row=0, column=1, padx=15, pady=8, sticky="e")
        
        ctk.CTkLabel(totals_frame, text="Desconto:", font=ctk.CTkFont(size=13)).grid(row=1, column=0, padx=15, pady=8, sticky="w")
        self.discount_entry = ctk.CTkEntry(totals_frame, width=100, height=30, font=ctk.CTkFont(size=13), placeholder_text="0.00")
        self.discount_entry.grid(row=1, column=1, padx=15, pady=8, sticky="e")
        self.discount_entry.insert(0, "0.00")
        self.discount_entry.bind("<KeyRelease>", lambda e: self.update_totals())
        
        ctk.CTkLabel(totals_frame, text="Total:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=2, column=0, padx=15, pady=10, sticky="w")
        self.total_label = ctk.CTkLabel(totals_frame, text="R$ 0.00", font=ctk.CTkFont(size=20, weight="bold"), text_color="#27ae60")
        self.total_label.grid(row=2, column=1, padx=15, pady=10, sticky="e")
        
        right_frame = ctk.CTkFrame(content, corner_radius=10)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(right_frame, text="💳 Pagamento", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.payment_frame = ctk.CTkScrollableFrame(right_frame, label_text="Formas de Pagamento")
        self.payment_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.payment_frame.grid_columnconfigure(0, weight=1)
        
        self.payment_methods = []
        self.add_payment_row()
        
        pay_totals = ctk.CTkFrame(right_frame, height=140, fg_color=("gray90", "gray15"), corner_radius=10)
        pay_totals.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        pay_totals.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(pay_totals, text="Total a Pagar:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=15, pady=8, sticky="w")
        self.pay_total_label = ctk.CTkLabel(pay_totals, text="R$ 0.00", font=ctk.CTkFont(size=16, weight="bold"))
        self.pay_total_label.grid(row=0, column=1, padx=15, pady=8, sticky="e")
        
        ctk.CTkLabel(pay_totals, text="Total Pago:", font=ctk.CTkFont(size=13)).grid(row=1, column=0, padx=15, pady=8, sticky="w")
        self.pay_paid_label = ctk.CTkLabel(pay_totals, text="R$ 0.00", font=ctk.CTkFont(size=14, weight="bold"), text_color="#2980b9")
        self.pay_paid_label.grid(row=1, column=1, padx=15, pady=8, sticky="e")
        
        ctk.CTkLabel(pay_totals, text="Troco:", font=ctk.CTkFont(size=13)).grid(row=2, column=0, padx=15, pady=8, sticky="w")
        self.change_label = ctk.CTkLabel(pay_totals, text="R$ 0.00", font=ctk.CTkFont(size=14, weight="bold"), text_color="#e67e22")
        self.change_label.grid(row=2, column=1, padx=15, pady=8, sticky="e")
        
        btn_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        btn_frame.grid_columnconfigure((0,1), weight=1)
        
        ctk.CTkButton(btn_frame, text="💾 Salvar Rascunho", height=45, fg_color="#f39c12", hover_color="#d4ac0d",
                     command=self.save_draft).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="✅ Finalizar Venda", height=45, font=ctk.CTkFont(size=14, weight="bold"),
                     command=self.finalize_sale).grid(row=0, column=1, padx=5, sticky="ew")
        
    def on_search(self, event=None):
        term = self.search_entry.get().strip()
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        if len(term) < 2:
            return
            
        products = self.controller.product_repo.search(term) if term else []
        
        for prod in products[:10]:
            if prod.current_stock <= 0:
                continue
            btn = ctk.CTkButton(self.results_frame, text=f"{prod.sku} - {prod.name}\n{prod.brand_name} | Estoque: {prod.current_stock} | R$ {prod.sale_price:.2f}",
                               height=60, anchor="w", font=ctk.CTkFont(size=12),
                               fg_color=("gray90", "gray15"), hover_color=("gray80", "gray25"),
                               command=lambda p=prod: self.add_to_cart(p))
            btn.pack(fill="x", padx=5, pady=2)
            
    def add_to_cart(self, product: Product):
        for item in self.sale_items:
            if item.product_id == product.id:
                if item.quantity >= product.current_stock:
                    messagebox.showwarning("Estoque", f"Estoque insuficiente. Disponível: {product.current_stock}")
                    return
                item.quantity += 1
                item.total = item.quantity * item.unit_price
                self.refresh_cart()
                return
                
        item = SaleItem(
            product_id=product.id,
            quantity=1,
            unit_price=product.sale_price,
            discount=0,
            total=product.sale_price,
            product_name=product.name,
            product_sku=product.sku
        )
        self.sale_items.append(item)
        self.refresh_cart()
        self.search_entry.delete(0, "end")
        self.on_search()
        
    def refresh_cart(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()
            
        for idx, item in enumerate(self.sale_items):
            row = ctk.CTkFrame(self.cart_frame, fg_color=("gray90", "gray15") if idx % 2 == 0 else "transparent")
            row.pack(fill="x", padx=5, pady=2)
            row.grid_columnconfigure(0, weight=1)
            
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            info_frame.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(info_frame, text=f"{item.product_sku} - {item.product_name}", font=ctk.CTkFont(size=12, weight="bold"), anchor="w").grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(info_frame, text=f"R$ {item.unit_price:.2f} cada", font=ctk.CTkFont(size=11), text_color="gray", anchor="w").grid(row=1, column=0, sticky="w")
            
            qty_frame = ctk.CTkFrame(row, fg_color="transparent")
            qty_frame.grid(row=0, column=1, rowspan=2, padx=10)
            
            ctk.CTkButton(qty_frame, text="−", width=30, height=30, command=lambda i=item: self.change_qty(i, -1)).pack(side="left")
            ctk.CTkLabel(qty_frame, text=str(item.quantity), font=ctk.CTkFont(size=14, weight="bold"), width=40).pack(side="left")
            ctk.CTkButton(qty_frame, text="+", width=30, height=30, command=lambda i=item: self.change_qty(i, +1)).pack(side="left")
            
            ctk.CTkLabel(row, text=f"R$ {item.total:.2f}", font=ctk.CTkFont(size=14, weight="bold"), width=80).grid(row=0, column=2, rowspan=2, padx=10)
            
            ctk.CTkButton(row, text="🗑", width=35, height=30, fg_color="#e74c3c", hover_color="#c0392b",
                         command=lambda i=item: self.remove_item(i)).grid(row=0, column=3, rowspan=2, padx=5)
            
        self.update_totals()
        
    def change_qty(self, item: SaleItem, delta: int):
        new_qty = item.quantity + delta
        if new_qty <= 0:
            self.remove_item(item)
            return
        product = self.controller.get_product_for_sale(str(item.product_id))
        if product and new_qty > product.current_stock:
            messagebox.showwarning("Estoque", f"Estoque insuficiente. Disponível: {product.current_stock}")
            return
        item.quantity = new_qty
        item.total = item.quantity * item.unit_price
        self.refresh_cart()
        
    def remove_item(self, item: SaleItem):
        self.sale_items.remove(item)
        self.refresh_cart()
        
    def update_totals(self):
        subtotal = sum(item.total for item in self.sale_items)
        try:
            discount = float(self.discount_entry.get() or 0)
        except ValueError:
            discount = 0
        total = max(0, subtotal - discount)
        
        self.subtotal_label.configure(text=f"R$ {subtotal:.2f}")
        self.total_label.configure(text=f"R$ {total:.2f}")
        self.pay_total_label.configure(text=f"R$ {total:.2f}")
        self.update_payment_totals(total)
        
    def add_payment_row(self, method: PaymentMethod = PaymentMethod.CASH, amount: float = 0):
        row_frame = ctk.CTkFrame(self.payment_frame, fg_color=("gray90", "gray15"))
        row_frame.pack(fill="x", padx=5, pady=3)
        row_frame.grid_columnconfigure(1, weight=1)
        
        method_combo = ctk.CTkComboBox(row_frame, values=[m.value.replace("_", " ").title() for m in PaymentMethod],
                                      width=130, height=32, font=ctk.CTkFont(size=12))
        method_combo.set(method.value.replace("_", " ").title())
        method_combo.grid(row=0, column=0, padx=5, pady=5)
        
        amount_entry = ctk.CTkEntry(row_frame, placeholder_text="Valor", width=100, height=32, font=ctk.CTkFont(size=12))
        amount_entry.grid(row=0, column=1, padx=5, pady=5)
        if amount > 0:
            amount_entry.insert(0, f"{amount:.2f}")
            
        extra_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        extra_frame.grid(row=0, column=2, padx=5)
        
        installment_entry = ctk.CTkEntry(extra_frame, placeholder_text="Parcelas", width=70, height=32, font=ctk.CTkFont(size=12))
        installment_entry.insert(0, "1")
        
        def on_method_change(choice):
            if choice in ["Cartão Crédito", "Parcelado"]:
                installment_entry.pack(side="left", padx=2)
            else:
                installment_entry.pack_forget()
                
        method_combo.configure(command=on_method_change)
        on_method_change(method_combo.get())
        
        remove_btn = ctk.CTkButton(row_frame, text="×", width=30, height=30, fg_color="#e74c3c",
                                  command=lambda: self.remove_payment_row(row_data))
        remove_btn.grid(row=0, column=3, padx=5)
        
        row_data = {
            "frame": row_frame,
            "method_combo": method_combo,
            "amount_entry": amount_entry,
            "installment_entry": installment_entry
        }
        self.payment_methods.append(row_data)
        amount_entry.bind("<KeyRelease>", lambda e: self.update_payment_totals(self.get_sale_total()))
        
    def remove_payment_row(self, row_data):
        if len(self.payment_methods) <= 1:
            return
        row_data["frame"].destroy()
        self.payment_methods.remove(row_data)
        self.update_payment_totals(self.get_sale_total())
        
    def update_payment_totals(self, total):
        paid = 0
        for row in self.payment_methods:
            try:
                paid += float(row["amount_entry"].get() or 0)
            except ValueError:
                pass
        self.pay_paid_label.configure(text=f"R$ {paid:.2f}")
        change = paid - total
        self.change_label.configure(text=f"R$ {change:.2f}" if change > 0 else "R$ 0.00")
        
    def get_sale_total(self):
        subtotal = sum(item.total for item in self.sale_items)
        try:
            discount = float(self.discount_entry.get() or 0)
        except ValueError:
            discount = 0
        return max(0, subtotal - discount)
        
    def select_customer(self):
        customers = self.controller.list_customers()
        if not customers:
            messagebox.showinfo("Clientes", "Nenhum cliente cadastrado")
            return
            
        dialog = CustomerSelector(self, customers, self.set_customer)
        dialog.grab_set()
        
    def set_customer(self, customer: Customer):
        self.current_sale = self.current_sale or Sale(user_id=self.auth.current_user.id)
        self.current_sale.customer_id = customer.id
        self.customer_label.configure(text=f"Cliente: {customer.name}")
        
    def add_customer(self):
        CustomerForm(self, self.controller)
        
    def new_sale(self):
        self.current_sale = Sale(user_id=self.auth.current_user.id)
        self.sale_items = []
        self.customer_label.configure(text="Cliente: Consumidor Final")
        self.discount_entry.delete(0, "end")
        self.discount_entry.insert(0, "0.00")
        self.refresh_cart()
        self.clear_payments()
        self.add_payment_row()
        
    def clear_payments(self):
        for row in self.payment_methods:
            row["frame"].destroy()
        self.payment_methods = []
        
    def save_draft(self):
        if not self.sale_items:
            messagebox.showwarning("Aviso", "Adicione itens à venda")
            return
            
        sale = self.build_sale(SaleStatus.OPEN)
        success, msg, sale_id = self.controller.create_sale(sale)
        if success:
            messagebox.showinfo("Sucesso", f"Rascunho salvo! Venda #{sale_id}")
            self.new_sale()
        else:
            messagebox.showerror("Erro", msg)
            
    def finalize_sale(self):
        if not self.sale_items:
            messagebox.showwarning("Aviso", "Adicione itens à venda")
            return
            
        total = self.get_sale_total()
        paid = 0
        payments = []
        
        for row in self.payment_methods:
            try:
                amount = float(row["amount_entry"].get() or 0)
                if amount <= 0:
                    continue
                method_str = row["method_combo"].get().lower().replace(" ", "_")
                method = PaymentMethod(method_str)
                installments = int(row["installment_entry"].get() or 1)
                
                payments.append(Payment(
                    payment_method=method,
                    amount=amount,
                    installments=installments
                ))
                paid += amount
            except ValueError:
                continue
                
        if paid < total - 0.01:
            if not messagebox.askyesno("Pagamento Parcial", f"Total: R$ {total:.2f} | Pago: R$ {paid:.2f}\nFinalizar como pagamento parcial?"):
                return
                
        sale = self.build_sale(SaleStatus.COMPLETED, payments)
        success, msg, sale_id = self.controller.create_sale(sale)
        if success:
            messagebox.showinfo("Sucesso", f"Venda finalizada! #{sale_id}")
            self.print_receipt(sale_id)
            self.new_sale()
        else:
            messagebox.showerror("Erro", msg)
            
    def build_sale(self, status: SaleStatus, payments=None) -> Sale:
        subtotal = sum(item.total for item in self.sale_items)
        try:
            discount = float(self.discount_entry.get() or 0)
        except ValueError:
            discount = 0
        total = max(0, subtotal - discount)
        
        sale = Sale(
            customer_id=self.current_sale.customer_id if self.current_sale else None,
            user_id=self.auth.current_user.id,
            sale_number="",
            subtotal=subtotal,
            discount=discount,
            tax=0,
            total=total,
            payment_status=PaymentStatus.PAID if payments and sum(p.amount for p in payments) >= total - 0.01 else PaymentStatus.PARTIAL,
            sale_status=status,
            items=self.sale_items.copy(),
            payments=payments or []
        )
        return sale
        
    def print_receipt(self, sale_id):
        receipt = f"""
╔═══════════════════════════════╗
║      CELLSHOP - CUPOM        ║
║     Loja de Celulares        ║
╠═══════════════════════════════╣
"""
        for item in self.sale_items:
            receipt += f"║ {item.product_name[:20]:20s} {item.quantity}x R$ {item.unit_price:.2f}\n"
        receipt += f"╠═══════════════════════════════╣\n"
        receipt += f"║ Total: R$ {self.get_sale_total():.2f}\n"
        receipt += f"╚═══════════════════════════════╝\n"
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Cupom Fiscal")
        dialog.geometry("400x500")
        dialog.transient(self)
        dialog.grab_set()
        
        textbox = ctk.CTkTextbox(dialog, font=ctk.CTkFont(family="Consolas", size=12))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", receipt)
        textbox.configure(state="disabled")
        
        ctk.CTkButton(dialog, text="Imprimir", command=lambda: messagebox.showinfo("Impressão", "Enviado para impressora")).pack(pady=10)
        ctk.CTkButton(dialog, text="Fechar", command=dialog.destroy).pack(pady=5)
        
    def show_open_sales(self):
        OpenSalesDialog(self, self.controller, self.load_sale)
        
    def load_sale(self, sale: Sale):
        self.current_sale = sale
        self.sale_items = sale.items.copy()
        self.customer_label.configure(text=f"Cliente: {sale.customer_name}")
        self.discount_entry.delete(0, "end")
        self.discount_entry.insert(0, f"{sale.discount:.2f}")
        self.refresh_cart()
        self.clear_payments()
        for pay in sale.payments:
            self.add_payment_row(pay.payment_method, pay.amount)
            self.payment_methods[-1]["installment_entry"].delete(0, "end")
            self.payment_methods[-1]["installment_entry"].insert(0, str(pay.installments))
        self.update_payment_totals(sale.total)
        
    def manage_customers(self):
        CustomerManager(self, self.controller)


class CustomerSelector(ctk.CTkToplevel):
    def __init__(self, parent, customers, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Selecionar Cliente")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()
        self.center_window()
        
        ctk.CTkLabel(self, text="Selecione um cliente", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=15)
        
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for cust in customers:
            btn = ctk.CTkButton(self.list_frame, text=f"{cust.name} - {cust.phone or 'Sem telefone'}",
                               height=40, anchor="w", font=ctk.CTkFont(size=12),
                               command=lambda c=cust: self.select(c))
            btn.pack(fill="x", padx=5, pady=2)
            
        ctk.CTkButton(self, text="Consumidor Final", height=40, fg_color="gray",
                     command=lambda: self.select(None)).pack(fill="x", padx=20, pady=10)
        
    def center_window(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - 250
        y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - 200
        self.geometry(f"+{x}+{y}")
        
    def select(self, customer):
        if customer:
            self.callback(customer)
        else:
            self.callback(Customer(id=0, name="Consumidor Final"))
        self.destroy()


class CustomerForm(ctk.CTkToplevel):
    def __init__(self, parent, controller: SaleController, customer=None, callback=None):
        super().__init__(parent)
        self.controller = controller
        self.customer = customer
        self.callback = callback
        self.is_edit = customer is not None
        
        self.title("Editar Cliente" if self.is_edit else "Novo Cliente")
        self.geometry("500x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.center_window()
        self.setup_ui()
        if self.is_edit:
            self.load_data()
            
    def center_window(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - 250
        y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - 275
        self.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        scroll.grid_columnconfigure(1, weight=1)
        
        fields = [
            ("name", "Nome *", "entry"),
            ("phone", "Telefone", "entry"),
            ("email", "E-mail", "entry"),
            ("cpf_cnpj", "CPF/CNPJ", "entry"),
            ("address", "Endereço", "entry"),
            ("city", "Cidade", "entry"),
            ("state", "Estado", "entry"),
            ("zip_code", "CEP", "entry"),
            ("notes", "Observações", "text"),
        ]
        
        self.widgets = {}
        for row, (field, label, ftype) in enumerate(fields):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=13)).grid(row=row, column=0, padx=10, pady=8, sticky="w")
            if ftype == "text":
                w = ctk.CTkTextbox(scroll, font=ctk.CTkFont(size=13), height=80)
            else:
                w = ctk.CTkEntry(scroll, font=ctk.CTkFont(size=13), height=35)
            w.grid(row=row, column=1, padx=10, pady=8, sticky="ew")
            self.widgets[field] = w
            
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        btn_frame.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(btn_frame, text="Cancelar", height=40, fg_color="gray", command=self.destroy).grid(row=0, column=0, padx=10, sticky="ew")
        ctk.CTkButton(btn_frame, text="Salvar", height=40, command=self.save).grid(row=0, column=1, padx=10, sticky="ew")
        
    def load_data(self):
        c = self.customer
        self.widgets["name"].insert(0, c.name)
        if c.phone: self.widgets["phone"].insert(0, c.phone)
        if c.email: self.widgets["email"].insert(0, c.email)
        if c.cpf_cnpj: self.widgets["cpf_cnpj"].insert(0, c.cpf_cnpj)
        if c.address: self.widgets["address"].insert(0, c.address)
        if c.city: self.widgets["city"].insert(0, c.city)
        if c.state: self.widgets["state"].insert(0, c.state)
        if c.zip_code: self.widgets["zip_code"].insert(0, c.zip_code)
        if c.notes: self.widgets["notes"].insert("1.0", c.notes)
        
    def save(self):
        from src.models import Customer
        customer = Customer(
            id=self.customer.id if self.is_edit else None,
            name=self.widgets["name"].get().strip(),
            phone=self.widgets["phone"].get().strip() or None,
            email=self.widgets["email"].get().strip() or None,
            cpf_cnpj=self.widgets["cpf_cnpj"].get().strip() or None,
            address=self.widgets["address"].get().strip() or None,
            city=self.widgets["city"].get().strip() or None,
            state=self.widgets["state"].get().strip() or None,
            zip_code=self.widgets["zip_code"].get().strip() or None,
            notes=self.widgets["notes"].get("1.0", "end-1c").strip() or None
        )
        
        if not customer.name:
            messagebox.showerror("Erro", "Nome é obrigatório")
            return
            
        success, msg, _ = self.controller.create_customer(customer)
        if success:
            messagebox.showinfo("Sucesso", msg)
            if self.callback:
                self.callback()
            self.destroy()
        else:
            messagebox.showerror("Erro", msg)


class CustomerManager(ctk.CTkToplevel):
    def __init__(self, parent, controller: SaleController):
        super().__init__(parent)
        self.controller = controller
        self.title("Gerenciar Clientes")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        self.center_window()
        self.setup_ui()
        self.refresh()
        
    def center_window(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - 400
        y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - 300
        self.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        toolbar = ctk.CTkFrame(self, height=50)
        toolbar.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkButton(toolbar, text="➕ Novo Cliente", command=self.new_customer).pack(side="left", padx=5, pady=5)
        
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="right")
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Buscar...", width=200, height=35)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())
        
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.list_frame.grid_columnconfigure(0, weight=1)
        
    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        term = self.search_entry.get().strip()
        customers = self.controller.search_customers(term) if term else self.controller.list_customers()
        
        for idx, cust in enumerate(customers):
            row = ctk.CTkFrame(self.list_frame, fg_color=("gray90", "gray15") if idx % 2 == 0 else "transparent")
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(row, text=cust.name, font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            ctk.CTkLabel(row, text=cust.phone or "-", font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=10, pady=10)
            ctk.CTkLabel(row, text=cust.email or "-", font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=10, pady=10)
            ctk.CTkButton(row, text="Editar", width=80, height=30, command=lambda c=cust: self.edit_customer(c)).grid(row=0, column=3, padx=5, pady=5)
            ctk.CTkButton(row, text="Excluir", width=80, height=30, fg_color="#e74c3c", command=lambda c=cust: self.delete_customer(c)).grid(row=0, column=4, padx=5, pady=5)
            
    def new_customer(self):
        CustomerForm(self, self.controller, callback=self.refresh)
        
    def edit_customer(self, customer):
        CustomerForm(self, self.controller, customer, self.refresh)
        
    def delete_customer(self, customer):
        if messagebox.askyesno("Confirmar", f"Excluir cliente {customer.name}?"):
            self.controller.customer_repo.delete(customer.id)
            self.refresh()


class OpenSalesDialog(ctk.CTkToplevel):
    def __init__(self, parent, controller: SaleController, callback):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.title("Vendas em Aberto")
        self.geometry("800x500")
        self.transient(parent)
        self.grab_set()
        self.center_window()
        self.setup_ui()
        self.refresh()
        
    def center_window(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - 400
        y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - 250
        self.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.list_frame.grid_columnconfigure(0, weight=1)
        
    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        sales = self.controller.get_open_sales()
        if not sales:
            ctk.CTkLabel(self.list_frame, text="Nenhuma venda em aberto", font=ctk.CTkFont(size=14), text_color="gray").pack(pady=50)
            return
            
        for sale in sales:
            row = ctk.CTkFrame(self.list_frame)
            row.pack(fill="x", pady=5, padx=5)
            row.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(row, text=f"#{sale.sale_number}", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, padx=10, pady=10)
            ctk.CTkLabel(row, text=f"{sale.customer_name} - {len(sale.items)} itens", font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=10, pady=10, sticky="w")
            ctk.CTkLabel(row, text=f"R$ {sale.total:.2f}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#27ae60").grid(row=0, column=2, padx=10, pady=10)
            ctk.CTkButton(row, text="Carregar", width=100, height=30, command=lambda s=sale: self.load(s)).grid(row=0, column=3, padx=5, pady=5)
            ctk.CTkButton(row, text="Cancelar", width=100, height=30, fg_color="#e74c3c", command=lambda s=sale: self.cancel_sale(s)).grid(row=0, column=4, padx=5, pady=5)
            
    def load(self, sale):
        self.callback(sale)
        self.destroy()
        
    def cancel_sale(self, sale):
        if messagebox.askyesno("Confirmar", f"Cancelar venda #{sale.sale_number}?"):
            success, msg = self.controller.cancel_sale(sale.id, self.auth.current_user.id)
            if success:
                messagebox.showinfo("Sucesso", msg)
                self.refresh()
            else:
                messagebox.showerror("Erro", msg)