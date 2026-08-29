from __future__ import annotations

import random

ENCOURAGEMENTS = [
    '今天也稳稳完成了，继续保持。',
    '打卡成功，节奏很好。',
    '先把小事做好，今天就赢了一半。',
    '你在认真推进自己，真不错。',
    '每一次打卡，都是一次自我确认。',
    '今天的状态很棒，继续向前。',
    '打卡完成，给自己点个赞。',
    '行动比焦虑更有力量。',
    '坚持这件事，本身就很了不起。',
    '今天也在向目标靠近一步。',
    '不错，执行力在线。',
    '把该做的做完，心就会安稳很多。',
    '又完成了一次自律打卡。',
    '慢慢来，但别停下。',
    '今天也值得被肯定。',
    '你正在把计划变成结果。',
    '这一下很关键，继续保持。',
    '很好，今天的第一项任务完成了。',
    '稳定输出，比偶尔爆发更重要。',
    '继续这样走，路会越来越清楚。',
]


def pick_encouragement(previous: str | None = None) -> str:
    pool = [item for item in ENCOURAGEMENTS if item != previous]
    if not pool:
        pool = ENCOURAGEMENTS[:]
    return random.choice(pool)
