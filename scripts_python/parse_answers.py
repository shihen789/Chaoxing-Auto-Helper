# -*- coding: utf-8 -*-
"""解析 DeepSeek 答案 → answers.json（含校验）"""
import json, re


parsed = {}
for m in re.finditer(r'(\d+)-(\d+):\s*([A-D]|对|错)', raw):
    parsed[(int(m.group(1)), int(m.group(2)))] = m.group(3)

chapters = list(qs.keys())  # [第一章客观题, 第二章客观题（新）]
out = {}
errors = []
for ci, chap in enumerate(chapters, 1):
    items = []
    for i, q in enumerate(qs[chap]['questions'], 1):
        ans = parsed.get((ci, i))
        if ans is None:
            errors.append(f'{chap} #{i} 无答案')
        elif q['type'] == '单选题' and ans not in [o['key'] for o in q['options']]:
            errors.append(f'{chap} #{i} 答案 {ans} 不在选项 {[o["key"] for o in q["options"]]}')
        elif q['type'] == '判断题' and ans not in ('对', '错'):
            errors.append(f'{chap} #{i} 判断答案异常: {ans}')
        items.append({'n': i, 'qid': q['qid'], 'type': q['type'], 'stem': q['stem'][:50], 'answer': ans})
    out[chap] = items

          ensure_ascii=False, indent=1)
total = sum(len(v) for v in out.values())
print(f'答案数: {total} / 题数: {sum(len(v) for v in qs.values())}')
print('校验错误:', errors if errors else '无')
# 抽样打印
for chap, items in out.items():
    print(chap, '前3:', [(x['n'], x['answer']) for x in items[:3]])
