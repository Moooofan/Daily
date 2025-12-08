"""極簡版 Flask 應用程式"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import date, datetime, timedelta
from database_simple import SimpleDatabase
from ai_helper import AIHelper
from google_calendar_helper import GoogleCalendarHelper
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# 初始化
db = SimpleDatabase()
gcal = GoogleCalendarHelper()

# AI Helper 延遲初始化（避免啟動時缺少 API Key 導致錯誤）
ai = None

def get_ai():
    global ai
    if ai is None:
        try:
            ai = AIHelper()
        except Exception as e:
            print(f"⚠️ AI Helper 初始化失敗: {e}")
            return None
    return ai


@app.route('/')
def index():
    """首頁 - 需要 Google 登入"""
    # 檢查是否已經登入 Google
    if 'google_credentials' not in session:
        print("⚠️ 用戶尚未登入 Google，顯示登入頁面")
        return render_template('login.html')

    print("✅ 用戶已登入 Google，載入首頁")
    return render_template('index_simple.html')


# ===== 待辦事項 API =====

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """取得待辦事項（可選類型和日期篩選）"""
    todo_type = request.args.get('type')  # daily, weekly, monthly, quick
    target_date = request.args.get('target_date')  # YYYY-MM-DD
    todos = db.get_todos(todo_type, target_date)
    return jsonify(todos)


@app.route('/api/todos', methods=['POST'])
def add_todo():
    """新增待辦事項"""
    data = request.json
    todo_type = data.get('type', 'daily')  # 預設為日待辦
    todo_id = db.add_todo(data['content'], todo_type)
    return jsonify({'id': todo_id, 'success': True})


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """刪除待辦事項"""
    db.delete_todo(todo_id)
    return jsonify({'success': True})


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """更新待辦事項"""
    data = request.json
    db.update_todo(
        todo_id,
        content=data.get('content'),
        todo_type=data.get('type'),
        estimated_minutes=data.get('estimated_minutes')
    )
    return jsonify({'success': True})


@app.route('/api/todos/<int:todo_id>/toggle', methods=['POST'])
def toggle_todo_complete(todo_id):
    """切換待辦事項完成狀態"""
    db.toggle_todo_complete(todo_id)
    return jsonify({'success': True})


# ===== 排程 API =====

@app.route('/api/schedule/<date_str>', methods=['GET'])
def get_schedule(date_str):
    """取得指定日期的排程"""
    items = db.get_schedule(date_str)
    return jsonify(items)


@app.route('/api/schedule', methods=['POST'])
def add_schedule_item():
    """新增排程項目"""
    data = request.json
    item_id = db.add_schedule_item(
        data['date'],
        data['title'],
        data['start_time'],
        data['end_time']
    )
    return jsonify({'id': item_id, 'success': True})


@app.route('/api/schedule/<int:item_id>', methods=['PUT'])
def update_schedule_item(item_id):
    """更新排程項目"""
    data = request.json
    db.update_schedule_item(
        item_id,
        title=data.get('title'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time')
    )
    return jsonify({'success': True})


@app.route('/api/schedule/<int:item_id>', methods=['DELETE'])
def delete_schedule_item(item_id):
    """刪除排程項目"""
    db.delete_schedule_item(item_id)
    return jsonify({'success': True})


@app.route('/api/schedule/<int:item_id>/toggle', methods=['POST'])
def toggle_schedule_complete(item_id):
    """切換排程完成狀態"""
    db.toggle_schedule_complete(item_id)
    return jsonify({'success': True})


@app.route('/api/schedule/clear/<date_str>', methods=['DELETE'])
def clear_schedule(date_str):
    """清空指定日期的所有排程"""
    db.clear_schedule(date_str)
    return jsonify({'success': True, 'message': f'{date_str} 的排程已清空'})


# ===== AI 功能 API =====

@app.route('/api/ai/process-voice', methods=['POST'])
def process_voice():
    """處理語音輸入"""
    data = request.json
    text = data.get('text', '')

    try:
        ai_helper = get_ai()
        if not ai_helper:
            return jsonify({'success': False, 'error': 'AI 服務未設定'}), 500
        result = ai_helper.process_voice_input(text)

        # 去重處理：使用 dict 來過濾重複的 schedules
        seen_schedules = {}
        unique_schedules = []
        for schedule in result['schedules']:
            # 建立唯一鍵
            key = (
                schedule.get('date', date.today().isoformat()),
                schedule['title'],
                schedule['start_time'],
                schedule['end_time']
            )
            if key not in seen_schedules:
                seen_schedules[key] = True
                unique_schedules.append(schedule)

        # 更新為去重後的 schedules
        result['schedules'] = unique_schedules

        # 自動新增待辦事項(包含類型、預估時間和目標日期)
        for todo in result['todos']:
            if isinstance(todo, dict):
                # 新格式：包含 type、estimated_minutes 和 date
                db.add_todo(
                    todo['content'],
                    todo.get('type', 'daily'),
                    todo.get('estimated_minutes', 30),
                    todo.get('date')  # 可能是 None（不限定日期）或具體日期
                )
            else:
                # 舊格式：純字串（備案）
                db.add_todo(todo)

        # 自動新增排程（使用 AI 回傳的日期）
        for schedule in unique_schedules:
            schedule_date = schedule.get('date', date.today().isoformat())
            db.add_schedule_item(
                schedule_date,
                schedule['title'],
                schedule['start_time'],
                schedule['end_time']
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ai/generate-schedule', methods=['POST'])
def generate_schedule():
    """AI 生成排程"""
    data = request.json
    date_str = data.get('date', date.today().isoformat())
    current_time = data.get('current_time')  # 前端可以傳遞當前時間

    try:
        ai_helper = get_ai()
        if not ai_helper:
            return jsonify({'success': False, 'error': 'AI 服務未設定'}), 500

        # 只取得「日待辦」事項來生成排程
        # 週待辦、月待辦等使用者說有空時再手動加入
        todos = db.get_todos(todo_type='daily')
        uncompleted_todos = [t for t in todos if not t.get('completed')]

        # AI 生成排程（傳入完整待辦資訊，包含預計時間）
        schedule_items = ai_helper.generate_daily_schedule(uncompleted_todos, date_str, current_time)

        # 儲存到資料庫
        db.batch_add_schedule(date_str, schedule_items)

        return jsonify({
            'success': True,
            'schedule': schedule_items,
            'count': len(schedule_items)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ai/suggest-now', methods=['GET'])
def suggest_now():
    """AI 推薦現在可以做什麼"""
    from datetime import datetime

    try:
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        date_str = now.strftime('%Y-%m-%d')

        ai_helper = get_ai()
        if not ai_helper:
            return jsonify({'success': False, 'error': 'AI 服務未設定'}), 500

        # 取得今日排程和未完成待辦
        schedule = db.get_schedule(date_str)
        uncompleted_todos = db.get_uncompleted_todos_by_date()

        # 呼叫 AI Helper 的建議方法
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/delay/check', methods=['GET'])
def check_delays():
    """檢查延誤的排程"""
    try:
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        date_str = now.strftime('%Y-%m-%d')

        # 取得延誤的排程
        delayed_items = db.get_delayed_schedules(date_str, current_time)

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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/delay/suggest-reschedule', methods=['POST'])
def suggest_reschedule():
    """為延誤項目提供重排建議"""
    try:
        data = request.json
        date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))

        # 取得延誤項目
        current_time = datetime.now().strftime('%H:%M')
        delayed_items = db.get_delayed_schedules(date_str, current_time)

        if not delayed_items:
            return jsonify({
                'success': True,
                'message': '沒有延誤項目',
                'suggestions': []
            })

        ai_helper = get_ai()
        if not ai_helper:
            return jsonify({'success': False, 'error': 'AI 服務未設定'}), 500

        # 呼叫 AI 生成重排建議
        result = ai_helper.suggest_reschedule(delayed_items, date_str)

        return jsonify({
            'success': True,
            'suggestions': result['suggestions']
        })

    except Exception as e:
        print(f"❌ 重排建議錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/delay/apply-reschedule', methods=['POST'])
def apply_reschedule():
    """套用重排建議"""
    try:
        data = request.json
        item_id = data.get('item_id')
        action = data.get('action')  # 'today', 'tomorrow', 'cancel'
        new_time = data.get('time')  # 'HH:MM-HH:MM'

        if action == 'cancel':
            # 刪除排程項目
            db.delete_schedule_item(item_id)
            return jsonify({
                'success': True,
                'message': '已取消排程'
            })

        elif action == 'today':
            # 更新今天的時間
            start_time, end_time = new_time.split('-')
            db.update_schedule_item(item_id, start_time=start_time, end_time=end_time)
            return jsonify({
                'success': True,
                'message': '已更新為今日新時段'
            })

        elif action == 'tomorrow':
            # 移動到明天
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            start_time, end_time = new_time.split('-')
            db.move_schedule_to_date(item_id, tomorrow, start_time, end_time)
            return jsonify({
                'success': True,
                'message': '已移至明天'
            })

        else:
            return jsonify({
                'success': False,
                'error': '無效的操作'
            }), 400

    except Exception as e:
        print(f"❌ 套用重排錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== Google Calendar API =====

@app.route('/google/authorize')
def google_authorize():
    """開始 Google OAuth 授權流程"""
    try:
        authorization_url, state = gcal.get_authorization_url()
        session['google_auth_state'] = state
        return redirect(authorization_url)
    except Exception as e:
        print(f"❌ Google 授權錯誤: {type(e).__name__}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/google/logout')
def google_logout():
    """登出 Google 帳號"""
    if 'google_credentials' in session:
        session.pop('google_credentials')
        print("✅ 用戶已登出 Google")
    if 'google_auth_state' in session:
        session.pop('google_auth_state')
    return redirect('/')


@app.route('/oauth2callback')
def oauth2callback():
    """Google OAuth 回調"""
    try:
        # 取得授權碼
        code = request.args.get('code')
        if not code:
            return jsonify({
                'success': False,
                'error': '未收到授權碼'
            }), 400

        # 用授權碼交換憑證
        credentials = gcal.exchange_code_for_credentials(code)

        # 將憑證儲存到 session
        credentials_dict = gcal.credentials_to_dict(credentials)
        session['google_credentials'] = credentials_dict

        # 自動匯入未來 30 天的 Google Calendar 事件
        try:
            today = date.today()
            start_date = today.isoformat()
            end_date = (today + timedelta(days=30)).isoformat()

            print(f"📅 開始自動匯入 Google Calendar 事件 ({start_date} 到 {end_date})")

            # 取得未來 30 天的事件
            events = gcal.get_calendar_events_range(credentials_dict, start_date, end_date)

            # 匯入到資料庫
            imported_count = 0
            skipped_count = 0
            for event in events:
                try:
                    db.add_schedule_item(
                        event['date'],
                        event['title'],
                        event['start_time'],
                        event['end_time']
                    )
                    imported_count += 1
                except Exception as e:
                    # 忽略重複項目
                    skipped_count += 1
                    continue

            print(f"✅ 自動匯入完成：成功 {imported_count} 個，跳過 {skipped_count} 個重複項目")

        except Exception as import_error:
            print(f"⚠️ 自動匯入失敗（不影響授權）: {type(import_error).__name__}: {str(import_error)}")
            import traceback
            traceback.print_exc()

        # 重定向回首頁
        return redirect('/')

    except Exception as e:
        print(f"❌ OAuth 回調錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/google/events', methods=['GET'])
def get_google_events():
    """取得 Google Calendar 事件"""
    try:
        # 檢查是否已授權
        if 'google_credentials' not in session:
            return jsonify({
                'success': False,
                'error': '未授權',
                'need_auth': True
            }), 401

        # 取得日期參數
        date_str = request.args.get('date', date.today().isoformat())

        # 取得事件
        events = gcal.get_calendar_events(session['google_credentials'], date_str)

        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        })

    except Exception as e:
        print(f"❌ 取得 Google 事件錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/google/import', methods=['POST'])
def import_google_events():
    """匯入 Google Calendar 事件到排程"""
    try:
        # 檢查是否已授權
        if 'google_credentials' not in session:
            return jsonify({
                'success': False,
                'error': '未授權',
                'need_auth': True
            }), 401

        data = request.json
        date_str = data.get('date', date.today().isoformat())

        # 取得 Google Calendar 事件
        events = gcal.get_calendar_events(session['google_credentials'], date_str)

        # 匯入到資料庫
        imported_count = 0
        for event in events:
            try:
                db.add_schedule_item(
                    event['date'],
                    event['title'],
                    event['start_time'],
                    event['end_time']
                )
                imported_count += 1
            except Exception as e:
                # 忽略重複項目
                print(f"⚠️ 跳過事件: {event['title']} - {str(e)}")
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== 每日固定排程 API =====

@app.route('/api/routines', methods=['GET'])
def get_routines():
    """取得所有每日固定排程"""
    routines = db.get_routines()
    return jsonify(routines)


@app.route('/api/routines', methods=['POST'])
def add_routine():
    """新增每日固定排程"""
    data = request.json
    routine_id = db.add_routine(
        data['title'],
        data['start_time'],
        data['end_time']
    )
    return jsonify({'id': routine_id, 'success': True})


@app.route('/api/routines/<int:routine_id>', methods=['PUT'])
def update_routine(routine_id):
    """更新每日固定排程"""
    data = request.json
    db.update_routine(
        routine_id,
        title=data.get('title'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        enabled=data.get('enabled')
    )
    return jsonify({'success': True})


@app.route('/api/routines/<int:routine_id>', methods=['DELETE'])
def delete_routine(routine_id):
    """刪除每日固定排程"""
    db.delete_routine(routine_id)
    return jsonify({'success': True})


@app.route('/api/routines/<int:routine_id>/toggle', methods=['POST'])
def toggle_routine(routine_id):
    """切換每日固定排程的啟用狀態"""
    db.toggle_routine_enabled(routine_id)
    return jsonify({'success': True})


@app.route('/api/routines/apply', methods=['POST'])
def apply_routines():
    """將固定排程套用到指定日期"""
    data = request.json
    date_str = data.get('date', date.today().isoformat())
    added_count = db.apply_routines_to_date(date_str)
    return jsonify({
        'success': True,
        'added': added_count,
        'date': date_str
    })


if __name__ == '__main__':
    port = 5001
    print("=" * 60)
    print("Daily Schedule AI - 極簡版")
    print("=" * 60)
    print(f"開啟瀏覽器訪問: http://localhost:{port}")
    print("=" * 60)

    app.run(debug=Config.DEBUG, host='0.0.0.0', port=port)
