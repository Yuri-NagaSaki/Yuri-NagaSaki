# GitHub 个人介绍页设置指南

这个项目可以自动更新你的GitHub个人介绍页面，显示最近star的项目、WordPress博客文章和Steam游戏记录。

## 🚀 快速开始

### 1. 创建个人介绍仓库

1. 在GitHub上创建一个与你的用户名**完全相同**的仓库
2. 将此项目的文件复制到该仓库
3. 确保仓库是**公开**的（Public）

### 2. 配置GitHub Secrets

在你的仓库中，进入 `Settings` → `Secrets and variables` → `Actions`，添加以下Secrets：

#### 必需的Secrets

| Secret Name | 描述 | 获取方法 |
|------------|------|---------|
| `GH_USERNAME` | 你的GitHub用户名 | 直接填入你的用户名 |
| `GH_TOKEN` | GitHub Personal Access Token | [生成方法](#github-token) |

#### 可选的Secrets

| Secret Name | 描述 | 获取方法 |
|------------|------|---------|
| `WORDPRESS_URL` | WordPress站点URL | 你的博客地址，如 `https://yourblog.com` |
| `STEAM_API_KEY` | Steam API密钥 | [生成方法](#steam-api) |
| `STEAM_USER_ID` | Steam用户ID（64位） | [查找方法](#steam-user-id) |

### 3. 个性化设置

编辑 `README.md` 文件，替换以下占位符：

- `[Your Name]` → 你的姓名
- `yourusername` → 你的GitHub用户名
- `[你的项目名称]` → 当前主要项目
- `[your-email@example.com]` → 你的邮箱
- 更新社交媒体链接
- 修改技术栈图标

## 🔑 API密钥获取方法

### GitHub Token

1. 登录GitHub，点击右上角头像 → `Settings`
2. 左侧菜单点击 `Developer settings`
3. 点击 `Personal access tokens` → `Tokens (classic)`
4. 点击 `Generate new token` → `Generate new token (classic)`
5. 设置名称和过期时间
6. 勾选以下权限：
   - `repo` (如果仓库是私有的)
   - `public_repo` (如果仓库是公开的)
   - `user:read` (读取用户信息)
7. 生成并复制token

### Steam API

1. 登录Steam，访问 [Steam API Key页面](https://steamcommunity.com/dev/apikey)
2. 填写域名（可以填 `localhost`）
3. 同意条款并获取API密钥

### Steam User ID

方法1 - 使用在线工具：
1. 访问 [SteamID.io](https://steamid.io/)
2. 输入你的Steam个人资料URL或用户名
3. 复制 `steamID64` 数值

方法2 - 从Steam个人资料获取：
1. 登录Steam，查看你的个人资料
2. 如果URL是 `https://steamcommunity.com/profiles/76561198XXXXXXXXX`
3. 那么后面的数字就是你的Steam ID

## 📝 WordPress设置

确保你的WordPress站点：

1. **启用REST API**（WordPress 4.7+默认启用）
2. **设置为公开访问**（不需要认证）
3. **测试API连接**：访问 `https://yourblog.com/wp-json/wp/v2/posts`

如果遇到问题：
- 检查WordPress版本是否支持REST API
- 确认没有插件禁用REST API
- 检查服务器防火墙设置

## ⚙️ 工作流程设置

### 自动更新时间

默认每天凌晨2点（UTC）自动更新，你可以修改 `.github/workflows/update-readme.yml` 中的cron表达式：

```yaml
schedule:
  - cron: '0 2 * * *'  # 每天凌晨2点 (UTC)
```

### 手动触发更新

1. 进入仓库的 `Actions` 标签页
2. 选择 `Update README` 工作流
3. 点击 `Run workflow` 按钮

## 🔧 自定义配置

### 修改显示数量

在 `scripts/update_readme.py` 中修改：

```python
# 获取GitHub stars数量
stars_content = await get_recent_stars(github_username, github_token, limit=10)

# 获取WordPress文章数量  
blog_content = await get_recent_posts(wordpress_url, limit=8)

# 获取Steam游戏数量
steam_content = await get_recent_games(steam_api_key, steam_user_id, limit=6)
```

### 修改样式主题

在 `README.md` 中可以修改图表主题：

- `tokyonight` → `dark`, `radical`, `merko`, `gruvbox`, `onedark` 等
- 更多主题查看 [GitHub Readme Stats Themes](https://github.com/anuraghazra/github-readme-stats/blob/master/themes/README.md)

## 🐛 故障排除

### 常见问题

1. **工作流执行失败**
   - 检查Secrets是否正确设置
   - 查看Actions页面的错误日志

2. **GitHub Stars不显示**
   - 确认GITHUB_TOKEN权限正确
   - 检查用户名是否正确

3. **WordPress文章不显示**
   - 测试WordPress REST API是否可访问
   - 确认站点URL格式正确

4. **Steam游戏不显示**
   - 确认Steam资料为公开状态
   - 检查API密钥和用户ID是否正确

### 调试方法

1. 查看Actions执行日志
2. 本地运行脚本测试：
   ```bash
   python scripts/update_readme.py
   ```

## 📞 获取帮助

如果遇到问题：

1. 查看Actions页面的详细错误信息
2. 检查各项配置是否正确
3. 确认API密钥权限和有效性

## 🎨 进阶定制

你可以进一步定制：

- 添加更多数据源（如Spotify、Goodreads等）
- 修改Markdown模板样式
- 添加更多统计图表
- 集成其他GitHub功能

---

**享受你的动态GitHub个人介绍页面吧！** 🎉 
