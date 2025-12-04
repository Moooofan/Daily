"""Flask 主應用程式"""
from flask import Flask, render_template, request, jsonify, redirect, session
from datetime import date, datetime
from database import Database
from scheduler import AIScheduler
from google_cal import GoogleCalendarClient
from config import Config
import os

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# 初始化組件
db = Database(Config.DATABASE_PATH)
scheduler = AIScheduler()
google_cal = GoogleCalendarClient()


# ===== 網頁路由 =====

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')


# ===== API 端點 =====

# ----- 任務管理 -----

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """取得所有任務"""
    tasks = db.get_tasks()
    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """新增任務"""
    data = request.json
    task_id = db.add_task(
        title=data.get('title'),
        duration=data.get('duration', 30),
        priority=data.get('priority', 0),
        category=data.get('category', 'other'),
        is_routine=data.get('is_routine', False),
        preferred_time=data.get('preferred_time')
    )
    return jsonify({'id': task_id, 'success': True})


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任務"""
    data = request.json
    db.update_task(task_id, **data)
    return jsonify({'success': True})


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """刪除任務"""
    db.delete_task(task_id)
    return jsonify({'success': True})


# ----- 排程管理 -----

@app.route('/api/schedule/generate', methods=['POST'])
def generate_schedule():
    """生成排程"""
    data = request.json
    target_date_str = data.get('date')

    if target_date_str:
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    else:
        target_date = date.today()

    # 取得資料
    tasks = db.get_tasks()
    preferences = db.get_preferences()

    # 取得 Google Calendar 事件（如果已連接）
    calendar_events = []
    if google_cal.load_credentials():
        calendar_events = google_cal.get_events(target_date)

    # 生成排程
    try:
        schedule = scheduler.generate_schedule(
            tasks=tasks,
            calendar_events=calendar_events,
            preferences=preferences,
            target_date=target_date
        )

        # 儲存排程
        db.save_schedule(target_date, schedule)

        return jsonify({
            'success': True,
            'schedule': schedule,
            'date': target_date.isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/schedule/<date_str>', methods=['GET'])
def get_schedule(date_str):
    """取得指定日期的排程"""
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        schedule = db.get_schedule(target_date)

        if schedule:
            return jsonify({
                'success': True,
                'schedule': schedule,
                'date': date_str
            })
        else:
            return jsonify({
                'success': False,
                'message': '尚未生成該日期的排程'
            }), 404

    except ValueError:
        return jsonify({
            'success': False,
            'error': '日期格式錯誤'
        }), 400


# ----- Google Calendar 整合 -----

@app.route('/api/google/auth-url', methods=['GET'])
def get_google_auth_url():
    """取得 Google OAuth 授權 URL"""
    try:
        auth_url = google_cal.get_authorization_url()
        return jsonify({
            'success': True,
            'auth_url': auth_url
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/oauth2callback')
def oauth2callback():
    """Google OAuth 回調"""
    code = request.args.get('code')

    if not code:
        return "授權失敗：未收到授權碼", 400

    if google_cal.handle_oauth_callback(code):
        return redirect('/?auth=success')
    else:
        return redirect('/?auth=failed')


@app.route('/api/google/status', methods=['GET'])
def google_status():
    """檢查 Google Calendar 連接狀態"""
    is_connected = google_cal.load_credentials()
    return jsonify({
        'connected': is_connected
    })


@app.route('/api/google/events', methods=['GET'])
def get_google_events():
    """取得 Google Calendar 事件"""
    date_str = request.args.get('date')

    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = date.today()

    if not google_cal.load_credentials():
        return jsonify({
            'success': False,
            'error': '未連接 Google Calendar'
        }), 401

    events = google_cal.get_events(target_date)
    return jsonify({
        'success': True,
        'events': events
    })


@app.route('/api/google/disconnect', methods=['POST'])
def disconnect_google():
    """中斷 Google Calendar 連接"""
    google_cal.disconnect()
    return jsonify({'success': True})


# ----- 偏好設定 -----

@app.route('/api/preferences', methods=['GET'])
def get_preferences():
    """取得使用者偏好設定"""
    preferences = db.get_preferences()
    return jsonify(preferences)


@app.route('/api/preferences', methods=['PUT'])
def update_preferences():
    """更新使用者偏好設定"""
    data = request.json
    db.update_preferences(**data)
    return jsonify({'success': True})


# ===== 啟動應用 =====

if __name__ == '__main__':
    port = 5001  # 使用 5001 避免與 AirPlay Receiver 衝突
    print("=" * 60)
    print("Daily Schedule AI 正在啟動...")
    print("=" * 60)
    print(f"開啟瀏覽器訪問: http://localhost:{port}")
    print("=" * 60)

    app.run(debug=Config.DEBUG, host='0.0.0.0', port=port)
