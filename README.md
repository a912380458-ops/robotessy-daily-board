# Robotessy 最新动态看板

这是一个按天聚合的 Robotessy 动态看板，分为中国与海外两栏。

## 功能

- 看板展示：按日期显示新闻动态
- 自动更新：每天北京时间 10:00（UTC 02:00）自动抓取并更新
- 公开访问：通过 GitHub Pages 提供公开 HTTP(S) 链接

## 本地手动更新

```bash
python scripts/update_digest.py
```

## 发布为公开链接

1. 将仓库推送到 GitHub。
2. 在仓库 `Settings -> Pages` 中启用 `GitHub Actions` 作为来源。
3. 工作流 `.github/workflows/update-dashboard.yml` 会自动发布。
4. 公开链接格式：
   - `https://<你的GitHub用户名>.github.io/<仓库名>/`

## 可选配置

- 修改关键词：设置环境变量 `KEYWORD`（默认 `Robotessy`）
- 调整回溯天数：设置 `LOOKBACK_DAYS`（默认 `14`）
- 调整每日展示条数：设置 `MAX_ITEMS_PER_DAY`（默认 `8`）
