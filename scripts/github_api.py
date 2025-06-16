#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional

async def get_recent_stars(username: str, token: str, limit: int = 5, return_data: bool = False):
    """
    获取用户最近star的项目
    
    Args:
        username: GitHub用户名
        token: GitHub personal access token
        limit: 返回项目数量限制
        return_data: 是否返回原始数据而不是格式化的markdown
    
    Returns:
        格式化的markdown字符串或原始数据列表
    """
    
    if not token:
        if return_data:
            return []
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
                    if return_data:
                        return repos
                    return format_starred_repos(repos)
                elif response.status == 401:
                    if return_data:
                        return []
                    return "<!-- GitHub Token 无效或已过期 -->"
                elif response.status == 404:
                    if return_data:
                        return []
                    return f"<!-- 用户 {username} 不存在 -->"
                else:
                    if return_data:
                        return []
                    return f"<!-- GitHub API 错误: {response.status} -->"
                    
    except Exception as e:
        if return_data:
            return []
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
        
        # 统一大小的卡片格式
        card = f"""
<div style="border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin: 8px; background: #0d1117; height: 120px; display: flex; flex-direction: column; justify-content: space-between;">
  <div>
    <h4 style="margin: 0 0 8px 0; font-size: 16px;">
      <a href="{url}" target="_blank" style="color: #58a6ff; text-decoration: none;">
        {lang_icon} {full_name}
      </a>
    </h4>
    <p style="color: #8b949e; font-size: 13px; margin: 0; line-height: 1.4; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
      {description}
    </p>
  </div>
  <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
    <span style="color: {lang_color}; font-size: 12px;">● {language}</span>
    <img src="https://img.shields.io/github/stars/{full_name}?style=social" alt="stars" style="height: 16px;"/>
  </div>
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
