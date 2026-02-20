#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理统一入口脚本
整合所有数据处理功能，生成标准化数据文件
"""

import os
import sys
import pandas as pd
import json
from pathlib import Path

def process_json_files(data_dirs, output_dir):
    """
    处理JSON数据文件，生成标准化比赛数据
    
    Args:
        data_dirs: 数据目录列表
        output_dir: 输出目录
    """
    print("=== 开始处理JSON数据文件 ===")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    all_matches = []
    
    # 遍历所有数据目录
    for data_dir in data_dirs:
        if not os.path.exists(data_dir):
            print(f"警告: 目录 {data_dir} 不存在，跳过")
            continue
            
        # 获取所有JSON文件
        json_files = list(Path(data_dir).glob("*.json"))
        print(f"找到 {len(json_files)} 个JSON文件在 {data_dir}")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 处理每场比赛
                for match in data:
                    # 提取基本字段
                    match_dict = {
                        'match_id': match.get('比赛id', ''),
                        'league': match.get('联赛名', ''),
                        'date': match.get('日期', ''),
                        'home_team': match.get('主队', ''),
                        'away_team': match.get('客队', ''),
                        'home_goals': int(match.get('比分', '0-0').split('-')[0]) if '-' in match.get('比分', '0-0') else 0,
                        'away_goals': int(match.get('比分', '0-0').split('-')[1]) if '-' in match.get('比分', '0-0') else 0,
                    }
                    
                    # 处理包含"/"的字段
                    fields_to_process = ['射门', '射正', '控球率', '传球成功率', '犯规', '黄牌', '角球', '半场角球', '红牌']
                    for field in fields_to_process:
                        value = match.get(field, '0/0')
                        if '/' in value:
                            parts = value.split('/')
                            home_val = parts[0].strip() if parts[0].strip() != '-' else '0'
                            away_val = parts[1].strip() if parts[1].strip() != '-' else '0'
                            
                            # 处理百分比字符串
                            if '%' in home_val:
                                home_val = home_val.replace('%', '')
                            if '%' in away_val:
                                away_val = away_val.replace('%', '')
                            
                            # 安全转换为数值
                            try:
                                match_dict[f'home_{field.lower()}'] = int(float(home_val))
                                match_dict[f'away_{field.lower()}'] = int(float(away_val))
                            except ValueError:
                                match_dict[f'home_{field.lower()}'] = 0
                                match_dict[f'away_{field.lower()}'] = 0
                        else:
                            match_dict[f'home_{field.lower()}'] = int(value) if value.isdigit() else 0
                            match_dict[f'away_{field.lower()}'] = 0
                    
                    all_matches.append(match_dict)
                    
            except Exception as e:
                print(f"处理文件 {json_file} 时出错: {e}")
    
    # 转换为DataFrame
    df = pd.DataFrame(all_matches)
    
    # 保存到CSV
    output_file = os.path.join(output_dir, 'matches.csv')
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"✅ 成功处理 {len(all_matches)} 场比赛数据")
    print(f"📊 数据已保存到: {output_file}")
    
    return df

def main():
    """主函数"""
    # 设置路径 (修正：使用项目根目录)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dirs = [
        os.path.join(project_root, 'data', 'raw', '2021'),
        os.path.join(project_root, 'data', 'raw', '2023')
    ]
    output_dir = os.path.join(project_root, 'data', 'processed')
    
    # 处理数据
    df = process_json_files(data_dirs, output_dir)
    
    # 显示统计信息
    print("\n=== 数据统计 ===")
    print(f"总比赛数: {len(df)}")
    if len(df) > 0:
        print(f"联赛分布: {df['league'].value_counts().to_dict()}")
        print(f"时间范围: {df['date'].min()} 到 {df['date'].max()}")
    
    return df

if __name__ == "__main__":
    main()