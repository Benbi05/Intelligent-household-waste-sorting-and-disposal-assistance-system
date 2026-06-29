import request from './request'

/** 获取当前积分规则 */
export function getCurrentRules() {
  return request.get('/admin/point-rules/current')
}

/** 获取规则历史版本 */
export function getRulesHistory() {
  return request.get('/admin/point-rules/history')
}

/** 发布新规则版本 */
export function publishRules(ruleList) {
  return request.post('/admin/point-rules', { ruleList })
}

/** 回滚规则 */
export function rollbackRules(targetVersion) {
  return request.post('/admin/point-rules/rollback', { targetVersion })
}
