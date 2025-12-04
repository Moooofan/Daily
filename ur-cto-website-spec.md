# UR CTO 官網原型規劃文件

## 1. 頁面路由結構

```
/                    - 首頁
/services            - 服務項目
/approach            - 我們的方法
/cases               - 案例展示
/team                - 團隊介紹
/contact             - 聯絡我們
```

---

## 2. 頁面佈局描述

### 首頁 (`/`)

**區塊結構：**
- **Hero 區**：全寬背景、中央對齊標題、副標、CTA 按鈕
- **問題陳述區**：3 欄式網格，列出目標客群常見痛點
- **服務概覽區**：4 個服務卡片（圖示 + 標題 + 簡述）
- **案例精選區**：2-3 個代表性案例卡片（圖片 + 標題 + 標籤）
- **顧問價值區**：左右排列，左側文字說明、右側數據或圖示
- **CTA 區**：深色背景、中央對齊、預約諮詢按鈕

**Tailwind 類別範例：**
```jsx
<section className="max-w-7xl mx-auto px-4 py-16 md:py-24">
  <div className="grid md:grid-cols-3 gap-8">
    <div className="flex flex-col items-start space-y-4">
```

---

### 服務項目頁 (`/services`)

**區塊結構：**
- **頁首區**：頁面標題、說明文字
- **服務詳細列表**：每個服務一個大區塊（標題、說明、適合對象、交付內容）
- **流程說明區**：步驟式流程圖（1→2→3→4）
- **CTA 區**：諮詢預約

**Tailwind 類別範例：**
```jsx
<div className="space-y-16 py-12">
  <article className="border-l-4 border-gray-900 pl-6">
    <h3 className="text-2xl font-semibold mb-4">
```

---

### 我們的方法頁 (`/approach`)

**區塊結構：**
- **理念說明區**：大標題 + 段落文字
- **方法論區**：3-4 個核心原則卡片
- **流程圖區**：視覺化工作流程
- **差異化說明**：表格或對比式呈現

**Tailwind 類別範例：**
```jsx
<section className="bg-gray-50 py-20">
  <div className="max-w-4xl mx-auto prose prose-lg">
    <h2 className="text-3xl font-bold text-gray-900 mb-6">
```

---

### 案例展示頁 (`/cases`)

**區塊結構：**
- **篩選器區**：按產業、服務類型篩選
- **案例網格區**：卡片式佈局（圖片 + 標題 + 標籤 + 簡述）
- **詳細案例區**：展開式查看（挑戰、解決方案、成果）

**Tailwind 類別範例：**
```jsx
<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
  <div className="group cursor-pointer bg-white border border-gray-200 hover:shadow-lg transition-shadow">
    <div className="aspect-video bg-gray-100 overflow-hidden">
```

---

### 團隊介紹頁 (`/team`)

**區塊結構：**
- **團隊理念區**：文字說明
- **顧問卡片區**：網格佈局（頭像、姓名、職稱、專長、簡介）
- **協作夥伴區**：Logo 牆或簡單列表

**Tailwind 類別範例：**
```jsx
<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-12">
  <div className="text-center">
    <img className="w-32 h-32 rounded-full mx-auto mb-4 grayscale hover:grayscale-0 transition">
    <h3 className="text-xl font-semibold">
```

---

### 聯絡我們頁 (`/contact`)

**區塊結構：**
- **表單區**：姓名、Email、公司、需求類型（下拉選單）、訊息
- **聯絡資訊區**：Email、地址（如有）、社群連結
- **FAQ 區**：常見問題摺疊式面板

**Tailwind 類別範例：**
```jsx
<form className="max-w-2xl mx-auto space-y-6">
  <div className="grid md:grid-cols-2 gap-6">
    <input type="text" className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent">
```

---

## 3. 資料模型 JSON

### 顧問團隊資料

