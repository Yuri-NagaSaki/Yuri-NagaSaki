#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import asyncio
from datetime import datetime, timezone
from github_api import get_recent_stars
from wordpress_api import get_recent_posts
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
        github_username = os.getenv('GITHUB_USERNAME', 'yourusername')
        github_token = os.getenv('GITHUB_TOKEN')
        stars_content = await get_recent_stars(github_username, github_token)
        
        # 获取WordPress文章
        print("📝 获取WordPress文章...")
        wordpress_url = os.getenv('WORDPRESS_URL')
        if wordpress_url:
            blog_content = await get_recent_posts(wordpress_url)
        else:
            blog_content = "<!-- 请在GitHub Secrets中设置WORDPRESS_URL -->"
        
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
            r'<!-- GITHUB_STARS:START -->.*?<!-- GITHUB_STARS:END -->',
            f'<!-- GITHUB_STARS:START -->\n{stars_content}\n<!-- GITHUB_STARS:END -->',
            content,
            flags=re.DOTALL
        )
        
        # 更新博客文章部分
        content = re.sub(
            r'<!-- BLOG_POSTS:START -->.*?<!-- BLOG_POSTS:END -->',
            f'<!-- BLOG_POSTS:START -->\n{blog_content}\n<!-- BLOG_POSTS:END -->',
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

if __name__ == "__main__":
    asyncio.run(update_readme()) 
