"""报告格式化：生成 Markdown 完整报告"""
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))


def build_full_report(stat_month: str, stat_area: str,
                      governance: dict, business: dict, stats: dict) -> str:
    """生成完整Markdown分析报告"""
    now = datetime.now(TZ).strftime('%Y-%m-%d %H:%M')
    lines = [
        f'# 智能垃圾分类月度分析报告',
        f'',
        f'**统计周期**: {stat_month}',
        f'**统计区域**: {stat_area}',
        f'**生成时间**: {now}',
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
    for p in governance.get('problemAreas', []):
        lines.append(f'- {p}')
    if not governance.get('problemAreas'):
        lines.append('暂无突出问题区域')

    lines.extend([
        f'', f'### 1.4 治理优化建议', f'',
        governance.get('optimizationAdvice', '暂无建议'),
        f'', f'---', f'', f'## 二、商业数据分析', f'',
        f'### 2.1 消费趋势', f'',
        business.get('consumeTrend', '暂无数据'),
        f'', f'### 2.2 热销商品推荐', f'',
    ])
    for p in business.get('hotProducts', []):
        lines.append(f'- {p}')
    lines.extend([
        f'', f'### 2.3 运营建议', f'',
        business.get('suggestion', '暂无建议'),
        f'',
    ])
    return '\n'.join(lines)


def build_merchant_report(stat_month: str, stat_area: str,
                           business: dict, stats: dict) -> str:
    """生成商家版Markdown报告"""
    now = datetime.now(TZ).strftime('%Y-%m-%d %H:%M')
    lines = [
        f'# 商家运营分析报告',
        f'',
        f'**统计周期**: {stat_month}',
        f'**统计区域**: {stat_area}',
        f'**生成时间**: {now}',
        f'', f'---', f'',
        f'## 消费趋势分析', f'',
        business.get('consumeTrend', '暂无数据'),
        f'', f'## 热销商品', f'',
    ]
    for p in business.get('hotProducts', []):
        lines.append(f'- {p}')
    lines.extend([f'', f'## 运营建议', f'', business.get('suggestion', '暂无建议')])
    return '\n'.join(lines)
