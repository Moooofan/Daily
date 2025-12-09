// 極簡版前端邏輯 + 語音輸入

// 全域狀態
const state = {
    currentEditId: null,
    currentEditType: null, // 'todo' or 'schedule'
    currentTodoType: 'daily', // 'daily', 'weekly', 'monthly'
    recognition: null,
    currentRoutineId: null // 固定排程編輯用
};

// DOM 元素
const el = {
    // 智能輸入
    smartInput: document.getElementById('smartInput'),
    processBtn: document.getElementById('processBtn'),
    voiceBtn: document.getElementById('voiceBtn'),
    voiceIcon: document.getElementById('voiceIcon'),
    voiceStatus: document.getElementById('voiceStatus'),

    // 待辦
    todoInput: document.getElementById('todoInput'),
    addTodoBtn: document.getElementById('addTodoBtn'),
    todoList: document.getElementById('todoList'),

    // 排程
    scheduleDate: document.getElementById('scheduleDate'),
    scheduleInput: document.getElementById('scheduleInput'),
    addScheduleBtn: document.getElementById('addScheduleBtn'),
    suggestBtn: document.getElementById('suggestBtn'),
    generateBtn: document.getElementById('generateBtn'),
    clearScheduleBtn: document.getElementById('clearScheduleBtn'),
    suggestion: document.getElementById('suggestion'),
    scheduleList: document.getElementById('scheduleList'),

    // 匯入彈窗
    importModal: document.getElementById('importModal'),
    confirmImport: document.getElementById('confirmImport'),
    skipImport: document.getElementById('skipImport'),
    rememberChoice: document.getElementById('rememberChoice'),

    // 碎片任務
    quickTasksList: document.getElementById('quickTasksList'),
    quickTaskCount: document.getElementById('quickTaskCount'),
    quickTaskToggle: document.getElementById('quickTaskToggle'),

    // 固定排程
    routinesList: document.getElementById('routinesList'),
    routineItems: document.getElementById('routineItems'),
    routineCount: document.getElementById('routineCount'),
    routineToggle: document.getElementById('routineToggle'),
    routineInput: document.getElementById('routineInput'),
    addRoutineBtn: document.getElementById('addRoutineBtn'),

    // 固定排程編輯彈窗
    routineEditModal: document.getElementById('routineEditModal'),
    routineTitle: document.getElementById('routineTitle'),
    routineStartHour: document.getElementById('routineStartHour'),
    routineStartMin: document.getElementById('routineStartMin'),
    routineEndHour: document.getElementById('routineEndHour'),
    routineEndMin: document.getElementById('routineEndMin'),
    saveRoutine: document.getElementById('saveRoutine'),
    cancelRoutine: document.getElementById('cancelRoutine'),

    // 模態框
    editModal: document.getElementById('editModal'),
    editInput: document.getElementById('editInput'),
    saveEdit: document.getElementById('saveEdit'),
    cancelEdit: document.getElementById('cancelEdit'),

    scheduleEditModal: document.getElementById('scheduleEditModal'),
    scheduleTitle: document.getElementById('scheduleTitle'),
    scheduleStartHour: document.getElementById('scheduleStartHour'),
    scheduleStartMin: document.getElementById('scheduleStartMin'),
    scheduleEndHour: document.getElementById('scheduleEndHour'),
    scheduleEndMin: document.getElementById('scheduleEndMin'),
    saveSchedule: document.getElementById('saveSchedule'),
    cancelSchedule: document.getElementById('cancelSchedule'),

    loading: document.getElementById('loading')
};

// ===== 初始化 =====

document.addEventListener('DOMContentLoaded', () => {
    init();
    attachEvents();
});

function init() {
    // 設定今日日期
    const today = new Date().toISOString().split('T')[0];
    el.scheduleDate.value = today;

    // 初始化時間選擇器
    initTimeSelects();

    // 初始化語音辨識
    initSpeechRecognition();

    // 載入資料
    loadTodos();
    loadSchedule(today);
    loadQuickTasks();
    loadRoutines();

    // 檢查是否需要顯示匯入彈窗
    checkAndShowImportModal();
}

// 初始化時間選擇器
function initTimeSelects() {
    // 填充小時選項 (00-23)
    const hourSelects = [
        el.scheduleStartHour, el.scheduleEndHour,
        el.routineStartHour, el.routineEndHour
    ];
    hourSelects.forEach(select => {
        for (let h = 0; h < 24; h++) {
            const option = document.createElement('option');
            option.value = h.toString().padStart(2, '0');
            option.textContent = h.toString().padStart(2, '0');
            select.appendChild(option);
        }
    });

    // 填充分鐘選項 (00, 05, 10, ... 55)
    const minSelects = [
        el.scheduleStartMin, el.scheduleEndMin,
        el.routineStartMin, el.routineEndMin
    ];
    minSelects.forEach(select => {
        for (let m = 0; m < 60; m += 5) {
            const option = document.createElement('option');
            option.value = m.toString().padStart(2, '0');
            option.textContent = m.toString().padStart(2, '0');
            select.appendChild(option);
        }
    });

    // 設定預設值（當前時間的下一個整點）
    const now = new Date();
    const currentHour = now.getHours();
    el.scheduleStartHour.value = currentHour.toString().padStart(2, '0');
    el.scheduleStartMin.value = '00';
    el.scheduleEndHour.value = ((currentHour + 1) % 24).toString().padStart(2, '0');
    el.scheduleEndMin.value = '00';

    // 固定排程預設值
    el.routineStartHour.value = '09';
    el.routineStartMin.value = '00';
    el.routineEndHour.value = '10';
    el.routineEndMin.value = '00';
}

