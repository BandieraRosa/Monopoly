from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import uuid
from typing import Dict, List
from game_logic import GameManager
from models import GameState

app = FastAPI(title="大富翁游戏服务器")

# 添加CORS中间件以支持跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量存储活跃的游戏
active_games: Dict[str, GameManager] = {}

class CreateRoomRequest(BaseModel):
    """创建房间请求模型"""
    room_name: str = "新游戏"

class CreateRoomResponse(BaseModel):
    """创建房间响应模型"""
    room_id: str
    message: str

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储每个房间的连接列表
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # 存储每个连接对应的玩家信息
        self.connection_info: Dict[WebSocket, Dict[str, str]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, player_id: str):
        """接受WebSocket连接"""
        await websocket.accept()
        
        # 初始化房间连接列表
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        
        # 添加连接到房间
        self.active_connections[room_id].append(websocket)
        
        # 存储连接信息
        self.connection_info[websocket] = {
            "room_id": room_id,
            "player_id": player_id
        }
    
    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.connection_info:
            room_id = self.connection_info[websocket]["room_id"]
            
            # 从房间连接列表中移除
            if room_id in self.active_connections:
                self.active_connections[room_id].remove(websocket)
                
                # 如果房间没有连接了，清理房间
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
            
            # 清理连接信息
            del self.connection_info[websocket]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_text(message)
    
    async def broadcast_to_room(self, message: str, room_id: str):
        """向房间内所有连接广播消息"""
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message)
                except:
                    # 如果发送失败，移除该连接
                    self.disconnect(connection)

# 创建连接管理器实例
manager = ConnectionManager()

@app.post("/create_room", response_model=CreateRoomResponse)
async def create_room(request: CreateRoomRequest):
    """创建新的游戏房间"""
    room_id = str(uuid.uuid4())[:8]  # 生成8位房间ID
    
    # 创建新的游戏管理器
    game_manager = GameManager(room_id)
    active_games[room_id] = game_manager
    
    return CreateRoomResponse(
        room_id=room_id,
        message=f"房间 {room_id} 创建成功"
    )

@app.get("/rooms")
async def get_active_rooms():
    """获取活跃房间列表"""
    rooms = []
    for room_id, game_manager in active_games.items():
        rooms.append({
            "room_id": room_id,
            "player_count": len(game_manager.game_state.players),
            "game_phase": game_manager.game_state.game_phase
        })
    return {"rooms": rooms}

@app.websocket("/ws/{room_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, player_id: str):
    """WebSocket端点处理游戏连接"""
    await manager.connect(websocket, room_id, player_id)
    
    # 检查房间是否存在，不存在则创建
    if room_id not in active_games:
        active_games[room_id] = GameManager(room_id)
    
    game_manager = active_games[room_id]
    
    try:
        # 发送欢迎消息
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": f"已连接到房间 {room_id}"
            }),
            websocket
        )
        
        # 发送当前游戏状态
        await manager.send_personal_message(
            json.dumps({
                "type": "game_state",
                "data": game_manager.get_game_state().dict()
            }),
            websocket
        )
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            response = {"type": "action_result", "success": False}
            
            if action == "join_game":
                player_name = message.get("player_name", f"玩家{player_id}")
                success = game_manager.add_player(player_id, player_name)
                response["success"] = success
                response["message"] = "加入游戏成功" if success else "加入游戏失败"
            
            elif action == "roll_dice":
                result = game_manager.roll_dice_and_move(player_id)
                response.update(result)
            
            elif action == "buy_property":
                result = game_manager.buy_property(player_id)
                response.update(result)
            
            elif action == "end_turn":
                result = game_manager.end_turn()
                response.update(result)
            
            else:
                response["message"] = "未知操作"
            
            # 发送操作结果给当前玩家
            await manager.send_personal_message(json.dumps(response), websocket)
            
            # 广播更新后的游戏状态给房间内所有玩家
            game_state_message = json.dumps({
                "type": "game_state",
                "data": game_manager.get_game_state().dict()
            })
            await manager.broadcast_to_room(game_state_message, room_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # 从游戏中移除玩家并清空其地产
        game_manager.remove_player(player_id)
        
        # 广播玩家离开消息
        await manager.broadcast_to_room(
            json.dumps({
                "type": "player_disconnect",
                "player_id": player_id,
                "message": f"玩家 {player_id} 离开了游戏"
            }),
            room_id
        )
        
        # 广播更新后的游戏状态
        game_state_message = json.dumps({
            "type": "game_state",
            "data": game_manager.get_game_state().dict()
        })
        await manager.broadcast_to_room(game_state_message, room_id)

@app.get("/")
async def root():
    """根路径"""
    return {"message": "大富翁游戏服务器运行中"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)