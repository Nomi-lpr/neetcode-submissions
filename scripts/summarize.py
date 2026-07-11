"""
自动为 NeetCode 提交生成复习笔记。

工作方式：
1. 扫描仓库中所有 <topic>/<problem-id>/submission-*.py
2. 对于还没有 NOTES.md 的题目（或 REGENERATE_ALL=yes 时对所有题目），
   把最新一次提交的代码发给 OpenAI API（ChatGPT 模型），按固定模板生成笔记
3. 把笔记写到该题目文件夹下的 NOTES.md
4. 重新生成仓库根目录的 PROGRESS.md 总索引（按 topic 分组，方便复习）
"""

import os
import re
import sys
from pathlib import Path

from openai import OpenAI

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL = "gpt-4.1"   # 想省钱可以改成 "gpt-4.1-mini"
REGENERATE_ALL = os.environ.get("REGENERATE_ALL", "no").lower() == "yes"

# ---------------------------------------------------------------
# 笔记模板：这是整套系统的灵魂。你可以随时改这里来调整笔记风格。
# ---------------------------------------------------------------
PROMPT_TEMPLATE = """\
你是一位帮助学生准备编程面试的导师。学生对 Python 还不够熟练，正在刷 NeetCode/LeetCode。
下面是学生对题目「{problem_id}」（分类：{topic}）的一份已通过的解法：

```python
{code}
```

请严格按下面的 Markdown 模板生成一份复习笔记，用中文写，代码和术语保留英文。
要求写得具体、贴合这份代码本身，不要泛泛而谈。直接输出 Markdown，不要任何开场白。

# {problem_id}

## 一句话思路
（用一两句话概括这个解法的核心 idea，要求学生复习时看一眼就能回忆起来）

## 复杂度分析
- **时间复杂度**：O(?)，逐行/逐块解释为什么（哪个循环贡献了什么，哈希表操作按 O(1) 均摊等）
- **空间复杂度**：O(?)，说明额外空间用在了哪里（不含输出）
- **能否更优**：如果存在更优复杂度的解法，简述方向；如果这已是最优，说明为什么（例如至少要读一遍输入所以 Ω(n)）

## 边界条件清单
列出这道题面试时必须考虑的边界情况（空输入、单元素、全部相同、负数/零、溢出、重复元素等，选适用的），
并指出这份代码分别是"天然覆盖"还是"需要显式处理"，如果有遗漏的要指出来。

## Python 语法笔记
针对代码里实际用到的 dict / set / list 及其他语法，给学生讲解 2-4 个知识点。
每个知识点：写出代码中的原句 → 解释它做什么 → 给出一个最小示例或常见变体（如 dict.get(k, default)、
set 的 in 是 O(1)、enumerate、defaultdict、列表切片等）。只讲代码里出现或密切相关的。

## 面试口述剧本
用 3-5 句话写出面试时应该如何向面试官讲解这个思路（先说暴力解及其复杂度 → 指出瓶颈 →
引出优化的数据结构/技巧 → 报出最终复杂度）。这是学生要背下来练习口述的部分。

## 同类题 & 可复用套路
指出这道题属于什么套路（如 hashmap 记录见过的元素、双指针、滑动窗口等），
列 2-3 道用同样套路的经典题名字，帮助学生建立"题型 → 套路"的映射。
"""

INDEX_HEADER = """\
# 刷题进度与复习索引

> 本文件由 CI 自动生成，请勿手动编辑。
> 复习方法：遮住右侧"一句话思路"，看题名回忆解法，再点进 NOTES.md 核对。

"""


def find_problems() -> list[Path]:
    """找到所有包含 submission-*.py 的题目文件夹。"""
    dirs = set()
    for f in REPO_ROOT.rglob("submission-*.py"):
        if ".git" not in f.parts:
            dirs.add(f.parent)
    return sorted(dirs)


def latest_submission(problem_dir: Path) -> Path:
    """按 submission-N 的 N 取最新一份。"""
    def num(p: Path) -> int:
        m = re.search(r"submission-(\d+)", p.stem)
        return int(m.group(1)) if m else -1
    return max(problem_dir.glob("submission-*.py"), key=num)


def one_liner_from_notes(notes_path: Path) -> str:
    """从 NOTES.md 里抓"一句话思路"用于索引。"""
    if not notes_path.exists():
        return ""
    text = notes_path.read_text(encoding="utf-8")
    m = re.search(r"## 一句话思路\s*\n+(.+)", text)
    return m.group(1).strip() if m else ""


def generate_note(client: OpenAI, topic: str, problem_id: str, code: str) -> str:
    prompt = PROMPT_TEMPLATE.format(problem_id=problem_id, topic=topic, code=code)
    resp = client.chat.completions.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content


def rebuild_index(problems: list[Path]) -> None:
    by_topic: dict[str, list[tuple[str, str, str]]] = {}
    for d in problems:
        topic = d.parent.name if d.parent != REPO_ROOT else "misc"
        rel = d.relative_to(REPO_ROOT)
        summary = one_liner_from_notes(d / "NOTES.md")
        by_topic.setdefault(topic, []).append((d.name, str(rel / "NOTES.md"), summary))

    lines = [INDEX_HEADER]
    total = sum(len(v) for v in by_topic.values())
    lines.append(f"**已完成：{total} 题**\n")
    for topic in sorted(by_topic):
        lines.append(f"\n## {topic}\n")
        lines.append("| 题目 | 一句话思路 |")
        lines.append("|---|---|")
        for name, notes_rel, summary in sorted(by_topic[topic]):
            lines.append(f"| [{name}]({notes_rel}) | {summary} |")
    (REPO_ROOT / "PROGRESS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    client = OpenAI(api_key=api_key)

    problems = find_problems()
    print(f"Found {len(problems)} problems")

    generated = 0
    for d in problems:
        notes = d / "NOTES.md"
        if notes.exists() and not REGENERATE_ALL:
            continue
        sub = latest_submission(d)
        code = sub.read_text(encoding="utf-8")
        topic = d.parent.name if d.parent != REPO_ROOT else "misc"
        print(f"Generating notes for {topic}/{d.name} ...")
        try:
            notes.write_text(generate_note(client, topic, d.name, code), encoding="utf-8")
            generated += 1
        except Exception as e:  # 单题失败不阻塞其他题
            print(f"  FAILED: {e}", file=sys.stderr)

    rebuild_index(problems)
    print(f"Done. Generated {generated} new note(s); index rebuilt.")


if __name__ == "__main__":
    main()
