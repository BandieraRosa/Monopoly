// 游戏地图数据（与后端保持一致）
const GAME_MAP = [
    {"id": 0, "name": "起点", "type": "start"},
    {"id": 1, "name": "南京路", "type": "property", "price": 1000, "rent": [100, 300, 700], "mortgage_value": 500, "upgrade_cost": 500},
    {"id": 2, "name": "厦门路", "type": "property", "price": 1200, "rent": [120, 360, 840], "mortgage_value": 600, "upgrade_cost": 600},
    {"id": 3, "name": "机会", "type": "chance"},
    {"id": 4, "name": "广州路", "type": "property", "price": 1500, "rent": [150, 450, 1050], "mortgage_value": 750, "upgrade_cost": 750},
    {"id": 5, "name": "监狱/探监", "type": "jail"},
    {"id": 6, "name": "深圳路", "type": "property", "price": 1800, "rent": [180, 540, 1260], "mortgage_value": 900, "upgrade_cost": 900},
    {"id": 7, "name": "杭州路", "type": "property", "price": 2000, "rent": [200, 600, 1400], "mortgage_value": 1000, "upgrade_cost": 1000},
    {"id": 8, "name": "命运", "type": "destiny"},
    {"id": 9, "name": "苏州路", "type": "property", "price": 2200, "rent": [220, 660, 1540], "mortgage_value": 1100, "upgrade_cost": 1100},
    {"id": 10, "name": "免费停车", "type": "free_parking"},
    {"id": 11, "name": "重庆路", "type": "property", "price": 2500, "rent": [250, 750, 1750], "mortgage_value": 1250, "upgrade_cost": 1250},
    {"id": 12, "name": "成都路", "type": "property", "price": 2800, "rent": [280, 840, 1960], "mortgage_value": 1400, "upgrade_cost": 1400},
    {"id": 13, "name": "税收", "type": "tax"},
    {"id": 14, "name": "武汉路", "type": "property", "price": 3000, "rent": [300, 900, 2100], "mortgage_value": 1500, "upgrade_cost": 1500},
    {"id": 15, "name": "前往监狱", "type": "go_to_jail"},
    {"id": 16, "name": "长沙路", "type": "property", "price": 3200, "rent": [320, 960, 2240], "mortgage_value": 1600, "upgrade_cost": 1600},
    {"id": 17, "name": "西安路", "type": "property", "price": 3500, "rent": [350, 1050, 2450], "mortgage_value": 1750, "upgrade_cost": 1750},
    {"id": 18, "name": "机会", "type": "chance"},
    {"id": 19, "name": "天津路", "type": "property", "price": 4000, "rent": [400, 1200, 2800], "mortgage_value": 2000, "upgrade_cost": 2000}
];

// 地产颜色组常量（与后端保持一致）
const PROPERTY_GROUPS = {
    'group1': [1, 2, 4],
    'group2': [6, 7, 9],
    'group3': [11, 12, 14],
    'group4': [16, 17, 19]
};

// 全局变量
let socket = null;
let roomId = null;
let playerId = null;
let playerName = null;
let gameState = null;
let lastShownCardLog = null; // 记录上次显示的卡片日志，避免重复显示

// DOM元素
const elements = {
    modal: document.getElementById('join-modal'),
    joinForm: document.getElementById('join-form'),
    createRoomBtn: document.getElementById('create-room-btn'),
    roomIdInput: document.getElementById('room-id-input'),
    playerNameInput: document.getElementById('player-name-input'),
    roomIdDisplay: document.getElementById('room-id-display'),
    playerIdDisplay: document.getElementById('player-id-display'),
    gameBoard: document.getElementById('game-board'),
    playersList: document.getElementById('players-list'),
    currentTurn: document.getElementById('current-turn'),
    rollDiceBtn: document.getElementById('roll-dice-btn'),
    buyPropertyBtn: document.getElementById('buy-property-btn'),
    endTurnBtn: document.getElementById('end-turn-btn'),
    diceValue: document.getElementById('dice-value'),
    logContent: document.getElementById('log-content'),
    connectionStatus: document.getElementById('connection-status'),
    statusText: document.getElementById('status-text')
};

