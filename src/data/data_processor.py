#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理模块
负责解析原始JSON数据，转换为结构化的比赛数据
"""

import json
import os
import re
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd

from ..models.data_models import RawMatchData, MatchData


class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        """初始化数据处理器"""
        pass
    
    def parse_percentage(self, percentage_str: str) -> tuple:
        """
        解析百分比字符串 "33%/67%" -> (33.0, 67.0)
        
        Args:
            percentage_str: 百分比字符串
            
        Returns:
            tuple: (主队百分比, 客队百分比)
        """
        if not percentage_str or percentage_str == "":
            return (0.0, 0.0)
            
        # 使用正则表达式匹配百分比
        matches = re.findall(r'(\d+(?:\.\d+)?)%', percentage_str)
        if len(matches) >= 2:
            return (float(matches[0]), float(matches[1]))
        elif len(matches) == 1:
            # 如果只有一个值，假设另一个是补数
            val1 = float(matches[0])
            val2 = 100.0 - val1
            return (val1, val2)
        else:
            return (0.0, 0.0)
    
    def parse_divided_values(self, divided_str: str) -> tuple:
        """
        解析分割值字符串 "7/5" -> (7, 5)
        
        Args:
            divided_str: 分割值字符串
            
        Returns:
            tuple: (主队值, 客队值)
        """
        if not divided_str or divided_str == "":
            return (0, 0)
            
        # 处理可能包含小数的情况
        matches = re.findall(r'(\d+(?:\.\d+)?)', divided_str)
        if len(matches) >= 2:
            return (int(float(matches[0])), int(float(matches[1])))
        elif len(matches) == 1:
            return (int(float(matches[0])), 0)
        else:
            return (0, 0)
    
    def parse_score(self, score_str: str) -> tuple:
        """
        解析比分字符串 "2-0" -> (2, 0)
        
        Args:
            score_str: 比分字符串
            
        Returns:
            tuple: (主队进球, 客队进球)
        """
        if not score_str or score_str == "":
            return (0, 0)
            
        # 移除"比分:"前缀
        clean_score = score_str.replace("比分:", "")
        matches = re.findall(r'(\d+)', clean_score)
        if len(matches) >= 2:
            return (int(matches[0]), int(matches[1]))
        elif len(matches) == 1:
            return (int(matches[0]), 0)
        else:
            return (0, 0)
    
    def convert_raw_to_structured(self, raw_data: RawMatchData) -> MatchData:
        """
        将原始数据转换为结构化比赛数据
        
        Args:
            raw_data: 原始比赛数据
            
        Returns:
            MatchData: 结构化比赛数据
        """
        # 解析各项数据
        home_goals, away_goals = self.parse_score(raw_data.full_time_score)
        home_shots, away_shots = self.parse_divided_values(raw_data.shots)
        home_shots_on_target, away_shots_on_target = self.parse_divided_values(raw_data.shots_on_target)
        home_possession, away_possession = self.parse_percentage(raw_data.possession)
        home_pass_success, away_pass_success = self.parse_percentage(raw_data.pass_success)
        home_fouls, away_fouls = self.parse_divided_values(raw_data.fouls)
        home_yellow_cards, away_yellow_cards = self.parse_divided_values(raw_data.yellow_cards)
        home_corners, away_corners = self.parse_divided_values(raw_data.corners)
        home_red_cards, away_red_cards = self.parse_divided_values(raw_data.red_cards)
        
        # 创建结构化数据对象
        structured_data = MatchData(
            match_id=raw_data.match_id,
            league=raw_data.league_name,
            date=raw_data.date,
            home_team=raw_data.home_team,
            away_team=raw_data.away_team,
            home_goals=home_goals,
            away_goals=away_goals,
            home_shots=home_shots,
            away_shots=away_shots,
            home_shots_on_target=home_shots_on_target,
            away_shots_on_target=away_shots_on_target,
            home_possession=home_possession,
            away_possession=away_possession,
            home_pass_success=home_pass_success,
            away_pass_success=away_pass_success,
            home_fouls=home_fouls,
            away_fouls=away_fouls,
            home_yellow_cards=home_yellow_cards,
            away_yellow_cards=away_yellow_cards,
            home_corners=home_corners,
            away_corners=away_corners,
            home_red_cards=home_red_cards,
            away_red_cards=away_red_cards
        )
        
        return structured_data
    
    def load_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载JSON文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            List[Dict]: JSON数据列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data if isinstance(data, list) else [data]
        except UnicodeDecodeError:
            # 尝试GBK编码
            try:
                with open(file_path, 'r', encoding='gbk') as file:
                    data = json.load(file)
                    return data if isinstance(data, list) else [data]
            except Exception as e:
                print(f"无法解析文件 {file_path}: {e}")
                return []
        except Exception as e:
            print(f"加载文件失败 {file_path}: {e}")
            return []
    
    def process_single_match(self, match_dict: Dict[str, Any]) -> RawMatchData:
        """
        处理单场比赛的原始字典数据
        
        Args:
            match_dict: 比赛字典数据
            
        Returns:
            RawMatchData: 原始比赛数据对象
        """
        return RawMatchData(
            match_id=str(match_dict.get("比赛id", "")),
            league_name=match_dict.get("联赛名", ""),
            date=match_dict.get("日期", ""),
            home_team=match_dict.get("主队", ""),
            away_team=match_dict.get("客队", ""),
            half_time_score=match_dict.get("半场", ""),
            full_time_score=match_dict.get("赛果", match_dict.get("比分", "")),
            shots=match_dict.get("射门", "0/0"),
            shots_on_target=match_dict.get("射正", "0/0"),
            possession=match_dict.get("控球率", "0%/0%"),
            pass_success=match_dict.get("传球成功率", "0%/0%"),
            fouls=match_dict.get("犯规", "0/0"),
            yellow_cards=match_dict.get("黄牌", "0/0"),
            corners=match_dict.get("角球", "0/0"),
            half_corners=match_dict.get("半场角球", "0/0"),
            red_cards=match_dict.get("红牌", "0/0"),
            shots_on_woodwork=match_dict.get("射中门框", "0/0")
        )
    
    def process_directory(self, directory_path: str) -> List[MatchData]:
        """
        处理整个目录的JSON文件
        
        Args:
            directory_path: 目录路径
            
        Returns:
            List[MatchData]: 处理后的结构化比赛数据列表
        """
        structured_matches = []
        
        # 获取目录下所有JSON文件
        json_files = list(Path(directory_path).glob("*.json"))
        
        for json_file in json_files:
            print(f"处理文件: {json_file}")
            raw_data_list = self.load_json_file(str(json_file))
            
            for raw_dict in raw_data_list:
                if raw_dict:  # 确保数据不为空
                    raw_match = self.process_single_match(raw_dict)
                    structured_match = self.convert_raw_to_structured(raw_match)
                    structured_matches.append(structured_match)
        
        print(f"总共处理了 {len(structured_matches)} 场比赛数据")
        return structured_matches
    
    def save_to_csv(self, matches: List[MatchData], output_path: str):
        """
        将结构化数据保存为CSV文件
        
        Args:
            matches: 比赛数据列表
            output_path: 输出文件路径
        """
        if not matches:
            print("没有数据可保存")
            return
            
        # 转换为字典列表
        data_dicts = [match.to_dict() for match in matches]
        
        # 创建DataFrame并保存
        df = pd.DataFrame(data_dicts)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"数据已保存到: {output_path}")


# 便捷函数
def process_football_data(input_dirs: List[str], output_file: str = "processed_football_data.csv"):
    """
    便捷函数：处理多个目录的足球数据
    
    Args:
        input_dirs: 输入目录列表
        output_file: 输出文件名
    """
    processor = DataProcessor()
    all_matches = []
    
    for directory in input_dirs:
        if os.path.exists(directory):
            matches = processor.process_directory(directory)
            all_matches.extend(matches)
        else:
            print(f"目录不存在: {directory}")
    
    if all_matches:
        processor.save_to_csv(all_matches, output_file)
        return all_matches
    else:
        print("没有找到任何比赛数据")
        return []