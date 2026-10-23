// extract.js — 注入到学习通测验页的提取脚本（去掉 GM_* 依赖，table.json 内嵌）
// 用法：P 通道 evaluate 时把 TyprMd5_CODE / TABLE 作为参数传入
function extract(TyprMd5_CODE, TABLE, opts = {}) {
    const out = { log: [], questions: [] };
    const log = m => out.log.push(m);

    // 1. 注入 Typr/md5
    try { eval(TyprMd5_CODE); }
    catch (e) { return { error: 'Typr 注入失败: ' + e.message, log: out.log }; }
    const { Typr, md5 } = (function () {
        // TyprMd5.js 会挂 window.Typr / window.md5（浏览器上下文）
        return { Typr: window.Typr, md5: window.md5 };
    })();

    // 2. 解析页面加密字体
    let font = null;
    const styles = document.getElementsByTagName('style');
    for (const st of styles) {
        const txt = st.textContent || '';
        if (txt.includes('font-cxsecret') && txt.includes('base64,')) {
            const m = txt.match(/base64,([\w\W]+?)'/);
            if (m) {
                try {
                    const bin = atob(m[1]);
                    const bytes = new Uint8Array(bin.length);
                    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
                    font = Typr.parse(bytes)[0];
                    log('字体解析成功');
                } catch (e) { log('字体解析失败: ' + e.message); }
            }
            break;
        }
    }
    if (!font) log('未找到 font-cxsecret 字体');

    // 3. 解密函数
    function decryptText(text) {
        if (!text || !font) return text || '';
        let result = '';
        for (let i = 0; i < text.length; i++) {
            const code = text.charCodeAt(i);
            const gi = Typr.U.codeToGlyph(font, code);
            if (gi > 0) {
                const p = Typr.U.glyphToPath(font, gi);
                if (p) {
                    const hash = md5(JSON.stringify(p)).slice(24);
                    const match = TABLE[hash];
                    if (match !== undefined) {
                        result += (typeof match === 'number') ? String.fromCharCode(match) : match;
                        continue;
                    }
                }
            }
            result += text[i];
        }
        return result;
    }

    // 4. 提取题目
    const questions = document.querySelectorAll('.TiMu');
    if (questions.length === 0) return { error: '未找到 .TiMu 题目', log: out.log };

    questions.forEach((q, index) => {
        let titleDiv = q.querySelector('.Zy_TItle . clearfix') ||
                       q.querySelector('.Zy_TItle') ||
                       q.querySelector('.newZy_TItle') ||
                       q.querySelector('.fontLabel');
        let titleText = titleDiv ? titleDiv.innerText.replace(/\s+/g, ' ').trim() : '未找到题目';
        titleText = decryptText(titleText);

        const item = { index: index + 1, title: titleText, options: [] };
        const opts = q.querySelectorAll('ul li');
        opts.forEach(opt => {
            let optText = opt.innerText.replace(/\s+/g, ' ').trim();
            optText = decryptText(optText);
            const isChecked = opt.querySelector('input:checked') ||
                              opt.querySelector('.ri') || opt.querySelector('.dui');
            item.options.push({ text: optText, checked: !!isChecked });
        });
        out.questions.push(item);
    });
    out.count = out.questions.length;
    return out;
}