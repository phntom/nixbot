from nixbot.extensions.settings import ExtendedSettings


def get_settings_for_bot(bot):
    settings = ExtendedSettings(
        # kubectl port-forward -n chat svc/mattermost-integ 8065:8065
        MATTERMOST_URL='http://localhost',
        MATTERMOST_PORT=8065,
        SSL_VERIFY=False,
        WEBHOOK_HOST_ENABLED=True,
        WEBHOOK_HOST_URL="http://0.0.0.0",
        DEBUG=True,
        BOT_TEAM='test',
    )
    if bot == 'chad':
        settings.BOT_TOKEN='jxaftu5jmb8g9gq8r93msxwwha'
        settings.SETTINGS_CHANNEL='chad-settings'
        settings.TARGET_USER='phntom'
        return settings
    if bot == 'x':
        settings.BOT_TOKEN='p7u7ckmmbbd3frwatc4o1zbowe'
        return settings
