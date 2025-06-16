#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import asyncio
from datetime import datetime, timezone
from github_api import get_recent_stars
from steam_api import get_recent_games

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
        
        # 获取Steam游戏
        print("🎮 获取Steam游戏...")
        steam_api_key = os.getenv('STEAM_API_KEY')
        steam_user_id = os.getenv('STEAM_USER_ID')
        if steam_api_key and steam_user_id:
            steam_content = await get_recent_games(steam_api_key, steam_user_id)
        else:
            steam_content = "<!-- 请在GitHub Secrets中设置STEAM_API_KEY和STEAM_USER_ID -->"
        
        # 更新README内容
        print("✏️ 更新README内容...")
        
        # 更新GitHub stars部分
        content = re.sub(
            r'## 🌟 最近动态.*?<!-- GITHUB_STARS:END -->',
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
        
        # 更新Steam游戏部分
        content = re.sub(
            r'<!-- STEAM_GAMES:START -->.*?<!-- STEAM_GAMES:END -->',
            f'<!-- STEAM_GAMES:START -->\n{steam_content}\n<!-- STEAM_GAMES:END -->',
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
    """格式化Star项目内容（居中显示）"""
    
    star_items = []
    if stars_data and isinstance(stars_data, list):
        for i, repo in enumerate(stars_data[:5]):  # 最多显示5个
            name = repo.get('name', 'Unknown')
            full_name = repo.get('full_name', 'Unknown')
            url = repo.get('html_url', '#')
            
            star_item = f"""
<div align="center" style="padding: 8px 12px; margin: 4px auto; max-width: 600px; border-radius: 6px; background: rgba(88, 166, 255, 0.08); border-left: 3px solid #58a6ff;">
  <div>
    <a href="{url}" target="_blank" style="color: #58a6ff; text-decoration: none; font-weight: 500; font-size: 14px;">
      ⭐ {full_name}
    </a>
  </div>
</div>"""
            star_items.append(star_item)
    else:
        star_items.append('<div align="center" style="color: #8b949e; padding: 20px;">暂无最近star的项目</div>')
    
    return f"""
<div align="center" style="border: 1px solid #30363d; border-radius: 8px; padding: 16px; background: #0d1117; max-width: 800px; margin: 0 auto;">
  <div style="margin-bottom: 16px;">
    {''.join(star_items)}
  </div>
</div>"""

if __name__ == "__main__":
    asyncio.run(update_readme()) 
