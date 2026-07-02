"""治理分析提示词"""
GOVERNANCE_PROMPT = """你是一个城市治理数据分析专家。根据以下垃圾分类投放数据，生成一份治理分析报告。

统计周期: {stat_month}
统计区域: {stat_area}

投放数据:
{stats_data}

请以JSON格式返回（不要markdown代码块）:
{{
  "deliveryTrend": "投放总量变化趋势分析",
  "correctRateTrend": "分类正确率变化分析",
  "problemAreas": ["问题区域1", "问题区域2"],
  "optimizationAdvice": "具体可行的治理优化建议"
}}

要求:
- deliveryTrend: 分析投放总量环比变化，指出增长最快/下降最多的区域
- correctRateTrend: 分析各区域分类正确率变化，识别明显改善/恶化的区域
- problemAreas: 字符串数组，标注主要问题和严重程度
- optimizationAdvice: 短期+长期措施，参考行业最佳实践
"""
