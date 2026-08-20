import re
import secrets
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star
from astrbot.api import logger

class DicePlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("r")
    async def roll_dice(self, event: AstrMessageEvent):
        """掷骰指令：/r ndm 或 /r ndm+修正值"""
        raw_message = event.message_str.strip()
        # 匹配格式：/r 数字d数字 或 /r 数字d数字+数字
        match = re.match(r'^/r\s+(\d+)d(\d+)(?:\+(\d+))?$', raw_message)
        if not match:
            yield event.plain_result("❌ 格式错误！请使用：/r ndm 或 /r ndm+修正值，例如 /r 1d20 或 /r 2d6+3")
            return

        num = int(match.group(1))      # 骰子个数
        sides = int(match.group(2))    # 骰子面数
        mod = int(match.group(3)) if match.group(3) else 0  # 修正值

        # 参数合法性校验
        if num <= 0 or sides <= 0 or num > 100 or sides > 10000:
            yield event.plain_result("❌ 参数不合法！骰子个数和面数应为正整数，且不超过合理范围。")
            return

        # 真随机掷骰 - 使用 secrets 模块
        results = [secrets.randbelow(sides) + 1 for _ in range(num)]
        total = sum(results) + mod

        # 构建回复
        detail = " + ".join(map(str, results))
        if mod > 0:
            detail += f" + {mod}"
        elif mod < 0:
            detail += f" - {abs(mod)}"

        reply = f"🎲 [{num}d{sides}"
        if mod != 0:
            reply += f"{'+' if mod > 0 else ''}{mod}"
        reply += f"] = {detail} = **{total}**"

        yield event.plain_result(reply)

    async def terminate(self):
        """插件卸载时调用"""
        logger.info("骰子插件已卸载")
