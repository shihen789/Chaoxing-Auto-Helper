# -*- coding: utf-8 -*-
"""提取已交作业的正确答案+解析，更新 answers_final.json"""
import sys, io, os, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from browser_channels.channels.playwright_ch import PlaywrightAttachChannel

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as cf:
    CHAPTERS = [(c['name'], c['url']) for c in json.load(cf)['chapters']]

EXTRACT_JS = '''(() => {
    const lis = [...document.querySelectorAll('.questionLi')];
    return lis.map(li => {
        const qid = li.id.replace('question', '');
        const stem = (li.querySelector('h3.mark_name')?.innerText || '').trim();
        // 正确答案: colorGreen marginRight40 fl 内的字母（单选）或 对/错（判断）
        let correct = '';
        const green = li.querySelector('.colorGreen.marginRight40');
        if (green) {
            // 数字母 span 或纯文本
            const nums = green.querySelectorAll('.num_option, span[data]');
            if (nums.length) correct = [...nums].map(s => s.getAttribute('data') || s.textContent.trim()).join('');
            else correct = green.innerText.replace(/^正确答案[:：]?\\s*/i, '').trim();
        }
        // 我的答案
        let mine = '';
        const mineEl = li.querySelector('.colorRed, .yourAnswer, [class*="your"]');
        // 通用：找含"我的答案"的行
        const allText = li.innerText;
        const mMine = allText.match(/我的答案[:：]\\s*([A-D对错truefalse,\\s]+)/i);
        if (mMine) mine = mMine[1].trim();
        const mCorr = allText.match(/正确答案[:：]\\s*([A-D对错truefalse,\\s]+)/i);
        if (mCorr && !correct) correct = mCorr[1].trim();
        // 解析
        let analysis = '';
        const ana = li.querySelector('.analysis');
        if (ana) analysis = ana.innerText.replace(/^答案解析[:：]?\\s*/i, '').replace(/^AI讲解\\s*/i, '').trim();
        // 得分
        let score = '';
        const mScore = allText.match(/([0-9.]+)\\s*分/);
        if (mScore) score = mScore[1];
        return {qid, stem: stem.slice(0, 80), correct, mine, analysis: analysis.slice(0, 300), score};
    });
})()'''

answers = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data', 'answers_final.json'), encoding='utf-8'))
c = PlaywrightAttachChannel(); c._ensure()
report = {}
for chap, url in CHAPTERS:
    page = c.open_tab(url, reuse=False)
    time.sleep(7)
    extracted = page.evaluate(EXTRACT_JS)
    print(chap, 'extracted', len(extracted), 'sample:', json.dumps(extracted[0], ensure_ascii=False))
    # 合并进 answers_final.json（按 qid 或按序号）
    chap_answers = answers[chap]
    updated = 0
    for i, item in enumerate(extracted):
        if i < len(chap_answers):
            rec = chap_answers[i]
            rec['correct'] = item['correct']
            rec['analysis'] = item['analysis']
            rec['score'] = item['score']
            rec['my_answer_on_server'] = item['mine']
            if item['correct'] and rec.get('answer') and item['correct'] != rec['answer']:
                rec['answer_mismatch'] = True
            updated += 1
    report[chap] = {'total': len(extracted), 'updated': updated}
    page.close()
c.close_tabs()

answers = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data', 'answers_final.json'), encoding='utf-8'))
print('report:', json.dumps(report, ensure_ascii=False))
# 统计 mismatch / 解析覆盖
mismatch, has_ana, total = 0, 0, 0
for chap, recs in answers.items():
    for r in recs:
        total += 1
        if r.get('answer_mismatch'): mismatch += 1
        if r.get('analysis'): has_ana += 1
print(f'total={total}, mismatch={mismatch}, with_analysis={has_ana}')
