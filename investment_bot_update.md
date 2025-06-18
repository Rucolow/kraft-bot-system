# KRAFT投資Botアップデート - 実践的投資教育システム（修正版）

## 🎯 アップデート概要

**「KRAFTで学んだことが実際の投資で生きる」** システムに大幅アップデート

### 核心コンセプト
- **時間軸**: 現実1年 = KRAFT1ヶ月（12倍速）
- **ライトユーザー**: Discord自動ニュースで簡単投資判断
- **ヘビーユーザー**: Webサイトでプロレベル分析
- **実践性**: 実際の投資理論・パターンを少し誇張して再現
- **効率性**: 高速レスポンス + 予測可能性重視

---

## ⏰ 統一時間管理システム

### KraftTimeManager（新設）
```python
# 新ファイル: shared/kraft_time.py
import datetime
from typing import Dict

class KraftTimeManager:
    """KRAFT世界の時間管理統一クラス"""
    
    KRAFT_START_DATE = datetime.datetime(2025, 1, 1)  # KRAFT世界開始日
    TIME_MULTIPLIER = 12  # 12倍速
    
    @classmethod
    def get_kraft_date(cls) -> datetime.datetime:
        """統一的なKRAFT日付取得"""
        real_now = datetime.datetime.utcnow()
        real_elapsed = real_now - cls.KRAFT_START_DATE
        kraft_elapsed = real_elapsed * cls.TIME_MULTIPLIER
        return cls.KRAFT_START_DATE + kraft_elapsed
    
    @classmethod
    def get_kraft_day_number(cls) -> int:
        """KRAFT開始からの経過日数"""
        kraft_date = cls.get_kraft_date()
        delta = kraft_date - cls.KRAFT_START_DATE
        return delta.days + 1
    
    @classmethod
    def get_season(cls, kraft_date: datetime.datetime = None) -> str:
        """景気サイクル判定"""
        if kraft_date is None:
            kraft_date = cls.get_kraft_date()
            
        month = kraft_date.month
        if month in [1, 2, 3]:
            return "景気回復期"
        elif month in [4, 5, 6]:
            return "景気拡大期"
        elif month in [7, 8, 9]:
            return "景気減速期"
        else:
            return "景気後退期"
    
    @classmethod
    def get_quarter(cls, kraft_date: datetime.datetime = None) -> str:
        """四半期取得"""
        if kraft_date is None:
            kraft_date = cls.get_kraft_date()
            
        month = kraft_date.month
        if month in [1, 2, 3]:
            return "Q1"
        elif month in [4, 5, 6]:
            return "Q2"
        elif month in [7, 8, 9]:
            return "Q3"
        else:
            return "Q4"
```

---

## 📊 統一企業データ設計

