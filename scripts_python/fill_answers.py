# -*- coding: utf-8 -*-
"""P 通道：按 answers_final.json 自动点选答案并暂时保存（第一章+第二章）"""
import sys, io, os, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from browser_channels.channels.playwright_ch import PlaywrightAttachChannel

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as cf:
    CHAPTERS = [(c['name'], c['url']) for c in json.load(cf)['chapters']]

answers = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data', 'answers_final.json'), encoding='utf-8'))

FILL_JS = '''((answers) => {
    const lis = [...document.querySelectorAll('.questionLi')];
    let filled = 0, failed = [];
    for (const [i, li] of lis.entries()) {
        const ans = answers[i];
        if (!ans) { failed.push({n: i+1, err: 'no answer'}); continue; }
        const qid = li.id.replace('question', '');
        // 判断题答案映射：对->true 错->false；单选直接字母
        let key = ans;
        if (li.getAttribute('typename') === '判断题') {
            key = (ans === '对') ? 'true' : 'false';
        }
        const opt = li.querySelector('.answerBg .num_option[data="' + key + '"]');
        if (!opt) { failed.push({n: i+1, err: 'option not found: ' + key}); continue; }
        // 点击所属 answerBg（触发 addChoice）
        opt.closest('.answerBg').click();
        filled++;
    }
    return {total: lis.length, filled, failed};
})'''

c = PlaywrightAttachChannel(); c._ensure()
for chap, url in CHAPTERS:
    page = c.open_tab(url, reuse=False)
    time.sleep(6)
    ans_list = [x['answer'] for x in answers[chap]]
    r = page.evaluate(FILL_JS, ans_list)
    print(chap, '| fill:', json.dumps(r, ensure_ascii=False))
    time.sleep(1)
    # 校验隐藏域 value 已写入
    check = page.evaluate('''(() => {
        const bad = [];
        for (const li of document.querySelectorAll('.questionLi')) {
            const qid = li.id.replace('question', '');
            const inp = document.getElementById('answer' + qid);
            if (!inp || !inp.value) bad.push(qid);
        }
        return {empty: bad.length, sample: bad.slice(0,5)};
    })()''')
    print(chap, '| verify:', json.dumps(check, ensure_ascii=False))
    # 暂时保存
    saved = page.evaluate('''(() => {
        const btns = [...document.querySelectorAll('a, button, input[type="button"], input[type="submit"]')];
        const b = btns.find(x => (x.innerText||x.value||'').includes('暂时保存'));
        if (b) { b.click(); return 'clicked'; }
        return 'not-found';
    })()''')
    print(chap, '| save:', saved)
    time.sleep(3)
    page.close()
c.close_tabs()
