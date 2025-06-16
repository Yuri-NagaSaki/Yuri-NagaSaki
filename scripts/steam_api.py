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
    """格式化Steam游戏为现代卡片样式"""
    
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
        achievement_info = ""
        achievement_progress = ""
        if achievements_data and 'achievements' in achievements_data:
            achievements = achievements_data['achievements']
            total_achievements = len(achievements)
            unlocked_achievements = sum(1 for ach in achievements if ach.get('achieved', 0) == 1)
            
            if total_achievements > 0:
                progress_percent = round((unlocked_achievements / total_achievements) * 100, 1)
                achievement_info = f"🏆 成就: {unlocked_achievements}/{total_achievements} ({progress_percent}%)"
                # 创建进度条
                progress_width = int(progress_percent * 2)  # 进度条宽度（最大200px）
                achievement_progress = f'<div style="background: #21262d; border-radius: 6px; padding: 2px; margin-top: 6px;"><div style="background: linear-gradient(90deg, #ffd700, #ffed4e); height: 6px; border-radius: 3px; width: {progress_width}px; max-width: 200px;"></div></div>'
        
        # 获取游戏描述
        game_description = game_details.get('short_description', '')
        if len(game_description) > 80:
            game_description = game_description[:80] + '...'
        
        # 现代卡片样式
        card = f'''
<div align="center" style="max-width: 700px; margin: 8px auto; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 12px; padding: 18px; border: 1px solid #30363d; box-shadow: 0 4px 12px rgba(0,0,0,0.4); transition: transform 0.2s ease;">
  <div style="display: flex; align-items: center; gap: 18px;">
    <div style="flex-shrink: 0; position: relative;">
      {f'<img src="{header_image}" width="120" height="90" alt="{name}" style="border-radius: 10px; border: 2px solid #30363d; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"/>' if header_image else '<div style="width: 120px; height: 90px; background: linear-gradient(135deg, #21262d, #30363d); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 28px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">🎮</div>'}
      <div style="position: absolute; top: -8px; right: -8px; background: #ffd700; color: #000; font-size: 16px; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">🎮</div>
    </div>
    <div style="flex: 1; text-align: left; min-width: 0;">
      <div style="margin-bottom: 8px;">
        <a href="{store_url}" target="_blank" style="color: #58a6ff; text-decoration: none; font-weight: 700; font-size: 19px; line-height: 1.2; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
          {name}
        </a>
      </div>
      {f'<div style="color: #8b949e; font-size: 13px; margin-bottom: 10px; line-height: 1.5; opacity: 0.9;">{game_description}</div>' if game_description else ''}
      {f'<div style="color: #ffd700; font-size: 14px; margin-bottom: 8px; font-weight: 600; display: flex; align-items: center; gap: 6px;"><span style="font-size: 16px;">🏆</span>{achievement_info[2:]}</div>' if achievement_info else ''}
      {achievement_progress}
    </div>
    <div style="text-align: right; flex-shrink: 0; background: rgba(88, 166, 255, 0.1); padding: 12px; border-radius: 8px; border: 1px solid rgba(88, 166, 255, 0.2);">
      <div style="color: #58a6ff; font-size: 24px; font-weight: 800; line-height: 1; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">{total_hours}</div>
      <div style="color: #8b949e; font-size: 11px; margin-top: 2px; font-weight: 500; letter-spacing: 0.5px;">小时</div>
      <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(88, 166, 255, 0.2);">
        <div style="color: #8b949e; font-size: 10px; opacity: 0.8; margin-bottom: 2px;">最后运行</div>
        <div style="color: #f0f6fc; font-size: 12px; font-weight: 500;">{last_played}</div>
      </div>
    </div>
  </div>
</div>'''
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
        async with session.get(url, params=params, timeout=8) as response:
            if response.status == 200:
                data = await response.json()
                app_data = data.get(str(app_id), {})
                if app_data.get('success') and 'data' in app_data:
                    game_data = app_data['data']
                    # 确保有 header_image，如果没有则构建默认的
                    if 'header_image' not in game_data or not game_data['header_image']:
                        game_data['header_image'] = f"https://cdn.akamai.steamstatic.com/steam/apps/{app_id}/header.jpg"
                    return game_data
    except Exception as e:
        # 如果API失败，至少返回基本的图片URL
        return {
            'header_image': f"https://cdn.akamai.steamstatic.com/steam/apps/{app_id}/header.jpg",
            'short_description': ''
        }
    
    return {
        'header_image': f"https://cdn.akamai.steamstatic.com/steam/apps/{app_id}/header.jpg",
        'short_description': ''
    }

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
