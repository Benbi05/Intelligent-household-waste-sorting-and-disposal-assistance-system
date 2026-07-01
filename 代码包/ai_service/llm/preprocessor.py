"""数据预处理：聚合统计 → 提示词数据"""
import json


def prepare_governance_data(delivery_records: list, point_records: list,
                            areas: list, categories: list) -> dict:
    """准备治理分析所需的结构化数据"""
    # 按区域统计投放量
    area_stats = {}
    for a in areas:
        area_stats[a] = {'total': 0, 'correct': 0, 'wrong': 0}

    for r in delivery_records:
        area = r.get('area', 'unknown')
        if area not in area_stats:
            area_stats[area] = {'total': 0, 'correct': 0, 'wrong': 0}
        area_stats[area]['total'] += 1
        if r.get('isCorrect'):
            area_stats[area]['correct'] += 1
        else:
            area_stats[area]['wrong'] += 1

    # 品类分布
    category_counts = {}
    for r in delivery_records:
        cat = r.get('garbageCategory', 'unknown')
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        'delivery_trend': area_stats,
        'correct_rate_trend': {
            area: {
                'total': s['total'],
                'correct_rate': round(s['correct'] / max(s['total'], 1), 2)
            } for area, s in area_stats.items()
        },
        'category_breakdown': category_counts,
        'total_deliveries': len(delivery_records),
    }


def prepare_business_data(delivery_records: list, order_records: list,
                          categories: list, commodities: list) -> dict:
    """准备商业分析所需的结构化数据"""
    # 品类变化率
    from collections import Counter
    cat_counts = Counter(r.get('garbageCategory', '') for r in delivery_records)

    # 积分兑换统计
    exchange_stats = Counter(o.get('commodityName', '') for o in order_records)

    return {
        'category_breakdown': {
            cat: {
                'deliveryCount': count,
                'changeRate': 0.0  # 需要历史数据对比
            } for cat, count in cat_counts.most_common(20)
        },
        'exchange_stats': dict(exchange_stats),
        'total_orders': len(order_records),
        'total_commodities': len(commodities),
    }


def merge_stats(basic_stats: dict) -> str:
    """将统计数据转为JSON字符串，供提示词使用"""
    return json.dumps(basic_stats, ensure_ascii=False, indent=2)
