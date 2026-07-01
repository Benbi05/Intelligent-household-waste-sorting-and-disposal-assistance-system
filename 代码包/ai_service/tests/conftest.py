"""
Pytest configuration and fixtures for AI service tests.
"""
import os
import sys
import pytest

# Ensure ai_service is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset global singletons before each test for isolation."""
    import 代码包.ai_service.services.recognition_service as rs
    import 代码包.ai_service.services.analysis_service as analysis_svc
    import 代码包.ai_service.services.guide_service as gs
    import 代码包.ai_service.services.training_service as ts
    import 代码包.ai_service.models.model_loader as ml
    import 代码包.ai_service.models.category_mapper as cm
    import 代码包.ai_service.models.model_registry as mr

    rs._recognition_service = None
    analysis_svc._analysis_service = None
    gs._guide_service = None
    ts._training_service = None
    ml._model_loader = None
    cm._category_mapper = None
    mr._registry = None

    yield