### kraft_config.py（大幅統合）
```python
# shared/kraft_config.py - 統合版
import os
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

# =====================================
# 統一企業マスターデータ
# =====================================

UNIFIED_COMPANY_DATA = {
    "WICR": {
        # 基本情報
        "name": "Wicrosoft",
        "industry": "AI・Bot開発",
        "initial_price": 85,
        "volatility": 0.02,
        "dividend_yield": 0.015,
        
        # 事業詳細
        "business_detail": "AI・ボット開発プラットフォーム事業",
        "revenue_breakdown": {"AI開発ツール": 60, "クラウドサービス": 30, "コンサルティング": 10},
        "competitive_advantage": "圧倒的な開発者コミュニティ",
        "growth_drivers": ["企業DX需要", "AI導入拡大", "ノーコード開発トレンド"],
        "key_metrics": {"月間アクティブ開発者": "120万人", "プラットフォーム利用企業": "15000社"},
        
        # 決算・財務
        "earnings_months": [3, 6, 9, 12],
        "beat_probability": 0.7,
        "financial_profile": {
            "per_base": 45, "pbr_base": 8.5, "roe_base": 18, "profit_margin_base": 25
        },
        
        # ストーリーアーク
        "story_arcs": {
            "2025_q1": {
                "theme": "新AI技術開発プロジェクト",
                "description": "次世代AIアシスタント開発",
                "events": [
                    {"day": 15, "event": "研究開発チーム拡大発表", "impact": 2, "type": "組織強化"},
                    {"day": 45, "event": "プロトタイプ技術デモ公開", "impact": 3, "type": "技術革新"},
                    {"day": 75, "event": "大手企業との戦略的提携", "impact": 4, "type": "業務提携"},
                    {"day": 90, "event": "新サービス商用化開始", "impact": 5, "type": "事業展開"}
                ]
            },
            "2025_q2": {
                "theme": "海外市場進出戦略",
                "description": "アジア太平洋地域への事業拡大",
                "events": [
                    {"day": 105, "event": "海外市場調査結果発表", "impact": 1, "type": "市場分析"},
                    {"day": 130, "event": "現地パートナー企業決定", "impact": 3, "type": "業務提携"},
                    {"day": 160, "event": "海外子会社設立認可", "impact": 4, "type": "事業展開"},
                    {"day": 180, "event": "海外向けサービス開始", "impact": 5, "type": "事業展開"}
                ]
            }
        }
    },
    
    "QOOG": {
        "name": "Qoogle",
        "industry": "量子コンピュータ",
        "initial_price": 158,
        "volatility": 0.035,
        "dividend_yield": 0.0,
        "business_detail": "量子コンピュータ・量子暗号技術",
        "revenue_breakdown": {"量子コンピュータ": 70, "暗号化ソリューション": 20, "研究開発受託": 10},
        "competitive_advantage": "量子もつれ技術の特許",
        "growth_drivers": ["政府量子戦略", "金融機関需要", "科学計算分野拡大"],
        "key_metrics": {"量子ビット数": "1024qubit", "計算速度": "従来比10000倍"},
        "earnings_months": [2, 5, 8, 11],
        "beat_probability": 0.6,
        "financial_profile": {
            "per_base": 60, "pbr_base": 12.0, "roe_base": 15, "profit_margin_base": 20
        },
        "story_arcs": {
            "2025_q1": {
                "theme": "量子コンピュータ商用化",
                "description": "金融機関向け量子暗号システム",
                "events": [
                    {"day": 20, "event": "計算性能大幅向上達成", "impact": 2, "type": "技術革新"},
                    {"day": 50, "event": "大手銀行での試験導入", "impact": 3, "type": "実証実験"},
                    {"day": 80, "event": "商用システム正式発表", "impact": 5, "type": "製品発表"}
                ]
            }
        }
    },
    
    "RBLX": {
        "name": "Roblux",
        "industry": "ゲーム開発",
        "initial_price": 72,
        "volatility": 0.025,
        "dividend_yield": 0.02,
        "business_detail": "ゲーム開発・ゲーミングプラットフォーム",
        "revenue_breakdown": {"ゲーム販売": 50, "アプリ内課金": 35, "広告収入": 15},
        "competitive_advantage": "独自のゲームエンジン技術",
        "growth_drivers": ["メタバース需要", "eスポーツ拡大", "VR/AR技術普及"],
        "key_metrics": {"月間アクティブユーザー": "800万人", "ゲーム本数": "150タイトル"},
        "earnings_months": [1, 4, 7, 10],
        "beat_probability": 0.8,
        "financial_profile": {
            "per_base": 25, "pbr_base": 4.5, "roe_base": 22, "profit_margin_base": 30
        },
        "story_arcs": {
            "2025_q1": {
                "theme": "メタバースプラットフォーム構築",
                "description": "次世代ゲーミング体験の創造",
                "events": [
                    {"day": 25, "event": "VR/AR技術統合発表", "impact": 3, "type": "技術革新"},
                    {"day": 55, "event": "著名クリエイター参画", "impact": 2, "type": "人材獲得"},
                    {"day": 85, "event": "メタバース空間β版公開", "impact": 4, "type": "製品発表"}
                ]
            }
        }
    },
    
    # 簡略化のため他7社は基本情報のみ
    "NFOX": {
        "name": "Netfox", "industry": "動画配信", "initial_price": 64,
        "earnings_months": [2, 5, 8, 11], "beat_probability": 0.6,
        "financial_profile": {"per_base": 35, "pbr_base": 6.0, "roe_base": 16, "profit_margin_base": 15}
    },
    "MOSL": {
        "name": "Mosla", "industry": "再生エネルギー", "initial_price": 48,
        "earnings_months": [3, 6, 9, 12], "beat_probability": 0.7,
        "financial_profile": {"per_base": 20, "pbr_base": 2.5, "roe_base": 12, "profit_margin_base": 10}
    },
    "NKDA": {
        "name": "Nikuda", "industry": "物流・配送", "initial_price": 32,
        "earnings_months": [1, 4, 7, 10], "beat_probability": 0.6,
        "financial_profile": {"per_base": 18, "pbr_base": 2.0, "roe_base": 14, "profit_margin_base": 8}
    },
    "FSCH": {
        "name": "Firma Schnitzel", "industry": "バイオテクノロジー", "initial_price": 142,
        "earnings_months": [2, 5, 8, 11], "beat_probability": 0.8,
        "financial_profile": {"per_base": 80, "pbr_base": 15.0, "roe_base": 10, "profit_margin_base": 35}
    },
    "IRHA": {
        "name": "Iroha", "industry": "医療IT", "initial_price": 76,
        "earnings_months": [3, 6, 9, 12], "beat_probability": 0.7,
        "financial_profile": {"per_base": 40, "pbr_base": 7.0, "roe_base": 20, "profit_margin_base": 22}
    },
    "STRK": {
        "name": "Strike", "industry": "デジタル決済", "initial_price": 98,
        "earnings_months": [1, 4, 7, 10], "beat_probability": 0.6,
        "financial_profile": {"per_base": 30, "pbr_base": 5.0, "roe_base": 18, "profit_margin_base": 28}
    },
    "ASST": {
        "name": "Assist", "industry": "銀行・金融", "initial_price": 45,
        "earnings_months": [2, 5, 8, 11], "beat_probability": 0.5,
        "financial_profile": {"per_base": 12, "pbr_base": 1.2, "roe_base": 10, "profit_margin_base": 35}
    }
}

# セクターローテーション（簡素化）
SECTOR_ROTATION_CYCLE = {
    "景気回復期": {
        "strong_sectors": ["AI・Bot開発", "ゲーム開発"],
        "weak_sectors": ["銀行・金融", "再生エネルギー"],
        "description": "成長株が強い時期",
        "factor": 2.0
    },
    "景気拡大期": {
        "strong_sectors": ["物流・配送", "医療IT"],
        "weak_sectors": ["デジタル決済"],
        "description": "実需関連が強い時期",
        "factor": 2.0
    },
    "景気減速期": {
        "strong_sectors": ["銀行・金融", "再生エネルギー"],
        "weak_sectors": ["ゲーム開発", "量子コンピュータ"],
        "description": "ディフェンシブ株が強い時期",
        "factor": 1.5
    },
    "景気後退期": {
        "strong_sectors": ["動画配信", "デジタル決済"],
        "weak_sectors": ["物流・配送", "バイオテクノロジー"],
        "description": "内需・消費関連が強い時期",
        "factor": 1.5
    }
}

# Discord設定
CHANNEL_IDS = {
    "investment_news": 1378237887446777997,
    "level_up_notifications": 1352859030715891782,
    "general": 1352859030715891782
}

ADMIN_USER_IDS = [
    "1249582099825164312",
    "867343308426444801"
]
```

