import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from src.controllers.auth_controller import AuthController
from src.controllers.business_controllers import ProductController, PurchaseController, SaleController, ReportController
from src.views.products_view import ProductsView
from src.views.purchases_view import PurchasesView
from src.views.sales_view import SalesView
from src.views.reports_view import ReportsView
from src.views.settings_view import SettingsView


class MainWindow(ctk.CTk):
    def __init__(self, auth_controller: AuthController):
        super().__init__()
        self.auth = auth_controller
        self.user = auth_controller.current_user
        
        self.product_ctrl = ProductController()
        self.purchase_ctrl = PurchaseController()
        self.sale_ctrl = SaleController()
        self.report_ctrl = ReportController()
        
        self.title(f"CellShop - {self.user.full_name} ({self.user.role.value})")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
        self.load_dashboard()
        
    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        self.setup_sidebar()
        
        self.main_area = ctk.CTkFrame(self, corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)
        
        self.header_frame = ctk.CTkFrame(self.main_area, height=70, corner_radius=10)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.setup_header()
        
        self.content_frame = ctk.CTkFrame(self.main_area, corner_radius=10)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        self.current_view = None
        
    def setup_sidebar(self):
        logo_label = ctk.CTkLabel(
            self.sidebar, text="📱 CellShop",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        
        user_label = ctk.CTkLabel(
            self.sidebar, text=f"👤 {self.user.full_name}",
            font=ctk.CTkFont(size=13), text_color="gray"
        )
        user_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
        
        role_label = ctk.CTkLabel(
            self.sidebar, text=self.user.role.value.capitalize(),
            font=ctk.CTkFont(size=11), text_color=("blue", "lightblue")
        )
        role_label.grid(row=2, column=0, padx=20, pady=(0, 30), sticky="w")
        
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊 Dashboard", self.show_dashboard),
            ("products", "📦 Produtos/Estoque", self.show_products),
            ("purchases", "📥 Compras", self.show_purchases),
            ("sales", "💰 Vendas/PDV", self.show_sales),
            ("reports", "📈 Relatórios", self.show_reports),
        ]
        
        if self.auth.has_permission(self.auth.current_user.role.__class__.ADMIN):
            nav_items.append(("settings", "⚙️ Configurações", self.show_settings))
        
        for i, (key, text, cmd) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar, text=text, height=45,
                font=ctk.CTkFont(size=14), corner_radius=10,
                anchor="w", command=cmd,
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray25")
            )
            btn.grid(row=3+i, column=0, padx=15, pady=5, sticky="ew")
            self.nav_buttons[key] = btn
        
        logout_btn = ctk.CTkButton(
            self.sidebar, text="🚪 Sair", height=45,
            font=ctk.CTkFont(size=14), corner_radius=10,
            fg_color="#e74c3c", hover_color="#c0392b",
            command=self.logout
        )
        logout_btn.grid(row=100, column=0, padx=15, pady=(20, 30), sticky="ew")
        
    def setup_header(self):
        self.page_title = ctk.CTkLabel(
            self.header_frame, text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.page_title.grid(row=0, column=0, padx=25, pady=15, sticky="w")
        
        self.datetime_label = ctk.CTkLabel(
            self.header_frame, text="",
            font=ctk.CTkFont(size=13), text_color="gray"
        )
        self.datetime_label.grid(row=0, column=1, padx=25, pady=15, sticky="e")
        self.update_datetime()
        
    def update_datetime(self):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.datetime_label.configure(text=now)
        self.after(1000, self.update_datetime)
        
    def set_active_nav(self, key: str):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=("gray80", "gray25"), text_color=("blue", "lightblue"))
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))
                
    def clear_content(self):
        if self.current_view:
            self.current_view.destroy()
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_dashboard(self):
        self.set_active_nav("dashboard")
        self.page_title.configure(text="Dashboard")
        self.clear_content()
        self.load_dashboard()
        
    def load_dashboard(self):
        stats = self.report_ctrl.get_dashboard_stats()
        
        cards_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        cards_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        cards_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        cards_data = [
            ("Vendas Hoje", f"{stats['today_sales_count']}", f"R$ {stats['today_sales_revenue']:.2f}", "#27ae60"),
            ("Vendas no Mês", f"{stats['month_sales_count']}", f"R$ {stats['month_sales_revenue']:.2f}", "#2980b9"),
            ("Estoque Baixo", f"{stats['low_stock_count']}", "Produtos", "#e67e22"),
            ("Vendas Abertas", f"{stats['open_sales_count']}", "Pendentes", "#8e44ad"),
        ]
        
        for i, (title, value, subtitle, color) in enumerate(cards_data):
            card = ctk.CTkFrame(cards_frame, corner_radius=15, border_width=2, border_color=color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13), text_color="gray").grid(row=0, column=0, pady=(15, 5))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=32, weight="bold"), text_color=color).grid(row=1, column=0)
            ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont(size=12), text_color="gray").grid(row=2, column=0, pady=(0, 15))
            
        low_stock_frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        low_stock_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        low_stock_frame.grid_columnconfigure(0, weight=1)
        low_stock_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(low_stock_frame, text="⚠️ Produtos com Estoque Baixo",
                    font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        low_products = self.product_ctrl.get_low_stock_products()[:10]
        if low_products:
            from customtkinter import CTkScrollableFrame
            scroll = CTkScrollableFrame(low_stock_frame, height=250)
            scroll.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
            scroll.grid_columnconfigure(0, weight=1)
            
            header = ctk.CTkFrame(scroll, fg_color=("gray85", "gray20"))
            header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            columns = ("SKU", "Produto", "Marca", "Estoque", "Mínimo")
            for i, col in enumerate(columns):
                header.grid_columnconfigure(i, weight=1)
                ctk.CTkLabel(header, text=col, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=10, pady=8)
            
            for idx, prod in enumerate(low_products):
                row_frame = ctk.CTkFrame(scroll, fg_color=("gray90", "gray15") if idx % 2 == 0 else "transparent")
                row_frame.grid(row=idx+1, column=0, sticky="ew", padx=5, pady=2)
                for i, col in enumerate(columns):
                    row_frame.grid_columnconfigure(i, weight=1)
                vals = [prod.sku, prod.name, prod.brand_name, str(prod.current_stock), str(prod.min_stock)]
                for i, val in enumerate(vals):
                    color = "#e74c3c" if i == 3 and prod.current_stock <= prod.min_stock else ("gray10", "gray90")
                    ctk.CTkLabel(row_frame, text=val, font=ctk.CTkFont(size=12), text_color=color).grid(row=0, column=i, padx=10, pady=8)
        else:
            ctk.CTkLabel(low_stock_frame, text="✅ Todos os produtos com estoque adequado",
                        font=ctk.CTkFont(size=14), text_color="green").grid(row=1, column=0, padx=20, pady=30)
            
    def show_products(self):
        self.set_active_nav("products")
        self.page_title.configure(text="Produtos / Estoque")
        self.clear_content()
        self.current_view = ProductsView(self.content_frame, self.product_ctrl, self.auth)
        self.current_view.grid(row=0, column=0, sticky="nsew")
        
    def show_purchases(self):
        self.set_active_nav("purchases")
        self.page_title.configure(text="Compras / Fornecedores")
        self.clear_content()
        self.current_view = PurchasesView(self.content_frame, self.purchase_ctrl, self.auth)
        self.current_view.grid(row=0, column=0, sticky="nsew")
        
    def show_sales(self):
        self.set_active_nav("sales")
        self.page_title.configure(text="Vendas / PDV")
        self.clear_content()
        self.current_view = SalesView(self.content_frame, self.sale_ctrl, self.auth)
        self.current_view.grid(row=0, column=0, sticky="nsew")
        
    def show_reports(self):
        self.set_active_nav("reports")
        self.page_title.configure(text="Relatórios")
        self.clear_content()
        self.current_view = ReportsView(self.content_frame, self.report_ctrl, self.auth)
        self.current_view.grid(row=0, column=0, sticky="nsew")
        
    def show_settings(self):
        self.set_active_nav("settings")
        self.page_title.configure(text="Configurações")
        self.clear_content()
        self.current_view = SettingsView(self.content_frame, self.auth)
        self.current_view.grid(row=0, column=0, sticky="nsew")
        
    def logout(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            self.auth.logout()
            self.destroy()
            from src.views.login_window import LoginWindow
            app = LoginWindow()
            app.mainloop()