// 全域狀態
const state = {
    tasks: [],
    schedule: [],
    preferences: {},
    googleConnected: false
};

// DOM 元素
const elements = {
    // Google Calendar
    statusIcon: document.getElementById('statusIcon'),
    statusText: document.getElementById('statusText'),
    googleAuthBtn: document.getElementById('googleAuthBtn'),
    googleDisconnectBtn: document.getElementById('googleDisconnectBtn'),

    // 任務
    tasksList: document.getElementById('tasksList'),
    addTaskBtn: document.getElementById('addTaskBtn'),
    taskModal: document.getElementById('taskModal'),
    taskForm: document.getElementById('taskForm'),
    cancelTaskBtn: document.getElementById('cancelTaskBtn'),

    // 排程
    scheduleDate: document.getElementById('scheduleDate'),
    generateScheduleBtn: document.getElementById('generateScheduleBtn'),
    scheduleView: document.getElementById('scheduleView'),

    // 設定
    settingsToggle: document.getElementById('settingsToggle'),
    settingsPanel: document.getElementById('settingsPanel'),
    saveSettingsBtn: document.getElementById('saveSettingsBtn'),

    // Loading
    loadingOverlay: document.getElementById('loadingOverlay')
};

// ===== 初始化 =====

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    attachEventListeners();
});

async function initializeApp() {
    // 設定今日日期
    const today = new Date().toISOString().split('T')[0];
    elements.scheduleDate.value = today;

    // 載入資料
    await Promise.all([
        checkGoogleStatus(),
        loadTasks(),
        loadPreferences(),
        loadSchedule(today)
    ]);

    // 檢查 URL 參數（OAuth 回調）
    const urlParams = new URLSearchParams(window.location.search);
    const authStatus = urlParams.get('auth');
    if (authStatus === 'success') {
        showNotification('Google Calendar 連接成功！', 'success');
        checkGoogleStatus();
    } else if (authStatus === 'failed') {
        showNotification('Google Calendar 連接失敗', 'error');
    }
}

function attachEventListeners() {
    // Google Calendar
    elements.googleAuthBtn.addEventListener('click', connectGoogle);
    elements.googleDisconnectBtn.addEventListener('click', disconnectGoogle);

    // 任務
    elements.addTaskBtn.addEventListener('click', () => openTaskModal());
    elements.taskForm.addEventListener('submit', handleTaskSubmit);
    elements.cancelTaskBtn.addEventListener('click', closeTaskModal);
    document.querySelector('.close').addEventListener('click', closeTaskModal);

    // 排程
    elements.generateScheduleBtn.addEventListener('click', generateSchedule);
    elements.scheduleDate.addEventListener('change', (e) => {
        loadSchedule(e.target.value);
    });

    // 設定
    elements.settingsToggle.addEventListener('click', toggleSettings);
    elements.saveSettingsBtn.addEventListener('click', savePreferences);

    // Modal 外部點擊關閉
    window.addEventListener('click', (e) => {
        if (e.target === elements.taskModal) {
            closeTaskModal();
        }
    });
}

// ===== Google Calendar =====

async function checkGoogleStatus() {
    try {
        const response = await fetch('/api/google/status');
        const data = await response.json();

        state.googleConnected = data.connected;

        if (data.connected) {
            elements.statusIcon.textContent = '🟢';
            elements.statusText.textContent = 'Google Calendar 已連接';
            elements.googleAuthBtn.style.display = 'none';
            elements.googleDisconnectBtn.style.display = 'inline-block';
        } else {
            elements.statusIcon.textContent = '⚪';
            elements.statusText.textContent = 'Google Calendar 未連接';
            elements.googleAuthBtn.style.display = 'inline-block';
            elements.googleDisconnectBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('檢查 Google 狀態失敗:', error);
    }
}

async function connectGoogle() {
    try {
        const response = await fetch('/api/google/auth-url');
        const data = await response.json();

        if (data.success) {
            window.location.href = data.auth_url;
        }
    } catch (error) {
        showNotification('連接 Google Calendar 失敗', 'error');
    }
}

async function disconnectGoogle() {
    if (!confirm('確定要中斷與 Google Calendar 的連接嗎？')) {
        return;
    }

    try {
        const response = await fetch('/api/google/disconnect', {
            method: 'POST'
        });

        if (response.ok) {
            showNotification('已中斷 Google Calendar 連接', 'success');
            checkGoogleStatus();
        }
    } catch (error) {
        showNotification('中斷連接失敗', 'error');
    }
}

// ===== 任務管理 =====

async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        state.tasks = await response.json();
        renderTasks();
    } catch (error) {
        console.error('載入任務失敗:', error);
    }
}