---

## 📈 最適化された株価変動システム

### 高速・予測可能な価格計算
```python
# kraft_stock_market.py 内の関数
from shared.kraft_time import KraftTimeManager
from shared.kraft_config import UNIFIED_COMPANY_DATA, SECTOR_ROTATION_CYCLE

def calculate_optimized_price_change(ticker: str) -> float:
    """最適化された株価変動計算（高速・予測可能）"""
    
    company = UNIFIED_COMPANY_DATA[ticker]
    kraft_date = KraftTimeManager.get_kraft_date()
    kraft_day = KraftTimeManager.get_kraft_day_number()
    season = KraftTimeManager.get_season(kraft_date)
    
    # 1. 決定論的基本変動 (25%の比重)
    hash_seed = f"{ticker}{kraft_date.strftime('%Y-%m-%d')}"
    base_change = (hash(hash_seed) % 1000 / 1000 * 6 - 3) * 0.25
    
    # 2. セクターローテーション (40%の比重)
    sector_factor = get_sector_factor(company["industry"], season) * 0.40
    
    # 3. 決算効果 (30%の比重)
    earnings_factor = get_earnings_factor(ticker, kraft_date) * 0.30
    
    # 4. 小さなランダム要素 (5%の比重)
    random_factor = (hash(f"{ticker}{kraft_day}") % 100 / 100 - 0.5) * 0.1 * 0.05
    
    total_change = base_change + sector_factor + earnings_factor + random_factor
    
    return max(-8, min(8, round(total_change, 2)))

def get_sector_factor(industry: str, season: str) -> float:
    """セクター要因計算（予測可能）"""
    cycle_data = SECTOR_ROTATION_CYCLE[season]
    
    if industry in cycle_data["strong_sectors"]:
        return cycle_data["factor"]
    elif industry in cycle_data["weak_sectors"]:
        return -cycle_data["factor"] * 0.7
    else:
        return 0.0

def get_earnings_factor(ticker: str, kraft_date: datetime.datetime) -> float:
    """決算効果計算（予測可能）"""
    company = UNIFIED_COMPANY_DATA[ticker]
    earnings_months = company["earnings_months"]
    
    if kraft_date.month in earnings_months:
        # 決算月の効果
        beat_prob = company["beat_probability"]
        # 決定論的な好決算判定
        earnings_seed = hash(f"{ticker}{kraft_date.strftime('%Y-%m')}")
        if (earnings_seed % 100) / 100 < beat_prob:
            return 4.0  # 好決算
        else:
            return -3.0  # 失望決算
    
    return 0.0
```