function attachEvents() {
    // 智能輸入
    el.processBtn.addEventListener('click', processSmartInput);
    el.voiceBtn.addEventListener('click', toggleVoiceRecognition);

    // 待辦分頁切換
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // 移除所有 active
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            // 添加 active 到當前
            e.target.classList.add('active');
            // 更新狀態並重新載入
            state.currentTodoType = e.target.dataset.type;
            loadTodos();
        });
    });

    // 待辦
    el.addTodoBtn.addEventListener('click', addTodo);
    el.todoInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addTodo();
    });

    // 排程
    el.addScheduleBtn.addEventListener('click', addScheduleManually);
    el.scheduleInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addScheduleManually();
    });
    el.generateBtn.addEventListener('click', generateSchedule);
    el.clearScheduleBtn.addEventListener('click', clearDailySchedule);
    el.suggestBtn.addEventListener('click', getSuggestion);

    // 匯入彈窗
    el.confirmImport.addEventListener('click', handleConfirmImport);
    el.skipImport.addEventListener('click', handleSkipImport);
    el.scheduleDate.addEventListener('change', (e) => {
        loadSchedule(e.target.value);
        // 如果當前在日待辦分頁，也要重新載入日待辦
        if (state.currentTodoType === 'daily') {
            loadTodos();
        }
    });

    // 模態框
    el.saveEdit.addEventListener('click', saveEdit);
    el.cancelEdit.addEventListener('click', closeEditModal);
    el.saveSchedule.addEventListener('click', saveScheduleEdit);
    el.cancelSchedule.addEventListener('click', closeScheduleEditModal);

    // 固定排程
    el.addRoutineBtn.addEventListener('click', openAddRoutineModal);
    el.routineInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') openAddRoutineModal();
    });
    el.saveRoutine.addEventListener('click', saveRoutineEdit);
    el.cancelRoutine.addEventListener('click', closeRoutineEditModal);

    // 點擊外部關閉模態框
    el.editModal.addEventListener('click', (e) => {
        if (e.target === el.editModal) closeEditModal();
    });
    el.scheduleEditModal.addEventListener('click', (e) => {
        if (e.target === el.scheduleEditModal) closeScheduleEditModal();
    });
    el.routineEditModal.addEventListener('click', (e) => {
        if (e.target === el.routineEditModal) closeRoutineEditModal();
    });

    // 點擊外部關閉所有選單
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.schedule-actions')) {
            const allMenus = document.querySelectorAll('.schedule-menu');
            allMenus.forEach(menu => {
                menu.style.display = 'none';
            });
        }
    });
}

// ===== 智能輸入處理 =====

async function processSmartInput() {
    const text = el.smartInput.value.trim();
    if (!text) {
        el.voiceStatus.textContent = '請輸入內容';
        return;
    }

    el.voiceStatus.textContent = '處理中...';
    showLoading();

    try {
        const response = await fetch('/api/ai/process-voice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        if (data.success) {
            el.voiceStatus.textContent = `已新增 ${data.todos_added} 項待辦，${data.schedules_added} 項排程`;
            el.smartInput.value = '';

            // 重新載入資料
            await loadTodos();
            await loadSchedule(el.scheduleDate.value);

            setTimeout(() => {
                el.voiceStatus.textContent = '';
            }, 3000);
        } else {
            el.voiceStatus.textContent = `處理失敗: ${data.error || '未知錯誤'}`;
            console.error('API 錯誤:', data);
        }
    } catch (error) {
        console.error('處理輸入錯誤:', error);
        el.voiceStatus.textContent = `網路錯誤: ${error.message}`;
    } finally {
        hideLoading();
    }
}

// ===== 語音辨識 =====

function initSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.log('瀏覽器不支援語音辨識');
        el.voiceBtn.disabled = true;
        el.voiceBtn.style.opacity = '0.5';
        el.voiceStatus.textContent = '瀏覽器不支援語音功能';
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    state.recognition = new SpeechRecognition();

    // 優化設定
    state.recognition.lang = 'zh-TW';
    state.recognition.continuous = true;  // 改為持續錄音
    state.recognition.interimResults = true;  // 顯示即時結果
    state.recognition.maxAlternatives = 3;  // 增加替代方案

    state.recognition.onstart = () => {
        el.voiceBtn.classList.add('recording');
        el.voiceIcon.textContent = '🔴';
        el.voiceStatus.textContent = '正在聆聽... 請說話';
    };

    state.recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }

        // 顯示即時辨識結果
        if (interimTranscript) {
            el.voiceStatus.textContent = `聆聽中：${interimTranscript}`;
        }

        // 處理最終結果
        if (finalTranscript) {
            el.voiceStatus.textContent = `辨識到：${finalTranscript}`;
            state.recognition.stop();
            // 填入文字框
            el.smartInput.value = (el.smartInput.value + ' ' + finalTranscript).trim();
        }
    };

    state.recognition.onerror = (event) => {
        console.error('語音辨識錯誤:', event.error);

        let errorMsg = '辨識失敗';
        switch(event.error) {
            case 'no-speech':
                errorMsg = '沒有檢測到語音，請重試';
                break;
            case 'audio-capture':
                errorMsg = '無法存取麥克風';
                break;
            case 'not-allowed':
                errorMsg = '麥克風權限被拒絕';
                break;
            case 'network':
                errorMsg = '網路錯誤';
                break;
            default:
                errorMsg = `錯誤：${event.error}`;
        }

        el.voiceStatus.textContent = errorMsg;
        el.voiceBtn.classList.remove('recording');
        el.voiceIcon.textContent = '🎤';
    };

    state.recognition.onend = () => {
        el.voiceBtn.classList.remove('recording');
        el.voiceIcon.textContent = '🎤';

        // 如果沒有處理任何結果，顯示提示
        setTimeout(() => {
            if (el.voiceStatus.textContent.includes('聆聽中') ||
                el.voiceStatus.textContent.includes('正在聆聽')) {
                el.voiceStatus.textContent = '未檢測到語音，請重試';
            }
        }, 500);
    };
}

function toggleVoiceRecognition() {
    if (!state.recognition) {
        el.voiceStatus.textContent = '語音功能未初始化';
        return;
    }

    if (el.voiceBtn.classList.contains('recording')) {
        // 停止錄音
        state.recognition.stop();
        el.voiceStatus.textContent = '已停止';
    } else {
        // 開始錄音
        try {
            state.recognition.start();
        } catch (error) {
            console.error('啟動語音辨識失敗:', error);

            // 如果是因為已經在運行中，先停止再重新開始
            if (error.name === 'InvalidStateError') {
                state.recognition.stop();
                setTimeout(() => {
                    try {
                        state.recognition.start();
                    } catch (e) {
                        el.voiceStatus.textContent = '啟動失敗，請重新整理頁面';
                    }
                }, 100);
            } else {
                el.voiceStatus.textContent = '無法啟動語音辨識';
            }
        }
    }
}

async function processVoiceInput(text) {
    showLoading();

    try {
        const response = await fetch('/api/ai/process-voice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        const data = await response.json();

        if (data.success) {
            el.voiceStatus.textContent = `已新增 ${data.todos_added} 項待辦，${data.schedules_added} 項排程`;

            // 重新載入資料
            await loadTodos();
            await loadSchedule(el.scheduleDate.value);

            setTimeout(() => {
                el.voiceStatus.textContent = '';
            }, 3000);
        } else {
            el.voiceStatus.textContent = `處理失敗: ${data.error || '未知錯誤'}`;
            console.error('API 錯誤:', data);
        }
    } catch (error) {
        console.error('處理語音輸入錯誤:', error);
        el.voiceStatus.textContent = `網路錯誤: ${error.message}`;
    } finally {
        hideLoading();
    }
}

// ===== 待辦事項 =====

async function loadTodos() {
    try {
        let url = `/api/todos?type=${state.currentTodoType}`;

        // 如果是日待辦，加上日期參數
        if (state.currentTodoType === 'daily') {
            const date = el.scheduleDate.value;
            url += `&target_date=${date}`;
        }

        const response = await fetch(url);
        const todos = await response.json();
        renderTodos(todos);
    } catch (error) {
        console.error('載入待辦失敗:', error);
    }
}

function renderTodos(todos) {
    if (todos.length === 0) {
        el.todoList.innerHTML = '<div class="empty-state">尚無待辦事項</div>';
        return;
    }

    el.todoList.innerHTML = todos.map(todo => {
        const completedClass = todo.completed ? 'completed' : '';
        const estimatedTime = todo.estimated_minutes || 30;

        return `
            <div class="todo-item ${completedClass}">
                <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''}
                       onchange="toggleTodoComplete(${todo.id})" />
                <div class="todo-content" onclick="editTodo(${todo.id}, '${escapeHtml(todo.content)}', ${estimatedTime})">${escapeHtml(todo.content)}</div>
                <div class="todo-time" onclick="editTodoTime(${todo.id}, ${estimatedTime})">⏱️ ${estimatedTime}分</div>
                <div class="todo-actions">
                    <button onclick="deleteTodo(${todo.id})">×</button>
                </div>
            </div>
        `;
    }).join('');
}

async function addTodo() {
    const content = el.todoInput.value.trim();
    if (!content) return;

    try {
        const todoData = {
            content,
            type: state.currentTodoType
        };

        // 日待辦需要指定日期
        if (state.currentTodoType === 'daily') {
            todoData.target_date = el.scheduleDate.value;
        }

        const response = await fetch('/api/todos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(todoData)
        });

        if (response.ok) {
            el.todoInput.value = '';
            await loadTodos();
        }
    } catch (error) {
        console.error('新增待辦失敗:', error);
    }
}

