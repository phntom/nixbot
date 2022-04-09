import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime
from time import time
from typing import Optional, List

from mmpy_bot.event_handler import EventHandler

from nixbot.extensions.websocket import ExtendedWebsocket
from nixbot.model.user import ExtendedUser

log = logging.getLogger(__name__)


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
        self.users = defaultdict(ExtendedUser)
        self.seq = 2
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
            'status_change': self.handle_status_change,
            'typing': None,
            'update_team': None,
            'user_added': self.handle_user_added,
            'user_removed': self.handle_user_removed,
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
        self.users[user_id] = ExtendedUser(id=user_id, is_bot=True)

    async def mark_user_online(self, user_id, post):
        self.users[user_id].last_activity_at = int(time())
        post['data']['post'] = {
            'id': '',
            'user_id': user_id,
            'message': 'user is now online',
            'channel_id': '',
            'parent_id': '',
            'root_id': '',
        }
        post['data']['channel_name'] = post['data']['channel_type'] = ''
        await self._handle_post(post)

    async def handle_status_change(self, post):
        user_id = post['data']['user_id']
        status = post['data']['status']
        self.users[user_id].status = status
        if status == 'online':
            await self.mark_user_online(user_id, post)

    async def handle_typing(self, post):
        user_id = post['data']['user_id']
        self.users[user_id].last_typing = datetime.now()
        await self.mark_user_online(user_id, post)

    async def handle_user_added(self, post):
        user_id = post['user_id']
        team_id = post['team_id']
        if user_id not in self.users:
            self.users[user_id] = ExtendedUser(**self.driver.get_user_info(user_id))
        self.users[user_id].teams.add(team_id)

    async def handle_user_updated(self, post):
        user = ExtendedUser(**post['data']['user'])
        self.users[user.id] = user

    async def handle_user_removed(self, post):
        user_id = post['user_id']
        team_id = post['team_id']
        user = self.users.get(user_id)
        if not user:
            log.info(f'handle_user_removed user_id: {user_id} not found. team_id: {team_id}')
            return
        user.teams.remove(team_id)
        if not user.teams:
            log.info(f'handle_user_removed user_id: {user_id} removed last team team_id: {team_id}')
            del self.users[user.id]

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