---

## 📰 効率化されたニュース生成システム

### 段階的ニュース生成アプローチ
```python
class EfficientNewsEngine:
    """効率化されたニュース生成エンジン"""
    
    def __init__(self):
        self.claude_client = anthropic.Anthropic() if os.getenv("CLAUDE_API_KEY") else None
        
    async def generate_daily_news(self, kraft_date: datetime.datetime) -> List[Dict]:
        """日次ニュース生成（効率重視）"""
        
        kraft_day = KraftTimeManager.get_kraft_day_number()
        
        # 1. 予定イベントチェック（最優先・高速）
        scheduled_news = self.get_scheduled_events(kraft_day, kraft_date)
        if scheduled_news:
            return await self.process_scheduled_news(scheduled_news, kraft_date)
        
        # 2. 決算ニュース（予測可能）
        earnings_news = self.get_earnings_news(kraft_date)
        if earnings_news:
            return earnings_news
        
        # 3. AI生成ニュース（週2回程度）
        if self.claude_client and kraft_day % 3 == 0:  # 3日に1回
            ai_news = await self.generate_ai_news(kraft_date)
            if ai_news:
                return ai_news
        
        # 4. フォールバック：テンプレートニュース
        return self.generate_template_news(kraft_date)
    
    def get_scheduled_events(self, kraft_day: int, kraft_date: datetime.datetime) -> List[Dict]:
        """予定イベント取得（高速）"""
        events = []
        
        for ticker, company in UNIFIED_COMPANY_DATA.items():
            story_arcs = company.get("story_arcs", {})
            quarter = KraftTimeManager.get_quarter(kraft_date)
            
            quarter_key = f"{kraft_date.year}_q{quarter[-1]}"
            if quarter_key in story_arcs:
                arc = story_arcs[quarter_key]
                for event in arc["events"]:
                    if abs(event["day"] - kraft_day) <= 1:  # ±1日の余裕
                        events.append({
                            "ticker": ticker,
                            "company": company,
                            "event": event,
                            "arc": arc
                        })
        
        return events
    
    async def process_scheduled_news(self, events: List[Dict], kraft_date: datetime.datetime) -> List[Dict]:
        """予定イベントニュース処理"""
        news_list = []
        
        for event_data in events:
            if self.claude_client:
                # AI生成
                news = await self.generate_event_news_ai(event_data, kraft_date)
            else:
                # テンプレート生成
                news = self.generate_event_news_template(event_data, kraft_date)
            
            if news:
                news_list.append(news)
        
        return news_list
    
    def get_earnings_news(self, kraft_date: datetime.datetime) -> List[Dict]:
        """決算ニュース生成（テンプレート・高速）"""
        news_list = []
        
        for ticker, company in UNIFIED_COMPANY_DATA.items():
            if kraft_date.month in company["earnings_months"]:
                # 決算結果の判定
                beat_prob = company["beat_probability"]
                earnings_seed = hash(f"{ticker}{kraft_date.strftime('%Y-%m')}")
                is_beat = (earnings_seed % 100) / 100 < beat_prob
                
                news = {
                    "headline": f"{company['name']}、{kraft_date.month}月期決算を発表",
                    "content": f"{company['name']}は{kraft_date.month}月期決算を発表。"
                              f"{'市場予想を上回る好調な業績' if is_beat else '市場予想をやや下回る結果'}となった。"
                              f"同社の{company['industry']}事業が{'順調に成長' if is_beat else '一部で伸び悩み'}を見せている。",
                    "impact_score": 4 if is_beat else -3,
                    "ticker": ticker,
                    "news_type": "決算発表",
                    "kraft_date": kraft_date.isoformat(),
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    "is_template": True
                }
                news_list.append(news)
        
        return news_list
    
    def generate_template_news(self, kraft_date: datetime.datetime) -> List[Dict]:
        """テンプレートニュース生成（フォールバック）"""
        season = KraftTimeManager.get_season(kraft_date)
        cycle_data = SECTOR_ROTATION_CYCLE[season]
        
        # セクター動向ニュース
        strong_sector = random.choice(cycle_data["strong_sectors"])
        
        news = {
            "headline": f"{strong_sector}セクターに注目集まる",
            "content": f"{cycle_data['description']}となる中、{strong_sector}関連企業への投資家の関心が高まっている。"
                      f"市場関係者は「現在の{season}では{strong_sector}企業の業績拡大が期待される」と分析している。",
            "impact_score": 1,
            "affected_sectors": [strong_sector],
            "news_type": "市場動向",
            "kraft_date": kraft_date.isoformat(),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "is_template": True
        }
        
        return [news]
    
    async def generate_ai_news(self, kraft_date: datetime.datetime) -> List[Dict]:
        """AI生成ニュース（週2回程度）"""
        if not self.claude_client:
            return []
        
        season = KraftTimeManager.get_season(kraft_date)
        
        prompt = f"""
KRAFT世界の投資ニュースを1件生成してください。

## 現在状況
- 日付: {kraft_date.strftime('%Y年%m月%d日')}
- 景気局面: {season}

## 企業情報
{self.get_companies_summary()}

## 要件
1. 現実的で説得力のある内容
2. 150-250文字程度
3. 株価への影響度（-3〜+3）

## 出力形式（JSON）
{{
  "headline": "ニュース見出し",
  "content": "ニュース本文",
  "impact_score": 2,
  "news_type": "技術革新",
  "affected_companies": ["WICR"]
}}
"""
        
        try:
            response = await asyncio.to_thread(
                self.claude_client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            
            news_data = json.loads(response.content[0].text)
            news_data.update({
                "kraft_date": kraft_date.isoformat(),
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "is_ai_generated": True
            })
            
            return [news_data]
            
        except Exception as e:
            logger.error(f"AIニュース生成エラー: {e}")
            return []
    
    def get_companies_summary(self) -> str:
        """企業サマリー（短縮版）"""
        companies = []
        for ticker, company in list(UNIFIED_COMPANY_DATA.items())[:5]:  # 最初の5社のみ
            companies.append(f"{company['name']} ({ticker}): {company['industry']}")
        return "\n".join(companies)
```