// 初始化游戏
function initGame() {
    // 显示加入游戏模态框
    elements.modal.style.display = 'flex';
    
    // 创建游戏棋盘
    createGameBoard();
    
    // 绑定事件监听器
    bindEventListeners();
}

// 创建游戏棋盘
function createGameBoard() {
    elements.gameBoard.innerHTML = '';
    
    // 创建20个地块的环形布局
    // 布局：上边6个，右边4个，下边6个，左边4个
    const positions = getCircularPositions();
    
    GAME_MAP.forEach((tile, index) => {
        const tileElement = document.createElement('div');
        tileElement.className = `tile ${tile.type}`;
        tileElement.id = `tile-${index}`;
        tileElement.style.gridArea = positions[index];
        
        tileElement.innerHTML = `
            <div class="tile-name">${tile.name}</div>
            ${tile.price > 0 ? `<div class="tile-price">$${tile.price}</div>` : ''}
        `;
        
        elements.gameBoard.appendChild(tileElement);
    });
}

// 获取环形布局的位置信息
function getCircularPositions() {
    const positions = [];
    
    // 地块0：左上角起点
    positions[0] = '1 / 1';
    
    // 地块1-5：上边（从左到右）
    for (let i = 1; i <= 5; i++) {
        positions[i] = `1 / ${i + 1}`;
    }
    
    // 地块6-9：右边（从上到下）
    for (let i = 6; i <= 9; i++) {
        positions[i] = `${i - 4} / 6`;
    }
    
    // 地块10-14：下边（从右到左）
    for (let i = 10; i <= 14; i++) {
        positions[i] = `6 / ${16 - i}`;
    }
    
    // 地块15-19：左边（从下到上）
    for (let i = 15; i <= 19; i++) {
        positions[i] = `${21 - i} / 1`;
    }
    
    return positions;
}

// 绑定事件监听器
function bindEventListeners() {
    // 加入游戏表单
    elements.joinForm.addEventListener('submit', handleJoinGame);
    
    // 创建房间按钮
    elements.createRoomBtn.addEventListener('click', handleCreateRoom);
    
    // 游戏控制按钮
    elements.rollDiceBtn.addEventListener('click', () => sendAction('roll_dice'));
    elements.buyPropertyBtn.addEventListener('click', () => sendAction('buy_property'));
    elements.endTurnBtn.addEventListener('click', () => sendAction('end_turn'));
}

// 处理加入游戏
async function handleJoinGame(event) {
    event.preventDefault();
    
    roomId = elements.roomIdInput.value.trim();
    playerName = elements.playerNameInput.value.trim();
    
    if (!playerName) {
        alert('请输入玩家姓名');
        return;
    }
    
    // 如果没有输入房间ID，创建新房间
    if (!roomId) {
        await createNewRoom();
    }
    
    // 生成玩家ID
    playerId = generatePlayerId();
    
    // 连接WebSocket
    connectWebSocket();
    
    // 隐藏模态框
    elements.modal.style.display = 'none';
    
    // 更新显示信息
    elements.roomIdDisplay.textContent = `房间ID: ${roomId}`;
    elements.playerIdDisplay.textContent = `玩家ID: ${playerId}`;
}

// 处理创建房间
async function handleCreateRoom() {
    try {
        const response = await fetch('http://localhost:8001/create_room', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ room_name: '新游戏' })
        });
        
        const data = await response.json();
        elements.roomIdInput.value = data.room_id;
        
        alert(`房间创建成功！房间ID: ${data.room_id}`);
    } catch (error) {
        console.error('创建房间失败:', error);
        alert('创建房间失败，请检查服务器连接');
    }
}

// 创建新房间
async function createNewRoom() {
    try {
        const response = await fetch('http://localhost:8001/create_room', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ room_name: '新游戏' })
        });
        
        const data = await response.json();
        roomId = data.room_id;
    } catch (error) {
        console.error('创建房间失败:', error);
        alert('创建房间失败，请检查服务器连接');
        throw error;
    }
}

// 生成玩家ID
function generatePlayerId() {
    return 'player_' + Math.random().toString(36).substr(2, 9);
}

