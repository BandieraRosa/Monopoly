import random
from models import Player, GameState, TileState
from typing import Dict, List

# 游戏地图常量 - 16个地块的4x4布局
GAME_MAP = [
    {"id": 0, "name": "起点", "type": "start", "price": 0},
    {"id": 1, "name": "中山路", "type": "property", "price": 1000, "rent": [100, 300, 700], "mortgage_value": 500, "upgrade_cost": 500},
    {"id": 2, "name": "建设路", "type": "property", "price": 1200, "rent": [120, 360, 840], "mortgage_value": 600, "upgrade_cost": 600},
    {"id": 3, "name": "机会", "type": "chance"},
    {"id": 4, "name": "解放路", "type": "property", "price": 1500, "rent": [150, 450, 1050], "mortgage_value": 750, "upgrade_cost": 750},
    {"id": 5, "name": "人民路", "type": "property", "price": 1800, "rent": [180, 540, 1260], "mortgage_value": 900, "upgrade_cost": 900},
    {"id": 6, "name": "命运", "type": "fate"},
    {"id": 7, "name": "和平路", "type": "property", "price": 2000, "rent": [200, 600, 1400], "mortgage_value": 1000, "upgrade_cost": 1000},
    {"id": 8, "name": "胜利路", "type": "property", "price": 2200, "rent": [220, 660, 1540], "mortgage_value": 1100, "upgrade_cost": 1100},
    {"id": 9, "name": "监狱", "type": "jail"},
    {"id": 10, "name": "光明路", "type": "property", "price": 2500, "rent": [250, 750, 1750], "mortgage_value": 1250, "upgrade_cost": 1250},
    {"id": 11, "name": "幸福路", "type": "property", "price": 2800, "rent": [280, 840, 1960], "mortgage_value": 1400, "upgrade_cost": 1400},
    {"id": 12, "name": "免费停车", "type": "free_parking"},
    {"id": 13, "name": "繁华街", "type": "property", "price": 3000, "rent": [300, 900, 2100], "mortgage_value": 1500, "upgrade_cost": 1500},
    {"id": 14, "name": "商业区", "type": "property", "price": 3500, "rent": [350, 1050, 2450], "mortgage_value": 1750, "upgrade_cost": 1750},
    {"id": 15, "name": "税收", "type": "tax", "price": 0}
]

# 地产颜色组常量 - 定义同一颜色组的地产ID
PROPERTY_GROUPS = {
    'group1': [1, 2],
    'group2': [4, 5],
    'group3': [7, 8],
    'group4': [10, 11],
    'group5': [13, 14]
}

# 机会卡片常量 - 偏向奖励
CHANCE_CARDS = [
    {'type': 'money_change', 'value': 1000, 'text': '银行分红，获得1000元'},
    {'type': 'money_change', 'value': 800, 'text': '股票投资收益，获得800元'},
    {'type': 'money_change', 'value': 1500, 'text': '彩票中奖，获得1500元'},
    {'type': 'move_to', 'value': 0, 'text': '前进到起点，获得起点奖励'},
    {'type': 'money_change', 'value': 500, 'text': '工作奖金，获得500元'},
    {'type': 'move_forward', 'value': 3, 'text': '搭乘快车，前进3格'},
    {'type': 'money_change', 'value': 1200, 'text': '房租收入，获得1200元'}
]

