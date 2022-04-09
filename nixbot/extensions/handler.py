import asyncio
import json
from datetime import datetime
from typing import Optional, List

from mmpy_bot.event_handler import EventHandler

from nixbot.extensions.websocket import ExtendedWebsocket


class ExtendedHandler(EventHandler):
    # noinspection PyMissingConstructor
    def __init__(self, event_handler: EventHandler):
        self.driver = event_handler.driver
        self.settings = event_handler.settings
        self.plugins = event_handler.plugins
        self.ignore_own_messages = event_handler.ignore_own_messages
        self.message_listeners = event_handler.message_listeners
        self.webhook_listeners = event_handler.webhook_listeners
        self._name_matcher = event_handler._name_matcher
        self.users = {}
        self.seq = 1
        self.handler_map = {
            'added_to_team': None,
            'authentication_challenge': None,
            'channel_converted': None,
            'channel_created': None,
            'channel_deleted': None,
            'channel_member_updated': None,
            'channel_updated': None,
            'channel_viewed': None,
            'config_changed': None,
            'delete_team': None,
            'direct_added': None,
            'emoji_added': None,
            'ephemeral_message': None,
            'group_added': None,
            'hello': self.handle_hello,
            'leave_team': None,
            'license_changed': None,
            'memberrole_updated': None,
            'new_user': None,
            'plugin_disabled': None,
            'plugin_enabled': None,
            'plugin_statuses_changed': None,
            'post_deleted': None,
            'post_edited': None,
            'post_unread': None,
            'posted': self._handle_post,
            'preference_changed': None,
            'preferences_changed': None,
            'preferences_deleted': None,
            'reaction_added': None,
            'reaction_removed': None,
            'response': None,
            'role_updated': None,
            'status_change': None,
            'typing': None,
            'update_team': None,
            'user_added': None,
            'user_removed': None,
            'user_role_updated': None,
            'user_updated': self.handle_user_updated,
            'dialog_opened': None,
            'thread_updated': None,
            'thread_follow_changed': None,
            'thread_read_changed': None,
        }

    def start(self):
        self.driver.init_websocket(self._handle_event, ExtendedWebsocket)

    async def _handle_event(self, data):
        post = json.loads(data)
        event_action = post.get("event")
        func = self.handler_map.get(event_action)
        if func is not None:
            await func(post)

    async def handle_hello(self, post):
        user_id = post['broadcast']['user_id']
        self.users[user_id] = {}

    async def mark_user_online(self, user_id, post):
        self.users[user_id]['active'] = datetime.now()
        post['post'] = {
            'id': '',
            'user_id': user_id,
            'message': 'user is now online',
            'channel_id': '',
            'parent_id': '',
            'root_id': '',
        }
        post['channel_name'] = post['channel_type'] = ''
        await self._handle_post(post)

    async def handle_status_change(self, post):
        user_id = post['data']['user_id']
        status = post['data']['status']
        self.users[user_id]['status'] = status
        if status == 'online':
            await self.mark_user_online(user_id, post)

    async def handle_typing(self, post):
        user_id = post['data']['user_id']
        self.users[user_id]['typing'] = datetime.now()
        await self.mark_user_online(user_id, post)

    async def handle_user_updated(self, post):
        pass
        # TODO: add user_updated
        # {'event': 'user_updated', 'data': {'user': {'id': 'jxs5xm3b37djjfqohbtp4urpho', 'create_at': 1624046154244, 'update_at': 1649523881960, 'delete_at': 0, 'username': 'phntom', 'auth_data': '', 'auth_service': '', 'email': 'phantom@kix.co.il', 'nickname': '', 'first_name': '', 'last_name': '', 'position': '', 'roles': 'system_admin system_user', 'props': {'customStatus': '{"emoji":"palm_tree","text":"On a vacation","duration":"this_week","expires_at":"2022-04-09T20:59:59.999Z"}', 'focalboard_onboardingTourStep': '999', 'focalboard_tourCategory': 'board', 'focalboard_welcomePageViewed': '1'}, 'locale': 'en', 'timezone': {'automaticTimezone': 'Asia/Jerusalem', 'manualTimezone': '', 'useAutomaticTimezone': 'true'}, 'disable_welcome_email': False}}, 'broadcast': {'omit_users': {'jxs5xm3b37djjfqohbtp4urpho': True}, 'user_id': '', 'channel_id': '', 'team_id': ''}, 'seq': 10}

    async def _send_websocket(self, action, data):
        self.seq += 1
        json_data = json.dumps({
            "seq": self.seq,
            "action": action,
            "data": data
        }).encode('utf8')
        await self.driver.websocket.websocket.send(json_data)

    async def user_typing(
        self,
        channel_id: str,
        parent_post_id: Optional[str] = None,
        sleep_duration: int = 0
    ):
        await self._send_websocket("user_typing", {
            "channel_id": channel_id,
            "parent_id": parent_post_id or '',
        })
        if sleep_duration > 0:
            await asyncio.sleep(sleep_duration)

    async def user_update_active_status(self, user_is_active: bool, manual: bool):
        await self._send_websocket('user_update_active_status', {'user_is_active': user_is_active, 'manual': manual})

    async def get_statuses(self):
        await self._send_websocket('get_statuses', {'a': True})

    async def get_statuses_by_ids(self, ids: List[str]):
        await self._send_websocket('get_statuses_by_ids', {'user_ids': ids})
