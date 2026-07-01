"""
ONNX Runtime Model Loader
Handles loading, caching, and unloading YOLOv11 ONNX models.
Supports CPU/GPU execution providers and model hot-switching.
"""
import os
import threading
import time
import numpy as np
import onnxruntime as ort
from typing import Optional
from 代码包.ai_service.config import (
    ONNX_CONFIG, MODEL_INPUT_SIZE, MODELS_STORE_DIR,
    ACTIVE_MODEL_VERSION, CANARY_CONFIG, logger,
)


class ModelLoader:
    """
    Loads and manages ONNX Runtime inference sessions.
    Supports multi-version model registry with hot-switch capability.
    """

    def __init__(self):
        self._sessions: dict[str, ort.InferenceSession] = {}
        self._lock = threading.RLock()
        self._model_metadata: dict[str, dict] = {}

        # Configure ONNX Runtime session options
        self._session_options = ort.SessionOptions()
        opt_level_str = f'ORT_{ONNX_CONFIG["graph_optimization_level"].upper()}'
        self._session_options.graph_optimization_level = getattr(
            ort.GraphOptimizationLevel, opt_level_str, ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        )
        self._session_options.inter_op_num_threads = ONNX_CONFIG['inter_op_num_threads']
        self._session_options.intra_op_num_threads = ONNX_CONFIG['intra_op_num_threads']
        self._session_options.enable_profiling = ONNX_CONFIG['enable_profiling']

        # Execution provider
        self._providers = [ONNX_CONFIG['execution_provider']]
        # Add CPU as fallback
        if 'CPUExecutionProvider' not in self._providers:
            self._providers.append('CPUExecutionProvider')

    def get_model_path(self, version: str) -> str:
        """Get the ONNX model file path for a given version."""
        model_dir = os.path.join(MODELS_STORE_DIR, version)
        model_path = os.path.join(model_dir, 'model.onnx')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f'Model file not found: {model_path}')
        return model_path

    def load_model(self, version: str) -> ort.InferenceSession:
        """
        Load a specific model version into an ONNX Runtime session.
        Uses caching — returns existing session if already loaded.
        """
        with self._lock:
            if version in self._sessions:
                logger.info(f'Model {version} already loaded (cache hit)')
                return self._sessions[version]

            model_path = self.get_model_path(version)
            logger.info(f'Loading model {version} from {model_path}')

            start_time = time.time()
            session = ort.InferenceSession(
                model_path,
                sess_options=self._session_options,
                providers=self._providers,
            )
            load_time = time.time() - start_time

            self._sessions[version] = session
            self._model_metadata[version] = {
                'version': version,
                'path': model_path,
                'load_time_ms': round(load_time * 1000),
                'input_name': session.get_inputs()[0].name,
                'input_shape': session.get_inputs()[0].shape,
                'output_names': [o.name for o in session.get_outputs()],
                'loaded_at': time.time(),
            }

            logger.info(
                f'Model {version} loaded in {load_time * 1000:.0f}ms, '
                f'input: {self._model_metadata[version]["input_name"]}, '
                f'outputs: {self._model_metadata[version]["output_names"]}'
            )
            return session

    def unload_model(self, version: str):
        """Unload a model version from memory."""
        with self._lock:
            if version in self._sessions:
                del self._sessions[version]
                self._model_metadata.pop(version, None)
                logger.info(f'Model {version} unloaded')

    def get_active_session(self) -> ort.InferenceSession:
        """
        Get the currently active inference session.
        Supports canary (grayscale) deployment — routes a percentage
        of traffic to the canary model version.
        """
        # Canary routing
        if CANARY_CONFIG.get('enabled') and CANARY_CONFIG.get('canary_version'):
            import random
            if random.random() * 100 < CANARY_CONFIG['canary_percent']:
                canary_version = CANARY_CONFIG['canary_version']
                try:
                    return self.load_model(canary_version)
                except Exception as e:
                    logger.error(f'Canary model {canary_version} failed, falling back: {e}')

        # Default: active version
        return self.load_model(ACTIVE_MODEL_VERSION)

    def run_inference(self, preprocessed_image: np.ndarray,
                      version: str = None) -> list[np.ndarray]:
        """
        Run inference on a preprocessed image.

        Args:
            preprocessed_image: numpy array shape (1, 3, H, W), float32, normalized
            version: optional model version override

        Returns:
            List of output arrays from the model
        """
        if version:
            session = self.load_model(version)
        else:
            session = self.get_active_session()

        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: preprocessed_image})
        return outputs

    def get_loaded_versions(self) -> list[str]:
        """Return list of currently loaded model versions."""
        with self._lock:
            return list(self._sessions.keys())

    def get_model_info(self, version: str) -> Optional[dict]:
        """Get metadata for a loaded model version."""
        return self._model_metadata.get(version)

    def health_check(self) -> dict:
        """Check if the model loader is healthy."""
        try:
            session = self.get_active_session()
            return {
                'status': 'healthy',
                'active_version': ACTIVE_MODEL_VERSION,
                'loaded_versions': self.get_loaded_versions(),
                'providers': session.get_providers(),
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
            }


# Global singleton
_model_loader: Optional[ModelLoader] = None
_loader_lock = threading.Lock()


def get_model_loader() -> ModelLoader:
    """Get or create the global ModelLoader singleton."""
    global _model_loader
    if _model_loader is None:
        with _loader_lock:
            if _model_loader is None:
                _model_loader = ModelLoader()
                # Pre-load the active model
                try:
                    _model_loader.load_model(ACTIVE_MODEL_VERSION)
                except FileNotFoundError:
                    logger.warning(
                        f'Active model {ACTIVE_MODEL_VERSION} not found at '
                        f'{MODELS_STORE_DIR}. Model files must be placed before use.'
                    )
    return _model_loader
