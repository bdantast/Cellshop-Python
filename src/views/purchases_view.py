import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from src.controllers.auth_controller import AuthController
from src.controllers.business_controllers import PurchaseController
from src.models import Purchase, PurchaseItem, PurchaseStatus, Product, Supplier


class PurchasesView(ctk.CTkFrame):
    def __init__(self, parent, controller: PurchaseController, auth: AuthController):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.auth = auth
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.setup_ui()
        self.refresh_list()
        
    def setup_ui(self):
        toolbar = ctk.CTkFrame(self, height=60, corner_radius=10)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkButton(toolbar, text="➕ Nova Compra", height=40,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     command=self.open_form).pack(side="left", padx=15, pady=10)
        
        ctk.CTkButton(toolbar, text="🏢 Fornecedores", height=40, width=130,
                     command=self.manage_suppliers).pack(side="left", padx=10, pady=10)
        
        self.status_filter = ctk.CTkComboBox(toolbar, values=["Todas", "Pendente", "Recebida", "Cancelada"],
                                            width=140, height=40, command=lambda _: self.refresh_list())
        self.status_filter.set("Todas")
        self.status_filter.pack(side="right", padx=15, pady=10)
        
        list_frame = ctk.CTkFrame(self, corner_radius=10)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.tree = ctk.CTkScrollableFrame(list_frame)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tree.grid_columnconfigure(0, weight=1)
        
        columns = ("ID", "Nº Nota", "Fornecedor", "Data", "Itens", "Total", "Status", "Ações")
        self.header_frame = ctk.CTkFrame(self.tree, fg_color=("gray85", "gray20"))
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        for i, col in enumerate(columns):
            self.header_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(self.header_frame, text=col, font=ctk.CTkFont(weight="bold", size=12)).grid(
                row=0, column=i, padx=10, pady=8, sticky="w")
        
        self.rows_frame = ctk.CTkFrame(self.tree, fg_color="transparent")
        self.rows_frame.grid(row=1, column=0, sticky="nsew")
        self.rows_frame.grid_columnconfigure(0, weight=1)
        
    def refresh_list(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
            
        status_map = {"Pendente": PurchaseStatus.PENDING, "Recebida": PurchaseStatus.RECEIVED, "Cancelada": PurchaseStatus.CANCELLED}
        status = status_map.get(self.status_filter.get())
        
        purchases = self.controller.list_purchases(status=status)
        
        for idx, pur in enumerate(purchases):
            row = ctk.CTkFrame(self.rows_frame, fg_color=("gray90", "gray15") if idx % 2 == 0 else "transparent")
            row.grid(row=idx, column=0, sticky="ew", pady=1)
            row.grid_columnconfigure(0, weight=1)
            
            status_colors = {
                PurchaseStatus.PENDING: "#f39c12",
                PurchaseStatus.RECEIVED: "#27ae60",
                PurchaseStatus.CANCELLED: "#e74c3c"
            }
            status_color = status_colors.get(pur.status, "gray")
            
            values = [
                str(pur.id), pur.invoice_number or "-", pur.supplier_name,
                pur.created_at.strftime("%d/%m/%Y") if pur.created_at else "-",
                str(len(pur.items)), f"R$ {pur.total:.2f}", pur.status.value
            ]
            
            for i, val in enumerate(values):
                lbl = ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=12), anchor="w")
                lbl.grid(row=0, column=i, padx=10, pady=8, sticky="w")
                
            status_lbl = ctk.CTkLabel(row, text=pur.status.value, font=ctk.CTkFont(size=12, weight="bold"),
                                     text_color=status_color)
            status_lbl.grid(row=0, column=6, padx=10, pady=8)
            
            actions_frame = ctk.CTkFrame(row, fg_color="transparent")
            actions_frame.grid(row=0, column=7, padx=10, pady=5)
            
            ctk.CTkButton(actions_frame, text="👁", width=35, height=30,
                         command=lambda p=pur: self.view_purchase(p)).pack(side="left", padx=2)
            
            if pur.status == PurchaseStatus.PENDING:
                ctk.CTkButton(actions_frame, text="✅ Receber", width=80, height=30,
                             fg_color="#27ae60", hover_color="#219a52",
                             command=lambda p=pur: self.receive_purchase(p)).pack(side="left", padx=2)
                ctk.CTkButton(actions_frame, text="❌", width=35, height=30,
                             fg_color="#e74c3c", hover_color="#c0392b",
                             command=lambda p=pur: self.cancel_purchase(p)).pack(side="left", padx=2)
                
    def open_form(self):
        PurchaseForm(self, self.controller, callback=self.refresh_list)
        
    def view_purchase(self, purchase: Purchase):
        PurchaseDetailDialog(self, purchase)
        
    def receive_purchase(self, purchase: Purchase):
        if messagebox.askyesno("Confirmar", f"Receber compra #{purchase.invoice_number or purchase.id}?"):
            success, msg = self.controller.receive_purchase(purchase.id, self.auth.current_user.id)
            messagebox.showinfo("Resultado", msg)
            self.refresh_list()
            
    def cancel_purchase(self, purchase: Purchase):
        if messagebox.askyesno("Confirmar", f"Cancelar compra #{purchase.invoice_number or purchase.id}?"):
            success, msg = self.controller.cancel_purchase(purchase.id)
            messagebox.showinfo("Resultado", msg)
            self.refresh_list()
            
    def manage_suppliers(self):
        SupplierManager(self, self.controller)


