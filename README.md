# CellShop - Sistema de Gestão para Loja de Celulares

Sistema completo de gestão de estoque, compras, vendas e relatórios para loja de celulares Android multimarcas, desenvolvido em Python com interface gráfica moderna.

## 🚀 Funcionalidades

### 📦 Gestão de Produtos/Estoque
- Cadastro completo de produtos (SKU, nome, marca, categoria, modelo, cor, armazenamento, RAM, tela, bateria)
- Controle de estoque em tempo real com alerta de estoque mínimo
- Ajuste de inventário com histórico de movimentações
- Busca avançada por SKU, nome, modelo ou marca
- Exportação para Excel

### 📥 Gestão de Compras/Fornecedores
- Cadastro de fornecedores (nome, contato, telefone, email, endereço, CNPJ)
- Criação de ordens de compra com múltiplos itens
- Recebimento de compras com atualização automática de estoque
- Controle de status: Pendente, Recebida, Cancelada
- Histórico de compras com filtros por data e status

### 💰 Gestão de Vendas/PDV
- Interface PDV (Ponto de Venda) intuitiva com 3 painéis
- Busca rápida de produtos com auto-complete
- Carrinho de compras com controle de quantidade
- Seleção de clientes (cadastro rápido incluso)
- **Múltiplas formas de pagamento**: Dinheiro, Cartão Débito, Cartão Crédito, PIX, Transferência, Parcelado
- Cálculo automático de troco
- Suporte a vendas a prazo/parceladas
- Impressão de cupom fiscal
- Controle de vendas em aberto (rascunhos)

### 📊 Relatórios e Dashboard
- Dashboard com métricas em tempo real (vendas hoje, mês, estoque baixo, vendas abertas)
- Relatório de vendas por período com resumo financeiro
- Análise de formas de pagamento
- Top 10 produtos mais vendidos
- Relatório de estoque completo com valorização
- Resumo financeiro (vendas, compras, lucro bruto, margem)
- Exportação de relatórios para Excel/CSV

### ⚙️ Configurações e Sistema
- Configurações da loja (nome, telefone, endereço, taxa padrão, moeda)
- Gestão de usuários com perfis (Admin, Gerente, Vendedor)
- Sistema de autenticação com bcrypt
- Troca de senha pelo próprio usuário
- Temas: Sistema, Claro, Escuro
- Backup e restauração do banco de dados
- Logs de auditoria

## 🛠️ Tecnologias

- **Python 3.10+**
- **CustomTkinter** - Interface gráfica moderna
- **SQLite** - Banco de dados local (zero configuração)
- **bcrypt** - Hash seguro de senhas
- **openpyxl** - Exportação para Excel
- **Pillow** - Manipulação de imagens
- **reportlab** - Geração de PDFs (futuro)

## 📁 Estrutura do Projeto

```
CellShop/
├── main.py                 # Ponto de entrada
├── requirements.txt        # Dependências
├── README.md              # Este arquivo
├── data/                  # Banco de dados SQLite (criado automaticamente)
│   └── cellshop.db
└── src/
    ├── database/
    │   ├── connection.py  # Conexão e schema do banco
    │   └── repositories.py # Camada de acesso a dados
    ├── models/
    │   └── __init__.py    # Dataclasses e Enums
    ├── controllers/
    │   ├── auth_controller.py      # Autenticação e autorização
    │   └── business_controllers.py # Regras de negócio
    └── views/
        ├── login_window.py   # Tela de login
        ├── main_window.py    # Janela principal com sidebar
        ├── products_view.py  # Gestão de produtos
        ├── purchases_view.py # Gestão de compras
        ├── sales_view.py     # PDV e vendas
        ├── reports_view.py   # Relatórios
        ├── settings_view.py  # Configurações
        └── widgets.py        # Componentes reutilizáveis
```

## 🚀 Como Executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar o sistema
```bash
python main.py
```

### 3. Login padrão
- **Usuário:** `admin`
- **Senha:** `admin123`

## 👥 Perfis de Usuário

| Perfil | Permissões |
|--------|------------|
| **Admin** | Acesso total, gestão de usuários, configurações, backup |
| **Gerente** | Produtos, compras, vendas, relatórios, clientes |
| **Vendedor** | Vendas/PDV, consulta de produtos e clientes |

## 💾 Banco de Dados

O sistema utiliza **SQLite** armazenado em `data/cellshop.db`. O banco é criado automaticamente na primeira execução com:
- 10 marcas pré-cadastradas (Samsung, Motorola, Xiaomi, Apple, LG, Asus, Realme, POCO, OnePlus, Nokia)
- 5 categorias (Smartphone, Acessório, Peça de Reposição, Wearable, Tablet)
- Usuário admin padrão
- Configurações padrão da loja

## 🔐 Segurança

- Senhas hasheadas com **bcrypt** (cost factor 12)
- Controle de acesso baseado em roles (RBAC)
- Sessão de usuário com last_login tracking
- Foreign keys ativas no SQLite
- Transações ACID em todas as operações

## 📦 Build Executável (opcional)

```bash
# Instalar PyInstaller
pip install pyinstaller

# Gerar executável
pyinstaller --onefile --windowed --icon=src/assets/icon.ico \
  --add-data "src;src" \
  --name "CellShop" \
  main.py
```

## 📝 Licença

Projeto educacional para portfólio. Livre para uso e modificação.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

**Desenvolvido com ❤️ para portfólio de desenvolvedor Python**