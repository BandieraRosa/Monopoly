import random
from models import Player, GameState
from typing import Dict, List

# 游戏地图常量 - 16个地块的4x4布局
GAME_MAP = [
    {"id": 0, "name": "起点", "type": "start", "price": 0},
    {"id": 1, "name": "中山路", "type": "property", "price": 1000},
    {"id": 2, "name": "建设路", "type": "property", "price": 1200},
    {"id": 3, "name": "机会", "type": "chance", "price": 0},
    {"id": 4, "name": "解放路", "type": "property", "price": 1500},
    {"id": 5, "name": "人民路", "type": "property", "price": 1800},
    {"id": 6, "name": "监狱", "type": "jail", "price": 0},
    {"id": 7, "name": "和平路", "type": "property", "price": 2000},
    {"id": 8, "name": "胜利路", "type": "property", "price": 2200},
    {"id": 9, "name": "命运", "type": "destiny", "price": 0},
    {"id": 10, "name": "光明路", "type": "property", "price": 2500},
    {"id": 11, "name": "幸福路", "type": "property", "price": 2800},
    {"id": 12, "name": "停车场", "type": "parking", "price": 0},
    {"id": 13, "name": "繁华街", "type": "property", "price": 3000},
    {"id": 14, "name": "商业区", "type": "property", "price": 3500},
    {"id": 15, "name": "税收", "type": "tax", "price": 0}
]

class GameManager:
    """游戏管理器类"""
    
    def __init__(self, room_id: str):
        """初始化游戏管理器"""
        self.game_state = GameState(
            room_id=room_id,
            players={},
            current_turn_player_id="",
            game_phase="waiting",
            game_log=[]
        )
    
    def add_player(self, player_id: str, player_name: str) -> bool:
        """添加玩家到游戏"""
        if player_id in self.game_state.players:
            self.game_state.game_log.append(f"玩家 {player_name} 已经在游戏中")
            return False
        
        # 创建新玩家
        new_player = Player(id=player_id, name=player_name)
        self.game_state.players[player_id] = new_player
        
        # 如果是第一个玩家，设置为当前回合玩家
        if len(self.game_state.players) == 1:
            self.game_state.current_turn_player_id = player_id
            self.game_state.game_phase = "playing"
        
        self.game_state.game_log.append(f"玩家 {player_name} 加入了游戏")
        return True
    
    def roll_dice_and_move(self, player_id: str) -> Dict:
        """掷骰子并移动玩家"""
        if player_id != self.game_state.current_turn_player_id:
            return {"success": False, "message": "不是你的回合"}
        
        if player_id not in self.game_state.players:
            return {"success": False, "message": "玩家不存在"}
        
        # 掷骰子（1-6）
        dice_roll = random.randint(1, 6)
        player = self.game_state.players[player_id]
        old_position = player.position
        
        # 移动玩家
        player.position = (player.position + dice_roll) % 16
        
        # 检查是否经过起点
        if player.position < old_position:
            player.money += 2000  # 经过起点获得2000元
            self.game_state.game_log.append(f"{player.name} 经过起点，获得2000元")
        
        current_tile = GAME_MAP[player.position]
        self.game_state.game_log.append(
            f"{player.name} 掷出了 {dice_roll} 点，移动到 {current_tile['name']}"
        )
        
        return {
            "success": True, 
            "dice_roll": dice_roll, 
            "new_position": player.position,
            "tile": current_tile
        }
    
    def buy_property(self, player_id: str) -> Dict:
        """购买地产"""
        if player_id != self.game_state.current_turn_player_id:
            return {"success": False, "message": "不是你的回合"}
        
        if player_id not in self.game_state.players:
            return {"success": False, "message": "玩家不存在"}
        
        player = self.game_state.players[player_id]
        current_tile = GAME_MAP[player.position]
        
        # 检查是否为可购买的地产
        if current_tile["type"] != "property":
            return {"success": False, "message": "当前位置不是可购买的地产"}
        
        # 检查地产是否已被购买
        for other_player in self.game_state.players.values():
            if player.position in other_player.properties:
                return {"success": False, "message": "该地产已被其他玩家拥有"}
        
        # 检查玩家资金是否足够
        if player.money < current_tile["price"]:
            return {"success": False, "message": "资金不足"}
        
        # 购买地产
        player.money -= current_tile["price"]
        player.properties.append(player.position)
        
        self.game_state.game_log.append(
            f"{player.name} 花费 {current_tile['price']} 元购买了 {current_tile['name']}"
        )
        
        return {"success": True, "message": f"成功购买 {current_tile['name']}"}
    
    def end_turn(self) -> bool:
        """结束当前玩家回合"""
        if not self.game_state.players:
            return False
        
        # 获取所有玩家ID列表
        player_ids = list(self.game_state.players.keys())
        current_index = player_ids.index(self.game_state.current_turn_player_id)
        
        # 切换到下一个玩家
        next_index = (current_index + 1) % len(player_ids)
        self.game_state.current_turn_player_id = player_ids[next_index]
        
        current_player_name = self.game_state.players[self.game_state.current_turn_player_id].name
        self.game_state.game_log.append(f"轮到 {current_player_name} 的回合")
        
        return True
    
    def get_game_state(self) -> GameState:
        """获取当前游戏状态"""
        return self.game_state