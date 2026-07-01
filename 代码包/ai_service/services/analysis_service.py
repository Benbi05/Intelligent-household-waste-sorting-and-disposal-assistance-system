"""
LLM Analysis Service
Generates governance and business analysis reports using large language models.
Supports monthly statistical analysis, consumption trend prediction,
hot product recommendations, and optimization advice.
"""
import os
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Optional
from 代码包.ai_service.config import LLM_CONFIG, PROMPTS_DIR, ASYNC_CONFIG, logger

TZ_BEIJING = timezone(timedelta(hours=8))


class AnalysisService:
    """
    LLM-powered analysis service for governance and business intelligence.
    Uses prompt templates to generate structured analysis reports.
    """

    def __init__(self):
        self._governance_prompt = self._load_prompt('governance_analysis.txt')
        self._business_prompt = self._load_prompt('business_analysis.txt')

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt template from file."""
        prompt_path = os.path.join(PROMPTS_DIR, filename)
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        logger.warning(f'Prompt template not found: {prompt_path}, using default')
        return ''

    def generate_governance_report(self, stats_data: dict,
                                    stat_month: str,
                                    stat_area: str = '全部区域') -> dict:
        """
        Generate a governance analysis report.

        Args:
            stats_data: Aggregated statistics including:
                - delivery_trend: monthly delivery counts by area
                - correct_rate_trend: classification accuracy by area
                - category_breakdown: waste type distribution
                - problem_areas: identified problem regions
            stat_month: Report period, e.g., '2026-06'
            stat_area: Target area, default all

        Returns:
            Dict with governance section content
        """
        start_time = time.time()

        # Build prompt
        prompt = self._build_governance_prompt(stats_data, stat_month, stat_area)

        # Call LLM
        response_text = self._call_llm(prompt)

        # Parse structured sections from LLM response
        sections = self._parse_governance_response(response_text, stats_data)

        elapsed = time.time() - start_time
        logger.info(f'Governance report generated in {elapsed:.1f}s')

        return {
            'deliveryTrend': sections.get('deliveryTrend', ''),
            'correctRateTrend': sections.get('correctRateTrend', ''),
            'problemAreas': sections.get('problemAreas', []),
            'optimizationAdvice': sections.get('optimizationAdvice', ''),
        }

    def generate_business_report(self, stats_data: dict,
                                  stat_month: str,
                                  stat_area: str = '全部区域') -> dict:
        """
        Generate a business analysis report for merchants.

        Args:
            stats_data: Aggregated statistics including:
                - category_breakdown: waste type delivery counts and change rates
                - merchant_exchange_data: point exchange trends
            stat_month: Report period
            stat_area: Target area

        Returns:
            Dict with business section content
        """
        start_time = time.time()

        prompt = self._build_business_prompt(stats_data, stat_month, stat_area)
        response_text = self._call_llm(prompt)
        sections = self._parse_business_response(response_text, stats_data)

        elapsed = time.time() - start_time
        logger.info(f'Business report generated in {elapsed:.1f}s')

        return {
            'consumeTrend': sections.get('consumeTrend', ''),
            'hotProducts': sections.get('hotProducts', []),
            'suggestion': sections.get('suggestion', ''),
        }

    def generate_full_report(self, stats_data: dict,
                              stat_month: str,
                              stat_area: str = '全部区域') -> dict:
        """
        Generate a complete report with both governance and business sections,
        plus a full Markdown content.
        """
        governance = self.generate_governance_report(stats_data, stat_month, stat_area)
        business = self.generate_business_report(stats_data, stat_month, stat_area)

        # Build full Markdown report
        full_content = self._build_markdown_report(
            stat_month, stat_area,
            governance, business,
            stats_data,
        )

        return {
            'reportId': f'RPT{stat_month.replace("-", "")}{int(time.time()) % 1000:03d}',
            'statMonth': stat_month,
            'statArea': stat_area,
            'reportType': 'all',
            'status': 'completed',
            'governanceSection': governance,
            'businessSection': business,
            'fullContent': full_content,
            'generateTime': datetime.now(TZ_BEIJING).isoformat(),
            'generateDuration': 0,  # will be set by caller
        }

    def generate_merchant_report(self, stats_data: dict,
                                  stat_month: str,
                                  stat_area: str) -> dict:
        """
        Generate a merchant-facing business analysis report.
        Simplified version focusing on consumption trends and product suggestions.
        """
        business = self.generate_business_report(stats_data, stat_month, stat_area)
        full_content = self._build_merchant_markdown(stat_month, stat_area, business, stats_data)

        # Build category breakdown for merchant view
        category_breakdown = {}
        raw_breakdown = stats_data.get('category_breakdown', {})
        for cat_name, cat_data in raw_breakdown.items():
            category_breakdown[cat_name] = {
                'deliveryCount': cat_data.get('deliveryCount', 0),
                'changeRate': cat_data.get('changeRate', 0),
            }

        return {
            'reportId': f'RPT{stat_month.replace("-", "")}{int(time.time()) % 1000:03d}',
            'statMonth': stat_month,
            'statArea': stat_area,
            'consumeTrend': business['consumeTrend'],
            'hotProducts': business['hotProducts'],
            'suggestion': business['suggestion'],
            'categoryBreakdown': category_breakdown,
            'fullContent': full_content,
        }

    # ─── Prompt Building ───────────────────────────────────────

    def _build_governance_prompt(self, stats_data: dict, month: str, area: str) -> str:
        """Build governance analysis prompt with data."""
        data_json = json.dumps(stats_data, ensure_ascii=False, indent=2)
        if self._governance_prompt:
            prompt = self._governance_prompt.format(
                stat_month=month,
                stat_area=area,
                stats_data=data_json,
            )
        else:
            prompt = self._default_governance_prompt(month, area, data_json)
        return prompt

    def _build_business_prompt(self, stats_data: dict, month: str, area: str) -> str:
        """Build business analysis prompt with data."""
        data_json = json.dumps(stats_data, ensure_ascii=False, indent=2)
        if self._business_prompt:
            prompt = self._business_prompt.format(
                stat_month=month,
                stat_area=area,
                stats_data=data_json,
            )
        else:
            prompt = self._default_business_prompt(month, area, data_json)
        return prompt

    # ─── LLM Call ─────────────────────────────────────────────

    def _call_llm(self, prompt: str) -> str:
        """
        Call the configured LLM provider.
        Supports Anthropic Claude API and OpenAI-compatible APIs.
        """
        provider = LLM_CONFIG['provider']

        if provider == 'anthropic':
            return self._call_anthropic(prompt)
        elif provider == 'openai':
            return self._call_openai(prompt)
        elif provider == 'local':
            return self._call_local(prompt)
        else:
            # Mock/fallback for development
            return self._generate_mock_response(prompt)

    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=LLM_CONFIG['api_key'])
            message = client.messages.create(
                model=LLM_CONFIG['model'],
                max_tokens=LLM_CONFIG['max_tokens'],
                temperature=LLM_CONFIG['temperature'],
                messages=[{'role': 'user', 'content': prompt}],
            )
            return message.content[0].text
        except ImportError:
            logger.warning('anthropic SDK not installed, using mock')
            return self._generate_mock_response(prompt)
        except Exception as e:
            logger.error(f'Anthropic API call failed: {e}')
            return self._generate_mock_response(prompt)

    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI-compatible API."""
        try:
            import openai
            client = openai.OpenAI(
                api_key=LLM_CONFIG['api_key'],
                base_url=LLM_CONFIG.get('base_url'),
            )
            response = client.chat.completions.create(
                model=LLM_CONFIG['model'],
                max_tokens=LLM_CONFIG['max_tokens'],
                temperature=LLM_CONFIG['temperature'],
                messages=[{'role': 'user', 'content': prompt}],
            )
            return response.choices[0].message.content
        except ImportError:
            logger.warning('openai SDK not installed, using mock')
            return self._generate_mock_response(prompt)
        except Exception as e:
            logger.error(f'OpenAI API call failed: {e}')
            return self._generate_mock_response(prompt)

    def _call_local(self, prompt: str) -> str:
        """Call a local LLM endpoint."""
        try:
            import requests
            response = requests.post(
                LLM_CONFIG.get('base_url', 'http://localhost:8000/v1/chat/completions'),
                json={
                    'model': LLM_CONFIG['model'],
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': LLM_CONFIG['max_tokens'],
                    'temperature': LLM_CONFIG['temperature'],
                },
                timeout=300,
            )
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f'Local LLM call failed: {e}')
            return self._generate_mock_response(prompt)

    # ─── Response Parsing ─────────────────────────────────────

    def _parse_governance_response(self, text: str, stats_data: dict) -> dict:
        """Parse governance analysis from LLM response text."""
        sections = {
            'deliveryTrend': '',
            'correctRateTrend': '',
            'problemAreas': [],
            'optimizationAdvice': '',
        }

        # Try JSON parsing first
        try:
            data = json.loads(text)
            return {**sections, **data}
        except (json.JSONDecodeError, TypeError):
            pass

        # Simple text-based parsing
        markers = {
            '投放趋势': 'deliveryTrend',
            '正确率趋势': 'correctRateTrend',
            '问题区域': 'problemAreas',
            '优化建议': 'optimizationAdvice',
        }
        current_key = None
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            for marker, key in markers.items():
                if marker in line:
                    current_key = key
                    if key == 'problemAreas':
                        sections[key] = []
                    else:
                        sections[key] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
                    break
            else:
                if current_key == 'problemAreas' and line.startswith('-'):
                    sections['problemAreas'].append(line.lstrip('- '))

        return sections

    def _parse_business_response(self, text: str, stats_data: dict) -> dict:
        """Parse business analysis from LLM response text."""
        sections = {
            'consumeTrend': '',
            'hotProducts': [],
            'suggestion': '',
        }

        try:
            data = json.loads(text)
            return {**sections, **data}
        except (json.JSONDecodeError, TypeError):
            pass

        markers = {
            '消费趋势': 'consumeTrend',
            '热销商品': 'hotProducts',
            '建议': 'suggestion',
        }
        current_key = None
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            for marker, key in markers.items():
                if marker in line:
                    current_key = key
                    if key == 'hotProducts':
                        sections[key] = []
                    else:
                        sections[key] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
                    break
            else:
                if current_key == 'hotProducts' and (line.startswith('-') or line.startswith('•')):
                    sections['hotProducts'].append(line.lstrip('- •'))

        return sections

    # ─── Markdown Report Building ─────────────────────────────

    def _build_markdown_report(self, month: str, area: str,
                                governance: dict, business: dict,
                                stats: dict) -> str:
        """Build a full Markdown analysis report."""
        lines = [
            f'# 智能垃圾分类月度分析报告',
            f'',
            f'**统计周期**: {month}',
            f'**统计区域**: {area}',
            f'**生成时间**: {datetime.now(TZ_BEIJING).strftime("%Y-%m-%d %H:%M")}',
            f'',
            f'---',
            f'',
            f'## 一、治理数据分析',
            f'',
            f'### 1.1 投放趋势',
            f'',
            governance.get('deliveryTrend', '暂无数据'),
            f'',
            f'### 1.2 分类正确率趋势',
            f'',
            governance.get('correctRateTrend', '暂无数据'),
            f'',
            f'### 1.3 问题区域',
            f'',
        ]

        for area_problem in governance.get('problemAreas', []):
            lines.append(f'- {area_problem}')
        if not governance.get('problemAreas'):
            lines.append('暂无突出问题区域')

        lines.extend([
            f'',
            f'### 1.4 治理优化建议',
            f'',
            governance.get('optimizationAdvice', '暂无建议'),
            f'',
            f'---',
            f'',
            f'## 二、商业数据分析',
            f'',
            f'### 2.1 消费趋势',
            f'',
            business.get('consumeTrend', '暂无数据'),
            f'',
            f'### 2.2 热销商品推荐',
            f'',
        ])

        for product in business.get('hotProducts', []):
            lines.append(f'- {product}')

        lines.extend([
            f'',
            f'### 2.3 运营建议',
            f'',
            business.get('suggestion', '暂无建议'),
            f'',
        ])

        return '\n'.join(lines)

    def _build_merchant_markdown(self, month: str, area: str,
                                  business: dict, stats: dict) -> str:
        """Build a merchant-facing Markdown report."""
        lines = [
            f'# 商家运营分析报告',
            f'',
            f'**统计周期**: {month}',
            f'**统计区域**: {area}',
            f'',
            f'---',
            f'',
            f'## 消费趋势分析',
            f'',
            business.get('consumeTrend', '暂无数据'),
            f'',
            f'## 热销商品',
            f'',
        ]
        for p in business.get('hotProducts', []):
            lines.append(f'- {p}')
        lines.extend([
            f'',
            f'## 运营建议',
            f'',
            business.get('suggestion', '暂无建议'),
        ])
        return '\n'.join(lines)

    # ─── Default prompts (fallback if template files missing) ──

    def _default_governance_prompt(self, month: str, area: str, data_json: str) -> str:
        return f"""你是一个城市治理数据分析专家。请根据以下垃圾分类投放数据，生成一份治理分析报告。

统计周期: {month}
统计区域: {area}

数据如下:
{data_json}

请分析以下四个方面，以JSON格式返回:
1. deliveryTrend: 投放总量变化趋势分析
2. correctRateTrend: 分类正确率变化分析
3. problemAreas: 问题区域列表（数组）
4. optimizationAdvice: 治理优化建议

请确保建议具体可行，仅返回JSON。"""

    def _default_business_prompt(self, month: str, area: str, data_json: str) -> str:
        return f"""你是一个零售商业数据分析专家。请根据以下垃圾投放与积分兑换数据，生成一份商业分析报告。

统计周期: {month}
统计区域: {area}

数据如下:
{data_json}

请分析以下三个方面，以JSON格式返回:
1. consumeTrend: 消费趋势分析
2. hotProducts: 热销商品推荐列表（数组）
3. suggestion: 商品运营建议

请确保建议具体可行，仅返回JSON。"""

    def _generate_mock_response(self, prompt: str) -> str:
        """Generate a mock response for development/testing."""
        if '治理' in prompt or 'governance' in prompt.lower():
            return json.dumps({
                'deliveryTrend': '本月投放总量环比增长12%，A区增幅最大达15%',
                'correctRateTrend': 'A区分类正确率上升3个百分点，C区略有下降',
                'problemAreas': ['C区厨余垃圾混投率偏高', 'B区有害垃圾误投增多'],
                'optimizationAdvice': '建议在C区增设厨余垃圾专项指引牌，加强B区有害垃圾分类宣传',
            }, ensure_ascii=False)
        elif '商业' in prompt or 'business' in prompt.lower():
            return json.dumps({
                'consumeTrend': '塑料类可回收物增长18%，对应日用消费品需求上升',
                'hotProducts': ['环保垃圾袋', '瓶装饮用水', '一次性餐具', '厨房清洁剂'],
                'suggestion': '建议增加日用清洁类商品库存，配合积分兑换活动引流',
            }, ensure_ascii=False)
        return '{}'


# Singleton
_analysis_service: Optional[AnalysisService] = None


def get_analysis_service() -> AnalysisService:
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service
