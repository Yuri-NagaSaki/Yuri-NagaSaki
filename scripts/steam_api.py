#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional

async def get_recent_games(api_key: str, steam_id: str, limit: int = 5) -> str:
    """
    获取Steam用户最近玩的游戏
    
    Args:
        api_key: Steam API密钥
        steam_id: Steam用户ID (64位)
        limit: 返回游戏数量限制
    
    Returns:
        格式化的markdown字符串
    """
    
    if not api_key or not steam_id:
        return "<!-- 请在GitHub Secrets中设置STEAM_API_KEY和STEAM_USER_ID -->"
    
    # Steam API URL
    url = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
    
    params = {
        'key': api_key,
        'steamid': steam_id,
        'format': 'json',
        'count': limit
    }
    
    headers = {
        'User-Agent': 'GitHub-Profile-Updater'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'response' in data and 'games' in data['response']:
                        games = data['response']['games']
                        return await format_steam_games(games, session, api_key)
                    else:
                        return "暂无最近游戏记录"
                elif response.status == 401:
                    return "<!-- Steam API密钥无效 -->"
                elif response.status == 403:
                    return "<!-- Steam用户资料为私人状态或API密钥权限不足 -->"
                else:
                    return f"<!-- Steam API 错误: {response.status} -->"
                    
    except asyncio.TimeoutError:
        return "<!-- Steam API 请求超时 -->"
    except Exception as e:
        return f"<!-- 获取 Steam 游戏时发生错误: {str(e)} -->"

async def format_steam_games(games: List[Dict], session: aiohttp.ClientSession, api_key: str) -> str:
    """格式化Steam游戏为markdown"""
    
    if not games:
        return "暂无最近游戏记录"
    
    markdown_lines = []
    
    # 获取游戏详细信息
    for game in games:
        app_id = game['appid']
        name = game['name']
        playtime_2weeks = game.get('playtime_2weeks', 0)  # 最近两周游戏时间（分钟）
        playtime_forever = game.get('playtime_forever', 0)  # 总游戏时间（分钟）
        
        # 获取游戏详细信息
        game_details = await get_game_details(session, app_id)
        
        # 格式化游戏时间
        recent_hours = round(playtime_2weeks / 60, 1)
        total_hours = round(playtime_forever / 60, 1)
        
        # 游戏图标和链接
        game_icon = game_details.get('header_image', '')
        store_url = f"https://store.steampowered.com/app/{app_id}/"
        
        # 游戏类型/标签
        genres = game_details.get('genres', [])
        genre_names = [genre.get('description', '') for genre in genres[:3]]
        
        # 格式化单个游戏
        game_md = f"""
<div align="left">
  <h4>
    <a href="{store_url}" target="_blank">
      🎮 {name}
    </a>
  </h4>
  <p>
    <img src="https://img.shields.io/badge/最近2周-{recent_hours}小时-blue?style=flat-square" alt="recent">
    <img src="https://img.shields.io/badge/总时长-{total_hours}小时-green?style=flat-square" alt="total">
  </p>
  {f'<p>类型: {" | ".join(genre_names)}</p>' if genre_names else ''}
</div>

---
"""
        markdown_lines.append(game_md.strip())
    
    return '\n\n'.join(markdown_lines)

async def get_game_details(session: aiohttp.ClientSession, app_id: int) -> Dict:
    """获取游戏详细信息"""
    
    url = "https://store.steampowered.com/api/appdetails"
    params = {
        'appids': app_id,
        'cc': 'cn',  # 中国区
        'l': 'schinese'  # 简体中文
    }
    
    try:
        async with session.get(url, params=params, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                app_data = data.get(str(app_id), {})
                if app_data.get('success') and 'data' in app_data:
                    return app_data['data']
    except Exception:
        pass
    
    return {}

async def get_user_profile(api_key: str, steam_id: str) -> Dict:
    """获取Steam用户资料"""
    
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {
        'key': api_key,
        'steamids': steam_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'response' in data and 'players' in data['response']:
                        players = data['response']['players']
                        if players:
                            return players[0]
    except Exception:
        pass
    
    return {}

async def get_game_achievements(api_key: str, steam_id: str, app_id: int) -> Dict:
    """获取游戏成就信息"""
    
    url = "https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'appid': app_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('playerstats', {})
    except Exception:
        pass
    
    return {}

def convert_steam_id_format(steam_id: str) -> str:
    """
    转换Steam ID格式
    支持多种格式的Steam ID输入
    """
    
    # 如果已经是64位ID，直接返回
    if steam_id.isdigit() and len(steam_id) == 17:
        return steam_id
    
    # 如果是自定义URL格式，需要通过API解析
    # 这里简化处理，实际使用时可能需要额外的API调用
    return steam_id

async def test_steam_connection(api_key: str, steam_id: str) -> bool:
    """测试Steam API连接是否正常"""
    
    try:
        profile = await get_user_profile(api_key, steam_id)
        return bool(profile)
    except Exception:
        return False 
