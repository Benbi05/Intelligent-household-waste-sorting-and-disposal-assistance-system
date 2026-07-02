"""Tests for recognition service: preprocess, postprocess, security."""
import pytest
from unittest.mock import patch
from ai_service.recognition.preprocess import validate_image_url, _is_internal_ip
from ai_service.recognition.postprocess import get_parent_type, get_guide, process_detections


class TestSecurity:
    def test_internal_ip_detection(self):
        assert _is_internal_ip('127.0.0.1') is True
        assert _is_internal_ip('192.168.1.1') is True
        assert _is_internal_ip('10.0.0.1') is True
        assert _is_internal_ip('172.16.0.1') is True

    @patch('ai_service.recognition.preprocess.socket.gethostbyname')
    def test_internal_ip_hostname(self, mock_dns):
        mock_dns.return_value = '192.168.1.1'
        assert _is_internal_ip('internal-server.local') is True

    @patch('ai_service.recognition.preprocess._is_internal_ip')
    def test_validate_image_url_valid(self, mock_ip):
        mock_ip.return_value = False
        ok, err = validate_image_url('https://cdn.garbage-system.com/images/test.jpg')
        assert ok is True

    def test_validate_image_url_non_http(self):
        ok, err = validate_image_url('ftp://cdn.garbage-system.com/test.jpg')
        assert ok is False

    def test_validate_image_url_not_whitelisted(self):
        ok, err = validate_image_url('https://evil.com/test.jpg')
        assert ok is False


class TestPostprocess:
    def test_get_parent_type_recyclable(self):
        pt_key, pt_name = get_parent_type(0)
        assert pt_key == 'recyclable'

    def test_get_parent_type_kitchen(self):
        pt_key, pt_name = get_parent_type(12)
        assert pt_key == 'kitchen'

    def test_get_parent_type_hazardous(self):
        pt_key, pt_name = get_parent_type(20)
        assert pt_key == 'hazardous'

    def test_get_parent_type_other(self):
        pt_key, pt_name = get_parent_type(28)
        assert pt_key == 'other'

    def test_get_guide_specific(self):
        guide = get_guide('塑料饮料瓶', 'recyclable')
        assert '清空内容物' in guide

    def test_get_guide_generic(self):
        guide = get_guide('未知', 'recyclable')
        assert '可回收物桶' in guide

    def test_process_detections(self):
        dets = [{'class_id': 0, 'class_name': '塑料饮料瓶', 'confidence': 0.96,
                 'boxRegion': {'x': 0.1, 'y': 0.2, 'width': 0.3, 'height': 0.4}}]
        result = process_detections(dets)
        assert len(result) == 1
        assert result[0]['parentType'] == 'recyclable'
        assert result[0]['parentTypeName'] == '可回收物'
        assert 'confidence' in result[0]
        assert 'guide' in result[0]


class TestRecognizeAPI:
    @pytest.fixture
    def client(self):
        from ai_service.recognition.app import app
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c

    def test_health(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200

    def test_recognize_missing_url(self, client):
        resp = client.post('/recognize', json={})
        assert resp.status_code == 400

    def test_recognize_invalid_url(self, client):
        resp = client.post('/recognize', json={'imageUrl': 'ftp://bad.com/x.jpg'})
        assert resp.status_code == 400

    def test_delivery_missing_params(self, client):
        resp = client.post('/recognize/delivery', json={})
        assert resp.status_code == 400
