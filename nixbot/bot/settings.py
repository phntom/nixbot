from nixbot.extensions.settings import ExtendedSettings


def get_settings_for_bot(bot):
    return ExtendedSettings(
        # kubectl port-forward -n chat svc/mattermost-integ 8065:8065
        MATTERMOST_URL='http://localhost',
        MATTERMOST_PORT=8065,
        BOT_TOKEN='eprghcrzh7gpdf1czgkxrbz8nc',
        BOT_TEAM='test',
        SSL_VERIFY=False,
        WEBHOOK_HOST_ENABLED=True,
        WEBHOOK_HOST_URL="http://0.0.0.0",
        SETTINGS_CHANNEL='chad-settings',
        TARGET_USER='phntom',
        DEBUG=True,
    )

