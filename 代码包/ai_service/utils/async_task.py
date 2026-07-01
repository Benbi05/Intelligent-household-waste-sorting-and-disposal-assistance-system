"""
Async Task Manager
Handles long-running tasks (model training, analysis report generation) with:
- Thread pool execution
- Status tracking
- Callback notification
"""
from typing import Optional
import threading
import uuid
import time
import requests
from datetime import datetime, timezone, timedelta
from 代码包.ai_service.config import ASYNC_CONFIG, logger

TZ_BEIJING = timezone(timedelta(hours=8))

# In-memory task store (use Redis in production)
_tasks: dict[str, dict] = {}
_lock = threading.Lock()


class TaskStatus:
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'


def _now_iso() -> str:
    return datetime.now(TZ_BEIJING).isoformat()


def create_task(task_type: str, metadata: dict = None) -> str:
    """Create a new async task and return its ID."""
    task_id = f'{task_type}_{uuid.uuid4().hex[:12]}'
    with _lock:
        _tasks[task_id] = {
            'taskId': task_id,
            'type': task_type,
            'status': TaskStatus.PENDING,
            'progress': 0,
            'metadata': metadata or {},
            'result': None,
            'errorMessage': None,
            'createdAt': _now_iso(),
            'updatedAt': _now_iso(),
        }
    logger.info(f'Async task created: {task_id}')
    return task_id


def get_task(task_id: str) -> Optional[dict]:
    """Get task status by ID."""
    return _tasks.get(task_id)


def update_task(task_id: str, **kwargs):
    """Update task fields."""
    with _lock:
        if task_id in _tasks:
            _tasks[task_id].update(kwargs)
            _tasks[task_id]['updatedAt'] = _now_iso()


def run_async(task_id: str, func, *args, callback_url: str = None, **kwargs):
    """
    Run a function asynchronously in a thread pool.
    Updates task status on completion and optionally calls a callback URL.
    """
    def _runner():
        update_task(task_id, status=TaskStatus.RUNNING, progress=0)
        try:
            result = func(*args, **kwargs)
            update_task(
                task_id,
                status=TaskStatus.SUCCESS,
                progress=100,
                result=result,
            )
            logger.info(f'Async task completed: {task_id}')

            # Callback notification
            if callback_url:
                _send_callback(callback_url, task_id, TaskStatus.SUCCESS, result)

        except Exception as e:
            logger.error(f'Async task failed: {task_id}, error: {e}')
            update_task(
                task_id,
                status=TaskStatus.FAILED,
                errorMessage=str(e),
            )

            if callback_url:
                _send_callback(callback_url, task_id, TaskStatus.FAILED, {'error': str(e)})

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    return thread


def _send_callback(callback_url: str, task_id: str, status: str, result: dict):
    """Send callback notification with retries."""
    payload = {
        'taskId': task_id,
        'status': status,
        'result': result,
        'completeTime': _now_iso(),
    }

    max_retries = ASYNC_CONFIG['callback_retry_count']
    delays = ASYNC_CONFIG['callback_retry_delays']

    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(
                callback_url,
                json=payload,
                timeout=30,
                headers={
                    'Content-Type': 'application/json',
                    'X-Callback-Signature': _generate_signature(payload),
                },
            )
            if resp.status_code == 200:
                logger.info(f'Callback succeeded: {callback_url}')
                return
            else:
                logger.warning(f'Callback returned {resp.status_code}: {callback_url}')
        except requests.RequestException as e:
            logger.warning(f'Callback attempt {attempt + 1} failed: {e}')

        if attempt < max_retries:
            delay = delays[min(attempt, len(delays) - 1)]
            time.sleep(delay)

    logger.error(f'All callback retries exhausted for {task_id}')


def _generate_signature(payload: dict) -> str:
    """Generate HMAC signature for callback authentication."""
    import hmac
    import hashlib
    import json
    secret = 'garbage-system-callback-secret'  # Should be from config/env
    message = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
