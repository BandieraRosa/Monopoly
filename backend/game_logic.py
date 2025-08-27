import random
from models import Player, GameState
from typing import Dict, List

# 游戏地图常量 - 16个地块的4x4布局
GAME_MAP = [
    {"id": 0, "name": "起点", "type": "start", "price": 0},
    {"id": 1, "name": "中山路", "type": "property", "price": 1000, "rent": 100},
    {"id": 2, "name": "建设路", "type": "property", "price": 1200, "rent": 120},
    {"id": 3, "name": "机会", "type": "chance", "price": 0},
    {"id": 4, "name": "解放路", "type": "property", "price": 1500, "rent": 150},
    {"id": 5, "name": "人民路", "type": "property", "price": 1800, "rent": 180},
    {"id": 6, "name": "监狱", "type": "jail", "price": 0},
    {"id": 7, "name": "和平路", "type": "property", "price": 2000, "rent": 200},
    {"id": 8, "name": "胜利路", "type": "property", "price": 2200, "rent": 220},
    {"id": 9, "name": "命运", "type": "destiny", "price": 0},
    {"id": 10, "name": "光明路", "type": "property", "price": 2500, "rent": 250},
    {"id": 11, "name": "幸福路", "type": "property", "price": 2800, "rent": 280},
    {"id": 12, "name": "停车场", "type": "parking", "price": 0},
    {"id": 13, "name": "繁华街", "type": "property", "price": 3000, "rent": 300},
    {"id": 14, "name": "商业区", "type": "property", "price": 3500, "rent": 350},
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
        """掷骰子并移动玩家，自动处理所有地块事件"""
        if player_id != self.game_state.current_turn_player_id:
            return {"success": False, "message": "不是你的回合"}
        
        if player_id not in self.game_state.players:
            return {"success": False, "message": "玩家不存在"}
        
        if self.game_state.has_rolled_dice:
            return {"success": False, "message": "本回合已经掷过骰子了"}
        
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
        
        # 标记已掷骰子
        self.game_state.has_rolled_dice = True
        
        # 自动处理落地事件（如付租金）
        self._handle_landing(player_id)
        
        # 检查是否可以购买地产
        self._check_can_buy_property(player_id)
        
        # 检查回合是否完成
        self._check_turn_completion()
        
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
        
        if not self.game_state.can_buy_property:
            return {"success": False, "message": "当前无法购买地产"}
        
        if player_id not in self.game_state.players:
            return {"success": False, "message": "玩家不存在"}
        
        player = self.game_state.players[player_id]
        current_tile = GAME_MAP[player.position]
        
        # 检查玩家资金是否足够
        if player.money < current_tile["price"]:
            return {"success": False, "message": "资金不足"}
        
        # 购买地产
        player.money -= current_tile["price"]
        player.properties.append(player.position)
        
        # 购买后不能再购买
        self.game_state.can_buy_property = False
        
        self.game_state.game_log.append(
            f"{player.name} 购买了 {current_tile['name']}，花费 {current_tile['price']} 元"
        )
        
        # 检查回合是否完成
        self._check_turn_completion()
        
        return {
            "success": True,
            "message": f"成功购买 {current_tile['name']}",
            "property": current_tile
        }
    
    def end_turn(self) -> Dict:
        """结束当前玩家回合"""
        if not self.game_state.turn_completed:
            return {"success": False, "message": "回合尚未完成，无法结束回合"}
        
        player_ids = list(self.game_state.players.keys())
        if not player_ids:
            return {"success": False, "message": "没有玩家"}
        
        current_index = player_ids.index(self.game_state.current_turn_player_id)
        next_index = (current_index + 1) % len(player_ids)
        self.game_state.current_turn_player_id = player_ids[next_index]
        
        # 重置回合状态
        self.game_state.has_rolled_dice = False
        self.game_state.can_buy_property = False
        self.game_state.turn_completed = False
        
        current_player_name = self.game_state.players[self.game_state.current_turn_player_id].name
        self.game_state.game_log.append(f"轮到 {current_player_name} 的回合")
        
        return {"success": True, "message": "回合已结束"}
    
    def _handle_landing(self, player_id: str):
        """处理玩家落地事件（私有方法）"""
        if player_id not in self.game_state.players:
            return
        
        player = self.game_state.players[player_id]
        current_tile = GAME_MAP[player.position]
        
        # 只处理地产类型的地块
        if current_tile["type"] != "property":
            return
        
        # 查找地产所有者
        property_owner = None
        for other_player_id, other_player in self.game_state.players.items():
            if player.position in other_player.properties:
                property_owner = other_player
                break
        
        # 如果地产有所有者且不是当前玩家
        if property_owner and property_owner.id != player_id:
            rent = current_tile.get("rent", 0)
            
            if player.money >= rent:
                # 扣除租金
                player.money -= rent
                property_owner.money += rent
                
                self.game_state.game_log.append(
                    f"{player.name} 向 {property_owner.name} 支付了 {rent} 元租金（{current_tile['name']}）"
                )
            else:
                # 资金不足
                self.game_state.game_log.append(
                    f"{player.name} 资金不足，无法支付 {rent} 元租金给 {property_owner.name}（{current_tile['name']}）"
                )
    
    def remove_player(self, player_id: str):
        """删除玩家并清空其地产归属"""
        if player_id not in self.game_state.players:
            return
        
        player_name = self.game_state.players[player_id].name
        
        # 从玩家字典中删除该玩家
        del self.game_state.players[player_id]
        
        # 清空该玩家拥有的所有地产（从其他玩家的properties列表中移除）
        for remaining_player in self.game_state.players.values():
            remaining_player.properties = [prop for prop in remaining_player.properties if prop != player_id]
        
        # 如果当前轮到该玩家，切换到下一个玩家
        if self.game_state.current_turn_player_id == player_id:
            if self.game_state.players:
                player_ids = list(self.game_state.players.keys())
                self.game_state.current_turn_player_id = player_ids[0]
            else:
                self.game_state.current_turn_player_id = ""
                self.game_state.game_phase = "waiting"
        
        # 添加日志
        self.game_state.game_log.append(f"玩家 {player_name} 已离开游戏")
    
    def _check_can_buy_property(self, player_id: str):
        """检查是否可以购买地产（私有方法）"""
        if player_id not in self.game_state.players:
            return
        
        player = self.game_state.players[player_id]
        current_tile = GAME_MAP[player.position]
        
        # 只有地产类型的地块才能购买
        if current_tile["type"] != "property":
            self.game_state.can_buy_property = False
            return
        
        # 检查地产是否已被购买
        for other_player in self.game_state.players.values():
            if player.position in other_player.properties:
                self.game_state.can_buy_property = False
                return
        
        # 如果地产未被购买，则可以购买
        self.game_state.can_buy_property = True
    
    def _check_turn_completion(self):
        """检查回合是否完成（私有方法）"""
        # 如果已掷骰子且不能购买地产，则回合完成
        if self.game_state.has_rolled_dice and not self.game_state.can_buy_property:
            self.game_state.turn_completed = True
    
    def get_game_state(self) -> GameState:
        """获取当前游戏状态"""
        return self.game_state