```json
{
  "team": [
    {
      "id": 1,
      "name": "陳建志",
      "title": "技術策略顧問 / Co-founder",
      "expertise": ["企業架構設計", "技術選型", "團隊建置"],
      "bio": "15 年以上軟體開發與技術管理經驗,曾任多家新創公司技術長,專精於從商業需求推導技術架構。",
      "image": "/images/team/chen.jpg",
      "linkedin": "https://linkedin.com/in/example"
    },
    {
      "id": 2,
      "name": "林雅婷",
      "title": "產品策略顧問 / Co-founder",
      "expertise": ["產品規劃", "商業模式設計", "市場驗證"],
      "bio": "曾協助 20+ 企業從 0 到 1 建立數位產品,擅長將模糊的商業想法轉化為可執行的產品藍圖。",
      "image": "/images/team/lin.jpg",
      "linkedin": "https://linkedin.com/in/example"
    },
    {
      "id": 3,
      "name": "王大明",
      "title": "資深全端工程師",
      "expertise": ["React/Next.js", "Node.js", "雲端架構"],
      "bio": "10 年全端開發經驗,專注於高效能 Web 應用開發與雲端部署最佳化。",
      "image": "/images/team/wang.jpg",
      "linkedin": "https://linkedin.com/in/example"
    }
  ]
}
```

### 服務項目資料

```json
{
  "services": [
    {
      "id": 1,
      "title": "技術策略諮詢",
      "slug": "tech-strategy",
      "tagline": "從商業目標推導技術方向",
      "description": "協助企業釐清技術投資優先順序,評估現有系統,規劃長期技術路線圖。",
      "suitableFor": ["沒有技術背景的創業者", "需要技術決策支持的管理層", "準備轉型的傳統企業"],
      "deliverables": [
        "技術現況評估報告",
        "技術架構建議書",
        "3-6 個月技術路線圖",
        "技術選型與成本評估"
      ],
      "duration": "2-4 週",
      "icon": "strategy"
    },
    {
      "id": 2,
      "title": "產品開發顧問",
      "slug": "product-development",
      "tagline": "從想法到可驗證的產品原型",
      "description": "陪伴企業從商業構想、需求釐清、功能規劃到技術實作,確保產品符合市場需求。",
      "suitableFor": ["有產品想法但不知如何開始", "需要快速驗證市場的團隊", "想建立 MVP 的創業者"],
      "deliverables": [
        "產品需求文件(PRD)",
        "使用者流程與原型設計",
        "技術架構設計",
        "MVP 開發與上線"
      ],
      "duration": "6-12 週",
      "icon": "product"
    },
    {
      "id": 3,
      "title": "軟體開發服務",
      "slug": "software-development",
      "tagline": "專業團隊落地執行你的技術計畫",
      "description": "提供完整的軟體開發團隊,從前端、後端到部署維運,以敏捷方式交付高品質軟體。",
      "suitableFor": ["需要外部開發資源的企業", "想快速擴充技術能量的團隊", "專案型開發需求"],
      "deliverables": [
        "客製化 Web/App 應用",
        "API 與系統整合",
        "雲端部署與維運設定",
        "程式碼文件與交接"
      ],
      "duration": "依專案規模",
      "icon": "code"
    },
    {
      "id": 4,
      "title": "技術團隊建置",
      "slug": "team-building",
      "tagline": "協助企業建立自己的技術團隊",
      "description": "從職位定義、人才招募、面試協助到新人培訓,協助企業建立穩定的內部技術團隊。",
      "suitableFor": ["準備組建技術團隊的企業", "技術招募遇到困難的公司", "需要技術面試支援"],
      "deliverables": [
        "技術職位 JD 撰寫",
        "技術面試協助",
        "新人培訓計畫",
        "技術管理建議"
      ],
      "duration": "持續性服務",
      "icon": "team"
    }
  ]
}
```

### 案例展示資料

