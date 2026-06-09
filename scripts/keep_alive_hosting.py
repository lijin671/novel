#!/usr/bin/env python3
"""
webhostmost.com 免费主机保活脚本
=================================
自动登录 client.webhostmost.com 客户区，防止免费计划因 45 天未登录而被删除。

使用方式：
  1. GitHub Actions（推荐）：
     - 在仓库 Settings -> Secrets and variables -> Actions 中添加：
       HOSTING_EMAIL    = 你的登录邮箱
       HOSTING_PASSWORD = 你的登录密码
     - 工作流会每月1号和15号自动运行

  2. 本地运行：
     - 设置环境变量后运行：
       set HOSTING_EMAIL=your_email@example.com
       set HOSTING_PASSWORD=your_password
       python scripts/keep_alive_hosting.py
     - 或者使用 Windows 任务计划程序定期执行
"""

import os
import sys
import requests
from datetime import datetime, timezone, timedelta


LOGIN_URL = "https://client.webhostmost.com/dologin.php"
CLIENT_AREA_URL = "https://client.webhostmost.com/clientarea.php"


def keep_alive(email: str, password: str) -> bool:
    """登录 webhostmost.com 客户区并返回是否成功。"""

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    })

    # --- 第1步：获取登录页面和 CSRF token ---
    print("[1/3] 正在访问登录页面...")
    try:
        resp = session.get(CLIENT_AREA_URL, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ✗ 无法访问登录页面: {e}")
        return False

    # 提取 CSRF token（WHMCS 使用 hidden input）
    token = ""
    for line in resp.text.splitlines():
        if 'name="token"' in line and 'value="' in line:
            start = line.index('value="') + len('value="')
            end = line.index('"', start)
            token = line[start:end]
            break

    # --- 第2步：提交登录表单 ---
    print("[2/3] 正在登录...")
    login_data = {
        "username": email,
        "password": password,
    }
    if token:
        login_data["token"] = token
        print(f"  ✓ 找到 CSRF token: {token[:8]}...")
    else:
        print("  ⚠ 未找到 CSRF token，继续尝试登录...")

    try:
        resp = session.post(LOGIN_URL, data=login_data, timeout=30, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ✗ 登录请求失败: {e}")
        return False

    # --- 第3步：验证登录结果 ---
    print("[3/3] 正在验证登录状态...")
    try:
        resp = session.get(CLIENT_AREA_URL, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ✗ 无法访问客户区: {e}")
        return False

    # 检查是否登录成功（页面中应包含登出链接或用户信息）
    page = resp.text.lower()
    if "logout" in page or "log out" in page or "我的服务" in page or "my services" in page:
        print("  ✓ 登录成功！")
        return True

    # 如果页面仍包含登录表单，则登录失败
    if "dologin.php" in page or "login" in resp.url.lower():
        print("  ✗ 登录失败，请检查邮箱和密码是否正确。")
        return False

    # 无法确定状态，但请求没有报错
    print("  ⚠ 无法确认登录状态（可能已成功），请手动检查。")
    return True


def main():
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S CST")
    print(f"{'='*50}")
    print(f"  webhostmost.com 保活脚本")
    print(f"  运行时间: {now}")
    print(f"{'='*50}\n")

    email = os.environ.get("HOSTING_EMAIL", "")
    password = os.environ.get("HOSTING_PASSWORD", "")

    if not email or not password:
        print("错误: 未设置环境变量！")
        print("请设置以下环境变量：")
        print("  HOSTING_EMAIL    = 你的登录邮箱")
        print("  HOSTING_PASSWORD = 你的登录密码")
        sys.exit(1)

    print(f"账户: {email}\n")

    success = keep_alive(email, password)

    print()
    if success:
        print("✓ 保活任务完成，主机服务状态已刷新。")
        sys.exit(0)
    else:
        print("✗ 保活任务失败，请检查日志。")
        sys.exit(1)


if __name__ == "__main__":
    main()