async function deleteTodo(id) {
    try {
        const response = await fetch(`/api/todos/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadTodos();
        }
    } catch (error) {
        console.error('刪除待辦失敗:', error);
    }
}

function editTodo(id, content, estimatedTime) {
    state.currentEditId = id;
    state.currentEditType = 'todo';
    el.editInput.value = content;
    el.editModal.classList.add('show');
    el.editInput.focus();
}

async function toggleTodoComplete(id) {
    try {
        const response = await fetch(`/api/todos/${id}/toggle`, {
            method: 'POST'
        });

        if (response.ok) {
            await loadTodos();
        }
    } catch (error) {
        console.error('切換待辦完成狀態失敗:', error);
    }
}

async function editTodoTime(id, currentTime) {
    const newTime = prompt(`設定預估時間（分鐘）：`, currentTime);
    if (newTime === null || newTime === '') return;

    const minutes = parseInt(newTime);
    if (isNaN(minutes) || minutes <= 0) {
        alert('請輸入有效的分鐘數');
        return;
    }

    try {
        const response = await fetch(`/api/todos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ estimated_minutes: minutes })
        });

        if (response.ok) {
            await loadTodos();
        }
    } catch (error) {
        console.error('更新預估時間失敗:', error);
    }
}

async function saveEdit() {
    const content = el.editInput.value.trim();
    if (!content) return;

    try {
        const response = await fetch(`/api/todos/${state.currentEditId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });

        if (response.ok) {
            closeEditModal();
            await loadTodos();
        }
    } catch (error) {
        console.error('更新待辦失敗:', error);
    }
}

function closeEditModal() {
    el.editModal.classList.remove('show');
    el.editInput.value = '';
    state.currentEditId = null;
    state.currentEditType = null;
}

// ===== 排程 =====

async function loadSchedule(date) {
    try {
        // 先自動套用固定排程（如果還沒有的話）
        await applyRoutinesToDate(date);

        const response = await fetch(`/api/schedule/${date}`);
        const schedule = await response.json();
        renderSchedule(schedule);
    } catch (error) {
        console.error('載入排程失敗:', error);
    }
}

function renderSchedule(schedule) {
    if (schedule.length === 0) {
        el.scheduleList.innerHTML = '<div class="empty-state">點擊「生成」按鈕創建今日排程</div>';
        return;
    }

    el.scheduleList.innerHTML = schedule.map(item => {
        // 判斷是否完成
        const completedClass = item.completed ? 'completed' : '';
        // 判斷是否來自固定排程
        const isFromRoutine = item.routine_id !== null && item.routine_id !== undefined;
        const routineClass = isFromRoutine ? 'from-routine' : '';
        const routineBadge = isFromRoutine ? '<span class="routine-badge" title="來自固定排程">🔄</span>' : '';

        return `
            <div class="schedule-item ${completedClass} ${routineClass}" data-id="${item.id}" data-routine-id="${item.routine_id || ''}" draggable="true">
                <input type="checkbox" class="schedule-checkbox" ${item.completed ? 'checked' : ''}
                       onchange="toggleScheduleComplete(${item.id})" />
                <div class="schedule-time">${item.start_time}~${item.end_time}</div>
                <div class="schedule-title">${routineBadge}${escapeHtml(item.title)}</div>
                <button class="schedule-edit-btn" onclick="editSchedule(${item.id}, '${escapeHtml(item.title)}', '${item.start_time}', '${item.end_time}')" title="編輯">✏️</button>
                <div class="schedule-actions">
                    <button class="schedule-menu-btn" onclick="toggleScheduleMenu(${item.id})">⋮</button>
                    <div class="schedule-menu" id="menu-${item.id}" style="display: none;">
                        <button onclick="duplicateSchedule(${item.id})">複製</button>
                        ${isFromRoutine ? `<button onclick="excludeRoutineForToday(${item.routine_id})" class="warning">本日排除</button>` : ''}
                        <button onclick="deleteSchedule(${item.id})" class="danger">刪除</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    // 初始化拖拉功能
    initDragAndDrop();
}

async function generateSchedule() {
    const date = el.scheduleDate.value;
    showLoading();

    try {
        // 取得當前時間 (HH:MM 格式)
        const now = new Date();
        const currentTime = now.getHours().toString().padStart(2, '0') + ':' +
                          now.getMinutes().toString().padStart(2, '0');

        const response = await fetch('/api/ai/generate-schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                date,
                current_time: currentTime  // 傳遞當前時間
            })
        });

        const data = await response.json();

        if (data.success) {
            await loadSchedule(date);
        } else {
            alert('生成失敗：' + data.error);
        }
    } catch (error) {
        console.error('生成排程失敗:', error);
        alert('生成失敗');
    } finally {
        hideLoading();
    }
}

