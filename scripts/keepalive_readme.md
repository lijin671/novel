# Hosting Keep-Alive

自动登录 [client.webhostmost.com](https://client.webhostmost.com) 客户区，防止免费主机计划因 45 天未登录而被删除。

## 🚀 工作原理

通过 GitHub Actions 定时任务，每月 **1 号和 15 号** 自动模拟登录客户区，刷新账户活跃状态。

## 🔧 设置步骤

1. Fork 或克隆本仓库
2. 进入仓库 → **Settings** → **Secrets and variables** → **Actions**
3. 添加两个 Repository Secret：

| Secret 名称 | 值 |
|---|---|
| `HOSTING_EMAIL` | 你的 webhostmost 登录邮箱 |
| `HOSTING_PASSWORD` | 你的 webhostmost 登录密码 |

4. 推送代码后，GitHub Actions 会按计划自动运行

## 📋 手动触发

进入仓库 → **Actions** → **Keep Hosting Alive** → **Run workflow**

## 💻 本地运行

```bash
# Linux/Mac
export HOSTING_EMAIL="your_email@example.com"
export HOSTING_PASSWORD="your_password"
python scripts/keep_alive_hosting.py
```

```powershell
# Windows PowerShell
$env:HOSTING_EMAIL = "your_email@example.com"
$env:HOSTING_PASSWORD = "your_password"
python scripts/keep_alive_hosting.py
```

## ⚠️ 注意事项

- 请确保 Secrets 中的邮箱和密码正确
- 如果网站增加了验证码，脚本可能需要调整
- 建议首次配置后手动触发一次确认登录成功