class PurchaseForm(ctk.CTkToplevel):
    def __init__(self, parent, controller: PurchaseController, callback=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.items = []
        
        self.title("Nova Compra")
        self.geometry("900x700")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.center_window()
        
        self.suppliers = controller.list_suppliers()
        self.products = controller.product_repo.get_all(active_only=True)
        
        self.setup_ui()
        
    def center_window(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - 450
        y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - 350
        self.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        top_frame = ctk.CTkFrame(self, height=120, corner_radius=10)
        top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(top_frame, text="Fornecedor:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.supplier_combo = ctk.CTkComboBox(top_frame, values=[s.name for s in self.suppliers],
                                             font=ctk.CTkFont(size=13), height=35, width=300)
        self.supplier_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(top_frame, text="Nº Nota:", font=ctk.CTkFont(size=13)).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.invoice_entry = ctk.CTkEntry(top_frame, font=ctk.CTkFont(size=13), height=35, width=150)
        self.invoice_entry.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(top_frame, text="Data Nota:", font=ctk.CTkFont(size=13)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(top_frame, font=ctk.CTkFont(size=13), height=35, width=150,
                                      placeholder_text="DD/MM/AAAA")
        self.date_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.date_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        
        items_frame = ctk.CTkFrame(self, corner_radius=10)
        items_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        items_frame.grid_columnconfigure(0, weight=1)
        items_frame.grid_rowconfigure(1, weight=1)
        
        add_frame = ctk.CTkFrame(items_frame, height=60, fg_color="transparent")
        add_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        add_frame.grid_columnconfigure(1, weight=1)
        add_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(add_frame, text="Produto:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=5, sticky="w")
        self.product_combo = ctk.CTkComboBox(add_frame, values=[f"{p.sku} - {p.name}" for p in self.products],
                                            font=ctk.CTkFont(size=13), height=35, width=300)
        self.product_combo.grid(row=0, column=1, padx=5, sticky="ew")
        
        ctk.CTkLabel(add_frame, text="Qtd:", font=ctk.CTkFont(size=13)).grid(row=0, column=2, padx=5, sticky="w")
        self.qty_entry = ctk.CTkEntry(add_frame, font=ctk.CTkFont(size=13), height=35, width=80, placeholder_text="1")
        self.qty_entry.grid(row=0, column=3, padx=5, sticky="w")
        self.qty_entry.insert(0, "1")
        
        ctk.CTkLabel(add_frame, text="Custo:", font=ctk.CTkFont(size=13)).grid(row=0, column=4, padx=5, sticky="w")
        self.cost_entry = ctk.CTkEntry(add_frame, font=ctk.CTkFont(size=13), height=35, width=100, placeholder_text="0.00")
        self.cost_entry.grid(row=0, column=5, padx=5, sticky="w")
        
        ctk.CTkButton(add_frame, text="➕ Adicionar", height=35, width=110,
                     command=self.add_item).grid(row=0, column=6, padx=10)
        
        self.items_list = ctk.CTkScrollableFrame(items_frame, height=350)
        self.items_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.items_list.grid_columnconfigure(0, weight=1)
        
        self.items_header = ctk.CTkFrame(self.items_list, fg_color=("gray85", "gray20"))
        self.items_header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        item_cols = ["Produto", "Qtd", "Custo Unit.", "Total", "Ação"]
        for i, col in enumerate(item_cols):
            self.items_header.grid_columnconfigure(i, weight=1 if i == 0 else 0)
            ctk.CTkLabel(self.items_header, text=col, font=ctk.CTkFont(weight="bold", size=12)).grid(
                row=0, column=i, padx=10, pady=8, sticky="w")
                
        self.items_rows = ctk.CTkFrame(self.items_list, fg_color="transparent")
        self.items_rows.grid(row=1, column=0, sticky="nsew")
        self.items_rows.grid_columnconfigure(0, weight=1)
        
        bottom_frame = ctk.CTkFrame(self, height=100, corner_radius=10)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        bottom_frame.grid_columnconfigure(1, weight=1)
        
        self.subtotal_label = ctk.CTkLabel(bottom_frame, text="Subtotal: R$ 0.00", font=ctk.CTkFont(size=16, weight="bold"))
        self.subtotal_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        ctk.CTkLabel(bottom_frame, text="Desconto:", font=ctk.CTkFont(size=13)).grid(row=0, column=1, padx=10, sticky="e")
        self.discount_entry = ctk.CTkEntry(bottom_frame, font=ctk.CTkFont(size=13), height=35, width=100, placeholder_text="0.00")
        self.discount_entry.grid(row=0, column=2, padx=10, sticky="e")
        self.discount_entry.insert(0, "0.00")
        self.discount_entry.bind("<KeyRelease>", lambda e: self.update_totals())
        
        ctk.CTkLabel(bottom_frame, text="Imposto:", font=ctk.CTkFont(size=13)).grid(row=1, column=1, padx=10, sticky="e")
        self.tax_entry = ctk.CTkEntry(bottom_frame, font=ctk.CTkFont(size=13), height=35, width=100, placeholder_text="0.00")
        self.tax_entry.grid(row=1, column=2, padx=10, sticky="e")
        self.tax_entry.insert(0, "0.00")
        self.tax_entry.bind("<KeyRelease>", lambda e: self.update_totals())
        
        self.total_label = ctk.CTkLabel(bottom_frame, text="Total: R$ 0.00", font=ctk.CTkFont(size=18, weight="bold"), text_color="#27ae60")
        self.total_label.grid(row=1, column=0, padx=20, pady=15, sticky="w")
        
        btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=3, rowspan=2, padx=20, sticky="e")
        ctk.CTkButton(btn_frame, text="Cancelar", height=40, width=120, fg_color="gray", command=self.destroy).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Salvar Compra", height=40, width=140, command=self.save).pack(side="left", padx=5)
        
    def add_item(self):
        sel = self.product_combo.get()
        if not sel:
            return
        try:
            sku = sel.split(" - ")[0]
            product = next(p for p in self.products if p.sku == sku)
        except:
            return
            
        try:
            qty = int(self.qty_entry.get() or 1)
            cost = float(self.cost_entry.get() or 0)
        except ValueError:
            return
            
        if qty <= 0 or cost < 0:
            return
            
        for item in self.items:
            if item.product_id == product.id:
                item.quantity += qty
                item.unit_cost = cost
                item.total = item.quantity * item.unit_cost
                self.refresh_items_list()
                return
                
        item = PurchaseItem(
            product_id=product.id,
            quantity=qty,
            unit_cost=cost,
            total=qty * cost,
            product_name=product.name,
            product_sku=product.sku
        )
        self.items.append(item)
        self.refresh_items_list()
        self.qty_entry.delete(0, "end")
        self.qty_entry.insert(0, "1")
        self.cost_entry.delete(0, "end")
        
    def refresh_items_list(self):
        for widget in self.items_rows.winfo_children():
            widget.destroy()
            
        for idx, item in enumerate(self.items):
            row = ctk.CTkFrame(self.items_rows, fg_color=("gray90", "gray15") if idx % 2 == 0 else "transparent")
            row.grid(row=idx, column=0, sticky="ew", pady=1)
            row.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(row, text=f"{item.product_sku} - {item.product_name}", font=ctk.CTkFont(size=12), anchor="w").grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(row, text=str(item.quantity), font=ctk.CTkFont(size=12)).grid(row=0, column=1, padx=10, pady=8)
            ctk.CTkLabel(row, text=f"R$ {item.unit_cost:.2f}", font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=10, pady=8)
            ctk.CTkLabel(row, text=f"R$ {item.total:.2f}", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=3, padx=10, pady=8)
            ctk.CTkButton(row, text="🗑", width=35, height=28, fg_color="#e74c3c", hover_color="#c0392b",
                         command=lambda i=item: self.remove_item(i)).grid(row=0, column=4, padx=10, pady=5)
            
        self.update_totals()
        
    def remove_item(self, item: PurchaseItem):
        self.items.remove(item)
        self.refresh_items_list()
        
    def update_totals(self):
        subtotal = sum(item.total for item in self.items)
        try:
            discount = float(self.discount_entry.get() or 0)
            tax = float(self.tax_entry.get() or 0)
        except ValueError:
            discount = 0
            tax = 0
        total = subtotal - discount + tax
        self.subtotal_label.configure(text=f"Subtotal: R$ {subtotal:.2f}")
        self.total_label.configure(text=f"Total: R$ {total:.2f}")
        
    def save(self):
        if not self.supplier_combo.get():
            messagebox.showerror("Erro", "Selecione um fornecedor")
            return
        if not self.items:
            messagebox.showerror("Erro", "Adicione pelo menos um item")
            return
            
        supplier = next(s for s in self.suppliers if s.name == self.supplier_combo.get())
        
        try:
            invoice_date = None
            if self.date_entry.get():
                d, m, y = self.date_entry.get().split("/")
                invoice_date = date(int(y), int(m), int(d))
        except:
            invoice_date = date.today()
            
        purchase = Purchase(
            supplier_id=supplier.id,
            user_id=self.auth.current_user.id,
            invoice_number=self.invoice_entry.get().strip() or None,
            invoice_date=invoice_date,
            subtotal=sum(item.total for item in self.items),
            discount=float(self.discount_entry.get() or 0),
            tax=float(self.tax_entry.get() or 0),
            total=sum(item.total for item in self.items) - float(self.discount_entry.get() or 0) + float(self.tax_entry.get() or 0),
            status=PurchaseStatus.PENDING,
            items=self.items
        )
        
        success, msg, _ = self.controller.create_purchase(purchase)
        if success:
            messagebox.showinfo("Sucesso", msg)
            if self.callback:
                self.callback()
            self.destroy()
        else:
            messagebox.showerror("Erro", msg)


class PurchaseDetailDialog(ctk.CTkToplevel):
    def __init__(self, parent, purchase: Purchase):
        super().__init__(parent)
        self.title(f"Compra #{purchase.invoice_number or purchase.id}")
        self.geometry("700x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.center_window()
        
        ctk.CTkLabel(self, text=f"Fornecedor: {purchase.supplier_name}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        ctk.CTkLabel(self, text=f"Data: {purchase.created_at.strftime('%d/%m/%Y %H:%M') if purchase.created_at else '-'}", font=ctk.CTkFont(size=12)).pack()
        ctk.CTkLabel(self, text=f"Status: {purchase.status.value}", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        
        list_frame = ctk.CTkScrollableFrame(self)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for item in purchase.items:
            row = ctk.CTkFrame(list_frame)
            row.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(row, text=f"{item.product_sku} - {item.product_name}", font=ctk.CTkFont(size=12), anchor="w").pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(row, text=f"Qtd: {item.quantity}", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"R$ {item.unit_cost:.2f}", font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"Total: R$ {item.total:.2f}", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=10)
            
        ctk.CTkLabel(self, text=f"Total: R$ {purchase.total:.2f}", font=ctk.CTkFont(size=16, weight="bold"), text_color="#27ae60").pack(pady=10)
        ctk.CTkButton(self, text="Fechar", command=self.destroy).pack(pady=10)
        
    def center_window(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() // 2) - 350
        y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - 250
        self.geometry(f"+{x}+{y}")


class SupplierManager(ctk.CTkToplevel):
    def __init__(self, parent, controller: PurchaseController):
        super().__init__(parent)
        self.controller = controller
        self.title("Gerenciar Fornecedores")
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
        ctk.CTkButton(toolbar, text="➕ Novo Fornecedor", command=self.new_supplier).pack(side="left", padx=5, pady=5)
        
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.list_frame.grid_columnconfigure(0, weight=1)
        
    def refresh(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        suppliers = self.controller.supplier_repo.get_all(active_only=False)
        for idx, sup in enumerate(suppliers):
            row = ctk.CTkFrame(self.list_frame, fg_color=("gray90", "gray15") if idx % 2 == 0 else "transparent")
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(1, weight=1)
            
            status = "🟢" if sup.is_active else "🔴"
            ctk.CTkLabel(row, text=status, font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=10, pady=10)
            ctk.CTkLabel(row, text=sup.name, font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, padx=10, pady=10, sticky="w")
            ctk.CTkLabel(row, text=sup.contact_name or "-", font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=10, pady=10)
            ctk.CTkLabel(row, text=sup.phone or "-", font=ctk.CTkFont(size=12)).grid(row=0, column=3, padx=10, pady=10)
            ctk.CTkButton(row, text="Editar", width=80, height=30, command=lambda s=sup: self.edit_supplier(s)).grid(row=0, column=4, padx=5, pady=5)
            ctk.CTkButton(row, text="Excluir", width=80, height=30, fg_color="#e74c3c", command=lambda s=sup: self.delete_supplier(s)).grid(row=0, column=5, padx=5, pady=5)
            
    def new_supplier(self):
        SupplierForm(self, self.controller, callback=self.refresh)
        
    def edit_supplier(self, supplier):
        SupplierForm(self, self.controller, supplier, self.refresh)
        
    def delete_supplier(self, supplier):
        if messagebox.askyesno("Confirmar", f"Desativar fornecedor {supplier.name}?"):
            self.controller.supplier_repo.delete(supplier.id)
            self.refresh()


class SupplierForm(ctk.CTkToplevel):
    def __init__(self, parent, controller: PurchaseController, supplier=None, callback=None):
        super().__init__(parent)
        self.controller = controller
        self.supplier = supplier
        self.callback = callback
        self.is_edit = supplier is not None
        
        self.title("Editar Fornecedor" if self.is_edit else "Novo Fornecedor")
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
            ("name", "Nome *", "entry", {}),
            ("contact_name", "Contato", "entry", {}),
            ("phone", "Telefone", "entry", {}),
            ("email", "E-mail", "entry", {}),
            ("address", "Endereço", "entry", {}),
            ("cnpj", "CNPJ", "entry", {}),
        ]
        
        self.widgets = {}
        for row, (field, label, ftype, opts) in enumerate(fields):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=13)).grid(row=row, column=0, padx=10, pady=10, sticky="w")
            w = ctk.CTkEntry(scroll, font=ctk.CTkFont(size=13), height=35)
            w.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
            self.widgets[field] = w
            
        self.active_switch = ctk.CTkSwitch(scroll, text="Fornecedor Ativo", font=ctk.CTkFont(size=13))
        self.active_switch.grid(row=len(fields), column=0, columnspan=2, padx=10, pady=20, sticky="w")
        self.active_switch.select()
        
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
        btn_frame.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(btn_frame, text="Cancelar", height=40, fg_color="gray", command=self.destroy).grid(row=0, column=0, padx=10, sticky="ew")
        ctk.CTkButton(btn_frame, text="Salvar", height=40, command=self.save).grid(row=0, column=1, padx=10, sticky="ew")
        
    def load_data(self):
        s = self.supplier
        self.widgets["name"].insert(0, s.name)
        self.widgets["contact_name"].insert(0, s.contact_name or "")
        self.widgets["phone"].insert(0, s.phone or "")
        self.widgets["email"].insert(0, s.email or "")
        self.widgets["address"].insert(0, s.address or "")
        self.widgets["cnpj"].insert(0, s.cnpj or "")
        if s.is_active: self.active_switch.select()
        else: self.active_switch.deselect()
        
    def save(self):
        from src.models import Supplier
        supplier = Supplier(
            id=self.supplier.id if self.is_edit else None,
            name=self.widgets["name"].get().strip(),
            contact_name=self.widgets["contact_name"].get().strip() or None,
            phone=self.widgets["phone"].get().strip() or None,
            email=self.widgets["email"].get().strip() or None,
            address=self.widgets["address"].get().strip() or None,
            cnpj=self.widgets["cnpj"].get().strip() or None,
            is_active=self.active_switch.get() == 1
        )
        
        if not supplier.name:
            messagebox.showerror("Erro", "Nome é obrigatório")
            return
            
        if self.is_edit:
            self.controller.supplier_repo.update(supplier)
        else:
            self.controller.supplier_repo.create(supplier)
            
        if self.callback:
            self.callback()
        self.destroy()