async function clearDailySchedule() {
    const date = el.scheduleDate.value;

    // 確認刪除
    if (!confirm(`確定要清空 ${date} 的所有排程嗎？此操作無法復原。`)) {
        return;
    }

    showLoading();

    try {
        const response = await fetch(`/api/schedule/clear/${date}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            await loadSchedule(date);
            alert(data.message || '排程已清空');
        } else {
            alert('清空失敗：' + (data.error || '未知錯誤'));
        }
    } catch (error) {
        console.error('清空排程失敗:', error);
        alert('清空失敗');
    } finally {
        hideLoading();
    }
}

async function addScheduleManually() {
    const title = el.scheduleInput.value.trim();
    if (!title) return;

    // 打開排程編輯模態框，讓使用者設定時間
    state.currentEditId = null; // 新增模式
    state.currentEditType = 'schedule';
    el.scheduleTitle.value = title;

    // 設定預設時間為當前時間的下一個整點
    const now = new Date();
    const currentHour = now.getHours();
    el.scheduleStartHour.value = currentHour.toString().padStart(2, '0');
    el.scheduleStartMin.value = '00';
    el.scheduleEndHour.value = ((currentHour + 1) % 24).toString().padStart(2, '0');
    el.scheduleEndMin.value = '00';

    el.scheduleEditModal.classList.add('show');
    el.scheduleStartHour.focus();

    // 清空輸入框
    el.scheduleInput.value = '';
}

function toggleScheduleMenu(id) {
    const menu = document.getElementById(`menu-${id}`);
    const allMenus = document.querySelectorAll('.schedule-menu');

    // 關閉其他選單
    allMenus.forEach(m => {
        if (m.id !== `menu-${id}`) {
            m.style.display = 'none';
        }
    });

    // 切換當前選單
    menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
}

async function duplicateSchedule(id) {
    try {
        // 先取得當前排程資料
        const response = await fetch(`/api/schedule/${el.scheduleDate.value}`);
        const schedules = await response.json();
        const item = schedules.find(s => s.id === id);

        if (!item) return;

        // 創建新的排程項目
        const addResponse = await fetch('/api/schedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                date: el.scheduleDate.value,
                title: item.title + ' (副本)',
                start_time: item.start_time,
                end_time: item.end_time
            })
        });

        if (addResponse.ok) {
            await loadSchedule(el.scheduleDate.value);
            // 關閉選單
            toggleScheduleMenu(id);
        }
    } catch (error) {
        console.error('複製排程失敗:', error);
    }
}

async function deleteSchedule(id) {
    if (!confirm('確定要刪除這個排程項目嗎？')) {
        return;
    }

    try {
        const response = await fetch(`/api/schedule/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await loadSchedule(el.scheduleDate.value);
        }
    } catch (error) {
        console.error('刪除排程失敗:', error);
    }
}

function editSchedule(id, title, startTime, endTime) {
    state.currentEditId = id;
    state.currentEditType = 'schedule';
    el.scheduleTitle.value = title;

    // 解析時間並設定到選擇器
    const [startHour, startMin] = startTime.split(':');
    const [endHour, endMin] = endTime.split(':');

    el.scheduleStartHour.value = startHour;
    el.scheduleStartMin.value = getNearestFiveMin(startMin);
    el.scheduleEndHour.value = endHour;
    el.scheduleEndMin.value = getNearestFiveMin(endMin);

    el.scheduleEditModal.classList.add('show');
    el.scheduleTitle.focus();
}

// 取得最接近的 5 分鐘值
function getNearestFiveMin(min) {
    const m = parseInt(min);
    const rounded = Math.round(m / 5) * 5;
    return (rounded % 60).toString().padStart(2, '0');
}

async function saveScheduleEdit() {
    const title = el.scheduleTitle.value.trim();
    const startTime = `${el.scheduleStartHour.value}:${el.scheduleStartMin.value}`;
    const endTime = `${el.scheduleEndHour.value}:${el.scheduleEndMin.value}`;

    if (!title) {
        alert('請填寫標題');
        return;
    }

    // 驗證時間順序
    if (startTime >= endTime) {
        alert('結束時間必須晚於開始時間');
        return;
    }

    try {
        let response;
        if (state.currentEditId === null) {
            // 新增模式
            response = await fetch('/api/schedule', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    date: el.scheduleDate.value,
                    title,
                    start_time: startTime,
                    end_time: endTime
                })
            });
        } else {
            // 編輯模式
            response = await fetch(`/api/schedule/${state.currentEditId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, start_time: startTime, end_time: endTime })
            });
        }

        if (response.ok) {
            closeScheduleEditModal();
            await loadSchedule(el.scheduleDate.value);
        }
    } catch (error) {
        console.error('儲存排程失敗:', error);
    }
}

function closeScheduleEditModal() {
    el.scheduleEditModal.classList.remove('show');
    el.scheduleTitle.value = '';

    // 重設時間選擇器為當前時間的下一個整點
    const now = new Date();
    const currentHour = now.getHours();
    el.scheduleStartHour.value = currentHour.toString().padStart(2, '0');
    el.scheduleStartMin.value = '00';
    el.scheduleEndHour.value = ((currentHour + 1) % 24).toString().padStart(2, '0');
    el.scheduleEndMin.value = '00';

    state.currentEditId = null;
    state.currentEditType = null;
}

// ===== AI 建議 =====

async function getSuggestion() {
    showLoading();
    try {
        const response = await fetch('/api/ai/suggest-now');
        const data = await response.json();

        if (data.success) {
            el.suggestion.textContent = data.suggestion;
            el.suggestion.style.display = 'block';

            // 3秒後自動隱藏
            setTimeout(() => {
                el.suggestion.style.display = 'none';
            }, 10000);
        } else {
            el.suggestion.textContent = '建議生成失敗';
            el.suggestion.style.display = 'block';
        }
    } catch (error) {
        console.error('取得建議失敗:', error);
        el.suggestion.textContent = '建議生成失敗';
        el.suggestion.style.display = 'block';
    } finally {
        hideLoading();
    }
}

// ===== 完成標記 =====

async function toggleScheduleComplete(id) {
    try {
        const response = await fetch(`/api/schedule/${id}/toggle`, {
            method: 'POST'
        });

        if (response.ok) {
            await loadSchedule(el.scheduleDate.value);
        }
    } catch (error) {
        console.error('切換完成狀態失敗:', error);
    }
}

// ===== 拖拉排序 =====

let draggedElement = null;

function initDragAndDrop() {
    const items = document.querySelectorAll('.schedule-item');

    items.forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragover', handleDragOver);
        item.addEventListener('drop', handleDrop);
        item.addEventListener('dragend', handleDragEnd);
    });
}

function handleDragStart(e) {
    draggedElement = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';

    // 視覺反饋：在拖曳元素上方或下方顯示
    const afterElement = getDragAfterElement(el.scheduleList, e.clientY);
    if (afterElement == null) {
        el.scheduleList.appendChild(draggedElement);
    } else {
        el.scheduleList.insertBefore(draggedElement, afterElement);
    }

    return false;
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    return false;
}

function handleDragEnd(e) {
    this.classList.remove('dragging');

    // 更新排序到後端
    updateScheduleOrder();
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.schedule-item:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;

        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

async function updateScheduleOrder() {
    const items = document.querySelectorAll('.schedule-item');
    const updates = Array.from(items).map((item, index) => ({
        id: parseInt(item.dataset.id),
        order: index
    }));

    // 批次更新排序
    for (const update of updates) {
        try {
            await fetch(`/api/schedule/${update.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ display_order: update.order })
            });
        } catch (error) {
            console.error('更新排序失敗:', error);
        }
    }
}