// 连接WebSocket
function connectWebSocket() {
    updateConnectionStatus('connecting', '连接中...');
    
    const wsUrl = `ws://localhost:8001/ws/${roomId}/${playerId}`;
    socket = new WebSocket(wsUrl);
    
    socket.onopen = function(event) {
        console.log('WebSocket连接已建立');
        updateConnectionStatus('connected', '已连接');
        
        // 发送加入游戏请求
        sendAction('join_game', { player_name: playerName });
    };
    
    socket.onmessage = function(event) {
        const message = JSON.parse(event.data);
        handleServerMessage(message);
    };
    
    socket.onclose = function(event) {
        console.log('WebSocket连接已关闭');
        updateConnectionStatus('disconnected', '连接断开');
        
        // 尝试重连
        setTimeout(() => {
            if (roomId && playerId) {
                connectWebSocket();
            }
        }, 3000);
    };
    
    socket.onerror = function(error) {
        console.error('WebSocket错误:', error);
        updateConnectionStatus('disconnected', '连接错误');
    };
}

// 处理服务器消息
function handleServerMessage(message) {
    console.log('收到服务器消息:', message);
    
    switch (message.type) {
        case 'connection':
            addLogEntry(message.message);
            break;
            
        case 'game_state':
            gameState = message.data;
            render(gameState);
            checkForCardMessage(gameState.game_log);
            break;
            
        case 'action_result':
            handleActionResult(message);
            break;
            
        case 'player_disconnect':
            addLogEntry(message.message);
            break;
            
        default:
            console.log('未知消息类型:', message.type);
    }
}

// 处理操作结果
function handleActionResult(result) {
    if (result.success) {
        if (result.dice_roll) {
            elements.diceValue.textContent = result.dice_roll;
        }
        
        if (result.message) {
            addLogEntry(result.message);
        }
    } else {
        alert(result.message || '操作失败');
    }
}

// 发送操作到服务器
function sendAction(action, data = {}) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        const message = {
            action: action,
            ...data
        };
        socket.send(JSON.stringify(message));
    } else {
        alert('连接已断开，请刷新页面重试');
    }
}

// 处理地产抵押/赎回/升级操作
function handlePropertyAction(actionType, propertyId) {
    if (actionType === 'mortgage') {
        sendAction('mortgage_property', { property_id: propertyId });
    } else if (actionType === 'redeem') {
        sendAction('redeem_property', { property_id: propertyId });
    } else if (actionType === 'upgrade') {
        sendAction('upgrade_property', { property_id: propertyId });
    }
}

// 渲染游戏状态
function render(state) {
    if (!state) return;
    
    // 检查债务模式
    const isInDebtMode = state.player_in_debt_id === playerId;
    
    // 处理债务模式UI
    handleDebtMode(isInDebtMode);
    
    // 更新玩家信息
    renderPlayers(state.players, state.current_turn_player_id);
    
    // 更新玩家位置
    renderPlayerPositions(state.players);
    
    // 更新地块所有权显示
    renderPropertyOwnership(state.players);
    
    // 更新当前回合显示
    const currentPlayer = state.players[state.current_turn_player_id];
    elements.currentTurn.textContent = currentPlayer ? currentPlayer.name : '等待中...';
    
    // 更新按钮状态（考虑债务模式）
    updateButtonStates(state.current_turn_player_id === playerId, isInDebtMode);
    
    // 更新游戏日志
    renderGameLog(state.game_log);
}

