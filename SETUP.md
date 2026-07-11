# 安装步骤（一次性，约 10 分钟）

## 1. 把文件放进你的仓库

```bash
git clone https://github.com/Nomi-lpr/neetcode-submissions.git
cd neetcode-submissions

# 把本压缩包里的这两个文件按相同路径放进去：
#   .github/workflows/summarize.yml
#   scripts/summarize.py
#   INTERVIEW_GUIDE.md   （可选，放根目录）

git add .github scripts INTERVIEW_GUIDE.md
git commit -m "chore: add auto-summarize pipeline"
git push
```

## 2. 获取 OpenAI API Key

1. 打开 https://platform.openai.com/api-keys 注册/登录
2. 点 "Create new secret key"（形如 `sk-...`），复制保存（只显示一次）
3. 确保账户里有可用额度（Settings → Billing 充值几美元即可）
4. API 按用量计费。一道题一份笔记大约几千 token，用 `gpt-4.1` 生成一份笔记的成本约 1-2 美分，
   150 题全量生成约 2-3 美元；如果想更省钱，把 `scripts/summarize.py` 里的
   `MODEL = "gpt-4.1"` 改成 `MODEL = "gpt-4.1-mini"` 即可，质量略降但成本降至约十分之一

## 3. 把 Key 存进 GitHub Secrets（不要写进代码！）

1. 打开你的仓库页面 → Settings → Secrets and variables → Actions
2. 点 "New repository secret"
3. Name 填 `OPENAI_API_KEY`，Value 粘贴你的 key，保存

## 4. 首次运行：为历史题目补齐笔记

1. 仓库页面 → Actions → 左侧选 "Auto-generate review notes"
2. 点 "Run workflow"，`regenerate_all` 填 `yes`，运行
3. 跑完后仓库里每个题目文件夹会多一个 `NOTES.md`，根目录会出现 `PROGRESS.md` 索引

## 5. 之后的日常

什么都不用做。你在 NeetCode 上每提交一道新题 → 自动同步到 GitHub →
触发 workflow → 几十秒后这道题的 NOTES.md 就生成好并推回仓库了。

## 自定义

- **笔记的风格和内容**全部由 `scripts/summarize.py` 里的 `PROMPT_TEMPLATE` 控制。
  想加"Follow-up 变体题"或"我常犯的错"栏目，直接改模板文字再 push 即可。
- 想对某一道题重新生成：删掉它的 NOTES.md 再 push，或手动 Run workflow。

## 排错

- Actions 页面能看到每次运行的日志；单题失败不会影响其他题。
- 如果 workflow 没触发，检查文件路径是否匹配 `**/submission-*.py`。
