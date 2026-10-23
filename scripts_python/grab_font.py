# -*- coding: utf-8 -*-
"""P 通道：Playwright attach CDP(9222) 打开 chaoxing.com，抓 font-cxsecret base64"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from browser_channels.channels.playwright_ch import PlaywrightAttachChannel

c = PlaywrightAttachChannel()
r = c.do_open('https://www.chaoxing.com')
print('open:', r.ok, r.data)

js = r'''
(() => {
    const s = [...document.getElementsByTagName('style')];
    for (const st of s) {
        const txt = st.textContent || '';
        if (txt.includes('font-cxsecret') && txt.includes('base64,')) {
            const m = txt.match(/base64,([\w\W]+?)'/);
            if (m) return { len: m[1].length, head: m[1].slice(0, 50) };
        }
    }
    return 'no font-cxsecret found';
})()
'''
val = c._page.evaluate(js)
print('font probe:', json.dumps(val, ensure_ascii=False)[:300])
print('title:', c._page.title())
c.close_tabs()