// 端到端验证：用真实字体文件跑 decryptText，确认链路不崩 + 输出可读
const fs = require('fs');
const { decryptText, loadFontFromBase64 } = require('./chaoxing_decrypt.js');
const fontPath = process.argv[2];
const sample = process.argv[3] || '测试';
const b64 = fs.readFileSync(fontPath, 'utf8').trim();
const fontBytes = loadFontFromBase64(b64);
console.log('font bytes:', fontBytes.length, 'sample:', sample);
console.log('--- result ---');
console.log(decryptText(sample, fontBytes));