import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import date
from src.controllers.auth_controller import AuthController, UserRole
from src.database.repositories import UserRepository, SettingRepository
from src.models import User, Setting
from src.database.connection import get_db_path


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, auth: AuthController):
        super().__init__(parent, fg_color="transparent")
        self.auth = auth
        self.user_repo = UserRepository()
        self.setting_repo = SettingRepository()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.setup_ui()
        
    def setup_ui(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=10)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        sidebar.grid_propagate(False)
        
        ctk.CTkLabel(sidebar, text="⚙️ Configurações", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        self.settings_tabs = {}
        tabs = [
            ("store", "🏪 Loja", self.show_store_settings),
            ("users", "👥 Usuários", self.show_users_settings),
            ("system", "🔧 Sistema", self.show_system_settings),
            ("backup", "💾 Backup", self.show_backup_settings),
        ]
        
        for key, text, cmd in tabs:
            btn = ctk.CTkButton(sidebar, text=text, height=40, anchor="w",
                               font=ctk.CTkFont(size=13),
                               fg_color="transparent", text_color=("gray10", "gray90"),
                               hover_color=("gray80", "gray25"), command=cmd)
            btn.pack(fill="x", padx=10, pady=5)
            self.settings_tabs[key] = btn
            
        self.content_frame = ctk.CTkFrame(self, corner_radius=10)
        self.content_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        self.current_tab = "store"
        self.show_store_settings()
        
    def set_active_tab(self, key: str):
        for k, btn in self.settings_tabs.items():
            if k == key:
                btn.configure(fg_color=("gray80", "gray25"), text_color=("blue", "lightblue"))
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        self.current_tab = key
        
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_store_settings(self):
        self.set_active_tab("store")
        self.clear_content()
        
        scroll = ctk.CTkScrollableFrame(self.content_frame)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        scroll.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(scroll, text="Configurações da Loja", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        settings = [
            ("store_name", "Nome da Loja", "entry", "CellShop - Loja de Celulares"),
            ("store_phone", "Telefone", "entry", "(11) 99999-9999"),
            ("store_address", "Endereço", "text", "Rua das Flores, 123 - São Paulo/SP"),
            ("tax_rate", "Taxa Padrão (%)", "entry", "0"),
            ("currency", "Moeda", "combo", "BRL"),
            ("low_stock_alert", "Alerta Estoque Baixo", "entry", "5"),
            ("receipt_footer", "Rodapé do Cupom", "text", "Obrigado pela preferência!"),
        ]
        
        self.store_widgets = {}
        for row, (key, label, ftype, default) in enumerate(settings, 1):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=13)).grid(row=row, column=0, padx=15, pady=10, sticky="w")
            
            value = self.setting_repo.get(key, default)
            
            if ftype == "entry":
                w = ctk.CTkEntry(scroll, font=ctk.CTkFont(size=13), height=35)
                w.insert(0, value)
            elif ftype == "text":
                w = ctk.CTkTextbox(scroll, font=ctk.CTkFont(size=13), height=80)
                w.insert("1.0", value)
            elif ftype == "combo":
                w = ctk.CTkComboBox(scroll, values=["BRL", "USD", "EUR"], font=ctk.CTkFont(size=13), height=35)
                w.set(value)
                
            w.grid(row=row, column=1, padx=15, pady=10, sticky="ew")
            self.store_widgets[key] = (w, ftype)
            
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.grid(row=len(settings)+1, column=0, columnspan=2, pady=20)
        btn_frame.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(btn_frame, text="Salvar", height=40, command=self.save_store_settings).grid(row=0, column=0, padx=10, sticky="ew")
        
    def save_store_settings(self):
        for key, (widget, ftype) in self.store_widgets.items():
            if ftype == "text":
                value = widget.get("1.0", "end-1c")
            else:
                value = widget.get()
            self.setting_repo.set(key, value)
        messagebox.showinfo("Sucesso", "Configurações salvas!")
        
    def show_users_settings(self):
        if not self.auth.has_permission(UserRole.ADMIN):
            messagebox.showerror("Acesso Negado", "Apenas administradores")
            return
            
        self.set_active_tab("users")
        self.clear_content()
        
        toolbar = ctk.CTkFrame(self.content_frame, height=50, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(toolbar, text="➕ Novo Usuário", command=self.new_user).pack(side="left")
        
        self.users_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.users_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.users_frame.grid_columnconfigure(0, weight=1)
        
        self.refresh_users()
        
    def refresh_users(self):
        for widget in self.users_frame.winfo_children():
            widget.destroy()
            
        users = self.user_repo.get_all(active_only=False)
        for idx, user in enumerate(users):
            row = ctk.CTkFrame(self.users_frame, fg_color=("gray90", "gray15") if idx % 2 == 0 else "transparent")
            row.grid(row=idx, column=0, sticky="ew", pady=2)
            row.grid_columnconfigure(1, weight=1)
            
            status = "🟢" if user.is_active else "🔴"
            role_colors = {UserRole.ADMIN: "#e74c3c", UserRole.MANAGER: "#f39c12", UserRole.SELLER: "#27ae60"}
            
            ctk.CTkLabel(row, text=status, font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=10, pady=10)
            ctk.CTkLabel(row, text=user.full_name, font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, padx=10, pady=10, sticky="w")
            ctk.CTkLabel(row, text=f"@{user.username}", font=ctk.CTkFont(size=12), text_color="gray").grid(row=0, column=2, padx=10, pady=10)
            
            role_badge = ctk.CTkLabel(row, text=user.role.value.capitalize(), font=ctk.CTkFont(size=11, weight="bold"),
                                     text_color=role_colors.get(user.role, "white"),
                                     fg_color=role_colors.get(user.role, "gray"), corner_radius=5)
            role_badge.grid(row=0, column=3, padx=10, pady=10)
            
            ctk.CTkLabel(row, text=user.last_login.strftime("%d/%m/%Y") if user.last_login else "Nunca", font=ctk.CTkFont(size=11), text_color="gray").grid(row=0, column=4, padx=10, pady=10)
            
            ctk.CTkButton(row, text="Editar", width=80, height=30, command=lambda u=user: self.edit_user(u)).grid(row=0, column=5, padx=5, pady=5)
            if user.id != self.auth.current_user.id:
                ctk.CTkButton(row, text="Excluir", width=80, height=30, fg_color="#e74c3c", command=lambda u=user: self.delete_user(u)).grid(row=0, column=6, padx=5, pady=5)
                
    def new_user(self):
        UserForm(self, self.user_repo, self.auth, callback=self.refresh_users)
        
    def edit_user(self, user):
        UserForm(self, self.user_repo, self.auth, user, self.refresh_users)
        
    def delete_user(self, user):
        if messagebox.askyesno("Confirmar", f"Desativar usuário {user.full_name}?"):
            self.user_repo.delete(user.id)
            self.refresh_users()
            
    def show_system_settings(self):
        self.set_active_tab("system")
        self.clear_content()
        
        scroll = ctk.CTkScrollableFrame(self.content_frame)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(scroll, text="Configurações do Sistema", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 20))
        
        theme_frame = ctk.CTkFrame(scroll, corner_radius=10)
        theme_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(theme_frame, text="🎨 Tema", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=10)
        
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode().lower())
        for mode in ["system", "light", "dark"]:
            ctk.CTkRadioButton(theme_frame, text=mode.capitalize(), variable=self.theme_var, value=mode,
                              command=lambda: ctk.set_appearance_mode(self.theme_var.get())).pack(anchor="w", padx=25, pady=5)
            
        pwd_frame = ctk.CTkFrame(scroll, corner_radius=10)
        pwd_frame.pack(fill="x", pady=10, padx=10)
        ctk.CTkLabel(pwd_frame, text="🔐 Alterar Senha", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=10)
        
        self.old_pwd = ctk.CTkEntry(pwd_frame, placeholder_text="Senha Atual", show="•", height=35)
        self.old_pwd.pack(fill="x", padx=15, pady=5)
        self.new_pwd = ctk.CTkEntry(pwd_frame, placeholder_text="Nova Senha (mín. 6 chars)", show="•", height=35)
        self.new_pwd.pack(fill="x", padx=15, pady=5)
        self.confirm_pwd = ctk.CTkEntry(pwd_frame, placeholder_text="Confirmar Nova Senha", show="•", height=35)
        self.confirm_pwd.pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(pwd_frame, text="Alterar Senha", command=self.change_password).pack(pady=10)
        
    def change_password(self):
        old = self.old_pwd.get()
        new = self.new_pwd.get()
        confirm = self.confirm_pwd.get()
        
        if not old or not new or not confirm:
            messagebox.showerror("Erro", "Preencha todos os campos")
            return
        if new != confirm:
            messagebox.showerror("Erro", "Senhas não coincidem")
            return
        if len(new) < 6:
            messagebox.showerror("Erro", "Nova senha deve ter pelo menos 6 caracteres")
            return
            
        success, msg = self.auth.change_password(self.auth.current_user.id, old, new)
        if success:
            messagebox.showinfo("Sucesso", msg)
            self.old_pwd.delete(0, "end")
            self.new_pwd.delete(0, "end")
            self.confirm_pwd.delete(0, "end")
        else:
            messagebox.showerror("Erro", msg)
            
    def show_backup_settings(self):
        self.set_active_tab("backup")
        self.clear_content()
        
        frame = ctk.CTkFrame(self.content_frame, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="💾 Backup e Restauração", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        ctk.CTkButton(frame, text="📥 Fazer Backup Agora", height=50, font=ctk.CTkFont(size=14, weight="bold"),
                     command=self.do_backup).pack(pady=10, padx=50, fill="x")
        
        ctk.CTkButton(frame, text="📤 Restaurar Backup", height=50, font=ctk.CTkFont(size=14),
                     fg_color="#f39c12", hover_color="#d4ac0d",
                     command=self.restore_backup).pack(pady=10, padx=50, fill="x")
        
        ctk.CTkLabel(frame, text="\nO backup salva o banco de dados completo (SQLite)\nem um arquivo .db com timestamp.", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=20)
        
    def do_backup(self):
        import shutil
        from datetime import datetime
        import os
        
        src = get_db_path()
        
        backup_dir = os.path.join(os.path.dirname(src), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        dst = os.path.join(backup_dir, f"cellshop_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        
        try:
            shutil.copy2(src, dst)
            messagebox.showinfo("Sucesso", f"Backup salvo em:\n{dst}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no backup: {e}")
            
    def restore_backup(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Database", "*.db"), ("Todos", "*.*")],
            title="Selecionar arquivo de backup"
        )
        if not file_path:
            return
            
        if messagebox.askyesno("Confirmar", "Isso substituirá TODOS os dados atuais. Continuar?"):
            import shutil
            try:
                shutil.copy2(file_path, get_db_path())
                messagebox.showinfo("Sucesso", "Backup restaurado! Reinicie o sistema.")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao restaurar: {e}")


class UserForm(ctk.CTkToplevel):
    def __init__(self, parent, user_repo: UserRepository, auth: AuthController, user: User = None, callback=None):
        super().__init__(parent)
        self.user_repo = user_repo
        self.auth = auth
        self.user = user
        self.callback = callback
        self.is_edit = user is not None
        
        self.title("Editar Usuário" if self.is_edit else "Novo Usuário")
        self.geometry("500x500")
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
        y = self.master.winfo_rooty() + (self.master.winfo_height() // 2) - 250
        self.geometry(f"+{x}+{y}")
        
    def setup_ui(self):
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        scroll.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(scroll, text="Usuário", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")
        
        fields = [
            ("username", "Usuário *", "entry"),
            ("full_name", "Nome Completo *", "entry"),
            ("role", "Perfil", "combo"),
        ]
        
        self.widgets = {}
        for row, (field, label, ftype) in enumerate(fields, 1):
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=13)).grid(row=row, column=0, padx=10, pady=10, sticky="w")
            if ftype == "combo":
                w = ctk.CTkComboBox(scroll, values=[r.value.capitalize() for r in UserRole], font=ctk.CTkFont(size=13), height=35)
            else:
                w = ctk.CTkEntry(scroll, font=ctk.CTkFont(size=13), height=35)
            w.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
            self.widgets[field] = w
            
        pwd_label = "Senha *" if not self.is_edit else "Nova Senha (deixe vazio para manter)"
        ctk.CTkLabel(scroll, text=pwd_label, font=ctk.CTkFont(size=13)).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.pwd_entry = ctk.CTkEntry(scroll, placeholder_text="Mín. 6 caracteres", show="•", font=ctk.CTkFont(size=13), height=35)
        self.pwd_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        
        self.active_switch = ctk.CTkSwitch(scroll, text="Usuário Ativo", font=ctk.CTkFont(size=13))
        self.active_switch.grid(row=5, column=0, columnspan=2, padx=10, pady=20, sticky="w")
        self.active_switch.select()
        
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        btn_frame.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(btn_frame, text="Cancelar", height=40, fg_color="gray", command=self.destroy).grid(row=0, column=0, padx=10, sticky="ew")
        ctk.CTkButton(btn_frame, text="Salvar", height=40, command=self.save).grid(row=0, column=1, padx=10, sticky="ew")
        
    def load_data(self):
        u = self.user
        self.widgets["username"].insert(0, u.username)
        self.widgets["username"].configure(state="disabled")
        self.widgets["full_name"].insert(0, u.full_name)
        self.widgets["role"].set(u.role.value.capitalize())
        if u.is_active: self.active_switch.select()
        else: self.active_switch.deselect()
        
    def save(self):
        username = self.widgets["username"].get().strip()
        full_name = self.widgets["full_name"].get().strip()
        role_str = self.widgets["role"].get().lower()
        
        if not username or not full_name:
            messagebox.showerror("Erro", "Usuário e nome são obrigatórios")
            return
            
        try:
            role = UserRole(role_str)
        except ValueError:
            messagebox.showerror("Erro", "Perfil inválido")
            return
            
        if not self.is_edit:
            pwd = self.pwd_entry.get()
            if not pwd or len(pwd) < 6:
                messagebox.showerror("Erro", "Senha obrigatória (mín. 6 chars)")
                return
            success, msg = self.auth.create_user(username, pwd, full_name, role)
            if success:
                messagebox.showinfo("Sucesso", msg)
                if self.callback: self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erro", msg)
        else:
            u = self.user
            u.full_name = full_name
            u.role = role
            u.is_active = self.active_switch.get() == 1
            if self.user_repo.update(u):
                pwd = self.pwd_entry.get()
                if pwd:
                    if len(pwd) < 6:
                        messagebox.showerror("Erro", "Nova senha deve ter pelo menos 6 caracteres")
                        return
                    self.user_repo.update_password(u.id, self.auth.hash_password(pwd))
                messagebox.showinfo("Sucesso", "Usuário atualizado!")
                if self.callback: self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erro", "Falha ao atualizar")