"""商业分析提示词"""
BUSINESS_PROMPT = """你是一个零售商业数据分析专家。根据以下垃圾分类投放与积分兑换数据，生成一份商业分析报告。

统计周期: {stat_month}
统计区域: {stat_area}

运营数据:
{stats_data}

请以JSON格式返回（不要markdown代码块）:
{{
  "consumeTrend": "消费趋势分析",
  "hotProducts": ["热销商品1", "热销商品2", "热销商品3"],
  "suggestion": "商品运营建议"
}}

要求:
- consumeTrend: 从垃圾投放品类变化推断居民消费趋势，预测下一周期消费热点
- hotProducts: 根据品类趋势推荐3-5个热门商品，优先季节性商品
- suggestion: 给出库存调整、积分兑换活动主题、备货周期和促销时机建议
"""