# 命运卡片常量 - 偏向惩罚
DESTINY_CARDS = [
    {'type': 'money_change', 'value': -500, 'text': '缴纳个人所得税500元'},
    {'type': 'money_change', 'value': -800, 'text': '汽车维修费，支付800元'},
    {'type': 'money_change', 'value': -300, 'text': '医疗费用，支付300元'},
    {'type': 'money_change', 'value': -1000, 'text': '房屋维修费，支付1000元'},
    {'type': 'move_backward', 'value': 2, 'text': '交通堵塞，后退2格'},
    {'type': 'money_change', 'value': -600, 'text': '信用卡年费，支付600元'},
    {'type': 'money_change', 'value': -400, 'text': '水电费账单，支付400元'}
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
        
        # 初始化地块状态字典
        for i, tile in enumerate(GAME_MAP):
            self.game_state.tile_states[str(i)] = TileState()
    
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
        # 检查是否有玩家处于债务状态
        if self.game_state.player_in_debt_id:
            return {"success": False, "message": "你必须先处理你的债务！"}
        
        if player_id != self.game_state.current_turn_player_id:
            return {"success": False, "message": "不是你的回合"}
        
        if player_id not in self.game_state.players:
            return {"success": False, "message": "玩家不存在"}
        
        if self.game_state.has_rolled_dice:
            return {"success": False, "message": "本回合已经掷过骰子了"}
        
        player = self.game_state.players[player_id]
        
        # 处理监狱逻辑
        if player.is_in_jail:
            player.turns_in_jail += 1
            self.game_state.game_log.append(f"{player.name} 在监狱中度过第 {player.turns_in_jail} 个回合")
            
            if player.turns_in_jail >= 3:
                # 强制释放并扣除罚款
                fine = 500
                player.money -= fine
                player.is_in_jail = False
                player.turns_in_jail = 0
                self.game_state.game_log.append(f"{player.name} 被强制释放出狱，支付罚款 {fine} 元")
                # 检查债务状态
                self._handle_debt(player_id)
            else:
                # 标记已掷骰子但不移动
                self.game_state.has_rolled_dice = True
                self._check_turn_completion()
                return {
                    "success": True,
                    "message": f"在监狱中，无法移动。还需要 {3 - player.turns_in_jail} 个回合才能出狱",
                    "dice_roll": 0,
                    "new_position": player.position,
                    "tile": GAME_MAP[player.position]
                }
        
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
        # 检查是否有玩家处于债务状态
        if self.game_state.player_in_debt_id:
            return {"success": False, "message": "你必须先处理你的债务！"}
        
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
        player.properties.append(player.position)  # 保留原有逻辑用于兼容性
        
        # 在tile_states中记录所有权
        self.game_state.tile_states[str(player.position)].owner_id = player_id
        
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
        # 检查是否有玩家处于债务状态
        if self.game_state.player_in_debt_id:
            return {"success": False, "message": "你必须先处理你的债务！"}
        
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
        
        # 处理机会卡
        if current_tile["type"] == "chance":
            card = random.choice(CHANCE_CARDS)
            self._apply_card_effect(player_id, card)
            return
        
        # 处理命运卡
        if current_tile["type"] == "destiny":
            card = random.choice(DESTINY_CARDS)
            self._apply_card_effect(player_id, card)
            return
        
        # 处理监狱地块
        if current_tile["type"] == "jail":
            player.is_in_jail = True
            player.turns_in_jail = 0
            self.game_state.game_log.append(f"{player.name} 被关进了监狱")
            return

        # 处理税收地块
        if current_tile["type"] == "tax":
            tax_amount = 2000  # 固定税收金额2000元
            player.money -= tax_amount
            self.game_state.game_log.append(f"{player.name} 缴纳了 {tax_amount} 元税收")
            # 检查债务状态
            self._handle_debt(player_id)
            return

        # 只处理地产类型的地块
        if current_tile["type"] != "property":
            return
        
        # 从tile_states中获取地产所有者
        tile_state = self.game_state.tile_states[str(player.position)]
        property_owner = None
        
        if tile_state.owner_id and tile_state.owner_id != player_id:
            property_owner = self.game_state.players.get(tile_state.owner_id)
        
        # 如果地产有所有者且不是当前玩家
        if property_owner:
            # 检查地产是否被抵押
            if tile_state.mortgaged:
                self.game_state.game_log.append(
                    f"{current_tile['name']} 已被抵押，无需支付租金"
                )
                return
            
            # 根据地产等级计算租金
            rent_list = current_tile.get("rent", [0])
            if isinstance(rent_list, list):
                # 确保等级不超出租金列表范围
                level = min(tile_state.level, len(rent_list) - 1)
                rent = rent_list[level]
            else:
                # 兼容旧的单一租金格式
                rent = rent_list
            
            # 强制扣除租金，即使资金不足
            player.money -= rent
            property_owner.money += rent
            
            level_text = f"（等级{tile_state.level}）" if tile_state.level > 0 else ""
            self.game_state.game_log.append(
                f"{player.name} 向 {property_owner.name} 支付了 {rent} 元租金（{current_tile['name']}{level_text}）"
            )
            
            # 检查债务状态
            self._handle_debt(player_id)
    
    def _apply_card_effect(self, player_id: str, card: Dict):
        """应用卡片效果（私有方法）"""
        if player_id not in self.game_state.players:
            return
        
        player = self.game_state.players[player_id]
        
        # 记录抽到的卡片
        self.game_state.game_log.append(f"{player.name} 抽到卡片：{card['text']}")
        
        # 根据卡片类型应用效果
        if card['type'] == 'money_change':
            player.money += card['value']
            # 检查债务状态
            self._handle_debt(player_id)
        
        elif card['type'] == 'move_to':
            old_position = player.position
            player.position = card['value']
            self.game_state.game_log.append(
                f"{player.name} 从位置 {old_position} 移动到位置 {player.position}"
            )
            # 如果移动到起点或经过起点，给予奖励
            if card['value'] == 0:
                player.money += 2000
                self.game_state.game_log.append(f"{player.name} 到达起点，获得2000元奖励")
        
        elif card['type'] == 'move_forward':
            old_position = player.position
            player.position = (player.position + card['value']) % len(GAME_MAP)
            self.game_state.game_log.append(
                f"{player.name} 从位置 {old_position} 前进 {card['value']} 格到位置 {player.position}"
            )
            # 检查是否经过起点
            if old_position + card['value'] >= len(GAME_MAP):
                player.money += 2000
                self.game_state.game_log.append(f"{player.name} 经过起点，获得2000元奖励")
        
        elif card['type'] == 'move_backward':
            old_position = player.position
            player.position = (player.position - card['value']) % len(GAME_MAP)
            self.game_state.game_log.append(
                f"{player.name} 从位置 {old_position} 后退 {card['value']} 格到位置 {player.position}"
            )
        
        # 移动后处理新位置的落地事件
        if card['type'] in ['move_to', 'move_forward', 'move_backward']:
            self._handle_landing(player_id)
    
    def remove_player(self, player_id: str):
        """删除玩家并清空其地产归属"""
        if player_id not in self.game_state.players:
            return
        
        player_name = self.game_state.players[player_id].name
        player = self.game_state.players[player_id]
        
        # 清空该玩家所有地产的状态
        for property_id in player.properties:
            tile_state = self.game_state.tile_states[str(property_id)]
            tile_state.owner_id = ""
            tile_state.mortgaged = False
            tile_state.level = 0
        
        # 从玩家字典中删除该玩家
        del self.game_state.players[player_id]
        
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
        tile_state = self.game_state.tile_states[str(player.position)]
        if tile_state.owner_id:
            self.game_state.can_buy_property = False
            return
        
        # 如果地产未被购买，则可以购买
        self.game_state.can_buy_property = True
    
    def _check_turn_completion(self):
        """检查回合是否完成（私有方法）"""
        # 如果已掷骰子且不能购买地产，则回合完成
        if self.game_state.has_rolled_dice and not self.game_state.can_buy_property:
            self.game_state.turn_completed = True
    
    def mortgage_property(self, player_id: str, property_id: int) -> Dict:
        """抵押地产"""
        # 验证玩家是否存在
        if player_id not in self.game_state.players:
            return {"success": False, "message": "玩家不存在"}
        
        player = self.game_state.players[player_id]
        
        # 验证地产ID是否有效
        if property_id < 0 or property_id >= len(GAME_MAP):
            return {"success": False, "message": "无效的地产ID"}
        
        property_tile = GAME_MAP[property_id]
        
        # 验证是否为地产类型
        if property_tile["type"] != "property":
            return {"success": False, "message": "该地块不是地产"}
        
        # 验证玩家是否拥有该地产
        tile_state = self.game_state.tile_states[str(property_id)]
        if tile_state.owner_id != player_id:
            return {"success": False, "message": "您不拥有该地产"}
        
        # 验证地产是否已被抵押
        if tile_state.mortgaged:
            return {"success": False, "message": "该地产已被抵押"}
        
        # 执行抵押
        tile_state.mortgaged = True
        mortgage_value = property_tile["mortgage_value"]
        player.money += mortgage_value
        
        # 记录日志
        self.game_state.game_log.append(
            f"{player.name} 将 {property_tile['name']} 抵押给了银行，获得了 {mortgage_value} 元"
        )
        
        # 检查债务状态（抵押可能让玩家脱离债务状态）
        self._handle_debt(player_id)
        
        return {
            "success": True,
            "message": f"成功抵押 {property_tile['name']}，获得 {mortgage_value} 元",
            "mortgage_value": mortgage_value
        }
    
    def redeem_property(self, player_id: str, property_id: int) -> Dict:
        """赎回地产"""
        # 验证玩家是否存在
        if player_id not in self.game_state.players:
            return {"success": False, "message": "玩家不存在"}
        
        player = self.game_state.players[player_id]
        
        # 验证地产ID是否有效
        if property_id < 0 or property_id >= len(GAME_MAP):
            return {"success": False, "message": "无效的地产ID"}
        
        property_tile = GAME_MAP[property_id]
        
        # 验证是否为地产类型
        if property_tile["type"] != "property":
            return {"success": False, "message": "该地块不是地产"}
        
        # 验证玩家是否拥有该地产
        tile_state = self.game_state.tile_states[str(property_id)]
        if tile_state.owner_id != player_id:
            return {"success": False, "message": "您不拥有该地产"}
        
        # 验证地产是否处于抵押状态
        if not tile_state.mortgaged:
            return {"success": False, "message": "该地产未被抵押"}
        
        # 计算赎回金额（抵押价值的110%）
        redeem_amount = int(property_tile["mortgage_value"] * 1.1)
        
        # 验证玩家资金是否足够
        if player.money < redeem_amount:
            return {
                "success": False, 
                "message": f"资金不足，需要 {redeem_amount} 元赎回 {property_tile['name']}"
            }
        
        # 执行赎回
        tile_state.mortgaged = False
        player.money -= redeem_amount
        
        # 记录日志
        self.game_state.game_log.append(
            f"{player.name} 支付 {redeem_amount} 元赎回了 {property_tile['name']}"
        )
        
        return {
            "success": True,
            "message": f"成功赎回 {property_tile['name']}，支付 {redeem_amount} 元",
            "redeem_amount": redeem_amount
        }
    
    def upgrade_property(self, player_id: str, property_id: int) -> Dict:
        """升级地产"""
        # 检查玩家是否存在
        if player_id not in self.game_state.players:
            return {"success": False, "message": "玩家不存在"}
        
        player = self.game_state.players[player_id]
        
        # 检查地产ID是否有效
        if property_id < 0 or property_id >= len(GAME_MAP):
            return {"success": False, "message": "无效的地产ID"}
        
        property_tile = GAME_MAP[property_id]
        
        # 检查是否为地产类型
        if property_tile["type"] != "property":
            return {"success": False, "message": "该地块不是地产"}
        
        # 检查玩家是否拥有该地产
        if property_id not in player.properties:
            return {"success": False, "message": "你不拥有这个地产"}
        
        # 检查玩家是否拥有该地产所属颜色组的全部地产
        property_group = None
        for group_name, group_properties in PROPERTY_GROUPS.items():
            if property_id in group_properties:
                property_group = group_properties
                break
        
        if property_group:
            # 检查该颜色组中的所有地产是否都被当前玩家拥有
            for group_property_id in property_group:
                group_tile_state = self.game_state.tile_states[str(group_property_id)]
                if group_tile_state.owner_id != player_id:
                    return {"success": False, "message": "你必须拥有该颜色组的全部地产才能升级"}
        
        # 获取地块状态
        tile_state = self.game_state.tile_states[str(property_id)]
        
        # 检查地产是否被抵押
        if tile_state.mortgaged:
            return {"success": False, "message": "被抵押的地产无法升级"}
        
        # 检查是否已达到最高等级（最多3级：0,1,2）
        if tile_state.level >= 2:
            return {"success": False, "message": "该地产已达到最高等级"}
        
        # 检查玩家资金是否足够
        upgrade_cost = property_tile["upgrade_cost"]
        if player.money < upgrade_cost:
            return {
                "success": False, 
                "message": f"资金不足，升级需要{upgrade_cost}元"
            }
        
        # 执行升级
        player.money -= upgrade_cost
        tile_state.level += 1
        
        self.game_state.game_log.append(
            f"{player.name} 升级了 {property_tile['name']}，等级提升至 {tile_state.level} 级，花费 {upgrade_cost} 元"
        )
        
        return {
            "success": True, 
            "message": f"成功升级 {property_tile['name']} 至 {tile_state.level} 级",
            "new_level": tile_state.level,
            "cost": upgrade_cost
        }
    
    def _handle_debt(self, player_id: str):
        """处理玩家债务（私有方法）"""
        if player_id not in self.game_state.players:
            return
        
        player = self.game_state.players[player_id]
        
        # 检查玩家资金是否小于0
        if player.money < 0:
            # 检查玩家是否还有未抵押的地产
            has_unmortgaged_properties = False
            for property_id in player.properties:
                tile_state = self.game_state.tile_states[str(property_id)]
                if not tile_state.mortgaged:
                    has_unmortgaged_properties = True
                    break
            
            if has_unmortgaged_properties:
                # 情况A：有资产可卖
                self.game_state.player_in_debt_id = player_id
                self.game_state.game_log.append(
                    f"{player.name} 资金为负！必须抵押地产来偿还债务。"
                )
            else:
                # 情况B：无资产可卖，触发真正的破产
                self.game_state.game_log.append(
                    f"{player.name} 破产了！资金不足且无可抵押资产。"
                )
                self.remove_player(player_id)
                
                # 检查游戏是否只剩最后一名胜利者
                if len(self.game_state.players) == 1:
                    winner = list(self.game_state.players.values())[0]
                    self.game_state.game_log.append(
                        f"游戏结束！{winner.name} 获得胜利！"
                    )
                    self.game_state.game_phase = "finished"
        else:
            # 如果玩家资金已经恢复为非负数，清除债务状态
            if self.game_state.player_in_debt_id == player_id:
                self.game_state.player_in_debt_id = ""
                self.game_state.game_log.append(
                    f"{player.name} 已偿还债务，恢复正常状态。"
                )
    
    def get_game_state(self) -> GameState:
        """获取当前游戏状态"""
        return self.game_state