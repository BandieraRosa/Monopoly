from pydantic import BaseModel
from typing import Dict, List

class Player(BaseModel):
    """玩家模型"""
    id: str
    name: str
    money: int = 15000  # 默认起始资金15000
    position: int = 0   # 默认位置在起点
    properties: List[int] = []  # 拥有的地产列表

class GameState(BaseModel):
    """游戏状态模型"""
    room_id: str
    players: Dict[str, Player]  # 玩家ID到玩家对象的映射
    current_turn_player_id: str  # 当前回合的玩家ID
    game_phase: str  # 游戏阶段
    game_log: List[str] = []  # 游戏日志