```json
{
  "cases": [
    {
      "id": 1,
      "title": "電商平台從零到上線",
      "client": "某食品品牌",
      "industry": "零售電商",
      "services": ["產品開發顧問", "軟體開發服務"],
      "challenge": "傳統食品品牌想切入線上市場,但內部無技術團隊,不確定該如何開始。",
      "solution": "我們從商業模式驗證開始,協助釐清目標客群與核心功能,以 MVP 方式快速建立電商平台,並整合金流、物流系統。",
      "outcome": [
        "8 週內完成 MVP 上線",
        "成功驗證商業模式",
        "第一季營收達 200 萬",
        "後續自行招募技術團隊接手維運"
      ],
      "tags": ["電商", "MVP", "Next.js", "Stripe"],
      "image": "/images/cases/ecommerce.jpg",
      "featured": true
    },
    {
      "id": 2,
      "title": "內部管理系統現代化",
      "client": "某製造業公司",
      "industry": "製造業",
      "services": ["技術策略諮詢", "軟體開發服務"],
      "challenge": "10 年前建置的 ERP 系統老舊難維護,希望逐步現代化但不影響日常營運。",
      "solution": "進行系統現況評估,規劃分階段重構策略,優先處理痛點最大的模組,並建立 API 層串接舊系統。",
      "outcome": [
        "完成技術債評估與優先級排序",
        "3 個月內完成首個模組重構",
        "使用者操作效率提升 40%",
        "為後續全面改版奠定基礎"
      ],
      "tags": ["企業系統", "重構", "API 整合"],
      "image": "/images/cases/erp-modernization.jpg",
      "featured": true
    },
    {
      "id": 3,
      "title": "SaaS 產品技術架構規劃",
      "client": "某教育科技新創",
      "industry": "教育科技",
      "services": ["技術策略諮詢"],
      "challenge": "創辦人有明確的產品願景,但不確定技術架構該如何設計才能支撐未來成長。",
      "solution": "進行商業模式與技術需求分析,設計可擴展的雲端架構,並協助選擇合適的技術棧與開發團隊。",
      "outcome": [
        "完整技術架構設計文件",
        "技術選型與成本評估",
        "協助招募首位技術長",
        "產品順利進入開發階段"
      ],
      "tags": ["SaaS", "雲端架構", "技術選型"],
      "image": "/images/cases/saas-architecture.jpg",
      "featured": false
    }
  ]
}
```

---

## 4. 首頁 Hero 區完整文案

### 主標語
```
為企業打造以商業策略為核心的軟體解決方案
```

### 副標語
```
我們是技術顧問與開發團隊,從商業目標出發,協助沒有 CTO 或技術團隊的企業,
將構想轉化為可執行的技術策略與實際落地的產品。
```

### 按鈕文字
- 主要 CTA：`預約免費諮詢`
- 次要 CTA：`了解我們的服務`

### 完整 Hero 區 JSX 範例

```jsx
<section className="relative bg-white py-20 md:py-32">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="max-w-3xl">
      <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
        為企業打造以商業策略為核心的軟體解決方案
      </h1>
      <p className="text-xl md:text-2xl text-gray-600 leading-relaxed mb-10">
        我們是技術顧問與開發團隊,從商業目標出發,協助沒有 CTO 或技術團隊的企業,
        將構想轉化為可執行的技術策略與實際落地的產品。
      </p>
      <div className="flex flex-col sm:flex-row gap-4">
        <a
          href="/contact"
          className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-gray-900 hover:bg-gray-800 transition-colors rounded-lg"
        >
          預約免費諮詢
        </a>
        <a
          href="/services"
          className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-gray-900 bg-white border-2 border-gray-900 hover:bg-gray-50 transition-colors rounded-lg"
        >
          了解我們的服務
        </a>
      </div>
    </div>
  </div>
</section>
```

---

## 5. 色系與字型建議

