#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
from github_api import get_user_info, test_github_connection
from wordpress_api import test_wordpress_connection
from steam_api import test_steam_connection, get_user_profile

async def test_all_configurations():
    """测试所有API配置是否正确"""
    
    print("🔍 测试GitHub个人介绍页面配置...")
    print("=" * 50)
    
    # 测试GitHub配置
    print("\n📊 测试GitHub配置...")
    github_username = os.getenv('GITHUB_USERNAME', input("请输入GitHub用户名: "))
    github_token = os.getenv('GITHUB_TOKEN', input("请输入GitHub Token: "))
    
    if github_username and github_token:
        try:
            user_info = await get_user_info(github_username, github_token)
            if user_info:
                print(f"✅ GitHub连接成功！")
                print(f"   用户: {user_info.get('name', 'N/A')} (@{user_info.get('login', 'N/A')})")
                print(f"   公开仓库: {user_info.get('public_repos', 'N/A')}")
                print(f"   关注者: {user_info.get('followers', 'N/A')}")
            else:
                print("❌ GitHub连接失败！请检查用户名和Token")
        except Exception as e:
            print(f"❌ GitHub连接出错: {e}")
    else:
        print("⚠️ GitHub配置缺失")
    
    # 测试WordPress配置
    print("\n📝 测试WordPress配置...")
    wordpress_url = os.getenv('WORDPRESS_URL', input("请输入WordPress URL (可选，直接回车跳过): "))
    
    if wordpress_url:
        try:
            is_connected = await test_wordpress_connection(wordpress_url)
            if is_connected:
                print(f"✅ WordPress连接成功！")
                print(f"   站点: {wordpress_url}")
            else:
                print("❌ WordPress连接失败！请检查URL和REST API设置")
        except Exception as e:
            print(f"❌ WordPress连接出错: {e}")
    else:
        print("⚠️ WordPress配置跳过")
    
    # 测试Steam配置
    print("\n🎮 测试Steam配置...")
    steam_api_key = os.getenv('STEAM_API_KEY', input("请输入Steam API Key (可选，直接回车跳过): "))
    steam_user_id = os.getenv('STEAM_USER_ID', input("请输入Steam User ID (可选，直接回车跳过): "))
    
    if steam_api_key and steam_user_id:
        try:
            is_connected = await test_steam_connection(steam_api_key, steam_user_id)
            if is_connected:
                profile = await get_user_profile(steam_api_key, steam_user_id)
                print(f"✅ Steam连接成功！")
                print(f"   用户: {profile.get('personaname', 'N/A')}")
                print(f"   状态: {get_online_status(profile.get('personastate', 0))}")
            else:
                print("❌ Steam连接失败！请检查API Key和User ID")
        except Exception as e:
            print(f"❌ Steam连接出错: {e}")
    else:
        print("⚠️ Steam配置跳过")
    
    print("\n" + "=" * 50)
    print("✅ 配置测试完成！")
    print("\n💡 提示:")
    print("- 确保在GitHub Secrets中正确设置所有API密钥")
    print("- GitHub配置是必需的，其他配置是可选的")
    print("- 运行主脚本前请确保所有配置都正确")

def get_online_status(state):
    """获取Steam在线状态描述"""
    states = {
        0: "离线",
        1: "在线",
        2: "忙碌", 
        3: "离开",
        4: "打盹",
        5: "想要交易",
        6: "想要游戏"
    }
    return states.get(state, "未知")

if __name__ == "__main__":
    asyncio.run(test_all_configurations()) 
