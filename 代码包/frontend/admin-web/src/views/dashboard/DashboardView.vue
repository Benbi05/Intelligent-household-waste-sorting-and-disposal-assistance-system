<template>
  <div class="dashboard">

    <!-- ==================== 物业经理视图 ==================== -->
    <template v-if="isAdmin">

      <!-- 社区选择器 -->
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">
        <div class="page-title">{{ roleLabel }}工作台 — {{ community ? community+'社区' : '全部社区' }}</div>
        <el-select v-model="activeCommunity" placeholder="选择社区" size="default" style="width:160px" @change="onCommunityChange" clearable>
          <el-option v-for="c in communities" :key="c.value" :label="c.label" :value="c.value" />
        </el-select>
      </div>

      <!-- 一、核心指标区 -->
      <div class="metrics-row">
        <div class="metric-card" @click="openChartDialog('rate')">
          <div class="metric-info">
            <div class="metric-label">分类正确率</div>
            <div class="metric-value">{{ monthCorrectRate }}<span class="metric-unit">%</span></div>
            <div class="metric-trend" :class="compareDelta >= 0 ? 'up' : 'down'">
              {{ compareDelta >= 0 ? '▲' : '▼' }} {{ Math.abs(compareDelta) }}%
              <span class="trend-ref">较上月</span>
            </div>
          </div>
          <div class="metric-icon">✅</div>
        </div>
        <div class="metric-card" @click="openChartDialog('participation')">
          <div class="metric-info">
            <div class="metric-label">本月参与率</div>
            <div class="metric-value">{{ participationRate }}<span class="metric-unit">%</span></div>
            <div class="metric-trend up">▲ {{ participationChange }}% <span class="trend-ref">较上月</span></div>
          </div>
          <div class="metric-icon" style="background:#ecf5ff;color:#409eff">👥</div>
        </div>
        <div class="metric-card" @click="openChartDialog('delivery')">
          <div class="metric-info">
            <div class="metric-label">{{ displayDeliveryLabel }}</div>
            <div class="metric-value">{{ displayDeliveryCount }}<span class="metric-unit"> 次</span></div>
            <div class="metric-trend" :class="(overview.deliveryChangeRate || 12) >= 0 ? 'up' : 'down'">
              {{ (overview.deliveryChangeRate || 12) >= 0 ? '▲' : '▼' }} {{ Math.abs(overview.deliveryChangeRate || 12) }}%
              <span class="trend-ref">较上月</span>
            </div>
          </div>
          <div class="metric-icon" style="background:#fdf6ec;color:#e6a23c">📦</div>
        </div>
        <div class="metric-card alert-card" @click="showAlert=true">
          <div class="alert-badge"></div>
          <div class="metric-info">
            <div class="metric-label">待处理告警</div>
            <div class="metric-value" style="color:#f56c6c">{{ alertCount }}<span class="metric-unit" style="color:#f56c6c"> 条</span></div>
            <div class="metric-trend down">{{ alertSummary }}</div>
          </div>
          <div class="metric-icon" style="background:#fef0f0;color:#f56c6c">🔴</div>
        </div>
      </div>

      <!-- 二、楼栋排名 + 三、工作台 -->
      <div class="two-col">
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">🏘️ {{ community ? '楼栋' : '社区' }}分类排名</span>
            <div class="sort-tabs">
              <span class="sort-tab" :class="{active:buildingSortBy==='rate'}" @click="buildingSortBy='rate'">正确率</span>
              <span class="sort-tab" :class="{active:buildingSortBy==='participation'}" @click="buildingSortBy='participation'">参与率</span>
            </div>
          </div>
          <div class="panel-body">
            <div class="building-list">
              <div class="building-item" v-for="(b,i) in sortedBuildings" :key="b.name">
                <div class="building-rank" :class="rankClass(i)">{{ i+1 }}</div>
                <div class="building-info">
                  <div class="building-name">{{ b.name }}</div>
                  <div class="building-sub">{{ b.units ? b.units+'单元' : '' }} · {{ b.households || b.users || '' }}{{ b.households ? '户' : b.users ? '人' : '' }}</div>
                </div>
                <div class="building-bar-wrap">
                  <div class="building-bar" :style="{width:sortVal(b)+'%',background:barColor(sortVal(b))}"></div>
                </div>
                <div class="building-rate" :class="rateClass(sortVal(b))">{{ sortVal(b) }}%</div>
              </div>
            </div>
          </div>
        </div>
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">📋 工作台</span>
            <div style="display:flex;gap:8px">
              <el-tag size="small" type="warning" v-if="overview.pendingMerchantCount">{{ overview.pendingMerchantCount }} 家待审</el-tag>
              <el-tag size="small" type="danger" v-if="overview.offlineFaultDevices">{{ overview.offlineFaultDevices }} 台故障</el-tag>
            </div>
          </div>
          <div class="panel-body">
            <div class="task-group">
              <div class="task-group-title"><span class="task-dot" style="background:#f56c6c"></span>🔴 今日待办</div>
              <div class="task-item" v-for="t in tasks.today" :key="t.id" @click="toggleTask('today',t.id)" :class="{done:t.done}">
                <div class="task-check">{{ t.done?'✓':'' }}</div><span class="task-text">{{ t.text }}</span>
              </div>
            </div>
            <div class="task-group">
              <div class="task-group-title"><span class="task-dot" style="background:#e6a23c"></span>🟡 本周重点</div>
              <div class="task-item" v-for="t in tasks.week" :key="t.id" @click="toggleTask('week',t.id)" :class="{done:t.done}">
                <div class="task-check">{{ t.done?'✓':'' }}</div><span class="task-text">{{ t.text }}</span>
              </div>
            </div>
            <div class="task-group">
              <div class="task-group-title"><span class="task-dot" style="background:#67c23a"></span>🟢 本月目标</div>
              <div class="task-item" v-for="t in tasks.month" :key="t.id" @click="toggleTask('month',t.id)" :class="{done:t.done}">
                <div class="task-check">{{ t.done?'✓':'' }}</div><span class="task-text">{{ t.text }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 品类正确率 -->
      <div class="panel" style="margin-bottom:20px">
        <div class="panel-header">
          <span class="panel-title">🗂️ 四大类垃圾分类正确率</span>
          <span style="font-size:12px;color:#c0c4cc">厨余垃圾通常最难分</span>
        </div>
        <div class="panel-body" v-loading="loading">
          <div class="cat-grid">
            <div v-for="c in catData" :key="c.type" class="cat-card" :style="{borderTopColor:catColor(c.type)}">
              <div class="cat-name">{{ c.name }}</div>
              <div class="cat-rate" :style="{color:c.rate>=85?'#67c23a':c.rate>=75?'#e6a23c':'#f56c6c'}">{{ c.rate }}%</div>
              <div class="cat-count">正确{{ c.correct }}/共{{ c.total }}次</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 设备状态 + 违规行为TOP榜 -->
      <div class="two-col">
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">🗺️ 设备状态</span>
            <span style="font-size:12px;color:#c0c4cc">{{ staticDevices.length }} 台</span>
          </div>
          <div class="panel-body">
            <div class="device-grid">
              <div class="device-dot" v-for="d in staticDevices" :key="d.id">
                <div class="dot" :class="d.status">{{ d.status==='online'?'🟢':d.status==='warning'?'🟡':'🔴' }}</div>
                <div class="dot-label">{{ d.name }}</div>
                <div style="font-size:10px;color:#c0c4cc">{{ d.location }}</div>
              </div>
            </div>
            <div class="device-summary">
              <div class="device-summary-item"><div class="summary-num" style="color:#67c23a">{{ staticDevices.filter(d=>d.status==='online').length }}</div><div class="summary-label">正常</div></div>
              <div class="device-summary-item"><div class="summary-num" style="color:#e6a23c">{{ staticDevices.filter(d=>d.status==='warning').length }}</div><div class="summary-label">即将满溢</div></div>
              <div class="device-summary-item"><div class="summary-num" style="color:#f56c6c">{{ staticDevices.filter(d=>d.status==='offline').length }}</div><div class="summary-label">故障/离线</div></div>
            </div>
          </div>
        </div>
        <div class="panel">
          <div class="panel-header">
            <span class="panel-title">⚠️ 违规行为 TOP 榜</span>
            <span style="font-size:12px;color:#c0c4cc">近30天</span>
          </div>
          <div class="panel-body">
            <div class="violation-list">
              <div class="violation-item" v-for="(v,i) in staticViolations" :key="i">
                <div class="violation-rank">{{ i+1 }}</div>
                <div class="violation-info"><div class="violation-name">{{ v.name }}</div><div class="violation-detail">{{ v.desc }}</div></div>
                <div class="violation-count">{{ v.count }}次</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 五、趋势分析区 -->
      <div class="two-col">
        <div class="panel">
          <div class="panel-header"><span class="panel-title">📈 分类正确率趋势（近12周）</span></div>
          <div class="panel-body"><div class="chart-box" ref="chartRate"></div></div>
        </div>
        <div class="panel">
          <div class="panel-header"><span class="panel-title">📊 投放量与参与率趋势（近12周）</span></div>
          <div class="panel-body"><div class="chart-box" ref="chartVolume"></div></div>
        </div>
      </div>

      <!-- 设备地图 -->
      <div class="panel" style="margin-bottom:20px">
        <div class="panel-header">🗺️ 设备分布图 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 蓝点=正常 红点=离线/故障</span></div>
        <div class="panel-body"><div ref="deviceMapRef" style="height:600px;border-radius:6px" v-loading="loading"></div></div>
      </div>

      <!-- 图表弹窗 -->
      <el-dialog :model-value="chartPopup==='rate'" @update:model-value="chartPopup = $event ? 'rate' : null" title="📈 分类正确率趋势（近12周）" width="760px" @opened="renderPopupChart('rate')"><div ref="popupRateChart" style="height:380px"></div></el-dialog>
      <el-dialog :model-value="chartPopup==='participation'" @update:model-value="chartPopup = $event ? 'participation' : null" title="👥 参与率趋势（近12周）" width="760px" @opened="renderPopupChart('participation')">
        <div ref="popupPartChart" style="height:380px"></div>
        <div style="text-align:center;margin-top:12px;font-size:13px;color:#909399">当前参与率 <strong style="color:#409eff;font-size:18px">{{ participationRate }}%</strong> · 较上月 <span style="color:#67c23a">▲ {{ participationChange }}%</span></div>
      </el-dialog>
      <el-dialog :model-value="chartPopup==='delivery'" @update:model-value="chartPopup = $event ? 'delivery' : null" title="📦 投放总量趋势（近12周）" width="760px" @opened="renderPopupChart('delivery')">
        <div ref="popupDeliveryChart" style="height:380px"></div>
        <div style="text-align:center;margin-top:12px;font-size:13px;color:#909399">{{ displayDeliveryLabel }} <strong style="color:#e6a23c;font-size:18px">{{ displayDeliveryCount }}</strong> 次</div>
      </el-dialog>

      <!-- 告警弹窗 -->
      <el-dialog v-model="showAlert" title="🔴 待处理告警（4 条）" width="560px">
        <div class="alert-item">
          <span style="font-size:24px">🗑️</span>
          <div class="alert-info"><div class="alert-title">3号投放点 · 满溢告警</div><div class="alert-desc">虎溪花园3栋北侧 · 满溢率 92% · 30分钟前</div></div>
          <el-button size="small" type="danger" @click="$router.push('/devices')">查看详情</el-button>
        </div>
        <div class="alert-item">
          <span style="font-size:24px">⚠️</span>
          <div class="alert-info"><div class="alert-title">7号投放点 · 设备故障</div><div class="alert-desc">虎溪花园7栋东侧 · 摄像头离线 · 2小时前</div></div>
          <el-button size="small" type="warning" @click="$router.push('/devices')">查看详情</el-button>
        </div>
        <div class="alert-item warn">
          <span style="font-size:24px">🏪</span>
          <div class="alert-info"><div class="alert-title">待处理商家审批</div><div class="alert-desc">好邻居便利店 · 申请入驻 · 1天前</div></div>
          <el-button size="small" type="primary" @click="$router.push('/merchants')">查看详情</el-button>
        </div>
        <div class="alert-item warn">
          <span style="font-size:24px">👤</span>
          <div class="alert-info"><div class="alert-title">用户 138****5678 · 连续违规</div><div class="alert-desc">近7天违规投放5次 · 5栋单元2居民</div></div>
          <el-button size="small" type="primary" @click="$router.push('/users')">查看详情</el-button>
        </div>
      </el-dialog>

    </template>

    <!-- ==================== 城管视图 ==================== -->
    <template v-else>
      <div class="page-title">{{ roleLabel }}工作台 — {{ community ? community+'社区' : '虎溪街道全部8个社区' }}</div>
      <el-row :gutter="16" class="stat-row">
        <el-col :span="6"><router-link to="/delivery-compare" class="stat-link"><StatCard label="本月投放总量" :value="overview.monthDeliveryCount || 0" unit="次" color="#1a73e8" tip="点击查看各社区投放对比" :trend="overview.deliveryChangeRate || 0" /></router-link></el-col>
        <el-col :span="6"><router-link to="/rate-compare" class="stat-link"><StatCard label="分类正确率" :value="overview.monthCorrectRate ? (overview.monthCorrectRate*100).toFixed(1) : 0" unit="%" color="#2e7d32" tip="点击查看各社区分类正确率" :trend="monthTrend" /></router-link></el-col>
        <el-col :span="6"><router-link to="/device-maintenance" class="stat-link"><StatCard label="在线设备" :value="overview.onlineDevices || 0" unit="台" color="#ef6c00" tip="点击查看待处理设备" :sub="'待处理 ' + (overview.offlineFaultDevices || 0) + ' 台'" /></router-link></el-col>
        <el-col :span="6"><router-link to="/user-stats" class="stat-link"><StatCard label="注册用户" :value="overview.totalUsers || 0" unit="人" color="#78909c" tip="点击查看各社区用户统计" :sub="'本月新增 ' + (overview.newUsersThisMonth || 0) + ' 人'" /></router-link></el-col>
      </el-row>
      <el-row :gutter="16" style="margin-top:16px" class="equal-row">
        <el-col :span="12"><el-card shadow="never" class="full-card"><template #header>四大类垃圾分类正确率 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 厨余垃圾通常最难分</span></template><div class="cat-grid" v-loading="loading"><div v-for="c in catData" :key="c.type" class="cat-card" :style="{borderTopColor:catColor(c.type)}"><div class="cat-name">{{ c.name }}</div><div class="cat-rate" :style="{color:c.rate>=85?'#67c23a':c.rate>=75?'#e6a23c':'#f56c6c'}">{{ c.rate }}%</div><div class="cat-count">正确{{ c.correct }}/共{{ c.total }}次</div></div></div></el-card></el-col>
        <el-col :span="12"><el-card shadow="never" class="full-card"><template #header>本月 vs 上月 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 环比变化</span></template><div class="compare-box" v-loading="loading"><div ref="pieLastRef" style="width:160px;height:180px"></div><div class="compare-center"><span v-if="compareDelta>0" style="color:#67c23a;font-size:20px">▲</span><span v-else-if="compareDelta<0" style="color:#f56c6c;font-size:20px">▼</span><span v-else style="color:#c0c4cc;font-size:20px">—</span><div :style="{color:compareDelta>0?'#67c23a':'#f56c6c',fontSize:'16px',fontWeight:'700',marginTop:'4px'}">{{ compareDelta>0?'+':'' }}{{ compareDelta }}%</div></div><div ref="pieThisRef" style="width:160px;height:180px"></div></div></el-card></el-col>
      </el-row>
      <template v-if="community">
        <el-row :gutter="16" style="margin-top:16px"><el-col :span="24"><el-card shadow="never"><template #header>各栋分类正确率 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 红线=达标85%</span></template><div class="bar-chart" v-loading="loading"><div v-for="d in bldData" :key="d.building" class="bar-row"><span class="bar-label">{{ d.building }}</span><div class="bar-track"><div class="bar-fill" :style="{width:d.rate+'%',background:d.rate>=85?'#67c23a':d.rate>=80?'#e6a23c':'#f56c6c'}"></div></div><span class="bar-val" :style="{color:d.rate>=85?'#67c23a':'#f56c6c'}">{{ d.rate }}%</span></div></div></el-card></el-col></el-row>
        <el-row :gutter="16" style="margin-top:16px"><el-col :span="24"><el-card shadow="never"><template #header>近30天投放趋势 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 蓝柱=总投放 绿柱=正确 红线=正确率</span></template><div ref="trendChart" style="height:320px" v-loading="loading"></div></el-card></el-col></el-row>
      </template>
      <el-row :gutter="16" style="margin-top:16px"><el-col :span="24"><el-card shadow="never"><template #header>设备分布图 <span style="font-size:12px;color:#c0c4cc;font-weight:normal">— 蓝点=正常 红点=离线/故障</span></template><div ref="deviceMapRef" style="height:800px;border-radius:6px" v-loading="loading"></div></el-card></el-col></el-row>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOverview } from '@/api/statistics'
import { useUserStore } from '@/store/user'
import StatCard from '@/components/stat-card/StatCard.vue'
import request from '@/api/request'

const route = useRoute()
const userStore = useUserStore()
const isAdmin = computed(() => userStore.role === 'super_admin')
const community = computed(() => {
  if (isAdmin.value) return userStore.community
  return route.query.community || ''
})
const roleLabel = computed(() => isAdmin.value ? '物业经理' : '城管监管')

const overview = ref({})
const catData = ref([])
const monthCompare = ref({})
const bldData = ref([])
const trdData = ref([])
const deviceData = ref([])
const loading = ref(true)
const showAlert = ref(false)
const chartPopup = ref(null)
const buildingSortBy = ref('rate')
const trendChart = ref(null)
const pieLastRef = ref(null)
const pieThisRef = ref(null)
const deviceMapRef = ref(null)
const chartRate = ref(null)
const chartVolume = ref(null)
const popupRateChart = ref(null)
const popupPartChart = ref(null)
const popupDeliveryChart = ref(null)

// 静态演示数据
const staticDevices = reactive([
  { id:1,name:'1#箱',location:'1栋北侧',status:'online' },{ id:2,name:'2#箱',location:'2栋东侧',status:'online' },
  { id:3,name:'3#箱',location:'3栋南侧',status:'warning' },{ id:4,name:'4#箱',location:'4栋北侧',status:'online' },
  { id:5,name:'5#箱',location:'5栋西侧',status:'online' },{ id:6,name:'6#箱',location:'6栋北侧',status:'online' },
  { id:7,name:'7#箱',location:'7栋东侧',status:'offline' },{ id:8,name:'8#箱',location:'8栋南侧',status:'online' },
  { id:9,name:'9#箱',location:'9栋北侧',status:'online' },{ id:10,name:'10#箱',location:'10栋西侧',status:'warning' },
  { id:11,name:'11#箱',location:'11栋北侧',status:'online' },{ id:12,name:'12#箱',location:'12栋东侧',status:'online' },
  { id:13,name:'13#箱',location:'大门南侧',status:'online' },{ id:14,name:'14#箱',location:'会所西侧',status:'online' },
  { id:15,name:'15#箱',location:'广场北侧',status:'online' },{ id:16,name:'16#箱',location:'商业街口',status:'warning' },
])
const staticViolations = reactive([
  { name:'5栋·刘**',desc:'近30天厨房垃圾混入其他垃圾',count:12 },
  { name:'11栋·张**',desc:'多次将有害垃圾投入可回收桶',count:9 },
  { name:'8栋·陈**',desc:'夜间违规投放未分类垃圾',count:7 },
  { name:'3栋·王**',desc:'连续3天将厨余垃圾混投',count:6 },
  { name:'12栋·赵*',desc:'有害垃圾与可回收物混投',count:5 },
])
const tasks = reactive({
  today: [
    { id: 't1', text: '巡检满溢告警点位并更换垃圾桶', done: false },
    { id: 't2', text: '处理设备故障报修', done: false },
    { id: 't3', text: '跟进高风险楼栋违规投放问题', done: false },
  ],
  week: [
    { id: 'w1', text: '低正确率楼栋安排保洁重点巡查', done: false },
    { id: 'w2', text: '准备垃圾分类宣传物料', done: true },
    { id: 'w3', text: '检查各投放点二维码标识清晰度', done: false },
  ],
  month: [
    { id: 'm1', text: '本月参与率目标提升至68%', done: false },
    { id: 'm2', text: '完成2场垃圾分类社区宣传活动', done: true },
    { id: 'm3', text: '月底导出Excel报表报街道办', done: false },
  ],
})
function toggleTask(g, id) { const item = tasks[g].find(t => t.id === id); if (item) item.done = !item.done }

// 计算属性
const monthCorrectRate = computed(() => overview.value.monthCorrectRate ? (overview.value.monthCorrectRate * 100).toFixed(1) : (monthCompare.value.thisMonth?.rate ? monthCompare.value.thisMonth.rate.toFixed(1) : '0.0'))
const participationRate = computed(() => { const total = overview.value.totalUsers || 1; const monthD = overview.value.monthDeliveryCount || 0; return ((Math.min(monthD / 3, total) / total) * 100).toFixed(1) })
const participationChange = computed(() => { const d = overview.value.deliveryChangeRate || 0; return d.toFixed(1) })
const compareDelta = computed(() => { const t = overview.value.monthCorrectRate || 0; const l = overview.value.lastMonthCorrectRate || 0; return Math.round((t - l) * 1000) / 10 })
const displayDeliveryCount = computed(() => overview.value.monthDeliveryCount || 0)
const displayDeliveryLabel = computed(() => community.value ? '本月投放总量' : '今日投放总量')
const monthTrend = computed(() => { const d = compareDelta.value; return d > 0 ? Math.abs(d) : d < 0 ? -Math.abs(d) : 0 })

const deviceOnlineCount = computed(() => deviceData.value.filter(d => d.onlineStatus === 'online' || d.statusClass === 'online').length)
const deviceWarningCount = computed(() => deviceData.value.filter(d => d.onlineStatus === 'warning' || d.statusClass === 'warning' || (d.fullRate > 80 && d.onlineStatus === 'online')).length)
const deviceOfflineCount = computed(() => deviceData.value.filter(d => d.onlineStatus === 'offline' || d.statusClass === 'offline' || d.status === 'fault').length)
const deviceTotal = computed(() => overview.value.totalDevices || 0)
const deviceOnlineRate = computed(() => deviceData.value.length ? Math.round(deviceOnlineCount.value / deviceData.value.length * 100) : 88)
const alertCount = ref(4)
const alertSummary = ref('满溢1 · 故障1 · 待审1 · 违规1')

// 楼栋数据（优先使用后端数据，回退到静态模拟）
const staticBuildings = [
  { name: '1栋', units: 3, households: 252, rate: 92, participation: 71 }, { name: '2栋', units: 3, households: 252, rate: 88, participation: 68 },
  { name: '3栋', units: 3, households: 252, rate: 85, participation: 65 }, { name: '4栋', units: 4, households: 336, rate: 83, participation: 70 },
  { name: '5栋', units: 4, households: 336, rate: 62, participation: 48 }, { name: '6栋', units: 4, households: 336, rate: 86, participation: 62 },
  { name: '7栋', units: 2, households: 168, rate: 90, participation: 73 }, { name: '8栋', units: 2, households: 168, rate: 78, participation: 58 },
  { name: '9栋', units: 3, households: 252, rate: 81, participation: 60 }, { name: '10栋', units: 3, households: 252, rate: 86, participation: 67 },
  { name: '11栋', units: 4, households: 336, rate: 75, participation: 55 }, { name: '12栋', units: 4, households: 336, rate: 79, participation: 63 },
]
const buildings = computed(() => {
  return bldData.value.length ? bldData.value.map(d => ({
    name: d.building || d.name, rate: d.rate || 0, participation: d.participation || 0,
    units: d.units, households: d.households,
  })) : staticBuildings
})
const sortedBuildings = computed(() => [...buildings.value].sort((a, b) => b[buildingSortBy.value] - a[buildingSortBy.value]))
const worstBuildings = computed(() => sortedBuildings.value.filter(b => b.rate < 70).slice(0, 5))
function sortVal(b) { return b[buildingSortBy.value] }
function rankClass(i) { const v = sortedBuildings.value[i]; if (!v) return ''; return i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : v[buildingSortBy.value] < 70 ? 'warn' : '' }
function rateClass(v) { return v >= 85 ? 'good' : v >= 70 ? 'mid' : 'bad' }
function barColor(v) { return v >= 85 ? '#67c23a' : v >= 70 ? '#e6a23c' : '#f56c6c' }
function catColor(type) { return { recyclable: '#1a73e8', kitchen: '#ef6c00', hazardous: '#c62828', other: '#78909c' }[type] || '#78909c' }
function deviceEmoji(d) { const s = d.onlineStatus || d.statusClass; return s === 'online' ? '🟢' : s === 'warning' ? '🟡' : '🔴' }
function truncate(s, n) { return s && s.length > n ? s.substring(0, n) : s || '' }
function formatDeviceData(list) {
  return (list || []).map(d => {
    let statusClass = 'online'
    if (d.onlineStatus === 'offline' || d.status === 'fault') statusClass = 'offline'
    else if ((d.fullRate || 0) > 80) statusClass = 'warning'
    return { ...d, statusClass }
  })
}

// 图表函数
function makePie(el, rate, title) {
  if (!el || !window.echarts) return
  const c = window.echarts.init(el)
  c.setOption({
    title: { text: title, left: 'center', bottom: 0, textStyle: { fontSize: 12, color: '#909399' } },
    series: [{ type: 'pie', radius: ['50%', '70%'], center: ['50%', '45%'], itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.2)', shadowOffsetY: 2 }, label: { show: true, position: 'center', formatter: '{c}%', fontSize: 18, fontWeight: 'bold', color: rate >= 85 ? '#2e7d32' : rate >= 75 ? '#e65100' : '#c62828' }, data: [{ value: rate, name: '正确', itemStyle: { color: rate >= 85 ? '#4caf50' : rate >= 75 ? '#ff9800' : '#ef5350' } }, { value: 100 - rate, name: '错误', itemStyle: { color: '#eceff1' } }] }]
  })
}
function renderPieCharts() {
  const lm = monthCompare.value.lastMonth?.rate || 0
  const tm = monthCompare.value.thisMonth?.rate || 0
  if (pieLastRef.value) makePie(pieLastRef.value, lm, '上月')
  if (pieThisRef.value) makePie(pieThisRef.value, tm, '本月')
}

function makeRateChart(el) {
  if (!el || !window.echarts) return
  const c = window.echarts.init(el)
  c.setOption({
    tooltip: { trigger: 'axis' }, grid: { left: 50, right: 30, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: ['W19', 'W20', 'W21', 'W22', 'W23', 'W24', 'W25', 'W26', 'W27', 'W28', 'W29', 'W30'] },
    yAxis: { type: 'value', min: 50, max: 100, axisLabel: { formatter: '{value}%' } },
    series: [{ name: '正确率', type: 'line', data: [76, 78, 79, 77, 82, 83, 81, 85, 84, 86, 88, 87.3], smooth: true, symbol: 'circle', symbolSize: 8, lineStyle: { color: '#67c23a', width: 3 }, itemStyle: { color: '#67c23a' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(103,194,58,0.25)' }, { offset: 1, color: 'rgba(103,194,58,0.02)' }]) }, markLine: { silent: true, data: [{ yAxis: 85, label: { formatter: '达标线 85%' }, lineStyle: { color: '#e6a23c', type: 'dashed' } }] } }]
  })
}
function makePartChart(el) {
  if (!el || !window.echarts) return
  const c = window.echarts.init(el)
  c.setOption({
    tooltip: { trigger: 'axis' }, grid: { left: 50, right: 30, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: ['W19', 'W20', 'W21', 'W22', 'W23', 'W24', 'W25', 'W26', 'W27', 'W28', 'W29', 'W30'] },
    yAxis: { type: 'value', min: 30, max: 80, axisLabel: { formatter: '{value}%' } },
    series: [{ name: '参与率', type: 'line', data: [45, 48, 47, 52, 53, 55, 50, 56, 58, 59, 60, 62.5], smooth: true, symbol: 'circle', symbolSize: 8, lineStyle: { color: '#409eff', width: 3 }, itemStyle: { color: '#409eff' }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(64,158,255,0.25)' }, { offset: 1, color: 'rgba(64,158,255,0.02)' }]) }, markLine: { silent: true, data: [{ yAxis: 60, label: { formatter: '目标线 60%' }, lineStyle: { color: '#67c23a', type: 'dashed' } }] } }]
  })
}
function makeDeliveryChart(el) {
  if (!el || !window.echarts) return
  const c = window.echarts.init(el)
  c.setOption({
    tooltip: { trigger: 'axis' }, grid: { left: 50, right: 30, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: ['W19', 'W20', 'W21', 'W22', 'W23', 'W24', 'W25', 'W26', 'W27', 'W28', 'W29', 'W30'] },
    yAxis: { type: 'value', name: '次', min: 200 },
    series: [{ name: '投放量', type: 'bar', data: [320, 340, 310, 380, 360, 400, 350, 420, 390, 410, 380, 389], itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#f6a23c' }, { offset: 1, color: '#fde2b3' }]), borderRadius: [6, 6, 0, 0] }, barWidth: 20 }]
  })
}
function makeCombinedChart(el) {
  if (!el || !window.echarts) return
  const c = window.echarts.init(el)
  c.setOption({
    tooltip: { trigger: 'axis' }, legend: { data: ['投放量', '参与率'], top: 0, right: 10, textStyle: { fontSize: 12 } }, grid: { left: 40, right: 20, top: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['W19', 'W20', 'W21', 'W22', 'W23', 'W24', 'W25', 'W26', 'W27', 'W28', 'W29', 'W30'] },
    yAxis: [{ type: 'value', name: '次', min: 200 }, { type: 'value', name: '%', min: 30, max: 80 }],
    series: [{ name: '投放量', type: 'bar', data: [320, 340, 310, 380, 360, 400, 350, 420, 390, 410, 380, 389], itemStyle: { color: '#b3e19d', borderRadius: [4, 4, 0, 0] }, barWidth: 16 }, { name: '参与率', type: 'line', yAxisIndex: 1, data: [45, 48, 47, 52, 53, 55, 50, 56, 58, 59, 60, 62.5], smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: { color: '#409eff', width: 3 }, itemStyle: { color: '#409eff' } }]
  })
}

function openChartDialog(type) {
  chartPopup.value = type
  nextTick(() => setTimeout(() => {
    if (type === 'rate' && popupRateChart.value) makeRateChart(popupRateChart.value)
    else if (type === 'participation' && popupPartChart.value) makePartChart(popupPartChart.value)
    else if (type === 'delivery' && popupDeliveryChart.value) makeDeliveryChart(popupDeliveryChart.value)
  }, 200))
}
function renderPopupChart(type) { openChartDialog(type) }

async function renderDeviceMap() {
  if (!deviceMapRef.value || !window.L) return setTimeout(renderDeviceMap, 1000)
  try {
    const r = await request.get('/admin/community/device-map')
    const devices = r.data || []
    const valid = devices.filter(d => d.lat && d.lng)
    if (!valid.length) return
    const map = window.L.map(deviceMapRef.value).setView([29.6098, 106.2996], 15)
    window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OSM' }).addTo(map)
    for (const d of valid) {
      const isFault = d.status === 'offline' || d.status === 'fault'
      window.L.circleMarker([d.lat, d.lng], { radius: 6, fillColor: isFault ? '#ef5350' : '#1a73e8', color: '#fff', weight: 1.5, fillOpacity: 0.85 }).addTo(map).bindPopup('<b>' + d.deviceName + '</b><br>' + d.location + '<br>状态: ' + (isFault ? '故障/离线' : '正常'))
    }
  } catch {}
}

function renderTrendChart() {
  if (!trendChart.value || !trdData.value.length) return
  const ec = window.echarts
  if (!ec) return setTimeout(renderTrendChart, 500)
  const chart = ec.init(trendChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis', formatter: p => p[0].axisValue + '<br/>总投放: ' + p[0].value + '次<br/>正确: ' + p[1].value + '次<br/>正确率: ' + (p[1].value / p[0].value * 100).toFixed(1) + '%' },
    legend: { data: ['总投放', '正确', '正确率'], top: 5 }, grid: { top: 40, right: 60, bottom: 40, left: 50 },
    xAxis: { data: trdData.value.map(d => d.date), axisLabel: { fontSize: 10, rotate: 45, interval: 2 } },
    yAxis: [{ type: 'value', name: '次', axisLabel: { fontSize: 10 } }, { type: 'value', name: '%', min: 0, max: 100, axisLabel: { fontSize: 10, formatter: '{value}%' } }],
    series: [
      { name: '总投放', type: 'bar', data: trdData.value.map(d => d.total), itemStyle: { color: '#409eff', opacity: 0.5 }, barWidth: '40%' },
      { name: '正确', type: 'bar', data: trdData.value.map(d => d.correct), itemStyle: { color: '#67c23a', opacity: 0.8 }, barWidth: '40%' },
      { name: '正确率', type: 'line', yAxisIndex: 1, data: trdData.value.map(d => d.rate), itemStyle: { color: '#f56c6c' }, lineStyle: { width: 2 }, symbol: 'circle', symbolSize: 5, markLine: { silent: true, data: [{ yAxis: 85, label: { formatter: '达标线85%' }, lineStyle: { color: '#f56c6c', type: 'dashed' } }] } }
    ]
  })
}

const params = computed(() => community.value ? { community: community.value } : {})

async function fetchAll() {
  loading.value = true
  try { const r = await getOverview(params.value); overview.value = r.data } catch {}
  try {
    const apis = [
      request.get('/admin/statistics/category-breakdown', { params: params.value }),
      request.get('/admin/statistics/month-compare', { params: params.value }),
    ]
    if (community.value) {
      apis.push(request.get('/admin/statistics/building-compare', { params: params.value }))
      apis.push(request.get('/admin/statistics/daily-trend', { params: params.value }))
    }
    const results = await Promise.all(apis)
    catData.value = results[0].data || []
    monthCompare.value = results[1].data || {}
    if (community.value) {
      bldData.value = results[2]?.data || []
      trdData.value = results[3]?.data || []
      await nextTick(); renderTrendChart()
    }
  } catch {}
  // 获取设备列表
  try {
    const devRes = await request.get('/admin/devices', { params: { size: 100 } })
    deviceData.value = formatDeviceData(devRes.data?.records || [])
  } catch {}
  loading.value = false
  setTimeout(renderPieCharts, 200)
  setTimeout(renderDeviceMap, 400)
  // 初始化物业经理仪表盘固定图表
  nextTick(() => {
    setTimeout(() => {
      if (chartRate.value) makeRateChart(chartRate.value)
      if (chartVolume.value) makeCombinedChart(chartVolume.value)
    }, 300)
  })
}

onMounted(fetchAll)
watch(community, () => { fetchAll() })
</script>

<style scoped>
.dashboard { padding: 20px; }
.page-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 20px; display: flex; align-items: center; }
.stat-row { margin-bottom: 16px; }

/* 核心指标卡片 */
.metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.metric-card { background: #fff; border-radius: 10px; padding: 20px 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: transform .2s, box-shadow .2s; border-left: 4px solid #67c23a; position: relative; overflow: hidden; }
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
.metric-card.alert-card { border-left-color: #f56c6c; }
.metric-card.alert-card .metric-icon { background: #fef0f0; color: #f56c6c; }
.metric-info { flex: 1; }
.metric-label { font-size: 13px; color: #909399; margin-bottom: 6px; }
.metric-value { font-size: 32px; font-weight: 700; color: #1a1a1a; line-height: 1.1; }
.metric-unit { font-size: 18px; font-weight: 400; }
.metric-trend { display: flex; align-items: center; gap: 4px; margin-top: 8px; font-size: 13px; color: #606266; }
.metric-trend.up { color: #67c23a; } .metric-trend.down { color: #f56c6c; }
.trend-ref { color: #c0c4cc; margin-left: 4px; }
.metric-icon { width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 26px; background: #e5f5da; color: #67c23a; flex-shrink: 0; }
.alert-badge { position: absolute; top: 8px; right: 12px; width: 10px; height: 10px; border-radius: 50%; background: #f56c6c; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.2); } }

/* 面板 */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.panel { background: #fff; border-radius: 10px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); overflow: hidden; }
.panel-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #f0f0f0; }
.panel-title { font-size: 15px; font-weight: 600; color: #1a1a1a; }
.panel-body { padding: 16px 20px; }

/* 楼栋排名 */
.sort-tabs { display: flex; border-radius: 6px; overflow: hidden; border: 1px solid #dcdfe6; }
.sort-tab { padding: 4px 14px; font-size: 12px; cursor: pointer; transition: all .2s; color: #909399; background: #fff; user-select: none; }
.sort-tab:first-child { border-right: 1px solid #dcdfe6; }
.sort-tab.active { background: #67c23a; color: #fff; }
.sort-tab:hover:not(.active) { color: #67c23a; }
.building-list { display: flex; flex-direction: column; gap: 8px; }
.building-item { display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-radius: 8px; transition: background .2s; cursor: pointer; }
.building-item:hover { background: #f5f7fa; }
.building-rank { width: 28px; height: 28px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; flex-shrink: 0; }
.building-rank.gold { background: #fdf6ec; color: #e6a23c; } .building-rank.silver { background: #f2f3f5; color: #909399; }
.building-rank.bronze { background: #fdf2e9; color: #cd7a2f; } .building-rank.warn { background: #fef0f0; color: #f56c6c; }
.building-info { flex: 1; }
.building-name { font-size: 14px; font-weight: 500; color: #303133; }
.building-sub { font-size: 12px; color: #909399; margin-top: 2px; }
.building-rate { font-size: 18px; font-weight: 700; } .building-rate.good { color: #67c23a; } .building-rate.mid { color: #e6a23c; } .building-rate.bad { color: #f56c6c; }
.building-bar-wrap { flex: 1; height: 6px; background: #f0f0f0; border-radius: 3px; overflow: hidden; max-width: 100px; }
.building-bar { height: 100%; border-radius: 3px; transition: width .6s; }

/* 品类 */
.cat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.cat-card { border: 1px solid #ebeef5; border-top: 3px solid #ccc; border-radius: 8px; padding: 14px; text-align: center; }
.cat-name { font-size: 14px; color: #606266; margin-bottom: 8px; font-weight: 500; }
.cat-rate { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.cat-count { font-size: 12px; color: #c0c4cc; }
.compare-box { display: flex; gap: 12px; align-items: center; justify-content: center; padding: 0; }
.compare-center { text-align: center; font-size: 14px; color: #606266; }

/* 设备 */
.device-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.device-dot { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 8px; border-radius: 8px; background: #f5f7fa; cursor: pointer; transition: transform .2s; }
.device-dot:hover { transform: scale(1.05); }
.device-dot .dot { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.device-dot .dot.online { background: #e5f5da; color: #67c23a; }
.device-dot .dot.warning { background: #fdf6ec; color: #e6a23c; animation: pulse 2s infinite; }
.device-dot .dot.offline { background: #fef0f0; color: #f56c6c; }
.dot-label { font-size: 11px; color: #606266; text-align: center; }
.device-summary { display: flex; justify-content: space-around; margin-top: 12px; padding-top: 12px; border-top: 1px dashed #f0f0f0; }
.device-summary-item { text-align: center; }
.summary-num { font-size: 20px; font-weight: 700; }
.summary-label { font-size: 11px; color: #909399; margin-top: 2px; }

/* 违规 */
.violation-list { display: flex; flex-direction: column; gap: 6px; }
.violation-item { display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 6px; cursor: pointer; transition: background .2s; }
.violation-item:hover { background: #fef0f0; }
.violation-rank { font-size: 13px; font-weight: 700; color: #f56c6c; width: 20px; }
.violation-info { flex: 1; }
.violation-name { font-size: 13px; color: #303133; }
.violation-detail { font-size: 11px; color: #c0c4cc; }
.violation-count { font-size: 16px; font-weight: 700; }

/* 资源 */
.resource-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.resource-item { text-align: center; padding: 16px 12px; border-radius: 8px; background: #f5f7fa; transition: transform .2s; }
.resource-item:hover { transform: translateY(-2px); }
.r-icon { font-size: 28px; margin-bottom: 8px; }
.r-value { font-size: 22px; font-weight: 700; color: #1a1a1a; }
.r-label { font-size: 12px; color: #909399; margin-top: 4px; }
.r-sub { font-size: 11px; color: #c0c4cc; margin-top: 2px; }

/* 图表 */
.chart-box { width: 100%; height: 260px; }

/* 任务台 */
.task-group { margin-bottom: 16px; } .task-group:last-child { margin-bottom: 0; }
.task-group-title { font-size: 13px; font-weight: 600; color: #606266; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
.task-dot { width: 8px; height: 8px; border-radius: 50%; }
.task-item { display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 6px; font-size: 13px; color: #606266; cursor: pointer; transition: background .2s; }
.task-item:hover { background: #f5f7fa; }
.task-check { width: 18px; height: 18px; border: 2px solid #dcdfe6; border-radius: 4px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 11px; }
.task-item.done .task-check { background: #67c23a; border-color: #67c23a; color: #fff; }
.task-item.done .task-text { text-decoration: line-through; color: #c0c4cc; }

/* 告警弹窗 */
.alert-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 8px; margin-bottom: 8px; background: #fef0f0; }
.alert-item.warn { background: #fdf6ec; }
.alert-info { flex: 1; }
.alert-title { font-size: 14px; font-weight: 500; color: #303133; }
.alert-desc { font-size: 12px; color: #909399; margin-top: 4px; }

/* 城管视图复用 */
.stat-link { text-decoration: none; color: inherit; display: block; }
.stat-link:hover { opacity: 0.85; transform: translateY(-2px); transition: all .2s; }
.bar-chart { padding: 10px 0; }
.bar-row { display: flex; align-items: center; margin-bottom: 6px; }
.bar-label { width: 36px; font-size: 12px; color: #606266; text-align: right; margin-right: 8px; flex-shrink: 0; }
.bar-track { flex: 1; height: 18px; background: #f0f2f5; border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 4px; transition: width .5s; min-width: 2px; }
.bar-val { width: 44px; font-size: 12px; font-weight: 600; text-align: right; margin-left: 8px; flex-shrink: 0; }
.equal-row { align-items: stretch; }
.equal-row .el-col { display: flex; }
.equal-row .el-card { flex: 1; width: 100%; }
.full-card { height: 100%; }

@media (max-width: 1400px) { .metrics-row { grid-template-columns: repeat(2, 1fr); } .two-col, .three-col { grid-template-columns: 1fr; } .device-grid { grid-template-columns: repeat(4, 1fr); } .resource-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
