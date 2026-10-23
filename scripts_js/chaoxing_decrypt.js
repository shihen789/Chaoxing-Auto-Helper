// chaoxing_decrypt.js — 学习通加密字体解密（本地复刻版）
// 用法: node chaoxing_decrypt.js <fontBase64文件> <要解密的文本>
const fs = require('fs');
const path = require('path');
const { Typr, md5 } = require('./TyprMd5.js');

const TABLE = JSON.parse(fs.readFileSync(path.join(__dirname, 'table.json'), 'utf8'));

function decryptText(text, fontBytes) {
    if (!text) return '';
    if (!fontBytes) return text;
    const font = Typr.parse(fontBytes)[0];
    if (!font) return text;
    let result = '';
    for (let i = 0; i < text.length; i++) {
        const code = text.charCodeAt(i);
        const glyphIndex = Typr.U.codeToGlyph(font, code);
        if (glyphIndex > 0) {
            const p = Typr.U.glyphToPath(font, glyphIndex);
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

function loadFontFromBase64(b64) {
    const bin = Buffer.from(b64, 'base64');
    return bin;
}

module.exports = { decryptText, loadFontFromBase64, TABLE };

if (require.main === module) {
    const fontPath = process.argv[2];
    const text = process.argv[3] || '';
    const b64 = fs.readFileSync(fontPath, 'utf8').trim();
    const fontBytes = loadFontFromBase64(b64);
    console.log('table entries:', Object.keys(TABLE).length);
    console.log('--- decrypted ---');
    console.log(decryptText(text, fontBytes));
}