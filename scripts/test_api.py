#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API端点
"""

import requests
import time

def test_api():
    """测试API端点"""
    print("=== 测试API端点 ===")
    
    # 测试健康检查
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check失败: {e}")
    
    # 测试球队列表
    try:
        response = requests.get('http://localhost:5000/api/teams', timeout=5)
        data = response.json()
        print(f"Teams API: {response.status_code} - {len(data.get('data', []))} 个球队")
        if data.get('data'):
            print(f"前5个球队: {data['data'][:5]}")
    except Exception as e:
        print(f"Teams API失败: {e}")
    
    # 测试比赛数据
    try:
        response = requests.get('http://localhost:5000/api/matches', timeout=5)
        data = response.json()
        print(f"Matches API: {response.status_code} - {data.get('total', 0)} 场比赛")
    except Exception as e:
        print(f"Matches API失败: {e}")

if __name__ == "__main__":
    test_api()