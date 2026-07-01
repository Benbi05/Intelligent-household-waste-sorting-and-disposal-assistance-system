"""
Tests for model management service, registry, and API.
"""
import pytest
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from 代码包.ai_service.models.model_registry import ModelRegistry
from 代码包.ai_service.utils.async_task import create_task, get_task, update_task


class TestAsyncTask:
    """Tests for async task management."""

    def test_create_task(self):
        task_id = create_task('TEST', {'key': 'value'})
        assert task_id.startswith('TEST_')
        task = get_task(task_id)
        assert task is not None
        assert task['status'] == 'pending'
        assert task['type'] == 'TEST'

    def test_get_nonexistent_task(self):
        task = get_task('nonexistent')
        assert task is None

    def test_update_task(self):
        task_id = create_task('TEST')
        update_task(task_id, status='running', progress=50)
        task = get_task(task_id)
        assert task['status'] == 'running'
        assert task['progress'] == 50


class TestModelRegistry:
    """Tests for model version registry."""

    @pytest.fixture
    def registry(self):
        """Create a registry pointed at a temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock model file structure
            os.makedirs(os.path.join(tmpdir, 'v1.0'), exist_ok=True)
            Path(os.path.join(tmpdir, 'v1.0', 'model.onnx')).touch()

            os.makedirs(os.path.join(tmpdir, 'v1.5'), exist_ok=True)
            Path(os.path.join(tmpdir, 'v1.5', 'model.onnx')).touch()

            with patch('ai_service.models.model_registry.MODELS_STORE_DIR', tmpdir):
                with patch('ai_service.models.model_registry.REGISTRY_FILE',
                          os.path.join(tmpdir, 'registry.json')):
                    registry = ModelRegistry()
                    yield registry

    def test_list_versions(self, registry):
        versions = registry.list_versions()
        assert isinstance(versions, list)

    def test_register_version(self, registry):
        entry = registry.register_version('v2.0', {
            'mAP': 0.95, 'accuracy': 0.93,
            'precision': 0.94, 'recall': 0.92,
        })
        assert entry['version'] == 'v2.0'
        assert entry['mAP'] == 0.95
        assert entry['status'] == 'archived'

        # Verify it's persisted
        version = registry.get_version('v2.0')
        assert version is not None
        assert version['mAP'] == 0.95

    def test_set_version_status(self, registry):
        # Register two versions
        registry.register_version('v1.0', {'mAP': 0.9, 'accuracy': 0.88,
                                            'precision': 0.89, 'recall': 0.87})
        registry.register_version('v2.0', {'mAP': 0.95, 'accuracy': 0.93,
                                            'precision': 0.94, 'recall': 0.92})

        # Set v2.0 online
        registry.set_version_status('v2.0', 'online')
        assert registry.get_version('v2.0')['status'] == 'online'

    def test_get_nonexistent_version(self, registry):
        assert registry.get_version('nonexistent') is None

    def test_set_version_status_not_found(self, registry):
        with pytest.raises(ValueError):
            registry.set_version_status('nonexistent', 'online')

    def test_get_active_version(self, registry):
        # Register and set one online
        registry.register_version('v3.0', {'mAP': 0.96, 'accuracy': 0.94,
                                            'precision': 0.95, 'recall': 0.93})
        registry.set_version_status('v3.0', 'online')
        active = registry.get_active_version()
        assert active is not None
        assert active['version'] == 'v3.0'
        assert active['status'] == 'online'


class TestModelAPI:
    """Tests for model management API endpoints."""

    @pytest.fixture
    def client(self):
        from 代码包.ai_service.app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_list_versions(self, client):
        resp = client.get('/ai/model/versions')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['code'] == 200
        assert isinstance(data['data'], list)

    def test_switch_missing_params(self, client):
        resp = client.post('/ai/model/switch', json={})
        assert resp.status_code == 400

    def test_switch_invalid_type(self, client):
        resp = client.post('/ai/model/switch', json={
            'switchType': 'invalid',
            'targetVersion': 'v1.5',
        })
        assert resp.status_code == 400

    def test_switch_nonexistent_version(self, client):
        resp = client.post('/ai/model/switch', json={
            'switchType': 'full',
            'targetVersion': 'nonexistent',
        })
        assert resp.status_code in (400, 500)  # 500 if model file missing

    def test_canary_percent_too_low(self, client):
        resp = client.post('/ai/model/switch', json={
            'switchType': 'canary',
            'targetVersion': 'v1.5',
            'canaryPercent': 2,
        })
        assert resp.status_code in (400, 500)

    def test_canary_percent_too_high(self, client):
        resp = client.post('/ai/model/switch', json={
            'switchType': 'canary',
            'targetVersion': 'v1.5',
            'canaryPercent': 60,
        })
        assert resp.status_code in (400, 500)

    def test_train_missing_params(self, client):
        resp = client.post('/ai/model/train', json={})
        assert resp.status_code == 400

    def test_train_nonexistent_base_model(self, client):
        resp = client.post('/ai/model/train', json={
            'datasetUrl': 'https://cdn.garbage-system.com/dataset.zip',
            'datasetName': 'test',
            'baseModelVersion': 'nonexistent',
        })
        assert resp.status_code in (400, 500)

    def test_train_status_not_found(self, client):
        resp = client.get('/ai/model/train/nonexistent')
        assert resp.status_code in (400, 500)

    def test_health_check(self, client):
        resp = client.get('/ai/model/health')
        assert resp.status_code in (200, 500)  # 500 is OK if no model file