function renderTasks() {
    if (state.tasks.length === 0) {
        elements.tasksList.innerHTML = `
            <div class="empty-state">
                <p>尚未新增任務，點擊上方按鈕新增第一個任務</p>
            </div>
        `;
        return;
    }

    elements.tasksList.innerHTML = state.tasks.map(task => {
        const priorityClass = task.priority >= 3 ? 'priority-high' :
                             task.priority >= 1 ? 'priority-medium' : 'priority-low';
        const priorityText = task.priority >= 3 ? '高' :
                            task.priority >= 1 ? '中' : '低';

        return `
            <div class="task-item">
                <div class="task-item-header">
                    <div class="task-title">${escapeHtml(task.title)}</div>
                    <div class="task-actions">
                        <button class="edit-btn" onclick="editTask(${task.id})">編輯</button>
                        <button class="delete-btn" onclick="deleteTask(${task.id})">刪除</button>
                    </div>
                </div>
                <div class="task-meta">
                    <span class="task-badge">⏱ ${task.duration} 分鐘</span>
                    <span class="task-badge ${priorityClass}">優先級: ${priorityText}</span>
                    <span class="task-badge">${getCategoryName(task.category)}</span>
                    ${task.preferred_time ? `<span class="task-badge">🕐 ${task.preferred_time}</span>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function openTaskModal(task = null) {
    elements.taskModal.style.display = 'block';

    if (task) {
        document.getElementById('taskTitle').value = task.title;
        document.getElementById('taskDuration').value = task.duration;
        document.getElementById('taskPriority').value = task.priority;
        document.getElementById('taskCategory').value = task.category;
        document.getElementById('taskPreferredTime').value = task.preferred_time || '';
        elements.taskForm.dataset.editId = task.id;
    } else {
        elements.taskForm.reset();
        delete elements.taskForm.dataset.editId;
    }
}

function closeTaskModal() {
    elements.taskModal.style.display = 'none';
    elements.taskForm.reset();
    delete elements.taskForm.dataset.editId;
}

async function handleTaskSubmit(e) {
    e.preventDefault();

    const taskData = {
        title: document.getElementById('taskTitle').value,
        duration: parseInt(document.getElementById('taskDuration').value),
        priority: parseInt(document.getElementById('taskPriority').value),
        category: document.getElementById('taskCategory').value,
        preferred_time: document.getElementById('taskPreferredTime').value || null
    };

    const editId = elements.taskForm.dataset.editId;
    const url = editId ? `/api/tasks/${editId}` : '/api/tasks';
    const method = editId ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taskData)
        });

        if (response.ok) {
            showNotification(editId ? '任務已更新' : '任務已新增', 'success');
            closeTaskModal();
            await loadTasks();
        }
    } catch (error) {
        showNotification('操作失敗', 'error');
    }
}

async function editTask(taskId) {
    const task = state.tasks.find(t => t.id === taskId);
    if (task) {
        openTaskModal(task);
    }
}

async function deleteTask(taskId) {
    if (!confirm('確定要刪除這個任務嗎？')) {
        return;
    }

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showNotification('任務已刪除', 'success');
            await loadTasks();
        }
    } catch (error) {
        showNotification('刪除失敗', 'error');
    }
}

