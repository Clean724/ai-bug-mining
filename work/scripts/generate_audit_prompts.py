#!/usr/bin/env python3
"""Generate LLM audit prompts from candidate source locations."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HEADING_RE = re.compile(r"^## (?P<path>.+):(?P<line>\d+)$")


PROMPT_TEMPLATE = """请只基于下面提供的源码片段进行安全与稳定性审计，不要依赖项目名称、版本号、CVE、issue、PR 或任何已知漏洞信息。

审计目标：
1. 判断该代码是否存在可由外部输入触发的真实缺陷；
2. 优先寻找 shape、axis、stride、ksize、padding、dtype、index、长度、offset 等输入参数校验缺失；
3. 关注除零、整数溢出、越界访问、CHECK 崩溃、空指针、资源耗尽和拒绝服务；
4. 如果需要特定参数组合、重复调用状态或特定平台才能触发，请明确说明；
5. 不要只给静态猜测，必须给出最小复现思路和由你生成的测试代码。

请按以下格式输出：
- 漏洞是否成立：成立 / 可疑但需验证 / 不成立
- 问题源码位置：
- 触发条件：
- 现有校验为什么不足：
- 最小复现步骤：
- AI 生成测试代码：
- 预期失败现象：
- 修复建议：

候选位置：
{location}

源码上下文：
```{language}
{snippet}
```
"""


def parse_candidate_locations(candidate_file: Path, limit: int) -> list[tuple[str, int]]:
    locations: list[tuple[str, int]] = []
    for line in candidate_file.read_text(encoding="utf-8").splitlines():
        match = HEADING_RE.match(line.strip())
        if match:
            locations.append((match.group("path"), int(match.group("line"))))
            if len(locations) >= limit:
                break
    return locations


def read_snippet(repo: Path, rel_path: str, line_no: int, radius: int) -> str:
    path = repo / rel_path
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    start = max(1, line_no - radius)
    end = min(len(lines), line_no + radius)
    formatted = []
    for current in range(start, end + 1):
        marker = ">>" if current == line_no else "  "
        formatted.append(f"{marker} {current:5d}: {lines[current - 1]}")
    return "\n".join(formatted)


def language_for(path: str) -> str:
    suffix = Path(path).suffix
    if suffix in {".cc", ".h", ".cu", ".c"}:
        return "cpp"
    if suffix == ".py":
        return "python"
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--candidates", default="work/candidate_findings.md")
    parser.add_argument("--out-dir", default="work/audit_prompts")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--radius", type=int, default=45)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    candidate_file = Path(args.candidates)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not repo.exists():
        raise SystemExit(f"repository path does not exist: {repo}")
    if not candidate_file.exists():
        raise SystemExit(f"candidate file does not exist: {candidate_file}")

    locations = parse_candidate_locations(candidate_file, args.limit)
    for index, (rel_path, line_no) in enumerate(locations, start=1):
        snippet = read_snippet(repo, rel_path, line_no, args.radius)
        prompt = PROMPT_TEMPLATE.format(
            location=f"{rel_path}:{line_no}",
            language=language_for(rel_path),
            snippet=snippet,
        )
        out_path = out_dir / f"prompt_{index:03d}.md"
        out_path.write_text(prompt, encoding="utf-8")

    print(f"generated {len(locations)} prompts into {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