// 渲染玩家信息
function renderPlayers(players, currentTurnPlayerId) {
    elements.playersList.innerHTML = '';
    
    Object.values(players).forEach((player, index) => {
        const playerElement = document.createElement('div');
        playerElement.className = `player-item ${player.id === currentTurnPlayerId ? 'current-turn' : ''}`;
        
        // 检查玩家是否在监狱中
        const jailStatus = player.is_in_jail ? ' <span class="jail-indicator">（监狱中）</span>' : '';
        
        // 创建地产列表HTML
        let propertiesHtml = '';
        let hasProperties = false;
        
        // 遍历所有地块，找到属于当前玩家的地产
        propertiesHtml = '<div class="properties-list">';
        for (let propertyId = 0; propertyId < GAME_MAP.length; propertyId++) {
            const property = GAME_MAP[propertyId];
            
            // 只处理地产类型的地块
            if (property.type !== 'property') continue;
            
            // 检查该地产是否属于当前玩家
            const tileState = gameState && gameState.tile_states ? gameState.tile_states[propertyId.toString()] : null;
            if (!tileState || tileState.owner_id !== player.id) continue;
            
            hasProperties = true;
            const isMortgaged = tileState.mortgaged;
            const level = tileState.level;
            const mortgageStatus = isMortgaged ? ' <span class="mortgage-status">(已抵押)</span>' : '';
            const levelStatus = level > 0 ? ` <span class="level-status">Lv.${level}</span>` : '';
            
            propertiesHtml += `
                <div class="property-item ${isMortgaged ? 'mortgaged' : ''}">
                    <span class="property-name">${property.name}${mortgageStatus}${levelStatus}</span>
                    ${player.id === playerId ? `
                        <div class="property-buttons">
                            <button class="property-btn ${isMortgaged ? 'redeem-btn' : 'mortgage-btn'}" 
                                    onclick="handlePropertyAction('${isMortgaged ? 'redeem' : 'mortgage'}', ${propertyId})">
                                ${isMortgaged ? '赎回' : '抵押'}
                            </button>
                            ${!isMortgaged && level < 2 && hasCompletePropertyGroup(player.id, propertyId) ? `
                                <button class="property-btn upgrade-btn" 
                                        onclick="handlePropertyAction('upgrade', ${propertyId})">
                                    升级
                                </button>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>
            `;
        }
        propertiesHtml += '</div>';
        
        if (!hasProperties) {
            propertiesHtml = '<div class="no-properties">无</div>';
        }
        
        playerElement.innerHTML = `
            <div class="player-name">${player.name} ${player.id === playerId ? '(你)' : ''}${jailStatus}</div>
            <div class="player-money">资金: $${player.money}</div>
            <div class="player-position">位置: ${GAME_MAP[player.position].name}</div>
            <div class="player-properties">
                <div class="properties-header">地产:</div>
                ${propertiesHtml}
            </div>
        `;
        
        elements.playersList.appendChild(playerElement);
    });
}

// 渲染玩家位置
function renderPlayerPositions(players) {
    // 清除所有玩家标记
    document.querySelectorAll('.player-token').forEach(token => token.remove());
    
    // 为每个玩家添加标记
    Object.values(players).forEach((player, index) => {
        const tileElement = document.getElementById(`tile-${player.position}`);
        if (tileElement) {
            const tokenElement = document.createElement('div');
            tokenElement.className = `player-token player-${(index % 4) + 1}`;
            tokenElement.textContent = player.name.charAt(0);
            tokenElement.title = player.name;
            
            tileElement.appendChild(tokenElement);
        }
    });
}

// 渲染地块所有权
function renderPropertyOwnership(players) {
    // 清除所有地块的所有权样式和抵押状态
    document.querySelectorAll('.tile').forEach(tile => {
        tile.classList.remove('owned-by-player1', 'owned-by-player2', 'owned-by-player3', 'owned-by-player4', 'mortgaged');
        const ownerLabel = tile.querySelector('.owner-label');
        if (ownerLabel) {
            ownerLabel.remove();
        }
        const mortgageIndicator = tile.querySelector('.mortgage-indicator');
        if (mortgageIndicator) {
            mortgageIndicator.remove();
        }
        const levelIndicator = tile.querySelector('.level-indicator');
        if (levelIndicator) {
            levelIndicator.remove();
        }
    });
    
    // 为每个玩家的地产添加所有权标识
    Object.values(players).forEach((player, index) => {
        const playerClass = `owned-by-player${(index % 4) + 1}`;
        
        // 遍历所有地块，找到属于当前玩家的地产
        for (let propertyPosition = 0; propertyPosition < GAME_MAP.length; propertyPosition++) {
            const property = GAME_MAP[propertyPosition];
            
            // 只处理地产类型的地块
            if (property.type !== 'property') continue;
            
            // 检查该地产是否属于当前玩家
            const tileState = gameState && gameState.tile_states ? gameState.tile_states[propertyPosition.toString()] : null;
            if (!tileState || tileState.owner_id !== player.id) continue;
            
            const tileElement = document.getElementById(`tile-${propertyPosition}`);
            
            if (tileElement) {
                // 添加所有权CSS类
                tileElement.classList.add(playerClass);
                
                const isMortgaged = tileState.mortgaged;
                const level = tileState.level;
                
                // 检查是否被抵押
                if (isMortgaged) {
                    tileElement.classList.add('mortgaged');
                    
                    // 添加抵押标识
                    const mortgageIndicator = document.createElement('div');
                    mortgageIndicator.className = 'mortgage-indicator';
                    mortgageIndicator.textContent = '抵押';
                    tileElement.appendChild(mortgageIndicator);
                }
                
                // 添加等级标识
                if (level > 0) {
                    const levelIndicator = document.createElement('div');
                    levelIndicator.className = 'level-indicator';
                    levelIndicator.textContent = `Lv.${level}`;
                    tileElement.appendChild(levelIndicator);
                }
                
                // 添加玩家名字首字母标识
                const ownerLabel = document.createElement('div');
                ownerLabel.className = 'owner-label';
                ownerLabel.textContent = player.name.charAt(0);
                ownerLabel.title = `拥有者: ${player.name}${isMortgaged ? ' (已抵押)' : ''}${level > 0 ? ` (等级${level})` : ''}`;
                
                tileElement.appendChild(ownerLabel);
            }
        }
    });
}

// 处理债务模式UI
function handleDebtMode(isInDebtMode) {
    const debtModal = document.getElementById('debt-modal');
    
    if (isInDebtMode) {
        // 进入债务模式
        if (!debtModal) {
            // 创建债务模式提示框
            createDebtModal();
        } else {
            debtModal.style.display = 'flex';
        }
    } else {
        // 退出债务模式
        if (debtModal) {
            debtModal.style.display = 'none';
        }
    }
}

// 创建债务模式提示框
function createDebtModal() {
    const modal = document.createElement('div');
    modal.id = 'debt-modal';
    modal.className = 'debt-modal';
    modal.innerHTML = `
        <div class="debt-modal-content">
            <button class="debt-modal-close" onclick="closeDebtModal()">&times;</button>
            <div class="debt-icon">⚠️</div>
            <h2>资金不足！</h2>
            <p>您的资金为负数，必须抵押地产来偿还债务！</p>
            <p>在偿还债务之前，您无法进行其他操作。</p>
            <div class="debt-actions">
                <p>请在右侧玩家信息面板中选择要抵押的地产</p>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// 关闭债务模式提示框
function closeDebtModal() {
    const debtModal = document.getElementById('debt-modal');
    if (debtModal) {
        debtModal.style.display = 'none';
    }
}

// 更新按钮状态
function updateButtonStates(isMyTurn, isInDebtMode = false) {
    if (!isMyTurn || !gameState || isInDebtMode) {
        // 不是我的回合时，或处于债务模式时，禁用游戏控制按钮
        elements.rollDiceBtn.disabled = true;
        elements.buyPropertyBtn.disabled = true;
        elements.endTurnBtn.disabled = true;
        return;
    }
    
    // 是我的回合且不在债务模式时，根据游戏状态控制按钮
    // 掷骰子按钮：只有在未掷骰子时才能点击
    elements.rollDiceBtn.disabled = gameState.has_rolled_dice;
    
    // 购买地产按钮：根据后端返回的 can_buy_property 状态
    elements.buyPropertyBtn.disabled = !gameState.can_buy_property;
    
    // 结束回合按钮：只有在回合完成时才能点击
    elements.endTurnBtn.disabled = !gameState.turn_completed;
}

// 检查地产是否已被拥有
function isPropertyOwned(position) {
    if (!gameState || !gameState.tile_states) return false;
    
    const tileState = gameState.tile_states[position.toString()];
    return tileState && tileState.owner_id !== '';
}

// 检查玩家是否拥有指定地产所属颜色组的全部地产
function hasCompletePropertyGroup(playerId, propertyId) {
    if (!gameState || !gameState.tile_states) return false;
    
    // 找到该地产所属的颜色组
    let propertyGroup = null;
    for (const [groupName, groupProperties] of Object.entries(PROPERTY_GROUPS)) {
        if (groupProperties.includes(propertyId)) {
            propertyGroup = groupProperties;
            break;
        }
    }
    
    // 如果找不到所属颜色组，返回false
    if (!propertyGroup) return false;
    
    // 检查该颜色组中的所有地产是否都被当前玩家拥有
    for (const groupPropertyId of propertyGroup) {
        const tileState = gameState.tile_states[groupPropertyId.toString()];
        if (!tileState || tileState.owner_id !== playerId) {
            return false;
        }
    }
    
    return true;
}

// 渲染游戏日志
function renderGameLog(logs) {
    elements.logContent.innerHTML = '';
    
    // 显示最近的10条日志
    const recentLogs = logs.slice(-10);
    
    recentLogs.forEach(log => {
        const logElement = document.createElement('div');
        logElement.className = 'log-entry';
        logElement.textContent = log;
        elements.logContent.appendChild(logElement);
    });
    
    // 滚动到底部
    elements.logContent.scrollTop = elements.logContent.scrollHeight;
}

// 添加日志条目
function addLogEntry(message) {
    const logElement = document.createElement('div');
    logElement.className = 'log-entry';
    logElement.textContent = message;
    elements.logContent.appendChild(logElement);
    
    // 滚动到底部
    elements.logContent.scrollTop = elements.logContent.scrollHeight;
}

// 更新连接状态
function updateConnectionStatus(status, text) {
    elements.connectionStatus.className = status;
    elements.statusText.textContent = text;
}

// 检查游戏日志中的卡片信息
function checkForCardMessage(logs) {
    if (!logs || logs.length === 0) return;
    
    // 检查最新的几条日志
    const recentLogs = logs.slice(-3);
    
    for (let log of recentLogs) {
        if (log.includes('抽到卡片：')) {
            // 检查是否已经显示过这条日志
            if (lastShownCardLog === log) {
                continue;
            }
            
            const cardText = log.split('抽到卡片：')[1];
            let cardType = '卡片';
            
            // 判断卡片类型
            if (log.includes('机会') || cardText.includes('银行分红') || cardText.includes('股票') || 
                cardText.includes('彩票') || cardText.includes('奖金') || cardText.includes('收入') || 
                cardText.includes('前进') || cardText.includes('快车')) {
                cardType = '机会卡';
            } else if (log.includes('命运') || cardText.includes('税') || cardText.includes('维修') || 
                      cardText.includes('医疗') || cardText.includes('年费') || cardText.includes('账单') || 
                      cardText.includes('后退') || cardText.includes('堵塞')) {
                cardType = '命运卡';
            }
            
            // 记录已显示的卡片日志
            lastShownCardLog = log;
            showCardModal(cardType, cardText);
            break;
        }
    }
}

// 显示卡片模态框
function showCardModal(cardType, cardText) {
    const modal = document.getElementById('card-modal');
    const typeElement = document.getElementById('card-type');
    const textElement = document.getElementById('card-text');
    
    if (!modal || !typeElement || !textElement) return;
    
    // 设置卡片内容
    typeElement.textContent = cardType;
    textElement.textContent = cardText;
    
    // 设置卡片样式类
    modal.className = 'card-modal';
    if (cardType === '机会卡') {
        modal.classList.add('chance');
    } else if (cardType === '命运卡') {
        modal.classList.add('destiny');
    }
    
    // 显示模态框
    modal.style.display = 'flex';
    
    // 添加显示动画
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
    
    // 2秒后开始淡出
    setTimeout(() => {
        modal.classList.add('fade-out');
        modal.classList.remove('show');
        
        // 淡出动画完成后隐藏
        setTimeout(() => {
            modal.style.display = 'none';
            modal.classList.remove('fade-out', 'chance', 'destiny');
        }, 300);
    }, 2000);
}

// 页面加载完成后初始化游戏
document.addEventListener('DOMContentLoaded', initGame);

// 页面卸载时关闭WebSocket连接
window.addEventListener('beforeunload', function() {
    if (socket) {
        socket.close();
    }
});