from typing import Optional
from src.database.repositories import UserRepository
from src.models import User, UserRole


class AuthController:
    def __init__(self):
        self.user_repo = UserRepository()
        self._current_user: Optional[User] = None

    @property
    def current_user(self) -> Optional[User]:
        return self._current_user

    def login(self, username: str, password: str) -> tuple[bool, str]:
        user = self.user_repo.get_by_username(username)
        if not user:
            return False, "Usuário não encontrado"
        if not user.is_active:
            return False, "Usuário inativo"
        if not self.user_repo.verify_password(password, user.password_hash):
            return False, "Senha incorreta"
        
        self.user_repo.update_last_login(user.id)
        self._current_user = user
        return True, "Login realizado com sucesso"

    def logout(self) -> None:
        self._current_user = None

    def is_authenticated(self) -> bool:
        return self._current_user is not None

    def has_permission(self, required_role: UserRole) -> bool:
        if not self._current_user:
            return False
        role_hierarchy = {
            UserRole.SELLER: 1,
            UserRole.MANAGER: 2,
            UserRole.ADMIN: 3
        }
        return role_hierarchy.get(self._current_user.role, 0) >= role_hierarchy.get(required_role, 0)

    def change_password(self, user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False, "Usuário não encontrado"
        if not self.user_repo.verify_password(old_password, user.password_hash):
            return False, "Senha atual incorreta"
        if len(new_password) < 6:
            return False, "Nova senha deve ter pelo menos 6 caracteres"
        
        new_hash = self.user_repo.hash_password(new_password)
        if self.user_repo.update_password(user_id, new_hash):
            return True, "Senha alterada com sucesso"
        return False, "Erro ao alterar senha"

    def create_user(self, username: str, password: str, full_name: str, role: UserRole) -> tuple[bool, str]:
        if self.user_repo.get_by_username(username):
            return False, "Nome de usuário já existe"
        if len(password) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres"
        
        user = User(
            username=username,
            password_hash=self.user_repo.hash_password(password),
            full_name=full_name,
            role=role
        )
        self.user_repo.create(user)
        return True, "Usuário criado com sucesso"