// ===== 延誤偵測與智能重排 =====

async function checkDelays() {
    try {
        const response = await fetch('/api/delay/check');
        const data = await response.json();

        if (data.success && data.delayed_count > 0) {
            // 有延誤項目，詢問是否要智能重排
            const message = `偵測到 ${data.delayed_count} 個延誤項目，是否要 AI 幫你重新安排？`;
            if (confirm(message)) {
                await showRescheduleOptions(data.delayed_items);
            }
        }
    } catch (error) {
        console.error('檢查延誤失敗:', error);
    }
}

async function showRescheduleOptions(delayedItems) {
    showLoading();

    try {
        const response = await fetch('/api/delay/suggest-reschedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date: el.scheduleDate.value })
        });

        const data = await response.json();

        if (data.success && data.suggestions.length > 0) {
            // 顯示重排建議
            displayRescheduleSuggestions(data.suggestions);
        }
    } catch (error) {
        console.error('取得重排建議失敗:', error);
    } finally {
        hideLoading();
    }
}

function displayRescheduleSuggestions(suggestions) {
    // 創建建議顯示區
    let html = '<div style="background: #fff3cd; padding: 15px; margin: 10px 0; border-radius: 5px;">';
    html += '<h3 style="margin: 0 0 10px 0;">🔄 智能重排建議</h3>';

    suggestions.forEach(item => {
        html += `<div style="margin-bottom: 15px; padding: 10px; background: white; border-radius: 4px;">`;
        html += `<strong>${item.original_title}</strong><br/>`;

        item.options.forEach((option, index) => {
            const buttonStyle = index === 0 ? 'background: #4CAF50; color: white;' :
                              index === 1 ? 'background: #2196F3; color: white;' :
                              'background: #f44336; color: white;';

            let label = '';
            if (option.action === 'today') label = '今晚完成';
            else if (option.action === 'tomorrow') label = '明天完成';
            else if (option.action === 'cancel') label = '取消';

            html += `<button onclick="applyReschedule(${item.item_id}, '${option.action}', '${option.time || ''}')"
                            style="${buttonStyle} border: none; padding: 5px 10px; margin: 5px 5px 0 0; border-radius: 3px; cursor: pointer;">
                        ${label}: ${option.time || ''} - ${option.reason}
                     </button>`;
        });

        html += '</div>';
    });

    html += '</div>';

    // 在排程列表上方插入
    el.scheduleList.insertAdjacentHTML('beforebegin', html);
}

async function applyReschedule(itemId, action, time) {
    showLoading();

    try {
        const response = await fetch('/api/delay/apply-reschedule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item_id: itemId,
                action: action,
                time: time
            })
        });

        const data = await response.json();

        if (data.success) {
            // 移除建議區
            const suggestionBox = document.querySelector('[style*="background: #fff3cd"]');
            if (suggestionBox) {
                suggestionBox.remove();
            }

            // 重新載入排程
            await loadSchedule(el.scheduleDate.value);
        } else {
            alert('操作失敗：' + data.error);
        }
    } catch (error) {
        console.error('套用重排失敗:', error);
        alert('操作失敗');
    } finally {
        hideLoading();
    }
}

// ===== 碎片任務 =====

async function loadQuickTasks() {
    try {
        const response = await fetch('/api/todos?type=quick');
        const quickTasks = await response.json();
        renderQuickTasks(quickTasks);
    } catch (error) {
        console.error('載入碎片任務失敗:', error);
    }
}

