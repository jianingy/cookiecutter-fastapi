from datetime import datetime, timedelta
from typing import Any

import jwt

from {{ cookiecutter.project_slug }}.models.admin_user import AdminUser


def create_admin_user_access_token(admin_user: AdminUser, expire_secs: int, secret_key: str, algorithm: str) -> str:
    expired_at = datetime.now() + timedelta(seconds=expire_secs)
    user_data = {
        'id': admin_user.id,
        'username': admin_user.username,
        'exp': expired_at,
    }
    access_token = jwt.encode(user_data, secret_key, algorithm=algorithm)
    return access_token


def decode_access_token(token: str, secret_key: str, algorithm: str) -> dict[str, Any]:
    return jwt.decode(token, key=secret_key, algorithms=[algorithm])