### 色彩配置

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',  // 主色:深灰黑
        },
        accent: {
          500: '#3b82f6',  // 輔助色:專業藍(用於連結、特殊強調)
        }
      }
    }
  }
}
```

**使用原則：**
- **主色 (Primary)**：Gray-900 (#111827) - 用於標題、按鈕、重要文字
- **輔色 (Accent)**：Blue-500 (#3b82f6) - 用於連結、圖示、次要強調
- **背景色**：White (#ffffff) + Gray-50 (#f9fafb) - 交替使用創造層次
- **文字色**：Gray-900 (主要)、Gray-600 (次要)、Gray-400 (輔助)

### 字型建議

```javascript
// 選項一：使用 Google Fonts (推薦)
import { Inter, Noto_Sans_TC } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const notoSansTC = Noto_Sans_TC({
  weight: ['400', '500', '700'],
  subsets: ['latin'],
  variable: '--font-noto-sans-tc',
})

// 在 layout.tsx 中使用
<body className={`${inter.variable} ${notoSansTC.variable} font-sans`}>
```

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'var(--font-noto-sans-tc)', 'sans-serif'],
      }
    }
  }
}
```

**字型原則：**
- **英文**：Inter - 現代、專業、易讀
- **中文**：Noto Sans TC - 黑體、乾淨、專業感
- **字重**：400 (正文)、500 (小標)、700 (標題)

---

## 6. Tailwind CSS 佈局範例

### 首頁 - 問題陳述區

```jsx
<section className="py-16 md:py-24 bg-gray-50">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <h2 className="text-3xl md:text-4xl font-bold text-center text-gray-900 mb-12">
      您是否正面臨這些挑戰？
    </h2>
    <div className="grid md:grid-cols-3 gap-8">
      <div className="bg-white p-8 rounded-lg border border-gray-200">
        <h3 className="text-xl font-semibold text-gray-900 mb-3">
          有想法,不知如何開始
        </h3>
        <p className="text-gray-600 leading-relaxed">
          構想很清楚,但不確定技術可行性、開發成本,以及該從哪裡著手。
        </p>
      </div>
      {/* 其他卡片... */}
    </div>
  </div>
</section>
```

### 服務頁 - 服務詳細列表

```jsx
<section className="py-16 max-w-5xl mx-auto px-4">
  <div className="space-y-16">
    {services.map(service => (
      <article key={service.id} className="border-l-4 border-gray-900 pl-8 py-4">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
              {service.title}
            </h3>
            <p className="text-lg text-gray-600 italic">
              {service.tagline}
            </p>
          </div>
        </div>
        <p className="text-gray-700 leading-relaxed mb-6">
          {service.description}
        </p>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">適合對象</h4>
            <ul className="space-y-2">
              {service.suitableFor.map((item, idx) => (
                <li key={idx} className="text-gray-700 flex items-start">
                  <span className="mr-2">•</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">交付內容</h4>
            <ul className="space-y-2">
              {service.deliverables.map((item, idx) => (
                <li key={idx} className="text-gray-700 flex items-start">
                  <span className="mr-2">✓</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </article>
    ))}
  </div>
</section>
```

### 案例頁 - 案例卡片網格

```jsx
<section className="py-16 max-w-7xl mx-auto px-4">
  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
    {cases.map(caseItem => (
      <div
        key={caseItem.id}
        className="group cursor-pointer bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-xl transition-shadow duration-300"
      >
        <div className="aspect-video bg-gray-100 overflow-hidden">
          <img
            src={caseItem.image}
            alt={caseItem.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        <div className="p-6">
          <div className="flex flex-wrap gap-2 mb-3">
            {caseItem.tags.map(tag => (
              <span
                key={tag}
                className="px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-500 transition-colors">
            {caseItem.title}
          </h3>
          <p className="text-gray-600 text-sm mb-4">
            {caseItem.industry} · {caseItem.client}
          </p>
          <p className="text-gray-700 leading-relaxed line-clamp-3">
            {caseItem.challenge}
          </p>
        </div>
      </div>
    ))}
  </div>
</section>
```

### 團隊頁 - 顧問卡片

