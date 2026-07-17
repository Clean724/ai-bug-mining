# 审计执行手册

## 阶段 1：候选点收集

运行：

```bash
python work/scripts/collect_candidates.py --repo code/tensorflow_v2_11_0 --out work/candidate_findings_v2_11_0.md
```

输出 `work/candidate_findings_v2_11_0.md`。该文件不是最终漏洞结论，只是让 LLM 深审的候选入口。

## 阶段 2：生成 LLM 审计提示词

运行：

```bash
python work/scripts/generate_audit_prompts.py --repo code/tensorflow_v2_11_0 --candidates work/candidate_findings_v2_11_0.md --out-dir work/audit_prompts --limit 20
```

然后按顺序把 `work/audit_prompts/prompt_*.md` 投喂给模型。注意不要额外告诉模型项目名称、版本号、已知漏洞、CVE、issue 或 PR。

## 阶段 3：人工与 AI 联合筛选

每个候选点只保留满足至少两项的问题：

- 有外部可控输入。
- 有明确缺失校验或校验位置不一致。
- 有可执行最小复现。
- 能导致崩溃、拒绝服务、越界、整数溢出、资源耗尽或明显错误行为。
- 能由 AI 生成测试证明。

## 阶段 4：验证优先级

优先验证以下类型：

1. Python API 能直接触发的 C++ kernel 崩溃。
2. TFLite 模型或 tensor 参数畸形触发崩溃。
3. 图像、字符串、解码、解析类输入触发崩溃或资源耗尽。
4. 特定 shape、axis、stride、ksize、padding 组合触发除零或 CHECK 失败。

暂缓验证以下类型：

- 仅代码风格问题。
- 只有理论风险、没有输入路径的问题。
- 需要修改源码才能触发的问题。
- 依赖已知 CVE 或上游 issue 才能证明的问题。

## 阶段 5：交付填写

通过验证后更新：

- `work/vulnerability_list.md`
- `work/llm_chat_log.json`
- `work/vulnerability_report.md`

报告中要说明：源码分析用于定位成因，漏洞成立依据是 AI 生成测试或最小复现的运行证据。
