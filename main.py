"""
AstrBot 消息撤回插件 - 纯白名单版
指令：动态配置（默认：撤回）
权限：仅限 config.json 中 allowed_members 列表内的成员
效果：撤回被回复的消息，完全静默，不触发 AI
"""

import json
import os
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Reply

@register(
    "astrbot_plugin_silent_recall",
    "abc55515",
    "纯文本指令，仅限插件白名单成员使用，静默撤回被回复的消息",
    "1.0.1"
)
class SilentRecallPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = self._load_config()

    def _load_config(self):
        """纯读取配置文件，不进行任何自动写入或文件创建操作"""
        default = {
            "silent": True,
            "command": "撤回",
            "show_log": True,
            "allowed_members": []   # 白名单：允许使用撤回的用户ID列表
        }
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    for k, v in default.items():
                        if k not in cfg:
                            cfg[k] = v
                    return cfg
            except Exception as e:
                logger.warning(f"读取 config.json 失败: {e}")
        return default

    def _is_allowed(self, event: AstrMessageEvent) -> bool:
        """检查用户是否在白名单中"""
        sender_id = None
        if hasattr(event, 'get_sender_id'):
            sender_id = event.get_sender_id()
        elif hasattr(event, 'sender') and hasattr(event.sender, 'user_id'):
            sender_id = str(event.sender.user_id)
        elif hasattr(event, '_raw_message'):
            raw = event._raw_message
            if isinstance(raw, dict):
                sender_id = str(raw.get('user_id', ''))

        if not sender_id:
            if self.config.get("show_log"):
                logger.warning("[权限] 无法获取发送者ID")
            return False

        allowed = [str(uid) for uid in self.config.get('allowed_members', [])]
        result = sender_id in allowed

        if self.config.get("show_log"):
            logger.info(f"[权限] 用户ID: {sender_id} | 在白名单中: {result}")

        return result

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def recall_cmd(self, event: AstrMessageEvent):
        # 1. 动态获取配置的指令词
        cmd = self.config.get("command", "撤回")
        
        # 2. 严格匹配文本指令
        if not event.message_str or event.message_str.strip() != cmd:
            return

        # 3. 匹配成功后立即拦截，阻止 AI 响应
        try:
            event.stop_event()
        except AttributeError:
            pass
        event.call_llm = False

        # 4. 权限检查
        if not self._is_allowed(event):
            return

        # 5. 获取被回复的消息 ID
        target_msg_id = None
        if event.message_obj and hasattr(event.message_obj, 'message'):
            for comp in event.message_obj.message:
                if isinstance(comp, Reply):
                    target_msg_id = str(comp.id)
                    break

        if not target_msg_id:
            return

        if self.config.get("show_log"):
            logger.info(f"[撤回] 获取到回复消息ID: {target_msg_id}")

        # 6. 执行撤回动作
        try:
            if hasattr(event, 'bot') and hasattr(event.bot, 'call_action'):
                # 兼容性处理：如果是纯数字则转为 int（适配 OneBot），否则保持字符串
                msg_id_param = int(target_msg_id) if target_msg_id.isdigit() else target_msg_id
                
                await event.bot.call_action("delete_msg", message_id=msg_id_param)
                
                if self.config.get("show_log"):
                    logger.info(f"[撤回] 撤回成功: {target_msg_id}")
                if not self.config.get("silent", True):
                    yield event.plain_result("✅")
        except Exception as e:
            logger.error(f"[撤回] 异常: {e}")
            if not self.config.get("silent", True):
                yield event.plain_result(f"❌ {str(e)}")

    async def terminate(self):
        logger.info("纯白名单撤回插件已卸载")