```jsx
<section className="py-16 max-w-7xl mx-auto px-4">
  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-12">
    {team.map(member => (
      <div key={member.id} className="text-center group">
        <img
          src={member.image}
          alt={member.name}
          className="w-32 h-32 rounded-full mx-auto mb-4 object-cover grayscale group-hover:grayscale-0 transition-all duration-300"
        />
        <h3 className="text-xl font-semibold text-gray-900 mb-1">
          {member.name}
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          {member.title}
        </p>
        <div className="flex flex-wrap justify-center gap-2 mb-4">
          {member.expertise.map(skill => (
            <span
              key={skill}
              className="px-3 py-1 text-xs text-gray-700 bg-gray-100 rounded-full"
            >
              {skill}
            </span>
          ))}
        </div>
        <p className="text-sm text-gray-700 leading-relaxed text-left">
          {member.bio}
        </p>
      </div>
    ))}
  </div>
</section>
```

### 聯絡頁 - 表單

```jsx
<section className="py-16 max-w-2xl mx-auto px-4">
  <form className="space-y-6">
    <div className="grid md:grid-cols-2 gap-6">
      <div>
        <label className="block text-sm font-medium text-gray-900 mb-2">
          您的姓名 *
        </label>
        <input
          type="text"
          required
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all"
          placeholder="王大明"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Email *
        </label>
        <input
          type="email"
          required
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all"
          placeholder="example@company.com"
        />
      </div>
    </div>

    <div>
      <label className="block text-sm font-medium text-gray-900 mb-2">
        公司名稱
      </label>
      <input
        type="text"
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all"
        placeholder="您的公司名稱"
      />
    </div>

    <div>
      <label className="block text-sm font-medium text-gray-900 mb-2">
        您的需求 *
      </label>
      <select
        required
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all bg-white"
      >
        <option value="">請選擇服務類型</option>
        <option value="strategy">技術策略諮詢</option>
        <option value="product">產品開發顧問</option>
        <option value="development">軟體開發服務</option>
        <option value="team">技術團隊建置</option>
        <option value="other">其他</option>
      </select>
    </div>

    <div>
      <label className="block text-sm font-medium text-gray-900 mb-2">
        詳細說明 *
      </label>
      <textarea
        required
        rows={6}
        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all resize-none"
        placeholder="請簡述您的需求、目前狀況,以及希望我們協助的部分..."
      />
    </div>

    <button
      type="submit"
      className="w-full py-4 px-6 text-lg font-medium text-white bg-gray-900 hover:bg-gray-800 rounded-lg transition-colors"
    >
      送出諮詢
    </button>
  </form>
</section>
```

### 通用 - Navigation Bar

```jsx
<nav className="sticky top-0 z-50 bg-white border-b border-gray-200">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="flex justify-between items-center h-16">
      <div className="flex items-center">
        <a href="/" className="text-2xl font-bold text-gray-900">
          UR CTO
        </a>
      </div>
      <div className="hidden md:flex items-center space-x-8">
        <a href="/services" className="text-gray-700 hover:text-gray-900 transition-colors">
          服務項目
        </a>
        <a href="/approach" className="text-gray-700 hover:text-gray-900 transition-colors">
          我們的方法
        </a>
        <a href="/cases" className="text-gray-700 hover:text-gray-900 transition-colors">
          案例展示
        </a>
        <a href="/team" className="text-gray-700 hover:text-gray-900 transition-colors">
          團隊介紹
        </a>
        <a
          href="/contact"
          className="px-6 py-2 text-white bg-gray-900 hover:bg-gray-800 rounded-lg transition-colors"
        >
          聯絡我們
        </a>
      </div>
    </div>
  </div>
</nav>
```

---

## 7. 文案語氣與提示事項

### 語氣原則

✅ **應該：**
- 使用顧問式語氣：專業、客觀、值得信賴
- 從商業痛點出發：「我們理解...」「協助您...」
- 強調方法論與流程：「我們如何做」而非「我們多厲害」
- 使用具體案例與成果：用數據和事實說話
- 保持謙虛專業：「協助」「陪伴」「支持」而非「保證」「最好」

❌ **避免：**
- 過度行銷語言：「業界第一」「最強」「革命性」
- 空泛承諾：「100% 成功」「絕對滿意」
- 自我吹噓：過度強調自己的成就
- 技術術語堆砌：除非必要,用商業語言溝通
- 催促式 CTA：避免「限時優惠」「立即搶購」等