---

## 💻 企業詳細ページ（簡素化版）

### 実装可能な規模での企業分析
```python
# kraft_analytics_web.py
from flask import Flask, render_template, jsonify
from shared.kraft_time import KraftTimeManager
from shared.kraft_config import UNIFIED_COMPANY_DATA, SECTOR_ROTATION_CYCLE

app = Flask(__name__)

@app.route('/company/<ticker>')
def company_detail(ticker):
    """企業詳細ページ（簡素化版）"""
    company = UNIFIED_COMPANY_DATA.get(ticker.upper())
    if not company:
        return "企業が見つかりません", 404
    
    kraft_date = KraftTimeManager.get_kraft_date()
    
    # 基本分析データ
    analysis_data = {
        "basic_info": get_basic_company_info(ticker, company),
        "financial_metrics": get_financial_simulation(ticker, company),
        "sector_analysis": get_sector_analysis(ticker, kraft_date),
        "investment_outlook": get_investment_outlook(ticker, kraft_date)
    }
    
    return render_template('company_simple.html', 
                         company=company,
                         ticker=ticker,
                         analysis=analysis_data,
                         kraft_date=kraft_date)

def get_basic_company_info(ticker: str, company: Dict) -> Dict:
    """基本企業情報"""
    current_price = get_current_stock_price(ticker)
    
    return {
        **company,
        "current_price": current_price,
        "market_cap": current_price * 1000000,  # 仮想発行株式数
        "price_change_today": calculate_optimized_price_change(ticker),
        "next_earnings": get_next_earnings_date(ticker)
    }

def get_financial_simulation(ticker: str, company: Dict) -> Dict:
    """財務指標シミュレーション（簡素版）"""
    profile = company.get("financial_profile", {})
    
    # 企業固有係数
    company_factor = (hash(ticker) % 100) / 100  # 0-1
    variation = 0.8 + company_factor * 0.4  # 0.8-1.2の範囲
    
    return {
        "per": round(profile.get("per_base", 20) * variation, 1),
        "pbr": round(profile.get("pbr_base", 3.0) * variation, 1),
        "roe": round(profile.get("roe_base", 15) * variation, 1),
        "profit_margin": round(profile.get("profit_margin_base", 15) * variation, 1),
        "beat_probability": company.get("beat_probability", 0.5) * 100,
        "dividend_yield": company.get("dividend_yield", 0) * 100
    }

def get_sector_analysis(ticker: str, kraft_date: datetime.datetime) -> Dict:
    """セクター分析"""
    company = UNIFIED_COMPANY_DATA[ticker]
    season = KraftTimeManager.get_season(kraft_date)
    cycle_data = SECTOR_ROTATION_CYCLE[season]
    
    industry = company["industry"]
    
    if industry in cycle_data["strong_sectors"]:
        outlook = "強気"
        factor = cycle_data["factor"]
    elif industry in cycle_data["weak_sectors"]:
        outlook = "弱気"
        factor = -cycle_data["factor"] * 0.7
    else:
        outlook = "中立"
        factor = 0
    
    return {
        "industry": industry,
        "season": season,
        "season_description": cycle_data["description"],
        "sector_outlook": outlook,
        "expected_factor": f"{factor:+.1f}%",
        "strong_sectors": cycle_data["strong_sectors"],
        "weak_sectors": cycle_data["weak_sectors"]
    }

def get_investment_outlook(ticker: str, kraft_date: datetime.datetime) -> Dict:
    """投資見通し（簡素版）"""
    company = UNIFIED_COMPANY_DATA[ticker]
    current_price = get_current_stock_price(ticker)
    
    # 簡易スコア計算
    sector_score = get_sector_score(ticker, kraft_date)
    earnings_score = get_earnings_score(ticker, kraft_date)
    
    total_score = (sector_score + earnings_score) / 2
    
    if total_score >= 3:
        recommendation = "買い"
        target_price = int(current_price * 1.2)
    elif total_score >= 1:
        recommendation = "中立"
        target_price = current_price
    else:
        recommendation = "売り"
        target_price = int(current_price * 0.9)
    
    return {
        "recommendation": recommendation,
        "target_price": target_price,
        "confidence": min(100, int(abs(total_score) * 25)),
        "key_factors": get_key_factors(ticker, kraft_date)
    }

# APIエンドポイント
@app.route('/api/market-summary')
def market_summary_api():
    """市場サマリーAPI"""
    kraft_date = KraftTimeManager.get_kraft_date()
    season = KraftTimeManager.get_season(kraft_date)
    
    summary = {
        "kraft_date": kraft_date.isoformat(),
        "season": season,
        "sector_rotation": SECTOR_ROTATION_CYCLE[season],
        "earnings_this_month": get_earnings_this_month(kraft_date),
        "top_movers": get_top_movers()
    }
    
    return jsonify(summary)
```

