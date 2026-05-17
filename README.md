# 静默撤回插件 (Silent Recall Plugin)

一个为 AstrBot 设计的轻量级插件，回复消息并发送指令 `撤回`，即可无痕撤回消息，全程无干扰。

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## ✨ 主要功能

- **🔇 完全静默**：撤回成功后，机器人不会发出任何提示消息。
- **👥 成员白名单**：只有你添加到 `allowed_members` 列表的成员才能使用。
- **🚫 不触发 AI**：插件会彻底拦截指令，防止大模型进行不必要的回复。
- **⚙️ 灵活配置**：支持自定义指令词和开关日志，通过 `config.json` 文件即可轻松修改。

## 📦 安装与配置

### 安装方式

1. **插件市场安装（推荐）**：在 AstrBot 插件市场中搜索 `astrbot_plugin_silent_recall`，点击安装即可。
2. **手动安装**：将本项目克隆到 AstrBot 的 `data/plugins` 目录下，然后重启 AstrBot。

```bash
git clone https://github.com/abc55515/astrbot_plugin_silent_recall.git