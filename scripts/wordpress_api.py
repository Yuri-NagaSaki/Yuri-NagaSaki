#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
import html
import re

async def get_recent_posts(wordpress_url: str, limit: int = 5) -> str:
    """
    从WordPress站点获取最新文章
    
    Args:
        wordpress_url: WordPress站点URL
        limit: 返回文章数量限制
    
    Returns:
        格式化的markdown字符串
    """
    
    if not wordpress_url:
        return "<!-- 请在GitHub Secrets中设置WORDPRESS_URL -->"
    
    # 确保URL格式正确
    if not wordpress_url.startswith(('http://', 'https://')):
        wordpress_url = f'https://{wordpress_url}'
    
    # 构建WordPress REST API URL
    api_url = f"{wordpress_url.rstrip('/')}/wp-json/wp/v2/posts"
    
    params = {
        'per_page': limit,
        'orderby': 'date',
        'order': 'desc',
        '_embed': 'true'  # 包含嵌入的媒体和作者信息
    }
    
    headers = {
        'User-Agent': 'GitHub-Profile-Updater'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers, params=params, timeout=10) as response:
                if response.status == 200:
                    posts = await response.json()
                    return format_blog_posts(posts, wordpress_url)
                elif response.status == 404:
                    return f"<!-- WordPress站点 {wordpress_url} 不存在或未启用REST API -->"
                else:
                    return f"<!-- WordPress API 错误: {response.status} -->"
                    
    except asyncio.TimeoutError:
        return "<!-- WordPress API 请求超时 -->"
    except Exception as e:
        return f"<!-- 获取 WordPress 文章时发生错误: {str(e)} -->"

def format_blog_posts(posts: List[Dict], base_url: str) -> str:
    """格式化博客文章为markdown - 简洁双列布局"""
    
    if not posts:
        return "暂无最新博客文章"
    
    # 创建双列布局
    post_items = []
    for post in posts:
        title = html.unescape(post['title']['rendered'])
        link = post['link']
        date_str = format_date(post['date'])
        
        # 简洁格式 - 只显示标题和日期
        post_item = f'<li><a href="{link}" target="_blank">📝 <strong>{title}</strong></a> <small>({date_str})</small></li>'
        post_items.append(post_item)
    
    # 分成两列
    mid = len(post_items) // 2 + len(post_items) % 2
    left_column = post_items[:mid]
    right_column = post_items[mid:]
    
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

def clean_excerpt(excerpt: str) -> str:
    """清理文章摘要，移除HTML标签"""
    
    if not excerpt:
        return "无摘要"
    
    # 移除HTML标签
    excerpt = re.sub(r'<[^>]+>', '', excerpt)
    # 解码HTML实体
    excerpt = html.unescape(excerpt)
    # 移除多余的空白字符
    excerpt = re.sub(r'\s+', ' ', excerpt).strip()
    
    # 限制长度
    if len(excerpt) > 150:
        excerpt = excerpt[:150] + "..."
    
    return excerpt

def format_date(date_str: str) -> str:
    """格式化日期字符串"""
    
    try:
        # WordPress通常返回ISO格式的日期
        date_obj = datetime.fromisoformat(date_str.replace('T', ' ').replace('Z', '+00:00'))
        return date_obj.strftime('%m/%d')
    except Exception:
        return '未知日期'

def get_post_categories(post: Dict) -> List[str]:
    """获取文章分类"""
    
    categories = []
    
    # 尝试从_embedded数据中获取分类
    if '_embedded' in post and 'wp:term' in post['_embedded']:
        for term_group in post['_embedded']['wp:term']:
            for term in term_group:
                if term.get('taxonomy') == 'category':
                    categories.append(term['name'])
    
    return categories

def get_featured_image(post: Dict) -> Optional[str]:
    """获取特色图片URL"""
    
    if '_embedded' in post and 'wp:featuredmedia' in post['_embedded']:
        featured_media = post['_embedded']['wp:featuredmedia']
        if featured_media:
            return featured_media[0].get('source_url')
    
    return None

async def test_wordpress_connection(wordpress_url: str) -> bool:
    """测试WordPress连接是否正常"""
    
    try:
        api_url = f"{wordpress_url.rstrip('/')}/wp-json/wp/v2/posts"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=5) as response:
                return response.status == 200
    except Exception:
        return False 
