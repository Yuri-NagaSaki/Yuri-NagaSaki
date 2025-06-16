#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional

async def get_recent_games(api_key: str, steam_id: str, limit: int = 3) -> str:
    """
    获取Steam用户最近玩的游戏
    
    Args:
        api_key: Steam API密钥
        steam_id: Steam用户ID (64位)
        limit: 返回游戏数量限制，默认3个
    
    Returns:
        格式化的markdown字符串
    """
    
    if not api_key or not steam_id:
        return '<div align="center" style="color: #8b949e; padding: 20px;">请在GitHub Secrets中设置STEAM_API_KEY和STEAM_USER_ID</div>'
    
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
                        return await format_steam_games(games, session, api_key, steam_id)
                    else:
                        return '<div align="center" style="color: #8b949e; padding: 20px;">暂无最近游戏记录</div>'
                elif response.status == 401:
                    return '<div align="center" style="color: #f85149; padding: 20px;">Steam API密钥无效</div>'
                elif response.status == 403:
                    return '<div align="center" style="color: #f85149; padding: 20px;">Steam用户资料为私人状态或API密钥权限不足</div>'
                else:
                    return f'<div align="center" style="color: #f85149; padding: 20px;">Steam API 错误: {response.status}</div>'
                    
    except asyncio.TimeoutError:
        return '<div align="center" style="color: #f85149; padding: 20px;">Steam API 请求超时</div>'
    except Exception as e:
        return f'<div align="center" style="color: #f85149; padding: 20px;">获取 Steam 游戏时发生错误: {str(e)}</div>'

async def format_steam_games(games: List[Dict], session: aiohttp.ClientSession, api_key: str, steam_id: str) -> str:
    """格式化Steam游戏为现代卡片样式（参考用户截图）"""
    
    if not games:
        return '<div align="center" style="color: #8b949e; padding: 20px;">暂无最近游戏记录</div>'
    
    game_cards = []
    
    # 获取游戏详细信息
    for game in games:
        app_id = game['appid']
        name = game['name']
        playtime_forever = game.get('playtime_forever', 0)  # 总游戏时间（分钟）
        
        # 获取游戏详细信息
        game_details = await get_game_details(session, app_id)
        
        # 获取成就信息
        achievements_data = await get_game_achievements(api_key, steam_id, app_id)
        
        # 格式化游戏时间
        total_hours = round(playtime_forever / 60, 1)
        
        # 游戏图标和链接
        header_image = game_details.get('header_image', '')
        store_url = f"https://store.steampowered.com/app/{app_id}/"
        
        # 获取最后运行时间（从最近游戏API获取）
        last_played_timestamp = game.get('rtime_last_played', 0)
        if last_played_timestamp:
            last_played = datetime.fromtimestamp(last_played_timestamp).strftime('%m月%d日')
        else:
            last_played = "未知"
        
        # 处理成就信息
        achievement_display = ""
        if achievements_data and 'achievements' in achievements_data:
            achievements = achievements_data['achievements']
            total_achievements = len(achievements)
            unlocked_achievements = sum(1 for ach in achievements if ach.get('achieved', 0) == 1)
            
            if total_achievements > 0:
                progress_percent = (unlocked_achievements / total_achievements) * 100
                achievement_display = f"""
    <div style="margin: 8px 0;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <span style="color: #a5a5a5; font-size: 12px;">成就进度</span>
        <span style="color: #ffffff; font-size: 12px; font-weight: bold;">{unlocked_achievements} / {total_achievements}</span>
        <div style="flex: 1; height: 8px; background: #3a3a3a; border-radius: 4px; overflow: hidden;">
          <div style="height: 100%; width: {progress_percent}%; background: linear-gradient(90deg, #4a90e2, #7b68ee); border-radius: 4px;"></div>
        </div>
      </div>
    </div>"""
        
        # 现代卡片格式（参考截图样式）
        card = f"""
<div align="center" style="max-width: 800px; margin: 8px auto; background: linear-gradient(135deg, #2d1b69 0%, #11101d 100%); border-radius: 12px; padding: 16px; border: 1px solid #3a3a4a;">
  <div style="display: flex; align-items: center; gap: 16px;">
    <div style="flex-shrink: 0;">
      {f'<img src="{header_image}" alt="{name}" style="width: 120px; height: 90px; border-radius: 8px; object-fit: cover;"/>' if header_image else '<div style="width: 120px; height: 90px; background: #3a3a3a; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #8b949e;">🎮</div>'}
    </div>
    <div style="flex: 1; text-align: left;">
      <h3 style="margin: 0 0 8px 0; color: #ffffff; font-size: 18px; font-weight: bold;">
        <a href="{store_url}" target="_blank" style="color: #ffffff; text-decoration: none;">
          {name}
        </a>
      </h3>
      {achievement_display}
    </div>
    <div style="flex-shrink: 0; text-align: right;">
      <div style="color: #a5a5a5; font-size: 12px; margin-bottom: 4px;">总时数</div>
      <div style="color: #ffffff; font-size: 18px; font-weight: bold; margin-bottom: 8px;">{total_hours} 小时</div>
      <div style="color: #a5a5a5; font-size: 12px;">最后运行日期: {last_played}</div>
    </div>
  </div>
</div>"""
        game_cards.append(card)
    
    return '\n\n'.join(game_cards)

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
