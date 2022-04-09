import logging
from datetime import datetime, timedelta

from mmpy_bot import listen_to, Message, listen_webhook, WebHookEvent, ActionEvent

from nixbot.extensions.plugin import ExtendedPlugin

log = logging.getLogger(__name__)


class Presence(ExtendedPlugin):
    webhook_name = 'presence_notified'

    def __init__(self):
        super().__init__()
        self.notify_about_user = {}

    @listen_to(r"^user is now online$")
    async def user_online(self, message: Message):
        if message.id != '':
            return
        if message.user_id in self.notify_about_user:
            trigger_user_id = message.user_id
            trigger_user = self.bot.event_handler.users[trigger_user_id]
            for target_user_id in self.notify_about_user[trigger_user_id]:
                target_user = self.bot.event_handler.users[target_user_id]
                target_user_status = target_user.status
                delta = datetime.now() - target_user.last_notified.get(trigger_user_id, datetime.fromtimestamp(0))
                min_delta = timedelta(days=1) if target_user_status == 'dnd' else timedelta(minutes=15)
                if delta < min_delta:
                    log.info(f'not notifying {target_user.username} about {trigger_user.username},'
                             f'time_delta too small {delta}')
                    return
                target_user.last_notified[trigger_user_id] = datetime.now()
                notice = f"@{trigger_user.username} is not available"
                url = f'{self.settings.WEBHOOK_HOST_URL}:{self.settings.WEBHOOK_HOST_PORT}/hooks/{self.webhook_name}'
                props = {
                    "attachments": [
                        {
                            "actions": [
                                {
                                    "id": 'presence_remove',
                                    "name": f'Remove this notification',
                                    "integration": {
                                        "url": url,
                                        "context": {
                                            "trigger_user_id": trigger_user_id,
                                            "target_user_id": target_user_id,
                                        }
                                    }
                                },
                                {
                                    "id": 'presence_disable',
                                    "name": f'Remove notifications for all users',
                                    "integration": {
                                        "url": url,
                                        "context": {
                                            "target_user_id": target_user_id,
                                        }
                                    }
                                },
                            ],
                        }
                    ]
                }
                channel_id = self.driver.channels.create_direct_message_channel(
                    [target_user_id, self.driver.user_id]
                )['id']
                self.driver.create_post(channel_id, notice, props=props)

    @listen_webhook(webhook_name)
    async def answer(self, event: WebHookEvent):
        if not isinstance(event, ActionEvent):
            return
        trigger_user_id = event.context.get('trigger_user_id')
        target_user_id = event.context.get('target_user_id')
        action_id = event.trigger_id
        if trigger_user_id:
            self.notify_about_user[trigger_user_id].remove(target_user_id)
        elif action_id == 'presence_disable':
            for notify in self.notify_about_user.values():
                notify.remove(target_user_id)
