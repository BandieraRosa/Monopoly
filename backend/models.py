from pydantic import BaseModel
from typing import Dict, List

class TileState(BaseModel):
    """地块状态模型"""
    owner_id: str = ""  # 地块所有者ID，空字符串表示无人拥有
    mortgaged: bool = False  # 是否被抵押
    level: int = 0  # 地产等级，0表示未升级

class Player(BaseModel):
    """玩家模型"""
    id: str
    name: str
    money: int = 15000  # 默认起始资金15000
    position: int = 0   # 默认位置在起点
    is_in_jail: bool = False  # 是否在监狱中
    turns_in_jail: int = 0  # 在监狱中的回合数

class GameState(BaseModel):
    """游戏状态模型"""
    room_id: str
    players: Dict[str, Player]  # 玩家ID到玩家对象的映射
    current_turn_player_id: str  # 当前回合的玩家ID
    game_phase: str  # 游戏阶段
    game_log: List[str] = []  # 游戏日志
    has_rolled_dice: bool = False  # 当前玩家是否已掷骰子
    can_buy_property: bool = False  # 当前玩家是否可以购买地产
    turn_completed: bool = False  # 当前回合是否已完成所有操作
    player_in_debt_id: str = ""  # 当前处于负资产状态需要变卖资产的玩家ID
    tile_states: Dict[str, TileState] = {}  # 地块状态字典，键为地块ID字符串