function renderQuickTasks(tasks) {
    const incompleteTasks = tasks.filter(t => !t.completed);

    // 更新計數
    el.quickTaskCount.textContent = incompleteTasks.length;

    if (incompleteTasks.length === 0) {
        el.quickTasksList.innerHTML = '<div style="padding: 15px; text-align: center; color: var(--gray);">沒有碎片任務</div>';
        return;
    }

    el.quickTasksList.innerHTML = incompleteTasks.map(task => {
        return `
            <div class="quick-task-item">
                <input type="checkbox" class="quick-task-checkbox"
                       onchange="toggleTodoComplete(${task.id}); loadQuickTasks();" />
                <div class="quick-task-content" onclick="editTodo(${task.id}, '${escapeHtml(task.content)}', 5)">${escapeHtml(task.content)}</div>
                <div class="quick-task-actions">
                    <button onclick="deleteTodo(${task.id}); loadQuickTasks();">×</button>
                </div>
            </div>
        `;
    }).join('');
}

function toggleQuickTasks() {
    const list = el.quickTasksList;
    const toggle = el.quickTaskToggle;

    if (list.classList.contains('collapsed')) {
        list.classList.remove('collapsed');
        toggle.classList.remove('collapsed');
        toggle.textContent = '▼';
    } else {
        list.classList.add('collapsed');
        toggle.classList.add('collapsed');
        toggle.textContent = '◀';
    }
}

// ===== 工具函數 =====

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoading() {
    el.loading.classList.add('show');
}

function hideLoading() {
    el.loading.classList.remove('show');
}

// ===== Google Calendar 整合 =====

async function importFromGoogleCalendar() {
    const date = el.scheduleDate.value;

    showLoading();

    try {
        // 呼叫匯入 API
        const response = await fetch('/api/google/import', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date })
        });

        const data = await response.json();

        if (data.need_auth) {
            // 需要授權，重定向到 Google 授權頁面
            alert('需要連接 Google Calendar，將跳轉到授權頁面');
            window.location.href = '/google/authorize';
            return;
        }

        if (data.success) {
            alert(`成功匯入 ${data.imported}/${data.total} 個事件`);
            await loadSchedule(date);
        } else {
            alert('匯入失敗：' + data.error);
        }
    } catch (error) {
        console.error('匯入 Google Calendar 失敗:', error);
        alert('匯入失敗');
    } finally {
        hideLoading();
    }
}

// ===== 自動功能 =====

// 定期檢查延誤（每30分鐘）- 已停用
// setInterval(checkDelays, 30 * 60 * 1000);

// 頁面載入時檢查一次 - 已停用
// setTimeout(checkDelays, 5000);

// ===== Google Calendar 匯入彈窗 =====

function checkAndShowImportModal() {
    // 檢查是否已經選擇過（使用 sessionStorage，關閉瀏覽器後會清除）
    const importChoice = sessionStorage.getItem('gcal_import_choice');

    if (importChoice === 'skip' || importChoice === 'done') {
        // 用戶已選擇略過或已匯入過，不再顯示
        return;
    }

    // 延遲一點點顯示，讓頁面先載入完成
    setTimeout(() => {
        el.importModal.classList.add('show');
    }, 500);
}

function handleConfirmImport() {
    const remember = el.rememberChoice.checked;

    // 關閉彈窗
    el.importModal.classList.remove('show');

    // 執行匯入
    importFromGoogleCalendar();

    // 如果勾選記住選擇
    if (remember) {
        sessionStorage.setItem('gcal_import_choice', 'done');
    }
}

function handleSkipImport() {
    const remember = el.rememberChoice.checked;

    // 關閉彈窗
    el.importModal.classList.remove('show');

    // 如果勾選記住選擇
    if (remember) {
        sessionStorage.setItem('gcal_import_choice', 'skip');
    }
}

// ===== 每日固定排程 =====

async function loadRoutines() {
    try {
        const date = el.scheduleDate.value;
        // 同時載入固定排程和當日例外
        const [routinesRes, exceptionsRes] = await Promise.all([
            fetch('/api/routines'),
            fetch(`/api/routines/exceptions/${date}`)
        ]);
        const routines = await routinesRes.json();
        const exceptionsData = await exceptionsRes.json();
        const exceptions = exceptionsData.exceptions || [];
        renderRoutines(routines, exceptions);
    } catch (error) {
        console.error('載入固定排程失敗:', error);
    }
}

