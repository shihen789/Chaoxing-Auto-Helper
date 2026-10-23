# Chaoxing Auto Helper

超星（学习通）网课作业自动化辅助工具。
包含字体加密逆向、题库提取、自动填答与提交。

## 环境要求
- Python 3.9+
- Node.js 18+
- Playwright (需要自行安装并配置好 CDP 接管环境)

## 准备工作
1. 将 `browser_channels` 模块放入 `lib/` 目录下（本仓库不提供具体的 CDP 接管通道实现）。
2. 复制 `config.example.json` 为 `config.json`，并将你实际的作业 URL 填入其中。
3. 确保 `data/` 目录下有你提取好的题库 JSON。

## 使用流程
1. **抓取字体**: `python scripts_python/grab_font.py`
2. **解密字体**: `node scripts_js/run_decrypt.js`
3. **提取题目**: `python scripts_python/extract_questions.py`
4. **自动填答**: `python scripts_python/fill_answers.py`
5. **提交作业**: `python scripts_python/submit_work.py`

## 免责声明
本项目仅供学习交流，请勿用于违反学校规定的学术不端行为。
