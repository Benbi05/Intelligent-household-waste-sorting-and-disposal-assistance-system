"""LLM报告生成器"""
import json, os, time
from datetime import datetime, timezone, timedelta
from .prompts.governance import GOVERNANCE_PROMPT
from .prompts.business import BUSINESS_PROMPT

TZ = timezone(timedelta(hours=8))

# LLM配置（从环境变量读取）
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'mock')  # anthropic | openai | mock
LLM_MODEL = os.environ.get('LLM_MODEL', 'claude-sonnet-4-6')
LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_BASE_URL = os.environ.get('LLM_BASE_URL', '')


def _call_llm(prompt: str, max_tokens: int = 2048, temperature: float = 0.3) -> str:
    """调用LLM（支持多种provider）"""
    if LLM_PROVIDER == 'anthropic':
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=LLM_API_KEY)
            msg = client.messages.create(model=LLM_MODEL, max_tokens=max_tokens,
                                         temperature=temperature,
                                         messages=[{'role': 'user', 'content': prompt}])
            return msg.content[0].text
        except Exception as e:
            return _mock_response(prompt)

    elif LLM_PROVIDER == 'openai':
        try:
            import openai
            client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
            resp = client.chat.completions.create(model=LLM_MODEL, max_tokens=max_tokens,
                                                  temperature=temperature,
                                                  messages=[{'role': 'user', 'content': prompt}])
            return resp.choices[0].message.content
        except Exception as e:
            return _mock_response(prompt)

    else:
        return _mock_response(prompt)


def _mock_response(prompt: str) -> str:
    """开发用模拟响应"""
    if '治理' in prompt or 'Governance' in prompt:
        return json.dumps({
            'deliveryTrend': '本月投放总量环比增长12%，A区增幅最大达15%',
            'correctRateTrend': 'A区分类正确率上升3个百分点，C区略有下降',
            'problemAreas': ['C区厨余垃圾混投率偏高', 'B区有害垃圾误投增多'],
            'optimizationAdvice': '建议在C区增设厨余垃圾指引牌，加强B区有害垃圾分类宣传',
        }, ensure_ascii=False)
    return json.dumps({
        'consumeTrend': '塑料类可回收物增长18%，对应日用消费品需求上升',
        'hotProducts': ['环保垃圾袋', '瓶装饮用水', '一次性餐具', '厨房清洁剂'],
        'suggestion': '建议增加日用清洁类商品库存，配合积分兑换活动引流',
    }, ensure_ascii=False)


def generate_governance_report(stats_data: dict, stat_month: str,
                                stat_area: str = '全部区域') -> dict:
    """生成治理分析报告"""
    start = time.time()
    prompt = GOVERNANCE_PROMPT.format(
        stat_month=stat_month, stat_area=stat_area,
        stats_data=json.dumps(stats_data, ensure_ascii=False, indent=2),
    )
    text = _call_llm(prompt)
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = _parse_fallback(text, 'governance')
    return {
        'deliveryTrend': result.get('deliveryTrend', ''),
        'correctRateTrend': result.get('correctRateTrend', ''),
        'problemAreas': result.get('problemAreas', []),
        'optimizationAdvice': result.get('optimizationAdvice', ''),
        'generateDuration': int((time.time() - start) * 1000),
    }


def generate_business_report(stats_data: dict, stat_month: str,
                              stat_area: str = '全部区域') -> dict:
    """生成商业分析报告"""
    start = time.time()
    prompt = BUSINESS_PROMPT.format(
        stat_month=stat_month, stat_area=stat_area,
        stats_data=json.dumps(stats_data, ensure_ascii=False, indent=2),
    )
    text = _call_llm(prompt)
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = _parse_fallback(text, 'business')
    return {
        'consumeTrend': result.get('consumeTrend', ''),
        'hotProducts': result.get('hotProducts', []),
        'suggestion': result.get('suggestion', ''),
        'generateDuration': int((time.time() - start) * 1000),
    }


def _parse_fallback(text: str, report_type: str) -> dict:
    """非JSON响应的回退解析"""
    result = {}
    lines = text.split('\n')
    if report_type == 'governance':
        for line in lines:
            if '投放趋势' in line:
                result['deliveryTrend'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
            elif '正确率' in line:
                result['correctRateTrend'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
            elif line.strip().startswith('-') and '区' in line:
                result.setdefault('problemAreas', []).append(line.strip('- '))
            elif '建议' in line:
                result['optimizationAdvice'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
    else:
        for line in lines:
            if '消费趋势' in line:
                result['consumeTrend'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
            elif line.strip().startswith('-'):
                result.setdefault('hotProducts', []).append(line.strip('- '))
            elif '建议' in line:
                result['suggestion'] = line.split('：', 1)[-1].split(':', 1)[-1].strip()
    return result
