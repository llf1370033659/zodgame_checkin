# zodgame_checkin
Zodgame automatic check-in using github action

使用者可自行在本仓库Actions中查询本项目运行状况。由于CloudFlare本身机制的更新，可能会导致本项目无法运作。

本仓库非必要不更新，如若更新，请尽可能保持同步。

## 功能描述

1. 每日自动进行签到
2. 每日自动完成Bux任务
3. 若签到失败或完成任务失败，由Assert机制报错。

## 使用方法
### 1. 添加 Cookie 至 Secrets

- 首先通过F12抓取到在浏览器中抓取`Cookie`.
<p align="center">
  <img src="imgs/Step1.png" />
</p>

- 在项目页面，依次点击`Settings`-->`Secrets`-->`New secret`
- 建立名为`ZODGAME_COOKIE`的 secret，值为复制的`Cookie`内容，最后点击`Add secret`
- secret名字必须为`ZODGAME_COOKIE`！
<p align="center">
  <img src="imgs/Step2.png" />
</p>
<p align="center">
  <img src="imgs/Step3.png" />
</p>

### 2. 启用 Actions

- 在**自己的仓库**中添加 Secret，名称为 `ZODGAME_COOKIE`：`Settings` → `Secrets and variables` → `Actions` → `New repository secret`。Cookie 必须是登录后请求的完整 Cookie 请求头，包含 `qhMq_2132_saltkey` 和 `qhMq_2132_auth`。不要将值写入源码、Issue 或运行命令。
- Fork 后先进入 `Actions`，按页面提示启用自己的工作流。如果定时任务已因仓库长期没有活动而被停用，在 `zodgame` 工作流页面选择 `Enable workflow`。
- 确认更新后的工作流和脚本已提交到默认分支 `main`。进入 `Actions` → `zodgame` → `Run workflow`，选择 `main`，先手动运行一次并检查 `Run check-in` 的日志。
- 定时任务每天北京时间 08:00 执行（UTC `0 0 * * *`），GitHub 调度可能延迟。也支持手动运行；向 `main` 提交工作流、脚本或测试更新时会自动运行，以验证修改。Pull Request 和仅修改文档的提交不会触发个人账户签到。
- 工作流安装匹配的 Chrome 和 ChromeDriver，并从 Actions Secret 读取 Cookie。独立的 keepalive 任务具有 `actions: write` 权限，即使签到失败也会运行，用于防止定时任务因仓库不活跃而停用；已经停用的工作流仍需先手动启用。
- 若日志提示缺少 Secret，检查是否添加到了自己的仓库的 Actions Secrets；若提示登录失败，重新获取并更新 Cookie。ChromeDriver 版本不匹配、Cloudflare 验证和登录失败是不同问题，请按失败步骤判断。真实签到仍取决于 Cookie 有效性和站点当前的 Cloudflare 策略。

### 本地开发

安装 `zodgame/requirements.txt` 和 `setuptools`。脚本优先读取环境变量 `ZODGAME_COOKIE`；未设置时仍兼容原来的命令行参数方式。可用 `CHROME_BINARY`、`CHROMEDRIVER_BINARY` 和 `CHROME_VERSION` 指定浏览器、驱动及版本；未指定时使用 `undetected-chromedriver` 自动发现或下载。Linux 无图形界面时可设置 `ZODGAME_HEADLESS=1`，但无头浏览器不保证能通过 Cloudflare。

执行离线回归测试：`python -m unittest discover -s tests -v`。这些测试不访问账号或执行真实签到。
