"""
Analysis API Blueprint
Provides endpoints for LLM-powered analysis report generation and retrieval.

Corresponding interface doc APIs:
  - API332: Admin analysis report (list & detail)
  - API408: Merchant analysis report
  - API409: Merchant operations dashboard
"""
from flask import Blueprint, request
from 代码包.ai_service.services.analysis_service import get_analysis_service
from 代码包.ai_service.utils.async_task import create_task, get_task, run_async
from 代码包.ai_service.utils.response import success, error, ai_error
from 代码包.ai_service.config import logger

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/analysis/generate', methods=['POST'])
def generate_report():
    """
    Trigger async analysis report generation.

    Request body (JSON):
        {
            "statMonth": "2026-06",
            "statArea": "全部区域",
            "reportType": "all",       // "all" | "governance" | "business"
            "statsData": { ... },      // aggregated statistics from backend
            "callbackUrl": "https://..."  // optional callback
        }

    Response:
        {
            "code": 200,
            "data": {
                "taskId": "ANALYSIS_abc123",
                "status": "pending"
            }
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return error('请求体不能为空', 400)

    stat_month = data.get('statMonth', '').strip()
    stat_area = data.get('statArea', '全部区域').strip()
    report_type = data.get('reportType', 'all').strip()
    stats_data = data.get('statsData', {})
    callback_url = data.get('callbackUrl', '').strip()

    if not stat_month:
        return error('缺少必填参数 statMonth', 400)
    if not stats_data:
        return error('缺少必填参数 statsData', 400)

    # Create async task
    task_id = create_task('ANALYSIS', {
        'statMonth': stat_month,
        'statArea': stat_area,
        'reportType': report_type,
    })

    # Run analysis async
    analysis_svc = get_analysis_service()

    if report_type == 'governance':
        func = lambda: analysis_svc.generate_governance_report(
            stats_data, stat_month, stat_area
        )
    elif report_type == 'business':
        func = lambda: analysis_svc.generate_business_report(
            stats_data, stat_month, stat_area
        )
    else:  # 'all'
        func = lambda: analysis_svc.generate_full_report(
            stats_data, stat_month, stat_area
        )

    run_async(task_id, func, callback_url=callback_url or None)

    logger.info(f'Analysis task created: {task_id} ({report_type})')
    return success({
        'taskId': task_id,
        'status': 'pending',
        'estimatedTime': 60,
    }, '分析报告生成任务已创建')


@analysis_bp.route('/analysis/report/<report_id>', methods=['GET'])
def get_report(report_id):
    """
    Get a generated analysis report by task ID.
    If task is complete, returns the full report data.
    """
    task = get_task(report_id)
    if task is None:
        return ai_error('REPORT_NOT_FOUND', f'报告 {report_id} 不存在')

    if task['status'] == 'pending' or task['status'] == 'running':
        return success({
            'taskId': task['taskId'],
            'status': task['status'],
            'progress': task.get('progress', 0),
        }, '报告生成中')

    if task['status'] == 'failed':
        return error(
            f'报告生成失败: {task.get("errorMessage", "未知错误")}',
            500,
        )

    # Task completed — return report
    result = task.get('result', {})
    return success(result, '查询成功')


@analysis_bp.route('/analysis/report/merchant', methods=['POST'])
def generate_merchant_report():
    """
    Generate a merchant-specific business analysis report.

    Request body: similar to /analysis/generate but returns merchant-tailored content.
    """
    data = request.get_json(silent=True)
    if not data:
        return error('请求体不能为空', 400)

    stat_month = data.get('statMonth', '').strip()
    stat_area = data.get('statArea', '').strip()
    stats_data = data.get('statsData', {})

    if not stat_month or not stat_area:
        return error('缺少必填参数 statMonth 和 statArea', 400)
    if not stats_data:
        return error('缺少必填参数 statsData', 400)

    # Merchant reports are faster, can be synchronous for smaller datasets
    try:
        service = get_analysis_service()
        result = service.generate_merchant_report(stats_data, stat_month, stat_area)
        return success(result, '查询成功')
    except Exception as e:
        logger.error(f'Merchant report generation error: {e}', exc_info=True)
        return error(f'报告生成失败: {str(e)}', 500)


@analysis_bp.route('/analysis/dashboard/merchant', methods=['POST'])
def merchant_dashboard():
    """
    Get merchant operations dashboard data.
    Returns real-time stats for the merchant operations view.

    Request body (JSON):
        {
            "merchantId": 1,
            "statArea": "A区"
        }

    Response includes:
        - consumeTrend
        - hotProducts
        - categoryBreakdown
        - suggestion
    """
    data = request.get_json(silent=True)
    if not data:
        return error('请求体不能为空', 400)

    merchant_id = data.get('merchantId')
    stat_area = data.get('statArea', '').strip()
    stats_data = data.get('statsData', {})

    if not merchant_id:
        return error('缺少必填参数 merchantId', 400)

    # Generate merchant dashboard with stats
    try:
        service = get_analysis_service()
        from datetime import datetime

        current_month = datetime.now().strftime('%Y-%m')
        result = service.generate_merchant_report(
            stats_data, current_month, stat_area
        )
        return success(result, '查询成功')
    except Exception as e:
        logger.error(f'Dashboard error: {e}', exc_info=True)
        return error(f'获取看板数据失败: {str(e)}', 500)


@analysis_bp.route('/analysis/health', methods=['GET'])
def analysis_health():
    """Health check for analysis service."""
    return success(None, 'Analysis service healthy')
