# AI 辅助软件缺陷挖掘

本仓库保存比赛交付件、AI 生成的黑盒复现脚本和工程化审查说明。

目标工程位于本地 `code/` 目录，但该目录由比赛平台提供，不纳入本仓库。

主要交付件：

- `INSTRUCTION.md`
- `work/vulnerability_list.md`
- `work/llm_chat_log.json`
- `work/vulnerability_report.md`

运行黑盒复现：

```powershell
python work/run_blackbox_repros.py
```

正式提交前，请将 `work/llm_chat_log.json` 替换为 OpenCode 导出的完整、未删改会话记录。
