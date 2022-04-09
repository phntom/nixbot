from dataclasses import dataclass, field


from datetime import datetime


@dataclass
class User:
    id: str
    create_at: int = field(default=0)
    update_at: int = field(default=0)
    delete_at: int = field(default=0)
    username: str = field(default='')
    email: str = field(default='')
    email_verified: bool = field(default=False)
    nickname: str = field(default='')
    first_name: str = field(default='')
    last_name: str = field(default='')
    position: str = field(default='')
    roles: str = field(default='')
    allow_marketing: bool = field(default=False)
    last_password_update: int = field(default=0)
    last_picture_update: int = field(default=0)
    failed_attempts: int = field(default=0)
    locale: str = field(default='')
    timezone: dict = field(default_factory=dict)
    mfa_active: bool = field(default=False)
    remote_id: str = field(default='')
    last_activity_at: int = field(default=0)
    is_bot: bool = field(default=False)
    bot_description: str = field(default='')
    bot_last_icon_update: int = field(default=0)
    terms_of_service_id: str = field(default='')
    terms_of_service_create_at: int = field(default=0)
    disable_welcome_email: bool = field(default=False)
    props: dict = field(default_factory=dict)
    notify_props: dict = field(default_factory=dict)


@dataclass
class ExtendedUser(User):
    status: str = field(default='')
    last_notified: dict = field(default_factory=dict)
    last_typing: datetime = field(default=datetime.fromtimestamp(0))
    teams: set = field(default_factory=set)
