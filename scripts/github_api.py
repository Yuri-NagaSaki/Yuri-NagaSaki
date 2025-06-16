#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional

async def get_recent_stars(username: str, token: str, limit: int = 5) -> str:
    """
    获取用户最近star的项目
    
    Args:
        username: GitHub用户名
        token: GitHub personal access token
        limit: 返回项目数量限制
    
    Returns:
        格式化的markdown字符串
    """
    
    if not token:
        return "<!-- 请在GitHub Secrets中设置GITHUB_TOKEN -->"
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'GitHub-Profile-Updater'
    }
    
    url = f'https://api.github.com/users/{username}/starred'
    params = {
        'sort': 'created',
        'direction': 'desc',
        'per_page': limit
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    repos = await response.json()
                    return format_starred_repos(repos)
                elif response.status == 401:
                    return "<!-- GitHub Token 无效或已过期 -->"
                elif response.status == 404:
                    return f"<!-- 用户 {username} 不存在 -->"
                else:
                    return f"<!-- GitHub API 错误: {response.status} -->"
                    
    except Exception as e:
        return f"<!-- 获取 GitHub stars 时发生错误: {str(e)} -->"

def format_starred_repos(repos: List[Dict]) -> str:
    """格式化star的仓库为markdown - 现代卡片样式"""
    
    if not repos:
        return "暂无最近star的项目"
    
    # 创建卡片样式
    repo_cards = []
    for repo in repos:
        name = repo['name']
        full_name = repo['full_name']
        description = repo.get('description', '无描述')
        url = repo['html_url']
        language = repo.get('language', 'Unknown')
        stars = repo['stargazers_count']
        
        # 语言图标和颜色
        lang_icon = get_language_icon(language)
        lang_color = get_language_color(language)
        
        # 格式化描述（限制长度）
        if len(description) > 60:
            description = description[:60] + "..."
        
        # 美化的卡片格式
        card = f"""
<div align="center">
  <table>
    <tr>
      <td>
        <a href="{url}">
          <img width="400" height="120" src="https://github-readme-stats.vercel.app/api/pin/?username={full_name.split('/')[0]}&repo={name}&theme=tokyonight&show_owner=true&hide_border=true" alt="{full_name}">
        </a>
      </td>
    </tr>
  </table>
</div>"""
        repo_cards.append(card)
    
    # 双列布局
    mid = len(repo_cards) // 2 + len(repo_cards) % 2
    left_cards = repo_cards[:mid]
    right_cards = repo_cards[mid:]
    
    left_content = '\n'.join(left_cards)
    right_content = '\n'.join(right_cards)
    
    return f"""
<table>
<tr>
<td width="50%" valign="top">

{left_content}

</td>
<td width="50%" valign="top">

{right_content}

</td>
</tr>
</table>"""

def get_language_icon(language: str) -> str:
    """根据编程语言返回对应的emoji图标"""
    
    icons = {
        'Python': '🐍',
        'JavaScript': '🟨',
        'TypeScript': '🔷',
        'Java': '☕',
        'C++': '⚡',
        'C': '🔧',
        'C#': '🔵',
        'Go': '🐹',
        'Rust': '🦀',
        'PHP': '🐘',
        'Ruby': '💎',
        'Swift': '🐦',
        'Kotlin': '🟣',
        'Dart': '🎯',
        'HTML': '🌐',
        'CSS': '🎨',
        'Shell': '💻',
        'Dockerfile': '🐳',
        'Vue': '💚',
        'React': '⚛️',
        'Angular': '🅰️',
        'Node.js': '🟢',
    }
    
    return icons.get(language, '📄')

def get_language_color(language: str) -> str:
    """根据编程语言返回对应的颜色"""
    
    colors = {
        'Python': '3776ab',
        'JavaScript': 'f7df1e',
        'TypeScript': '007acc',
        'Java': 'ed8b00',
        'C++': '00599c',
        'C': 'a8b9cc',
        'C#': '239120',
        'Go': '00add8',
        'Rust': 'dea584',
        'PHP': '777bb4',
        'Ruby': 'cc342d',
        'Swift': 'fa7343',
        'Kotlin': '0095d5',
        'Dart': '0175c2',
        'HTML': 'e34c26',
        'CSS': '1572b6',
        'Shell': '89e051',
        'Dockerfile': '384d54',
        'Vue': '4fc08d',
        'React': '61dafb',
        'Angular': 'dd0031',
    }
    
    return colors.get(language, '586069')

async def get_user_info(username: str, token: str) -> Dict:
    """获取用户基本信息"""
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'GitHub-Profile-Updater'
    }
    
    url = f'https://api.github.com/users/{username}'
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {}
    except Exception:
        return {}

async def test_github_connection(username: str, token: str) -> bool:
    """测试GitHub连接是否正常"""
    
    try:
        user_info = await get_user_info(username, token)
        return bool(user_info)
    except Exception:
        return False 
