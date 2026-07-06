from app.database.supabase import auth_supabase


def sign_in(email: str, password: str):
    return auth_supabase.auth.sign_in_with_password(
        {
            "email": email,
            "password": password,
        }
    )


def get_user_from_token(token: str):
    try:
        response = auth_supabase.auth.get_user(token)

        if response.user is None:
            return None

        return response.user

    except Exception:
        return None

def sign_up(email: str, password: str):
    return auth_supabase.auth.sign_up(
        {
            "email": email,
            "password": password,
        }
    )