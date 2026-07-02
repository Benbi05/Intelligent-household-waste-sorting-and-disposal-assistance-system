"""LLM分析报告服务"""
import uuid, threading
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify
from .generator import generate_governance_report, generate_business_report
from .formatter import build_full_report, build_merchant_report
from .preprocessor import prepare_governance_data, prepare_business_data

TZ = timezone(timedelta(hours=8))
app = Flask(__name__)

# 异步任务存储
_tasks: dict = {}
_lock = threading.Lock()


def _now():
    return datetime.now(TZ).isoformat()


def _ok(data=None, msg='操作成功'):
    return jsonify({'code': 200, 'message': msg, 'data': data, 'timestamp': _now()})


def _err(msg, code=400):
    return jsonify({'code': code, 'message': msg, 'data': None, 'timestamp': _now()}), 400


@app.route('/health', methods=['GET'])
def health():
    return _ok({'status': 'healthy', 'provider': __import__('os').environ.get('LLM_PROVIDER', 'mock')})


@app.route('/analysis/generate', methods=['POST'])
def generate():
    """触发异步分析报告生成

    Request: {"statMonth":"2026-06","statArea":"全部区域","reportType":"all",
              "statsData":{...}, "deliveryRecords":[...], "pointRecords":[...]}
    """
    body = request.get_json(silent=True) or {}
    stat_month = (body.get('statMonth') or '').strip()
    stat_area = body.get('statArea', '全部区域').strip()
    report_type = body.get('reportType', 'all').strip()
    stats_data = body.get('statsData', {})
    callback_url = body.get('callbackUrl', '').strip()

    if not stat_month:
        return _err('缺少 statMonth')

    task_id = 'ANALYSIS_' + uuid.uuid4().hex[:12].upper()
    with _lock:
        _tasks[task_id] = {'taskId': task_id, 'status': 'pending', 'progress': 0,
                           'createdAt': _now()}

    def _run():
        with _lock:
            _tasks[task_id]['status'] = 'running'
        try:
            gov = generate_governance_report(stats_data, stat_month, stat_area) if report_type in ('all', 'governance') else {}
            biz = generate_business_report(stats_data, stat_month, stat_area) if report_type in ('all', 'business') else {}
            if report_type == 'all':
                full = build_full_report(stat_month, stat_area, gov, biz, stats_data)
            elif report_type == 'business':
                full = build_merchant_report(stat_month, stat_area, biz, stats_data)
            else:
                full = f'# 治理分析报告\n\n{gov.get("deliveryTrend","")}'

            result = {
                'reportId': 'RPT' + stat_month.replace('-', '') + uuid.uuid4().hex[:3].upper(),
                'statMonth': stat_month, 'statArea': stat_area,
                'reportType': report_type, 'status': 'completed',
                'governanceSection': gov if report_type in ('all', 'governance') else None,
                'businessSection': biz if report_type in ('all', 'business') else None,
                'fullContent': full,
                'generateTime': _now(),
                'generateDuration': gov.get('generateDuration', 0) + biz.get('generateDuration', 0),
            }
            with _lock:
                _tasks[task_id].update({'status': 'completed', 'progress': 100, 'result': result})
            if callback_url:
                import requests
                try:
                    requests.post(callback_url, json={'taskId': task_id, 'status': 'success', 'result': result}, timeout=30)
                except Exception:
                    pass
        except Exception as e:
            with _lock:
                _tasks[task_id].update({'status': 'failed', 'errorMessage': str(e)})

    threading.Thread(target=_run, daemon=True).start()
    return _ok({'taskId': task_id, 'status': 'pending', 'estimatedTime': 60}, '报告生成任务已创建')


@app.route('/analysis/report/<task_id>', methods=['GET'])
def get_report(task_id):
    """查询报告状态/结果"""
    task = _tasks.get(task_id)
    if not task:
        return _err('报告不存在', 3403)
    if task['status'] in ('pending', 'running'):
        return _ok({'taskId': task['taskId'], 'status': task['status'], 'progress': task.get('progress', 0)}, '生成中')
    if task['status'] == 'failed':
        return _err(f'生成失败: {task.get("errorMessage", "")}', 500)
    return _ok(task['result'], '查询成功')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083, debug=False)
