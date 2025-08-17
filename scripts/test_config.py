#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
from github_api import get_user_info, test_github_connection
from wordpress_api import test_wordpress_connection

async def test_all_configurations():
    """测试所有API配置是否正确"""
    
    print("🔍 测试GitHub个人介绍页面配置...")
    print("=" * 50)
    
    # 测试GitHub配置
    print("\n📊 测试GitHub配置...")
    github_username = os.getenv('GH_USERNAME', input("请输入GitHub用户名: "))
    github_token = os.getenv('GH_TOKEN', input("请输入GitHub Token: "))
    
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
    
    print("\n" + "=" * 50)
    print("✅ 配置测试完成！")
    print("\n💡 提示:")
    print("- 确保在GitHub Secrets中正确设置所有API密钥")
    print("- GitHub配置是必需的，WordPress配置是可选的")
    print("- 运行主脚本前请确保所有配置都正确")

if __name__ == "__main__":
    asyncio.run(test_all_configurations()) 
