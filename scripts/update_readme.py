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
        github_username = os.getenv('GH_USERNAME', 'yourusername')
        github_token = os.getenv('GH_TOKEN')
        print(f"   GitHub用户名: {github_username}")
        print(f"   GitHub Token前缀: {github_token[:20] if github_token else 'None'}...")
        
        stars_data = await get_recent_stars(github_username, github_token, return_data=True)
        print(f"   获取到 {len(stars_data) if isinstance(stars_data, list) else 0} 个star项目")
        if isinstance(stars_data, list) and len(stars_data) > 0:
            print(f"   示例项目: {stars_data[0].get('full_name', 'Unknown')}")
        
        # 获取WordPress文章
        print("📝 获取WordPress文章...")
        wordpress_url = os.getenv('WORDPRESS_URL')
        print(f"   WordPress URL: {wordpress_url}")
        
        if wordpress_url:
            blog_data = await get_recent_posts(wordpress_url, return_data=True)
            print(f"   获取到 {len(blog_data) if isinstance(blog_data, list) else 0} 篇文章")
            if isinstance(blog_data, list) and len(blog_data) > 0:
                print(f"   示例文章: {blog_data[0].get('title', 'Unknown')}")
        else:
            blog_data = []
            print("   WordPress URL未设置")
        
        # 生成组合内容
        print("🔄 生成组合内容...")
        combined_content = format_combined_content(stars_data, blog_data)
        print(f"   组合内容长度: {len(combined_content)} 字符")
        
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
        
        # 使用新的组合内容替换原来的两个部分
        # 首先找到并替换GitHub stars部分
        print("DEBUG: Looking for GitHub stars section to replace...")
        old_content_length = len(content)
        content = re.sub(
            r'## 🌟 最近动态.*?<!-- GITHUB_STARS:END -->',
            f'## 🌟 最近动态\n\n<!-- GITHUB_STARS:START -->\n{combined_content}\n<!-- GITHUB_STARS:END -->',
            content,
            flags=re.DOTALL
        )
        new_content_length = len(content)
        print(f"DEBUG: Content length change after GitHub stars replacement: {old_content_length} -> {new_content_length}")
        
        # 移除博客文章部分（因为已经合并到上面）
        print("DEBUG: Looking for blog posts section to remove...")
        old_content_length = len(content)
        content = re.sub(
            r'## 📝 最新博客文章.*?<!-- BLOG_POSTS:END -->\n\n',
            '',
            content,
            flags=re.DOTALL
        )
        new_content_length = len(content)
        print(f"DEBUG: Content length change after blog posts removal: {old_content_length} -> {new_content_length}")
        
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

def format_combined_content(stars_data, blog_data):
    """格式化组合内容：左边是star项目，右边是博客文章"""
    
    print(f"DEBUG: format_combined_content called with:")
    print(f"  stars_data type: {type(stars_data)}, length: {len(stars_data) if isinstance(stars_data, list) else 'N/A'}")
    print(f"  blog_data type: {type(blog_data)}, length: {len(blog_data) if isinstance(blog_data, list) else 'N/A'}")
    
    # 格式化star项目（简化版）
    star_items = []
    if stars_data and isinstance(stars_data, list):
        print(f"DEBUG: Processing {len(stars_data)} star repos")
        for i, repo in enumerate(stars_data[:5]):  # 最多显示5个
            name = repo.get('name', 'Unknown')
            full_name = repo.get('full_name', 'Unknown')
            description = repo.get('description', '无描述')
            url = repo.get('html_url', '#')
            
            print(f"  Repo {i+1}: {full_name}")
            
            # 限制描述长度
            if len(description) > 50:
                description = description[:50] + "..."
            
            star_item = f"""
<div style="padding: 8px 12px; margin: 4px 0; border-radius: 6px; background: rgba(88, 166, 255, 0.08); border-left: 3px solid #58a6ff;">
  <div style="margin-bottom: 4px;">
    <a href="{url}" target="_blank" style="color: #58a6ff; text-decoration: none; font-weight: 500; font-size: 14px;">
      ⭐ {full_name}
    </a>
  </div>
  <div style="color: #8b949e; font-size: 12px; line-height: 1.3;">
    {description}
  </div>
</div>"""
            star_items.append(star_item)
    else:
        print("DEBUG: No valid stars data, using fallback")
        star_items.append('<div style="color: #8b949e; text-align: center; padding: 20px;">暂无最近star的项目</div>')
    
    # 格式化博客文章（只显示标题）
    blog_items = []
    if blog_data and isinstance(blog_data, list):
        print(f"DEBUG: Processing {len(blog_data)} blog posts")
        for i, post in enumerate(blog_data[:5]):  # 最多显示5个
            title = post.get('title', '无标题')
            url = post.get('link', '#')
            
            print(f"  Post {i+1}: {title}")
            
            blog_item = f"""
<div style="padding: 8px 12px; margin: 4px 0; border-radius: 6px; background: rgba(255, 165, 0, 0.08); border-left: 3px solid #ffa500;">
  <div>
    <a href="{url}" target="_blank" style="color: #ffa500; text-decoration: none; font-weight: 500; font-size: 14px;">
      📝 {title}
    </a>
  </div>
</div>"""
            blog_items.append(blog_item)
    else:
        print("DEBUG: No valid blog data, using fallback")
        blog_items.append('<div style="color: #8b949e; text-align: center; padding: 20px;">暂无最新博客文章</div>')
    
    # 组合两列布局
    stars_content = '\n'.join(star_items)
    blog_content = '\n'.join(blog_items)
    
    print(f"DEBUG: Generated content lengths - stars: {len(stars_content)}, blog: {len(blog_content)}")
    
    return f"""
<div style="border: 1px solid #30363d; border-radius: 8px; padding: 16px; background: #0d1117;">
  <table style="width: 100%; border-collapse: collapse;">
    <tr>
      <td style="width: 50%; vertical-align: top; padding-right: 8px;">
        <h4 style="margin: 0 0 12px 0; color: #58a6ff; font-size: 16px; text-align: center;">
          ⭐ 最近 Star 的项目
        </h4>
        {stars_content}
      </td>
      <td style="width: 50%; vertical-align: top; padding-left: 8px; border-left: 1px solid #30363d;">
        <h4 style="margin: 0 0 12px 0; color: #ffa500; font-size: 16px; text-align: center;">
          📝 最新博客文章
        </h4>
        {blog_content}
      </td>
    </tr>
  </table>
</div>"""

if __name__ == "__main__":
    asyncio.run(update_readme()) 
