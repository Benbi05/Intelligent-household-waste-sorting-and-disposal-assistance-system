"""
Model Version Registry
Manages model versions, metrics, and deployment state.
Tracks mAP, accuracy, precision, recall per version.
"""
import json
import os
import threading
from typing import Optional
from datetime import datetime, timezone, timedelta
from 代码包.ai_service.config import MODELS_STORE_DIR, CANARY_CONFIG, ACTIVE_MODEL_VERSION, logger

TZ_BEIJING = timezone(timedelta(hours=8))

# Model registry file path
REGISTRY_FILE = os.path.join(MODELS_STORE_DIR, 'registry.json')


class ModelRegistry:
    """
    Registry of all model versions with their metadata and metrics.
    Thread-safe with read/write lock.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._versions: dict[str, dict] = {}
        self._load_from_disk()

    def _load_from_disk(self):
        """Load registry from disk if exists."""
        if os.path.exists(REGISTRY_FILE):
            try:
                with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._versions = data.get('versions', {})
                logger.info(f'Loaded {len(self._versions)} model versions from registry')
            except Exception as e:
                logger.warning(f'Failed to load registry: {e}')
                self._versions = {}
        else:
            # Initialize with default version if model file exists
            self._init_default_registry()

    def _init_default_registry(self):
        """Create initial registry entry from available model files."""
        for version_dir in os.listdir(MODELS_STORE_DIR):
            version_path = os.path.join(MODELS_STORE_DIR, version_dir)
            model_file = os.path.join(version_path, 'model.onnx')
            if os.path.isdir(version_path) and os.path.exists(model_file):
                self._versions[version_dir] = {
                    'modelId': len(self._versions) + 1,
                    'version': version_dir,
                    'mAP': 0.0,
                    'accuracy': 0.0,
                    'precision': 0.0,
                    'recall': 0.0,
                    'categoryCount': 50,
                    'status': 'online' if version_dir == ACTIVE_MODEL_VERSION else 'archived',
                    'publishTime': datetime.now(TZ_BEIJING).isoformat(),
                    'modelPath': model_file,
                }
        self._save_to_disk()

    def _save_to_disk(self):
        """Persist registry to disk."""
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump({'versions': self._versions, 'updatedAt': datetime.now(TZ_BEIJING).isoformat()},
                      f, ensure_ascii=False, indent=2)

    def list_versions(self) -> list[dict]:
        """Get all model versions sorted by publish time (newest first)."""
        with self._lock:
            versions = list(self._versions.values())
            versions.sort(key=lambda v: v.get('publishTime', ''), reverse=True)
            return versions

    def get_version(self, version: str) -> Optional[dict]:
        """Get a specific version's metadata."""
        with self._lock:
            return self._versions.get(version)

    def get_active_version(self) -> Optional[dict]:
        """Get the currently active (online) version."""
        with self._lock:
            for v in self._versions.values():
                if v.get('status') == 'online':
                    return v
            return None

    def register_version(self, version: str, metrics: dict,
                         category_count: int = 50) -> dict:
        """
        Register a new model version (e.g., after training completes).

        Args:
            version: version string, e.g., 'v1.6'
            metrics: {'mAP': float, 'accuracy': float, 'precision': float, 'recall': float}
            category_count: number of supported categories
        """
        with self._lock:
            model_id = len(self._versions) + 1
            entry = {
                'modelId': model_id,
                'version': version,
                'mAP': metrics.get('mAP', 0.0),
                'accuracy': metrics.get('accuracy', 0.0),
                'precision': metrics.get('precision', 0.0),
                'recall': metrics.get('recall', 0.0),
                'categoryCount': category_count,
                'status': 'archived',  # new versions start as archived until switched
                'publishTime': datetime.now(TZ_BEIJING).isoformat(),
                'modelPath': os.path.join(MODELS_STORE_DIR, version, 'model.onnx'),
            }
            self._versions[version] = entry
            self._save_to_disk()
            logger.info(f'Registered new model version: {version}')
            return entry

    def set_version_status(self, version: str, status: str):
        """
        Update a version's status.
        status: 'online' | 'archived' | 'training' | 'failed'
        """
        with self._lock:
            if version not in self._versions:
                raise ValueError(f'Version not found: {version}')

            # If setting to 'online', archive the current online version
            if status == 'online':
                for v in self._versions.values():
                    if v.get('status') == 'online':
                        v['status'] = 'archived'

            self._versions[version]['status'] = status
            self._save_to_disk()
            logger.info(f'Model {version} status set to: {status}')

    def update_metrics(self, version: str, metrics: dict):
        """Update evaluation metrics for a version."""
        with self._lock:
            if version not in self._versions:
                raise ValueError(f'Version not found: {version}')
            for key in ['mAP', 'accuracy', 'precision', 'recall']:
                if key in metrics:
                    self._versions[version][key] = metrics[key]
            self._save_to_disk()


# Global singleton
_registry: Optional[ModelRegistry] = None


def get_model_registry() -> ModelRegistry:
    """Get or create the global ModelRegistry singleton."""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