### 文案範例對比

**❌ 過度行銷：**
> 「我們是業界最頂尖的技術團隊!擁有最先進的開發技術,保證讓您的產品在 30 天內成為市場第一!立即聯絡,享有早鳥優惠!」

**✅ 顧問式專業：**
> 「我們專注於從商業目標推導技術策略。過去三年,我們協助 20+ 企業從構想階段發展為實際產品,平均 8-12 週完成 MVP 驗證。讓我們聊聊您的需求。」

### SEO 與內容建議

- **頁面 Meta Title 格式**：`[頁面主題] | UR CTO - 企業技術顧問與軟體開發`
- **Meta Description**：120-150 字,包含核心關鍵字與價值主張
- **H1 標籤**：每頁一個,清楚說明頁面主題
- **內部連結**：服務頁連到案例、案例連到聯絡表單,形成轉換路徑

---

## 8. Next.js 專案結構建議

```
ur-cto-website/
├── app/
│   ├── layout.tsx                 # 根佈局
│   ├── page.tsx                   # 首頁
│   ├── services/
│   │   └── page.tsx              # 服務頁
│   ├── approach/
│   │   └── page.tsx              # 方法頁
│   ├── cases/
│   │   ├── page.tsx              # 案例列表
│   │   └── [slug]/
│   │       └── page.tsx          # 單一案例詳細頁
│   ├── team/
│   │   └── page.tsx              # 團隊頁
│   └── contact/
│       └── page.tsx              # 聯絡頁
├── components/
│   ├── Navigation.tsx            # 導航欄
│   ├── Footer.tsx                # 頁尾
│   ├── ServiceCard.tsx           # 服務卡片
│   ├── CaseCard.tsx              # 案例卡片
│   ├── TeamMember.tsx            # 團隊成員卡片
│   └── ContactForm.tsx           # 聯絡表單
├── data/
│   ├── services.json             # 服務資料
│   ├── cases.json                # 案例資料
│   └── team.json                 # 團隊資料
├── public/
│   └── images/
│       ├── team/                 # 團隊照片
│       └── cases/                # 案例圖片
├── tailwind.config.js
└── package.json
```

---

## 9. 開發優先順序建議

### Phase 1 - 核心頁面 (Week 1-2)
1. 設定 Next.js + Tailwind 專案
2. 建立共用元件 (Navigation, Footer)
3. 完成首頁
4. 完成服務頁

### Phase 2 - 內容頁面 (Week 2-3)
5. 完成案例展示頁
6. 完成團隊介紹頁
7. 完成聯絡表單 (先用 mailto 或 Formspree)

### Phase 3 - 優化與上線 (Week 3-4)
8. SEO 優化 (metadata, sitemap)
9. 響應式測試與調整
10. 效能優化 (圖片壓縮、lazy loading)
11. 部署到 Vercel

---

## 10. 技術細節補充

### 建議使用的套件

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0"
  }
}
```

### Metadata 範例 (SEO)

```typescript
// app/layout.tsx
export const metadata = {
  title: {
    default: 'UR CTO - 企業技術顧問與軟體開發',
    template: '%s | UR CTO'
  },
  description: '為企業打造以商業策略為核心的軟體解決方案。我們是技術顧問與開發團隊,協助沒有 CTO 或技術團隊的企業實現數位轉型。',
  keywords: ['技術顧問', '軟體開發', 'CTO 顧問', '產品開發', '技術策略'],
  authors: [{ name: 'UR CTO' }],
  openGraph: {
    type: 'website',
    locale: 'zh_TW',
    url: 'https://urcto.com',
    siteName: 'UR CTO',
  }
}
```

---

這份文件涵蓋了完整的網站規劃,包含結構、內容、設計與技術細節。您可以直接使用這些資料開始開發,或根據實際需求調整。所有文案都採用顧問式專業語氣,避免過度行銷,符合「UR CTO」品牌定位。