---

## 🚀 段階的実装ロードマップ（現実的版）

### Week 1: 基盤システム
- [x] **統一時間管理**: KraftTimeManager実装
- [x] **統合企業データ**: UNIFIED_COMPANY_DATA作成
- [x] **最適化株価計算**: 高速・予測可能な価格変動
- [ ] **基本Discord配信**: テンプレートニュース

### Week 2: ニュースシステム
- [ ] **EfficientNewsEngine**: 効率化ニュース生成
- [ ] **予定イベント**: ストーリーアーク基本実装
- [ ] **決算ニュース**: 自動決算発表
- [ ] **Discord統合**: 自動配信システム

### Week 3: AI強化（オプション）
- [ ] **Claude API統合**: AI生成ニュース
- [ ] **継続性エンジン**: 過去ニュース参照
- [ ] **ニュース履歴**: データベース保存・検索

### Week 4: Web分析サイト
- [ ] **Flask基盤**: 基本的なWebサイト
- [ ] **企業詳細ページ**: 簡素化版企業分析
- [ ] **市場サマリーAPI**: リアルタイム情報
- [ ] **統合テスト**: 全システム動作確認

### Week 5-6: 拡張・最適化
- [ ] **パフォーマンス調整**: レスポンス速度向上
- [ ] **エラーハンドリング**: 堅牢性向上
- [ ] **ユーザー学習機能**: 投資スキル測定
- [ ] **運用監視**: ログ・アラート機能

---

## 🎯 期待される効果（修正版）

### ✅ **実装可能性**
- **段階的開発**: 週単位の明確なマイルストーン
- **技術的実現性**: 複雑過ぎない設計
- **API効率化**: Claude呼び出し最小限

### ✅ **予測可能性の向上**
- **70%予測可能**: セクター(40%) + 決算(30%)
- **25%準予測可能**: 決定論的基本変動
- **5%ランダム**: 運要素を最小限

### ✅ **教育効果**
- **現実的パターン**: 実際の投資理論を反映
- **段階的学習**: Discord→Web の自然な流れ
- **継続的改善**: 予測精度向上で成長実感

### ✅ **運用効率**
- **高速レスポンス**: 複雑計算を排除
- **安定稼働**: フォールバック機能充実
- **拡張性**: 新機能追加が容易

この修正版により、**「実装可能で矛盾がなく、教育効果の高い投資シミュレーション」** が実現できます！