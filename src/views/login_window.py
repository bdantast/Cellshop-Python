import customtkinter as ctk
from tkinter import messagebox
from src.controllers.auth_controller import AuthController
from src.views.main_window import MainWindow


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.auth = AuthController()
        self.title("CellShop - Login")
        self.geometry("420x520")
        self.resizable(False, False)
        self.center_window()
        
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
        
    def center_window(self):
        self.update_idletasks()
        width = 420
        height = 520
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self, corner_radius=20)
        main_frame.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        logo_label = ctk.CTkLabel(
            main_frame, text="📱", font=ctk.CTkFont(size=60)
        )
        logo_label.grid(row=0, column=0, pady=(30, 10))
        
        title_label = ctk.CTkLabel(
            main_frame, text="CellShop", font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.grid(row=1, column=0, pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            main_frame, text="Sistema de Gestão de Celulares",
            font=ctk.CTkFont(size=14), text_color="gray"
        )
        subtitle_label.grid(row=2, column=0, pady=(0, 30))
        
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.grid(row=3, column=0, padx=40, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        self.username_entry = ctk.CTkEntry(
            form_frame, placeholder_text="Usuário", height=45,
            font=ctk.CTkFont(size=14), corner_radius=10
        )
        self.username_entry.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        
        self.password_entry = ctk.CTkEntry(
            form_frame, placeholder_text="Senha", height=45,
            font=ctk.CTkFont(size=14), corner_radius=10, show="•"
        )
        self.password_entry.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        self.remember_var = ctk.BooleanVar()
        remember_check = ctk.CTkCheckBox(
            form_frame, text="Lembrar-me", variable=self.remember_var,
            font=ctk.CTkFont(size=12)
        )
        remember_check.grid(row=2, column=0, pady=(0, 20), sticky="w")
        
        self.login_btn = ctk.CTkButton(
            form_frame, text="Entrar", height=45,
            font=ctk.CTkFont(size=15, weight="bold"), corner_radius=10,
            command=self.login
        )
        self.login_btn.grid(row=3, column=0, pady=(0, 20), sticky="ew")
        
        version_label = ctk.CTkLabel(
            main_frame, text="v1.0.0", font=ctk.CTkFont(size=11), text_color="gray"
        )
        version_label.grid(row=4, column=0, pady=(0, 20))
        
        self.username_entry.focus()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Erro", "Preencha usuário e senha")
            return
        
        self.login_btn.configure(state="disabled", text="Entrando...")
        self.update()
        
        success, msg = self.auth.login(username, password)
        
        self.login_btn.configure(state="normal", text="Entrar")
        
        if success:
            self.destroy()
            app = MainWindow(self.auth)
            app.mainloop()
        else:
            messagebox.showerror("Erro de Login", msg)
            self.password_entry.delete(0, "end")
            self.password_entry.focus()


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()