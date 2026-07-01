"""
Tests for garbage recognition service, security utils, and category mapper.
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from 代码包.ai_service.utils.security import (
    validate_image_url,
    is_internal_ip,
    is_domain_whitelisted,
)
from 代码包.ai_service.models.category_mapper import CategoryMapper
from 代码包.ai_service.services.guide_service import GuideService


class TestSecurity:
    """Tests for SSRF protection and URL validation."""

    def test_whitelisted_domain(self):
        assert is_domain_whitelisted('cdn.garbage-system.com') is True
        assert is_domain_whitelisted('img.garbage-system.com') is True
        assert is_domain_whitelisted('evil.com') is False

    def test_internal_ip_detection(self):
        # Localhost
        assert is_internal_ip('127.0.0.1') is True
        # Private ranges
        assert is_internal_ip('192.168.1.1') is True
        assert is_internal_ip('10.0.0.1') is True
        assert is_internal_ip('172.16.0.1') is True

    @patch('ai_service.utils.security.socket.gethostbyname')
    def test_internal_ip_hostname(self, mock_gethostbyname):
        mock_gethostbyname.return_value = '192.168.1.1'
        assert is_internal_ip('internal-server.local') is True

    @patch('ai_service.utils.security.is_internal_ip')
    def test_validate_image_url_valid(self, mock_is_internal):
        mock_is_internal.return_value = False
        valid_url = 'https://cdn.garbage-system.com/images/test.jpg'
        is_valid, error = validate_image_url(valid_url)
        assert is_valid is True
        assert error == ''

    def test_validate_image_url_non_http(self):
        is_valid, error = validate_image_url('ftp://cdn.garbage-system.com/test.jpg')
        assert is_valid is False

    def test_validate_image_url_not_whitelisted(self):
        is_valid, error = validate_image_url('https://evil.com/test.jpg')
        assert is_valid is False
        assert error == 'URL_NOT_WHITELISTED'

    @patch('ai_service.utils.security.is_internal_ip')
    def test_validate_image_url_internal(self, mock_is_internal):
        mock_is_internal.return_value = True
        is_valid, error = validate_image_url('https://cdn.garbage-system.com/test.jpg')
        assert is_valid is False
        assert error == 'URL_INTERNAL_IP'


class TestCategoryMapper:
    """Tests for the category mapping system."""

    def test_get_known_category(self):
        mapper = CategoryMapper()
        cat = mapper.get_category(101)
        assert cat['categoryName'] == '塑料饮料瓶'
        assert cat['parentType'] == 'recyclable'
        assert cat['parentTypeName'] == '可回收物'

    def test_get_kitchen_category(self):
        mapper = CategoryMapper()
        cat = mapper.get_category(201)
        assert cat['parentType'] == 'kitchen'

    def test_get_hazardous_category(self):
        mapper = CategoryMapper()
        cat = mapper.get_category(301)
        assert cat['parentType'] == 'hazardous'

    def test_get_unknown_category(self):
        mapper = CategoryMapper()
        cat = mapper.get_category(99999)
        assert cat['parentType'] == 'other'
        assert '未知' in cat['categoryName']

    def test_get_class_name_map(self):
        mapper = CategoryMapper()
        name_map = mapper.get_class_name_map()
        assert isinstance(name_map, dict)
        assert name_map[101] == '塑料饮料瓶'

    def test_get_categories_by_parent(self):
        mapper = CategoryMapper()
        recyclables = mapper.get_categories_by_parent('recyclable')
        assert len(recyclables) > 0
        for cat in recyclables:
            assert cat['parentType'] == 'recyclable'

    def test_update_from_database(self):
        mapper = CategoryMapper()
        db_data = [
            {'id': 101, 'category_name': '塑料瓶', 'parent_type': 1},
            {'id': 201, 'category_name': '剩饭', 'parent_type': 2},
        ]
        mapper.update_from_database(db_data)
        assert mapper.get_category(101)['categoryName'] == '塑料瓶'
        assert mapper.get_category(201)['categoryName'] == '剩饭'


class TestGuideService:
    """Tests for disposal guide generation."""

    def test_category_specific_guide(self):
        svc = GuideService()
        guide = svc.get_guide(101, 'recyclable')
        assert '清空内容物' in guide

    def test_generic_guide(self):
        svc = GuideService()
        guide = svc.get_guide(999, 'recyclable')
        assert '可回收物桶' in guide

    def test_error_guide(self):
        svc = GuideService()
        guide = svc.get_guide_for_error('recyclable', 'kitchen')
        assert '错误' in guide
        assert '可回收物' in guide
        assert '厨余垃圾桶' in guide

    def test_voice_text_correct(self):
        svc = GuideService()
        text = svc.get_voice_text(True, 15, '塑料瓶', '可回收物')
        assert '正确' in text
        assert '+15' in text

    def test_voice_text_wrong(self):
        svc = GuideService()
        text = svc.get_voice_text(False, -5, '塑料瓶', '厨余垃圾桶')
        assert '错误' in text
        assert '-5' in text


class TestRecognitionService:
    """Tests for the recognition service pipeline."""

    @patch('ai_service.services.recognition_service.download_image')
    @patch('ai_service.services.recognition_service.is_image_blurry')
    @patch('ai_service.models.model_loader.ModelLoader.load_model')
    def test_recognize_no_detections(self, mock_load, mock_blur, mock_download):
        """Test that blurry/empty images raise appropriate error."""
        mock_download.return_value = (b'fake_image_bytes', '')
        mock_blur.return_value = True
        mock_load.return_value = MagicMock()

        from 代码包.ai_service.services.recognition_service import RecognitionService
        svc = RecognitionService()

        with pytest.raises(ValueError) as exc:
            svc.recognize_from_url('https://cdn.garbage-system.com/test.jpg')
        assert 'IMAGE_BLURRY' in str(exc.value)

    @patch('ai_service.services.recognition_service.download_image')
    @patch('ai_service.models.model_loader.ModelLoader.load_model')
    def test_recognize_url_not_whitelisted(self, mock_load, mock_download):
        """Test that non-whitelisted URLs are rejected."""
        mock_download.return_value = (b'', 'URL_NOT_WHITELISTED')
        mock_load.return_value = MagicMock()

        from 代码包.ai_service.services.recognition_service import RecognitionService
        svc = RecognitionService()

        with pytest.raises(ValueError) as exc:
            svc.recognize_from_url('https://evil.com/test.jpg')
        assert 'URL_NOT_WHITELISTED' in str(exc.value)


class TestRecognizeAPI:
    """Tests for the recognition API endpoints."""

    @pytest.fixture
    def client(self):
        from 代码包.ai_service.app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_recognize_missing_url(self, client):
        resp = client.post('/ai/recognize', json={})
        assert resp.status_code == 400

    def test_recognize_empty_url(self, client):
        resp = client.post('/ai/recognize', json={'imageUrl': ''})
        assert resp.status_code == 400

    def test_health_check(self, client):
        resp = client.get('/ai/recognize/health')
        # 200 if model loads, 500 if model file missing
        assert resp.status_code in (200, 500)

    def test_delivery_missing_params(self, client):
        resp = client.post('/ai/recognize/delivery', json={})
        assert resp.status_code == 400

    def test_delivery_invalid_category(self, client):
        resp = client.post('/ai/recognize/delivery', json={
            'imageUrl': 'https://cdn.garbage-system.com/test.jpg',
            'boxCategory': 'invalid',
        })
        assert resp.status_code == 400
