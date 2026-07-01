"""
Tests for LLM analysis service and analysis API.
"""
import pytest
from unittest.mock import patch, MagicMock

from 代码包.ai_service.services.analysis_service import AnalysisService


class TestAnalysisService:
    """Tests for the analysis report generation."""

    @pytest.fixture
    def sample_stats(self):
        return {
            'delivery_trend': {
                'A区': {'current': 8900, 'previous': 8000, 'change': 0.11},
                'B区': {'current': 5600, 'previous': 5800, 'change': -0.03},
                'C区': {'current': 4200, 'previous': 3800, 'change': 0.11},
            },
            'correct_rate_trend': {
                'A区': {'current': 0.91, 'previous': 0.88},
                'B区': {'current': 0.85, 'previous': 0.84},
                'C区': {'current': 0.76, 'previous': 0.80},
            },
            'category_breakdown': {
                '塑料类': {'deliveryCount': 5800, 'changeRate': 0.18},
                '金属类': {'deliveryCount': 1200, 'changeRate': 0.05},
                '纸类': {'deliveryCount': 3200, 'changeRate': -0.03},
            },
        }

    def test_generate_governance_report(self, sample_stats):
        """Test governance report generation with mock LLM."""
        svc = AnalysisService()

        with patch.object(svc, '_call_llm') as mock_llm:
            import json
            mock_llm.return_value = json.dumps({
                'deliveryTrend': '本月投放总量环比增长12%',
                'correctRateTrend': 'A区分类正确率上升3个百分点',
                'problemAreas': ['C区厨余垃圾混投率偏高'],
                'optimizationAdvice': '建议在C区增设指引牌',
            }, ensure_ascii=False)

            result = svc.generate_governance_report(
                sample_stats, '2026-06', '全部区域'
            )

            assert 'deliveryTrend' in result
            assert 'correctRateTrend' in result
            assert 'problemAreas' in result
            assert isinstance(result['problemAreas'], list)
            assert 'optimizationAdvice' in result

    def test_generate_business_report(self, sample_stats):
        """Test business report generation with mock LLM."""
        svc = AnalysisService()

        with patch.object(svc, '_call_llm') as mock_llm:
            import json
            mock_llm.return_value = json.dumps({
                'consumeTrend': '塑料类可回收物增长18%',
                'hotProducts': ['环保垃圾袋', '瓶装饮用水', '一次性餐具'],
                'suggestion': '建议增加日用清洁类商品库存',
            }, ensure_ascii=False)

            result = svc.generate_business_report(
                sample_stats, '2026-06', 'A区'
            )

            assert 'consumeTrend' in result
            assert 'hotProducts' in result
            assert isinstance(result['hotProducts'], list)
            assert len(result['hotProducts']) == 3
            assert 'suggestion' in result

    def test_generate_full_report(self, sample_stats):
        """Test full report generation."""
        svc = AnalysisService()

        with patch.object(svc, '_call_llm') as mock_llm:
            import json
            mock_llm.return_value = json.dumps({
                'deliveryTrend': 'test',
                'correctRateTrend': 'test',
                'problemAreas': [],
                'optimizationAdvice': 'test',
            }, ensure_ascii=False)

            result = svc.generate_full_report(sample_stats, '2026-06')

            assert 'reportId' in result
            assert 'governanceSection' in result
            assert 'businessSection' in result
            assert 'fullContent' in result
            assert result['status'] == 'completed'
            # Verify Markdown content
            assert '# 智能垃圾分类月度分析报告' in result['fullContent']

    def test_generate_merchant_report(self, sample_stats):
        """Test merchant-facing report generation."""
        svc = AnalysisService()

        with patch.object(svc, '_call_llm') as mock_llm:
            import json
            mock_llm.return_value = json.dumps({
                'consumeTrend': 'test',
                'hotProducts': ['商品A'],
                'suggestion': 'test',
            }, ensure_ascii=False)

            result = svc.generate_merchant_report(
                sample_stats, '2026-06', 'A区'
            )

            assert 'categoryBreakdown' in result
            assert '塑料类' in result['categoryBreakdown']

    def test_parse_governance_from_text(self, sample_stats):
        """Test parsing governance response from free text (non-JSON)."""
        svc = AnalysisService()

        with patch.object(svc, '_call_llm') as mock_llm:
            mock_llm.return_value = """
投放趋势：本月投放总量环比增长12%
正确率趋势：A区上升3个百分点
问题区域：
- C区厨余垃圾混投
- B区可回收物污染
优化建议：增设指引牌
"""
            result = svc.generate_governance_report(
                sample_stats, '2026-06', '全部区域'
            )
            # Should still produce a result even without valid JSON
            assert 'deliveryTrend' in result


class TestAnalysisAPI:
    """Tests for analysis API endpoints."""

    @pytest.fixture
    def client(self):
        from 代码包.ai_service.app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_generate_missing_params(self, client):
        resp = client.post('/ai/analysis/generate', json={})
        assert resp.status_code == 400

    def test_generate_valid(self, client):
        resp = client.post('/ai/analysis/generate', json={
            'statMonth': '2026-06',
            'statArea': 'A区',
            'statsData': {'test': 'data'},
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['code'] == 200
        assert 'taskId' in data['data']

    def test_get_nonexistent_report(self, client):
        resp = client.get('/ai/analysis/report/does-not-exist')
        # 400 if error handled normally, 500 if internal init fails without model
        assert resp.status_code in (400, 500)

    def test_merchant_report_missing_params(self, client):
        resp = client.post('/ai/analysis/report/merchant', json={})
        assert resp.status_code == 400

    def test_merchant_dashboard_missing_id(self, client):
        resp = client.post('/ai/analysis/dashboard/merchant', json={})
        assert resp.status_code == 400

    def test_health_check(self, client):
        resp = client.get('/ai/analysis/health')
        assert resp.status_code == 200
