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
    """格式化star的仓库为markdown - 简洁双列布局"""
    
    if not repos:
        return "暂无最近star的项目"
    
    # 创建双列布局
    repo_items = []
    for repo in repos:
        name = repo['name']
        full_name = repo['full_name']
        url = repo['html_url']
        language = repo.get('language', 'Unknown')
        stars = repo['stargazers_count']
        
        # 语言图标
        lang_icon = get_language_icon(language)
        
        # 简洁格式
        repo_item = f'<li><a href="{url}" target="_blank">{lang_icon} <strong>{full_name}</strong></a> <img src="https://img.shields.io/github/stars/{full_name}?style=flat&color=yellow" alt="⭐"/></li>'
        repo_items.append(repo_item)
    
    # 分成两列
    mid = len(repo_items) // 2 + len(repo_items) % 2
    left_column = repo_items[:mid]
    right_column = repo_items[mid:]
    
    # 生成双列HTML
    left_list = f'<ul>\n{chr(10).join(left_column)}\n</ul>' if left_column else ''
    right_list = f'<ul>\n{chr(10).join(right_column)}\n</ul>' if right_column else ''
    
    return f"""
<table>
<tr>
<td width="50%">

{left_list}

</td>
<td width="50%">

{right_list}

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
