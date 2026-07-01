"""Tests for LLM analysis service."""
import pytest
from ai_service.llm.generator import generate_governance_report, generate_business_report
from ai_service.llm.formatter import build_full_report, build_merchant_report


class TestLLMGenerator:
    def test_generate_governance_report(self):
        stats = {'total_deliveries': 100, 'delivery_trend': {'A区': {'total': 50}}}
        result = generate_governance_report(stats, '2026-06', '全部区域')
        assert 'deliveryTrend' in result
        assert 'correctRateTrend' in result
        assert 'problemAreas' in result
        assert isinstance(result['problemAreas'], list)
        assert 'optimizationAdvice' in result
        assert 'generateDuration' in result

    def test_generate_business_report(self):
        stats = {'total_orders': 50}
        result = generate_business_report(stats, '2026-06', 'A区')
        assert 'consumeTrend' in result
        assert 'hotProducts' in result
        assert isinstance(result['hotProducts'], list)
        assert 'suggestion' in result

    def test_formatter_full_report(self):
        gov = {'deliveryTrend': 'test trend', 'correctRateTrend': 'test rate',
               'problemAreas': ['problem1'], 'optimizationAdvice': 'test advice'}
        biz = {'consumeTrend': 'test consume', 'hotProducts': ['p1', 'p2'], 'suggestion': 'test sug'}
        full = build_full_report('2026-06', '全部区域', gov, biz, {})
        assert '# 智能垃圾分类月度分析报告' in full
        assert 'test trend' in full
        assert 'p1' in full

    def test_formatter_merchant_report(self):
        biz = {'consumeTrend': 'trend', 'hotProducts': ['p1'], 'suggestion': 'sug'}
        report = build_merchant_report('2026-06', 'A区', biz, {})
        assert '# 商家运营分析报告' in report


class TestLLMAPI:
    @pytest.fixture
    def client(self):
        from ai_service.llm.app import app
        app.config['TESTING'] = True
        with app.test_client() as c:
            yield c

    def test_health(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200

    def test_generate_missing_month(self, client):
        resp = client.post('/analysis/generate', json={})
        assert resp.status_code == 400

    def test_generate_valid(self, client):
        resp = client.post('/analysis/generate', json={
            'statMonth': '2026-06', 'statsData': {'test': 1}
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'taskId' in data['data']

    def test_get_nonexistent_report(self, client):
        resp = client.get('/analysis/report/nonexistent')
        assert resp.status_code == 400
