#!/usr/bin/env python3
"""
CellShop - Sistema de Gestão para Loja de Celulares
===================================================
Sistema completo de gestão de estoque, compras, vendas e relatórios
para loja de celulares Android multimarcas.

Autor: Portfolio Project
Versão: 1.0.0
"""

import sys
import os
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import customtkinter as ctk
from src.views.login_window import LoginWindow
from src.database.connection import init_database


def setup_app():
    """Configurações iniciais da aplicação"""
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    
    # Configurações de DPI para Windows
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass


def main():
    """Ponto de entrada principal"""
    try:
        print("🚀 Iniciando CellShop...")
        print("📦 Inicializando banco de dados...")
        init_database()
        print("✅ Banco de dados pronto")
        
        print("🖥️  Iniciando interface gráfica...")
        app = LoginWindow()
        app.mainloop()
        
    except KeyboardInterrupt:
        print("\n👋 Encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        traceback.print_exc()
        input("Pressione Enter para sair...")


if __name__ == "__main__":
    setup_app()
    main()