// ===== 排程管理 =====

async function generateSchedule() {
    const date = elements.scheduleDate.value;

    elements.loadingOverlay.style.display = 'flex';

    try {
        const response = await fetch('/api/schedule/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date })
        });

        const data = await response.json();

        if (data.success) {
            state.schedule = data.schedule;
            renderSchedule();
            showNotification('行程已生成！', 'success');
        } else {
            showNotification('生成失敗: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('生成失敗', 'error');
    } finally {
        elements.loadingOverlay.style.display = 'none';
    }
}

async function loadSchedule(date) {
    try {
        const response = await fetch(`/api/schedule/${date}`);

        if (response.ok) {
            const data = await response.json();
            state.schedule = data.schedule;
            renderSchedule();
        } else {
            // 尚未生成
            elements.scheduleView.innerHTML = `
                <div class="empty-state">
                    <p>尚未生成該日期的行程，點擊「生成行程」按鈕開始規劃</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('載入排程失敗:', error);
    }
}

function renderSchedule() {
    if (!state.schedule || state.schedule.length === 0) {
        elements.scheduleView.innerHTML = `
            <div class="empty-state">
                <p>點擊「生成行程」按鈕，讓 AI 為你規劃今天的完整行程</p>
            </div>
        `;
        return;
    }

    elements.scheduleView.innerHTML = state.schedule.map(item => {
        const typeIcon = {
            'calendar': '📅',
            'task': '✅',
            'routine': '🔄',
            'break': '☕'
        }[item.type] || '📌';

        return `
            <div class="schedule-item schedule-type-${item.type}">
                <div class="schedule-time">
                    ${item.start_time}<br>
                    <small style="color: #94a3b8;">↓</small><br>
                    ${item.end_time}
                </div>
                <div class="schedule-details">
                    <div class="schedule-title">${typeIcon} ${escapeHtml(item.title)}</div>
                    ${item.description ? `<div class="schedule-description">${escapeHtml(item.description)}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// ===== 偏好設定 =====

async function loadPreferences() {
    try {
        const response = await fetch('/api/preferences');
        state.preferences = await response.json();

        document.getElementById('wakeTime').value = state.preferences.wake_time || '07:00';
        document.getElementById('sleepTime').value = state.preferences.sleep_time || '23:00';
        document.getElementById('breakfastTime').value = state.preferences.breakfast_time || '07:30';
        document.getElementById('lunchTime').value = state.preferences.lunch_time || '12:00';
        document.getElementById('dinnerTime').value = state.preferences.dinner_time || '18:30';
        document.getElementById('bufferTime').value = state.preferences.buffer_time || 10;
    } catch (error) {
        console.error('載入設定失敗:', error);
    }
}

function toggleSettings() {
    const panel = elements.settingsPanel;
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
}

async function savePreferences() {
    const preferences = {
        wake_time: document.getElementById('wakeTime').value,
        sleep_time: document.getElementById('sleepTime').value,
        breakfast_time: document.getElementById('breakfastTime').value,
        lunch_time: document.getElementById('lunchTime').value,
        dinner_time: document.getElementById('dinnerTime').value,
        buffer_time: parseInt(document.getElementById('bufferTime').value)
    };

    try {
        const response = await fetch('/api/preferences', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(preferences)
        });

        if (response.ok) {
            showNotification('設定已儲存', 'success');
            state.preferences = preferences;
        }
    } catch (error) {
        showNotification('儲存失敗', 'error');
    }
}

// ===== 工具函數 =====

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getCategoryName(category) {
    const names = {
        'work': '工作',
        'study': '學習',
        'personal': '個人',
        'health': '健康',
        'other': '其他'
    };
    return names[category] || category;
}

function showNotification(message, type = 'info') {
    // 簡易通知（可以後續改用更好的通知套件）
    const colors = {
        'success': '#10b981',
        'error': '#ef4444',
        'info': '#3b82f6'
    };

    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 添加動畫樣式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);
