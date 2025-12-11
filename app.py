"""極簡版 Flask 應用程式 - 支援多用戶"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import date, datetime, timedelta
from database import SimpleDatabase
from ai_helper import AIHelper
from google_calendar_helper import GoogleCalendarHelper
from config import Config
import os

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# 初始化資料庫
db = SimpleDatabase()

# Google Calendar Helper 延遲初始化
_gcal = None

def get_gcal():
    global _gcal
    if _gcal is None:
        _gcal = GoogleCalendarHelper()
    return _gcal

# AI Helper 延遲初始化
_ai = None

def get_ai():
    global _ai
    if _ai is None:
        try:
            _ai = AIHelper()
        except Exception as e:
            print(f"⚠️ AI Helper 初始化失敗: {e}")
            return None
    return _ai


# ===== 用戶輔助函數 =====

def get_current_user_id():
    """取得當前登入用戶的 ID"""
    return session.get('user_id')

def get_current_user():
    """取得當前登入用戶的完整資訊"""
    user_id = get_current_user_id()
    if user_id:
        return db.get_user_by_id(user_id)
    return None

def is_admin():
    """檢查當前用戶是否為管理員"""
    user = get_current_user()
    return user and user.get('is_admin')

def admin_required(f):
    """管理員權限裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            return jsonify({'success': False, 'error': '需要管理員權限'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ===== 健康檢查端點 =====

@app.route('/health')
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })


@app.route('/')
def index():
    """首頁 - 需要 Google 登入"""
    if 'google_credentials' not in session or 'user_id' not in session:
        return render_template('login.html')
    return render_template('index.html')


# ===== 待辦事項 API =====

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """取得待辦事項"""
    user_id = get_current_user_id()
    todo_type = request.args.get('type')
    target_date = request.args.get('target_date')
    todos = db.get_todos(todo_type, target_date, user_id=user_id)
    return jsonify(todos)


@app.route('/api/todos', methods=['POST'])
def add_todo():
    """新增待辦事項"""
    user_id = get_current_user_id()
    data = request.json
    todo_type = data.get('type', 'daily')
    target_date = data.get('target_date')
    todo_id = db.add_todo(data['content'], todo_type, target_date=target_date, user_id=user_id)
    return jsonify({'id': todo_id, 'success': True})


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """刪除待辦事項"""
    user_id = get_current_user_id()
    db.delete_todo(todo_id, user_id=user_id)
    return jsonify({'success': True})


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """更新待辦事項"""
    user_id = get_current_user_id()
    data = request.json
    db.update_todo(
        todo_id,
        content=data.get('content'),
        todo_type=data.get('type'),
        estimated_minutes=data.get('estimated_minutes'),
        user_id=user_id
    )
    return jsonify({'success': True})


@app.route('/api/todos/<int:todo_id>/toggle', methods=['POST'])
def toggle_todo_complete(todo_id):
    """切換待辦事項完成狀態"""
    user_id = get_current_user_id()
    db.toggle_todo_complete(todo_id, user_id=user_id)
    return jsonify({'success': True})


# ===== 排程 API =====

@app.route('/api/schedule/<date_str>', methods=['GET'])
def get_schedule(date_str):
    """取得指定日期的排程"""
    user_id = get_current_user_id()
    items = db.get_schedule(date_str, user_id=user_id)
    return jsonify(items)


@app.route('/api/schedule', methods=['POST'])
def add_schedule_item():
    """新增排程項目"""
    user_id = get_current_user_id()
    data = request.json
    item_id = db.add_schedule_item(
        data['date'],
        data['title'],
        data['start_time'],
        data['end_time'],
        user_id=user_id
    )
    return jsonify({'id': item_id, 'success': True})


