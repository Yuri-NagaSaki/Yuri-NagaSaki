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
    """格式化star的仓库为markdown"""
    
    if not repos:
        return "暂无最近star的项目"
    
    markdown_lines = []
    
    for repo in repos:
        name = repo['name']
        full_name = repo['full_name']
        description = repo.get('description', '无描述')
        language = repo.get('language', 'Unknown')
        stars = repo['stargazers_count']
        url = repo['html_url']
        
        # 获取star时间
        starred_at = repo.get('starred_at')
        if starred_at:
            starred_time = datetime.fromisoformat(starred_at.replace('Z', '+00:00'))
            time_str = starred_time.strftime('%Y-%m-%d')
        else:
            time_str = '未知时间'
        
        # 语言图标
        lang_icon = get_language_icon(language)
        
        # 格式化单个仓库
        repo_md = f"""
<div align="left">
  <h4>
    <a href="{url}" target="_blank">
      {lang_icon} {full_name}
    </a>
    <img src="https://img.shields.io/github/stars/{full_name}?style=social" alt="stars" align="right">
  </h4>
  <p>{description}</p>
  <p>
    <img src="https://img.shields.io/badge/Language-{language}-blue?style=flat-square" alt="language">
    <img src="https://img.shields.io/badge/Starred-{time_str}-green?style=flat-square" alt="starred">
  </p>
</div>

---
"""
        markdown_lines.append(repo_md.strip())
    
    return '\n\n'.join(markdown_lines)

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
