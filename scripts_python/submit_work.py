# -*- coding: utf-8 -*-
"""P 通道：提交第一章+第二章作业并确认状态"""
import sys, io, os, json, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from browser_channels.channels.playwright_ch import PlaywrightAttachChannel

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(CONFIG_PATH, 'r', encoding='utf-8') as cf:
    CHAPTERS = [(c['name'], c['url']) for c in json.load(cf)['chapters']]

c = PlaywrightAttachChannel(); c._ensure()
for chap, url in CHAPTERS:
    page = c.open_tab(url, reuse=False)
    time.sleep(6)
    # 状态检查
    status = page.evaluate('''(() => {
        const body = document.body.innerText;
        return {submitted: body.includes('已交') || body.includes('已提交'),
                hasSubmitBtn: !!([...document.querySelectorAll('a,button,input')].find(x => (x.innerText||x.value||'').trim() === '提交')),
                snippet: body.slice(0, 200)};
    })()''')
    print(chap, '| pre:', json.dumps(status, ensure_ascii=False))
    if status['submitted']:
        print(chap, '| 已是已交状态，跳过')
        page.close(); continue
    # 点提交（可能有确认弹窗）
    clicked = page.evaluate('''(() => {
        const b = [...document.querySelectorAll('a,button,input')].find(x => (x.innerText||x.value||'').trim() === '提交');
        if (b) { b.click(); return true; }
        return false;
    })()''')
    print(chap, '| submit clicked:', clicked)
    time.sleep(2)
    # 处理确认弹窗（alert/confirm 或页面内确认按钮）
    confirm = page.evaluate('''(() => {
        // 页面内二次确认按钮（如 "确定"/"确认提交"）
        const b = [...document.querySelectorAll('a,button,input,span')]
            .find(x => { const t = (x.innerText||x.value||'').trim(); return t === '确定' || t === '确认' || t === '确认提交'; });
        if (b) { b.click(); return 'clicked-confirm'; }
        return 'no-dialog';
    })()''')
    print(chap, '| confirm:', confirm)
    time.sleep(4)
    after = page.evaluate('''(() => {
        const body = document.body.innerText;
        return {url: location.href.slice(0,120), done: body.includes('已交') || body.includes('提交成功') || body.includes('已完成'),
                snippet: body.slice(0, 300)};
    })()''')
    print(chap, '| after:', json.dumps(after, ensure_ascii=False))
    page.close()
c.close_tabs()