@app.route('/api/schedule/<int:item_id>', methods=['PUT'])
def update_schedule_item(item_id):
    """更新排程項目"""
    user_id = get_current_user_id()
    data = request.json
    db.update_schedule_item(
        item_id,
        title=data.get('title'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        user_id=user_id
    )
    return jsonify({'success': True})


@app.route('/api/schedule/<int:item_id>', methods=['DELETE'])
def delete_schedule_item(item_id):
    """刪除排程項目"""
    user_id = get_current_user_id()
    db.delete_schedule_item(item_id, user_id=user_id)
    return jsonify({'success': True})


@app.route('/api/schedule/<int:item_id>/toggle', methods=['POST'])
def toggle_schedule_complete(item_id):
    """切換排程完成狀態"""
    user_id = get_current_user_id()
    db.toggle_schedule_complete(item_id, user_id=user_id)
    return jsonify({'success': True})


@app.route('/api/schedule/clear/<date_str>', methods=['DELETE'])
def clear_schedule(date_str):
    """清空指定日期的所有排程"""
    user_id = get_current_user_id()
    db.clear_schedule(date_str, user_id=user_id)
    return jsonify({'success': True, 'message': f'{date_str} 的排程已清空'})


# ===== AI 功能 API =====

@app.route('/api/ai/process-voice', methods=['POST'])
def process_voice():
    """處理語音輸入"""
    user_id = get_current_user_id()
    data = request.json
    text = data.get('text', '')

    try:
        ai_helper = get_ai()
        if not ai_helper:
            return jsonify({'success': False, 'error': 'AI 服務未設定'}), 500
        result = ai_helper.process_voice_input(text)

        # 去重處理
        seen_schedules = {}
        unique_schedules = []
        for schedule in result['schedules']:
            key = (
                schedule.get('date', date.today().isoformat()),
                schedule['title'],
                schedule['start_time'],
                schedule['end_time']
            )
            if key not in seen_schedules:
                seen_schedules[key] = True
                unique_schedules.append(schedule)

        result['schedules'] = unique_schedules

        # 自動新增待辦事項
        for todo in result['todos']:
            if isinstance(todo, dict):
                db.add_todo(
                    todo['content'],
                    todo.get('type', 'daily'),
                    todo.get('estimated_minutes', 30),
                    todo.get('date'),
                    user_id=user_id
                )
            else:
                db.add_todo(todo, user_id=user_id)

        # 自動新增排程
        for schedule in unique_schedules:
            schedule_date = schedule.get('date', date.today().isoformat())
            db.add_schedule_item(
                schedule_date,
                schedule['title'],
                schedule['start_time'],
                schedule['end_time'],
                user_id=user_id
            )

        return jsonify({
            'success': True,
            'todos_added': len(result['todos']),
            'schedules_added': len(result['schedules']),
            'result': result
        })

    except Exception as e:
        print(f"❌ AI 處理語音錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/generate-schedule', methods=['POST'])
def generate_schedule():
    """AI 生成排程"""
    user_id = get_current_user_id()
    data = request.json
    date_str = data.get('date', date.today().isoformat())
    current_time = data.get('current_time')

    try:
        ai_helper = get_ai()
        if not ai_helper:
            return jsonify({'success': False, 'error': 'AI 服務未設定'}), 500

        todos = db.get_todos(todo_type='daily', user_id=user_id)
        uncompleted_todos = [t for t in todos if not t.get('completed')]

        schedule_items = ai_helper.generate_daily_schedule(uncompleted_todos, date_str, current_time)
        db.batch_add_schedule(date_str, schedule_items, user_id=user_id)

        return jsonify({
            'success': True,
            'schedule': schedule_items,
            'count': len(schedule_items)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ai/suggest-now', methods=['GET'])
def suggest_now():
    """AI 推薦現在可以做什麼"""
    user_id = get_current_user_id()

    try:
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        date_str = now.strftime('%Y-%m-%d')

        ai_helper = get_ai()
        if not ai_helper:
            return jsonify({'success': False, 'error': 'AI 服務未設定'}), 500

        schedule = db.get_schedule(date_str, user_id=user_id)
        uncompleted_todos = db.get_uncompleted_todos_by_date(user_id=user_id)

        result = ai_helper.suggest_now_activity(schedule, uncompleted_todos, current_time)

        return jsonify({
            'success': True,
            'suggestion': result['suggestion'],
            'reason': result['reason'],
            'available_minutes': result['available_minutes'],
            'current_time': current_time
        })

    except Exception as e:
        print(f"❌ 建議活動錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delay/check', methods=['GET'])
def check_delays():
    """檢查延誤的排程"""
    user_id = get_current_user_id()
    try:
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        date_str = now.strftime('%Y-%m-%d')

        delayed_items = db.get_delayed_schedules(date_str, current_time, user_id=user_id)

        return jsonify({
            'success': True,
            'delayed_count': len(delayed_items),
            'delayed_items': delayed_items,
            'current_time': current_time
        })

    except Exception as e:
        print(f"❌ 檢查延誤錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delay/suggest-reschedule', methods=['POST'])
def suggest_reschedule():
    """為延誤項目提供重排建議"""
    user_id = get_current_user_id()
    try:
        data = request.json
        date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))

        current_time = datetime.now().strftime('%H:%M')
        delayed_items = db.get_delayed_schedules(date_str, current_time, user_id=user_id)

        if not delayed_items:
            return jsonify({
                'success': True,
                'message': '沒有延誤項目',
                'suggestions': []
            })

        ai_helper = get_ai()
        if not ai_helper:
            return jsonify({'success': False, 'error': 'AI 服務未設定'}), 500

        result = ai_helper.suggest_reschedule(delayed_items, date_str)

        return jsonify({
            'success': True,
            'suggestions': result['suggestions']
        })

    except Exception as e:
        print(f"❌ 重排建議錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/delay/apply-reschedule', methods=['POST'])
def apply_reschedule():
    """套用重排建議"""
    user_id = get_current_user_id()
    try:
        data = request.json
        item_id = data.get('item_id')
        action = data.get('action')
        new_time = data.get('time')

        if action == 'cancel':
            db.delete_schedule_item(item_id, user_id=user_id)
            return jsonify({'success': True, 'message': '已取消排程'})

        elif action == 'today':
            start_time, end_time = new_time.split('-')
            db.update_schedule_item(item_id, start_time=start_time, end_time=end_time, user_id=user_id)
            return jsonify({'success': True, 'message': '已更新為今日新時段'})

        elif action == 'tomorrow':
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            start_time, end_time = new_time.split('-')
            db.move_schedule_to_date(item_id, tomorrow, start_time, end_time, user_id=user_id)
            return jsonify({'success': True, 'message': '已移至明天'})

        else:
            return jsonify({'success': False, 'error': '無效的操作'}), 400

    except Exception as e:
        print(f"❌ 套用重排錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== Google Calendar API =====

@app.route('/api/google/config-status')
def google_config_status():
    """檢查 Google Calendar API 是否已設定"""
    gcal = get_gcal()
    return jsonify({
        'configured': gcal.is_configured(),
        'logged_in': 'google_credentials' in session
    })


@app.route('/google/authorize')
def google_authorize():
    """開始 Google OAuth 授權流程"""
    try:
        gcal = get_gcal()
        if not gcal.is_configured():
            return render_template('login.html', error='Google Calendar API 尚未設定，請聯繫管理員')

        authorization_url, state = gcal.get_authorization_url()
        session['google_auth_state'] = state
        return redirect(authorization_url)
    except Exception as e:
        print(f"❌ Google 授權錯誤: {type(e).__name__}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/google/logout')
def google_logout():
    """登出 Google 帳號"""
    session.clear()
    return redirect('/')


@app.route('/oauth2callback')
def oauth2callback():
    """Google OAuth 回調"""
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({'success': False, 'error': '未收到授權碼'}), 400

        # 用授權碼交換憑證
        credentials = get_gcal().exchange_code_for_credentials(code)
        credentials_dict = get_gcal().credentials_to_dict(credentials)
        session['google_credentials'] = credentials_dict

        # 取得用戶資訊
        try:
            user_info = get_gcal().get_user_info(credentials)
            google_id = user_info.get('id')
            email = user_info.get('email')
            name = user_info.get('name')
            picture = user_info.get('picture')

            # 建立或更新用戶
            user = db.get_or_create_user(google_id, email, name, picture)
            session['user_id'] = user['id']

            # 檢查是否為管理員（根據 Email）
            if email in Config.ADMIN_EMAILS and not user.get('is_admin'):
                db.set_user_admin(user['id'], True)
                print(f"✅ 已設定 {email} 為管理員")

            print(f"✅ 用戶登入成功: {name} ({email})")

        except Exception as user_error:
            print(f"⚠️ 取得用戶資訊失敗: {user_error}")
            # 即使取不到用戶資訊，也讓用戶繼續使用（向後相容）

        # 自動匯入 Google Calendar 事件
        user_id = session.get('user_id')
        try:
            today = date.today()
            start_date = today.isoformat()
            end_date = (today + timedelta(days=30)).isoformat()

            print(f"📅 開始自動匯入 Google Calendar 事件")
            events = get_gcal().get_calendar_events_range(credentials_dict, start_date, end_date)

            imported_count = 0
            for event in events:
                try:
                    db.add_schedule_item(
                        event['date'],
                        event['title'],
                        event['start_time'],
                        event['end_time'],
                        user_id=user_id
                    )
                    imported_count += 1
                except:
                    continue

            print(f"✅ 自動匯入完成：{imported_count} 個事件")

        except Exception as import_error:
            print(f"⚠️ 自動匯入失敗: {import_error}")

        return redirect('/')

    except Exception as e:
        print(f"❌ OAuth 回調錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/google/events', methods=['GET'])
def get_google_events():
    """取得 Google Calendar 事件"""
    try:
        if 'google_credentials' not in session:
            return jsonify({'success': False, 'error': '未授權', 'need_auth': True}), 401

        date_str = request.args.get('date', date.today().isoformat())
        events = get_gcal().get_calendar_events(session['google_credentials'], date_str)

        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        })

    except Exception as e:
        print(f"❌ 取得 Google 事件錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/google/import', methods=['POST'])
def import_google_events():
    """匯入 Google Calendar 事件到排程"""
    user_id = get_current_user_id()
    try:
        if 'google_credentials' not in session:
            return jsonify({'success': False, 'error': '未授權', 'need_auth': True}), 401

        data = request.json
        date_str = data.get('date', date.today().isoformat())

        events = get_gcal().get_calendar_events(session['google_credentials'], date_str)

        imported_count = 0
        for event in events:
            try:
                db.add_schedule_item(
                    event['date'],
                    event['title'],
                    event['start_time'],
                    event['end_time'],
                    user_id=user_id
                )
                imported_count += 1
            except:
                continue

        return jsonify({
            'success': True,
            'imported': imported_count,
            'total': len(events)
        })

    except Exception as e:
        print(f"❌ 匯入 Google 事件錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== 每日固定排程 API =====

@app.route('/api/routines', methods=['GET'])
def get_routines():
    """取得所有每日固定排程"""
    user_id = get_current_user_id()
    routines = db.get_routines(user_id=user_id)
    return jsonify(routines)


@app.route('/api/routines', methods=['POST'])
def add_routine():
    """新增每日固定排程"""
    user_id = get_current_user_id()
    data = request.json
    routine_id = db.add_routine(
        data['title'],
        data['start_time'],
        data['end_time'],
        user_id=user_id
    )
    return jsonify({'id': routine_id, 'success': True})


@app.route('/api/routines/<int:routine_id>', methods=['PUT'])
def update_routine(routine_id):
    """更新每日固定排程"""
    user_id = get_current_user_id()
    data = request.json
    db.update_routine(
        routine_id,
        title=data.get('title'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        enabled=data.get('enabled'),
        user_id=user_id
    )
    return jsonify({'success': True})


@app.route('/api/routines/<int:routine_id>', methods=['DELETE'])
def delete_routine(routine_id):
    """刪除每日固定排程"""
    user_id = get_current_user_id()
    db.delete_routine(routine_id, user_id=user_id)
    return jsonify({'success': True})


@app.route('/api/routines/<int:routine_id>/toggle', methods=['POST'])
def toggle_routine(routine_id):
    """切換每日固定排程的啟用狀態"""
    user_id = get_current_user_id()
    db.toggle_routine_enabled(routine_id, user_id=user_id)
    return jsonify({'success': True})


@app.route('/api/routines/apply', methods=['POST'])
def apply_routines():
    """將固定排程套用到指定日期"""
    user_id = get_current_user_id()
    data = request.json
    date_str = data.get('date', date.today().isoformat())
    added_count = db.apply_routines_to_date(date_str, user_id=user_id)
    return jsonify({
        'success': True,
        'added': added_count,
        'date': date_str
    })


@app.route('/api/routines/<int:routine_id>/exclude', methods=['POST'])
def exclude_routine_for_date(routine_id):
    """將固定排程從指定日期排除"""
    user_id = get_current_user_id()
    data = request.json
    date_str = data.get('date', date.today().isoformat())

    db.add_routine_exception(routine_id, date_str, user_id=user_id)
    db.delete_schedule_by_routine(routine_id, date_str, user_id=user_id)

    return jsonify({
        'success': True,
        'message': f'已將固定排程從 {date_str} 排除'
    })


@app.route('/api/routines/<int:routine_id>/restore', methods=['POST'])
def restore_routine_for_date(routine_id):
    """恢復固定排程到指定日期"""
    user_id = get_current_user_id()
    data = request.json
    date_str = data.get('date', date.today().isoformat())

    db.remove_routine_exception(routine_id, date_str, user_id=user_id)

    routines = db.get_routines(user_id=user_id)
    routine = next((r for r in routines if r['id'] == routine_id), None)

    if routine and routine.get('enabled'):
        db.add_schedule_item(
            date_str,
            routine['title'],
            routine['start_time'],
            routine['end_time'],
            routine_id=routine['id'],
            user_id=user_id
        )

    return jsonify({
        'success': True,
        'message': f'已恢復固定排程到 {date_str}'
    })


@app.route('/api/routines/exceptions/<date_str>', methods=['GET'])
def get_routine_exceptions(date_str):
    """取得指定日期的固定排程例外列表"""
    user_id = get_current_user_id()
    exceptions = db.get_routine_exceptions(date_str, user_id=user_id)
    return jsonify({
        'success': True,
        'exceptions': exceptions,
        'date': date_str
    })


# ===== 管理員 API =====

@app.route('/admin')
def admin_page():
    """管理員後台頁面"""
    if not is_admin():
        return redirect('/')
    return render_template('admin.html')


@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    """取得管理員統計資料"""
    stats = db.get_admin_stats()
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    """取得所有用戶列表"""
    users = db.get_all_users()
    return jsonify({'success': True, 'users': users})


@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def admin_get_user_data(user_id):
    """取得特定用戶的資料"""
    data = db.get_user_data(user_id)
    return jsonify({'success': True, 'data': data})


@app.route('/api/admin/users/<int:user_id>/admin', methods=['POST'])
@admin_required
def admin_toggle_user_admin(user_id):
    """切換用戶管理員權限"""
    data = request.json
    is_admin_flag = data.get('is_admin', False)
    db.set_user_admin(user_id, is_admin_flag)
    return jsonify({'success': True})


@app.route('/api/user/info', methods=['GET'])
def get_user_info():
    """取得當前用戶資訊"""
    user = get_current_user()
    if user:
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'name': user.get('name'),
                'email': user.get('email'),
                'picture': user.get('picture'),
                'is_admin': user.get('is_admin', False)
            }
        })
    return jsonify({'success': False, 'error': '未登入'}), 401


if __name__ == '__main__':
    port = 5001
    print("=" * 60)
    print("Daily Schedule AI - 多用戶版")
    print("=" * 60)
    print(f"開啟瀏覽器訪問: http://localhost:{port}")
    print("=" * 60)

    app.run(debug=Config.DEBUG, host='0.0.0.0', port=port)
