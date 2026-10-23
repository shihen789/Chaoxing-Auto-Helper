# -*- coding: utf-8 -*-
"""P 通道：提取第一章+第二章客观题 → JSON 文件"""
import sys, io, os, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from browser_channels.channels.playwright_ch import PlaywrightAttachChannel

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as cf:
    CHAPTERS = [(c['name'], c['url']) for c in json.load(cf)['chapters']]

EXTRACT_JS = '''(() => {
    const qs = [];
    for (const li of document.querySelectorAll('.questionLi')) {
        const q = {
            qid: li.id.replace('question', ''),
            type: li.getAttribute('typename') || '',
            stem: '',
            options: [],
        };
        const h3 = li.querySelector('h3.mark_name');
        if (h3) {
            q.stem = h3.innerText.replace(/\\s+/g, ' ').trim();
        }
        for (const opt of li.querySelectorAll('.stem_answer .answerBg, .answerBg')) {
            const key = opt.querySelector('.num_option');
            const val = opt.querySelector('.answer_p');
            if (key && val) {
                q.options.push({key: key.getAttribute('data') || key.innerText.trim(),
                                text: val.innerText.trim()});
            }
        }
        // 填空题：题干里的 input
        const blanks = [...li.querySelectorAll('input[type="text"], textarea')].map(i => i.id || i.name);
        if (blanks.length) q.blankInputs = blanks;
        qs.push(q);
    }
    return {title: (document.querySelector('.mark_title')||{}).innerText || '', questions: qs};
})()'''

c = PlaywrightAttachChannel()
c._ensure()
result = {}
for name, url in CHAPTERS:
    page = c.open_tab(url, reuse=False)
    time.sleep(6)
    data = page.evaluate(EXTRACT_JS)
    result[name] = data
    print(name, '| title:', data['title'], '| count:', len(data['questions']))
    page.close()

out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print('saved:', out_path)

# 统计题型
for name, data in result.items():
    types = {}
    for q in data['questions']:
        types[q['type']] = types.get(q['type'], 0) + 1
    print(name, '题型分布:', types)
c.close_tabs()