function renderRoutines(routines, exceptions = []) {
    // 更新計數
    const enabledCount = routines.filter(r => r.enabled).length;
    el.routineCount.textContent = enabledCount;

    if (routines.length === 0) {
        el.routineItems.innerHTML = '<div class="routine-empty">尚無固定排程，新增後每天會自動加入</div>';
        return;
    }

    const exceptedIds = new Set(exceptions);

    el.routineItems.innerHTML = routines.map(routine => {
        const disabledClass = routine.enabled ? '' : 'disabled';
        const isExcluded = exceptedIds.has(routine.id);
        const excludedClass = isExcluded ? 'excluded-today' : '';
        const excludedBadge = isExcluded ? '<span class="excluded-badge">本日已排除</span>' : '';

        return `
            <div class="routine-item ${disabledClass} ${excludedClass}" data-id="${routine.id}">
                <input type="checkbox" class="routine-toggle" ${routine.enabled ? 'checked' : ''}
                       onchange="toggleRoutineEnabled(${routine.id})" title="啟用/停用" />
                <div class="routine-time">${routine.start_time}~${routine.end_time}</div>
                <div class="routine-title">${escapeHtml(routine.title)}${excludedBadge}</div>
                <div class="routine-actions">
                    ${isExcluded ? `<button onclick="restoreRoutineForToday(${routine.id})" title="恢復本日" class="restore-btn">↩️</button>` : ''}
                    <button onclick="editRoutine(${routine.id}, '${escapeHtml(routine.title)}', '${routine.start_time}', '${routine.end_time}')" title="編輯">✏️</button>
                    <button class="danger" onclick="deleteRoutine(${routine.id})" title="刪除">×</button>
                </div>
            </div>
        `;
    }).join('');
}

function toggleRoutines() {
    const list = el.routinesList;
    const toggle = el.routineToggle;

    if (list.classList.contains('collapsed')) {
        list.classList.remove('collapsed');
        toggle.textContent = '▼';
    } else {
        list.classList.add('collapsed');
        toggle.textContent = '◀';
    }
}

function openAddRoutineModal() {
    const title = el.routineInput.value.trim();

    state.currentRoutineId = null; // 新增模式
    el.routineTitle.value = title;

    // 設定預設時間
    el.routineStartHour.value = '09';
    el.routineStartMin.value = '00';
    el.routineEndHour.value = '10';
    el.routineEndMin.value = '00';

    el.routineEditModal.classList.add('show');
    if (title) {
        el.routineStartHour.focus();
    } else {
        el.routineTitle.focus();
    }

    el.routineInput.value = '';
}

function editRoutine(id, title, startTime, endTime) {
    state.currentRoutineId = id;
    el.routineTitle.value = title;

    const [startHour, startMin] = startTime.split(':');
    const [endHour, endMin] = endTime.split(':');

    el.routineStartHour.value = startHour;
    el.routineStartMin.value = getNearestFiveMin(startMin);
    el.routineEndHour.value = endHour;
    el.routineEndMin.value = getNearestFiveMin(endMin);

    el.routineEditModal.classList.add('show');
    el.routineTitle.focus();
}

async function saveRoutineEdit() {
    const title = el.routineTitle.value.trim();
    const startTime = `${el.routineStartHour.value}:${el.routineStartMin.value}`;
    const endTime = `${el.routineEndHour.value}:${el.routineEndMin.value}`;

    if (!title) {
        alert('請填寫標題');
        return;
    }

    if (startTime >= endTime) {
        alert('結束時間必須晚於開始時間');
        return;
    }

    try {
        let response;
        if (state.currentRoutineId === null) {
            // 新增
            response = await fetch('/api/routines', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title,
                    start_time: startTime,
                    end_time: endTime
                })
            });
        } else {
            // 更新
            response = await fetch(`/api/routines/${state.currentRoutineId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title,
                    start_time: startTime,
                    end_time: endTime
                })
            });
        }

        if (response.ok) {
            closeRoutineEditModal();
            await loadRoutines();
        }
    } catch (error) {
        console.error('儲存固定排程失敗:', error);
    }
}

function closeRoutineEditModal() {
    el.routineEditModal.classList.remove('show');
    el.routineTitle.value = '';
    el.routineStartHour.value = '09';
    el.routineStartMin.value = '00';
    el.routineEndHour.value = '10';
    el.routineEndMin.value = '00';
    state.currentRoutineId = null;
}

async function toggleRoutineEnabled(id) {
    try {
        await fetch(`/api/routines/${id}/toggle`, { method: 'POST' });
        await loadRoutines();
    } catch (error) {
        console.error('切換固定排程狀態失敗:', error);
    }
}

async function deleteRoutine(id) {
    if (!confirm('確定要刪除這個固定排程嗎？')) return;

    try {
        await fetch(`/api/routines/${id}`, { method: 'DELETE' });
        await loadRoutines();
    } catch (error) {
        console.error('刪除固定排程失敗:', error);
    }
}

async function applyRoutinesToDate(date) {
    try {
        const response = await fetch('/api/routines/apply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date })
        });
        const data = await response.json();
        return data.added;
    } catch (error) {
        console.error('套用固定排程失敗:', error);
        return 0;
    }
}

async function excludeRoutineForToday(routineId) {
    const date = el.scheduleDate.value;

    if (!confirm('確定要將此固定排程從今日排除嗎？\n（可在「每日固定排程」區塊恢復）')) {
        return;
    }

    try {
        const response = await fetch(`/api/routines/${routineId}/exclude`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date })
        });

        if (response.ok) {
            await loadSchedule(date);
            await loadRoutines(); // 重新載入以更新狀態
        }
    } catch (error) {
        console.error('排除固定排程失敗:', error);
    }
}

async function restoreRoutineForToday(routineId) {
    const date = el.scheduleDate.value;

    try {
        const response = await fetch(`/api/routines/${routineId}/restore`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date })
        });

        if (response.ok) {
            await loadSchedule(date);
            await loadRoutines();
        }
    } catch (error) {
        console.error('恢復固定排程失敗:', error);
    }
}
