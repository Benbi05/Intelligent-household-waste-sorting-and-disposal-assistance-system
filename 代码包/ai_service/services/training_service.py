"""
Incremental Training Service
Manages model training tasks: dataset validation, training trigger, status tracking.
"""
from typing import Optional
import os
import time
import uuid
import zipfile
import json
from 代码包.ai_service.config import MODELS_STORE_DIR, ASYNC_CONFIG, logger
from 代码包.ai_service.models.model_registry import get_model_registry
from 代码包.ai_service.utils.async_task import create_task, get_task, update_task, run_async, TaskStatus


class TrainingService:
    """
    Manages incremental model training lifecycle:
    1. Validate uploaded dataset (YOLO format)
    2. Trigger training (async)
    3. Track status
    4. Register new model version on completion
    """

    def __init__(self):
        self.registry = get_model_registry()
        self._training_tasks: dict[str, dict] = {}

    def validate_dataset(self, dataset_url: str, dataset_name: str) -> tuple[bool, str]:
        """
        Validate an uploaded dataset for YOLO training format.

        Checks:
        - Dataset zip can be accessed
        - Contains images/ and labels/ directories
        - Labels are in YOLO format (.txt files with class_id x y w h)
        - classes.txt or data.yaml present

        Returns:
            (is_valid, error_message)
        """
        try:
            import requests
            import tempfile

            # Download dataset zip for validation
            logger.info(f'Downloading dataset for validation: {dataset_name}')
            response = requests.get(dataset_url, timeout=300, stream=True)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                for chunk in response.iter_content(8192):
                    tmp.write(chunk)
                tmp_path = tmp.name

            # Validate zip contents
            with zipfile.ZipFile(tmp_path, 'r') as zf:
                file_list = zf.namelist()

                # Check for required directories/files
                has_images = any('images/' in f for f in file_list)
                has_labels = any('labels/' in f for f in file_list)
                has_classes = any(f.endswith('classes.txt') for f in file_list)
                has_data_yaml = any(f.endswith('data.yaml') for f in file_list)

                if not has_images:
                    return False, '数据集缺少 images/ 目录'
                if not has_labels:
                    return False, '数据集缺少 labels/ 目录'
                if not has_classes and not has_data_yaml:
                    return False, '数据集缺少 classes.txt 或 data.yaml 配置文件'

                # Validate a few label files
                label_files = [f for f in file_list if f.endswith('.txt') and 'labels/' in f]
                for label_file in label_files[:5]:
                    content = zf.read(label_file).decode('utf-8').strip()
                    if content:
                        for line in content.split('\n')[:3]:
                            parts = line.strip().split()
                            if len(parts) != 5:
                                return False, f'标注格式错误: {label_file} 中行 "{line[:50]}..." 应为5列'
                            try:
                                [float(p) for p in parts]
                            except ValueError:
                                return False, f'标注格式错误: {label_file} 中坐标非数字'

                logger.info(f'Dataset validation passed: {len(label_files)} label files')
                return True, ''

        except requests.RequestException as e:
            return False, f'数据集下载失败: {e}'
        except zipfile.BadZipFile:
            return False, '数据集文件不是有效的ZIP格式'
        except Exception as e:
            logger.error(f'Dataset validation error: {e}')
            return False, f'数据集校验异常: {e}'
        finally:
            if 'tmp_path' in dir():
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    def trigger_training(self, dataset_url: str, dataset_name: str,
                         base_model_version: str,
                         callback_url: str = '') -> str:
        """
        Validate dataset and trigger asynchronous training.

        Args:
            dataset_url: URL to the dataset zip file
            dataset_name: Human-readable name
            base_model_version: Version to fine-tune from
            callback_url: URL to call on completion

        Returns:
            task_id for status tracking
        """
        # 1. Validate dataset
        is_valid, error_msg = self.validate_dataset(dataset_url, dataset_name)
        if not is_valid:
            raise ValueError(f'TRAIN_DATASET_INVALID: {error_msg}')

        # 2. Create async task
        task_id = create_task('TRAIN', {
            'datasetUrl': dataset_url,
            'datasetName': dataset_name,
            'baseModelVersion': base_model_version,
        })

        # 3. Run training async
        run_async(
            task_id,
            self._execute_training,
            dataset_url, dataset_name, base_model_version,
            callback_url=callback_url,
        )

        logger.info(f'Training task started: {task_id}')
        return task_id

    def get_training_status(self, task_id: str) -> Optional[dict]:
        """Get training task current status."""
        task = get_task(task_id)
        if task is None:
            return None

        return {
            'taskId': task['taskId'],
            'status': task['status'],
            'progress': task.get('progress', 0),
            'estimatedRemain': task.get('estimatedRemain'),
            'errorMessage': task.get('errorMessage'),
        }

    def _execute_training(self, dataset_url: str, dataset_name: str,
                          base_model_version: str) -> dict:
        """
        Execute the training pipeline.
        This is a placeholder that simulates training progress.
        In production, this would call a training script or ML pipeline.
        """
        logger.info(f'Starting training: {dataset_name} based on {base_model_version}')

        # Simulate training progress (in production: call YOLO training script)
        total_steps = 10
        for step in range(1, total_steps + 1):
            time.sleep(2)  # Simulate work
            progress = step / total_steps * 100
            logger.info(f'Training progress: {progress:.0f}%')

        # Generate new version
        current_versions = self.registry.list_versions()
        if current_versions:
            latest = current_versions[0]['version']  # e.g., 'v1.5'
            major, minor = latest.lstrip('v').split('.')
            new_version = f'v{major}.{int(minor) + 1}'
        else:
            new_version = 'v1.1'

        # Simulated metrics (in production: from validation set evaluation)
        metrics = {
            'mAP': 0.94,
            'accuracy': 0.93,
            'precision': 0.94,
            'recall': 0.91,
        }

        # Register new version
        self.registry.register_version(new_version, metrics)

        logger.info(f'Training complete: new model {new_version}')
        return {
            'newModelVersion': new_version,
            'modelId': self.registry.get_version(new_version)['modelId'],
            **metrics,
        }


# Singleton
_training_service: Optional[TrainingService] = None


def get_training_service() -> TrainingService:
    global _training_service
    if _training_service is None:
        _training_service = TrainingService()
    return _training_service
