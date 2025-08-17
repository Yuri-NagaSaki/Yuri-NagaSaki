#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import asyncio
from datetime import datetime, timezone
from github_api import get_recent_stars

async def update_readme():
    """更新README.md文件中的动态内容"""
    
    print("🚀 开始更新README.md...")
    
    # 读取当前README.md
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        # 获取GitHub stars
        print("📊 获取GitHub stars...")
        github_username = os.getenv('GH_USERNAME', 'yourusername')
        github_token = os.getenv('GH_TOKEN')
        
        stars_data = await get_recent_stars(github_username, github_token, return_data=True)
        
        # 生成Star项目内容
        stars_content = format_stars_content(stars_data)
        
        
        # 更新README内容
        print("✏️ 更新README内容...")
        
        # 更新GitHub stars部分
        content = re.sub(
            r'## (?:<div align="center">)?🌟 最近动态(?:</div>)?.*?<!-- GITHUB_STARS:END -->',
            f'## <div align="center">🌟 最近动态</div>\n\n<!-- GITHUB_STARS:START -->\n{stars_content}\n<!-- GITHUB_STARS:END -->',
            content,
            flags=re.DOTALL
        )
        
        # 移除博客文章部分
        content = re.sub(
            r'## 📝 最新博客文章.*?<!-- BLOG_POSTS:END -->\n\n',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 移除Steam游戏部分
        content = re.sub(
            r'## <div align="center">🎮 Steam 最近游戏</div>.*?<!-- STEAM_GAMES:END -->\n\n',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 更新时间戳
        current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        content = re.sub(
            r'<!-- UPDATE_TIME:START -->.*?<!-- UPDATE_TIME:END -->',
            f'<!-- UPDATE_TIME:START -->{current_time}<!-- UPDATE_TIME:END -->',
            content,
            flags=re.DOTALL
        )
        
        # 写入更新后的内容
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ README.md 更新完成!")
        
    except Exception as e:
        print(f"❌ 更新过程中发生错误: {e}")
        raise

def format_stars_content(stars_data):
    """格式化Star项目内容（优化排版）"""
    
    if not stars_data or not isinstance(stars_data, list):
        return '<div align="center" style="color: #8b949e; padding: 20px;">暂无最近star的项目</div>'
    
    star_items = []
    for i, repo in enumerate(stars_data[:5]):  # 最多显示5个
        name = repo.get('name', 'Unknown')
        full_name = repo.get('full_name', 'Unknown')
        url = repo.get('html_url', '#')
        description = repo.get('description', '')
        language = repo.get('language', '')
        
        # 截取描述到合适长度
        if description and len(description) > 80:
            description = description[:80] + "..."
        
        star_item = f"""
<div align="center" style="max-width: 700px; margin: 8px auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 10px; padding: 16px; border: 1px solid #30363d;">
  <div style="display: flex; align-items: center; gap: 12px;">
    <div style="color: #ffd700; font-size: 18px;">⭐</div>
    <div style="flex: 1; text-align: left;">
      <div>
        <a href="{url}" target="_blank" style="color: #58a6ff; text-decoration: none; font-weight: 600; font-size: 16px;">
          {full_name}
        </a>
      </div>
      {f'<div style="color: #8b949e; font-size: 13px; margin-top: 4px;">{description}</div>' if description else ''}
      {f'<div style="margin-top: 6px;"><span style="color: {get_language_color(language)}; font-size: 12px;">● {language}</span></div>' if language else ''}
    </div>
  </div>
</div>"""
        star_items.append(star_item)
    
    return '\n'.join(star_items)

def get_language_color(language):
    """获取编程语言对应的颜色"""
    colors = {
        'Python': '#3776ab',
        'JavaScript': '#f1e05a',
        'TypeScript': '#2b7489',
        'Java': '#b07219',
        'C++': '#f34b7d',
        'C': '#555555',
        'Go': '#00add8',
        'Rust': '#dea584',
        'PHP': '#4f5d95',
        'Ruby': '#701516',
        'Swift': '#ffac45',
        'Kotlin': '#f18e33',
        'Dart': '#00b4ab',
        'Shell': '#89e051',
        'HTML': '#e34c26',
        'CSS': '#1572b6',
        'Vue': '#4fc08d',
        'React': '#61dafb'
    }
    return colors.get(language, '#8b949e')

if __name__ == "__main__":
    asyncio.run(update_readme()) 
