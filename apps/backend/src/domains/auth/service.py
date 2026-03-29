"""Auth service – Supabase auth logic."""

from ...core.supabase import get_supabase_client


class AuthService:
    def __init__(self):
        self.client = get_supabase_client()

    async def get_user_by_token(self, token: str) -> dict | None:
        """Validate a Supabase JWT and return user info."""
        try:
            response = self.client.auth.get_user(token)
            return {"id": response.user.id, "email": response.user.email}
        except Exception:
            return None
