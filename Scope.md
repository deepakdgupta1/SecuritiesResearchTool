📊 Data Sources & Market Coverage

Market Coverage: Which securities markets do you want to analyze?
Geography: India, US
Securities Type: Equities/Stocks 
Data Granularity: Daily
Historical Depth: 20 years
Data Providers: Zerodha for Indian Market, I have not yet selected a data provider for US market
Data Recency: Historical only

🔍 Pattern Recognition & Analysis
Chart Patterns: Minvervini’s Trend Template, Volatility Contraction Pattern (VCP), Cup with Handle, Double Bottom, High-Tight Bull Flag (Power Play)

Technical Indicators: EMA, MACD, RSI, Volume-based indicators
Custom indicator creation capability: No
Pattern Detection: Automated
Pattern Confirmation: Manual
Alert/notification system when patterns are detected: Append to “ideas.log” file with timestamp

🧪 Backtesting Capabilities
Trading Strategies: Trend following, Mean reversion, Breakout
Position Type: Long positions, short selling
Securities Count: Single security (not portfolio based)
Analysis timeframes: Multiple

Execution Logic:
Entry/Exit rules complexity: High
Position sizing method: To be parked for future development (not part of the MVP).
Pyramid/scale-in/out capabilities: To be parked for future development (not part of the MVP).

Risk Management:
Stop-loss types (Fixed %, ATR-based, Trailing): Looking for a hybrid method that combines the best of all popular approaches and overcomes the flaws of each of them. To be discussed.
Take-profit/target mechanisms: Looking for a hybrid method that combines the best of all popular approaches and overcomes the flaws of each of them. To be discussed.
Maximum drawdown limits: Looking for a hybrid method that combines the best of all popular approaches and overcomes the flaws of each of them. To be discussed.
Portfolio-level risk controls: Yes, required.

Realism & Costs:
Slippage modeling: To be parked for future development. Not required in the MVP.
Commission/brokerage fees: To be parked for future development. Not required in the MVP.
Market impact (for large positions): To be parked for future development. Not required in the MVP.
Gap handling (overnight, weekend): To be parked for future development. Not required in the MVP.

Performance Metrics: Returns (Total, Annualized, CAGR), Risk metrics (Sharpe, Sortino, Max Drawdown), Win rate, Profit Factor

Optimization: To be parked for future development. Not required in the MVP.
Parameter optimization needed: To be parked for future development. Not required in the MVP.
Walk-forward testing: To be parked for future development. Not required in the MVP.
Monte Carlo simulation: To be parked for future development. Not required in the MVP.

💻 User Interface & Experience
Platform Type: Web application

User Interaction:
Interactive charting: To be parked for future development. Not required in the MVP.
Drag-and-drop capabilities: To be parked for future development. Not required in the MVP.
Scripting/coding interface for advanced users: To be parked for future development. Not required in the MVP.
Visual strategy builder: To be parked for future development. Not required in the MVP.

Visualization:
Charting library preferences: Open to suggestions.
Report formats: csv
Comparative analysis: To be parked for future development. Not required in the MVP.

Users:
Single user system
Need for user accounts, authentication: No
Collaboration features: No

⚙️ Technical Preferences & Constraints

Technology Stack:
Programming language preference: Open to recommendations
Any existing tech stack you want to leverage: Open to recommendations

Performance:
How many securities to analyze simultaneously: All
Speed requirements: Overnight batch processing for intermediate metrics
Data volume estimates: 5 million rows of price data dating back upto 20 years for 10000 securities

Infrastructure:
Deployment mode: Local installation. Cloud installation to be parked for future development (not part of the MVP)
Database preferences: Open to recommendations

Scalability requirements?
Integration:
Need to integrate with existing tools (TradingView, Excel, broker APIs): To be parked for future development. Not part of the MVP.
Export/Import capabilities: To be parked for future development. Not part of the MVP.

🎯 MVP Scope Definition
Must-Have vs. Nice-to-Have: all features that will help analyze historical data to identify investment opportunities are must-have. All other features are nice to have. Please refer to my remarks against each feature in the above list to discern prioritization.

Timeline:
Any target timeline for MVP: Flexible
Constraints that might affect scope: Minimize complexity of scope for MVP.

Success Criteria:
The system should be able to tell me, at any point of time, which securities are worth investing in with good chances of generating profit in the near future.
The specific use-case I want to validate first is whether the SEPA methodology developed by Mark Minervini actually generates supernormal profits over time or not.

Minvervini's Trend Template Criteria:
Stock above 150-day and 200-day moving averages
150-day MA > 200-day MA
200-day MA trending up for at least 1 month
50-day MA > 150-day MA and 200-day MA
Stock price > 30% above 52-week low
Stock price within 25% of 52-week high
Relative strength (RS) rating > 70 

VCP Pattern Recognition: 
Number of contractions required (2-4 pullbacks)
Each pullback must be shallower than the previous
Volume contraction during pullbacks
Tolerance level: 20%

Stage Analysis: The system should identify Weinstein's market stages - Stage 1 (Base), Stage 2 (Advancing), Stage 3 (Top), Stage 4 (Decline)
Analysis level: Individual stocks only

Risk Management - 
Stop-Loss: Start with fixed 10%, then switch to trailing stop once position is up x%
Take-Profit: Hybrid Proposal: Initial target at predetermined level, then trailing stop for remainder

Data Provider for US Market: Yahoo Finance (yfinance library)

Relative Strength Calculation
Mansfield RS: Stock price / Market index, then smoothed 

Backtesting Workflow needs to follow Scenario A for the MVP. We will target Scenario B in the future.

Scenario A (Systematic):
System scans all 10,000 stocks daily
Identifies stocks meeting criteria (e.g., Trend Template + VCP)
Automatically records recommended trades to ideas.log based on entry/exit rules
Tracks performance of the recommended trades over time
Generates performance metrics

Scenario B (Discretionary-Assisted):
System identifies candidates meeting pattern criteria
Logs to ideas.log with timestamp
User manually reviews and decides which to include in backtest
User specifies entry/exit rules per idea
Automatically records recommended trades to ideas.log based on entry/exit rules
Tracks performance of the recommended trades over time
Generates performance metrics

Portfolio-Level Risk Controls
Maximum position size as % of total capital (e.g., 10% per position)
Maximum number of concurrent positions being tracked
Total portfolio drawdown limit (stop all new positions if portfolio down X%)

Multiple Timeframe Analysis:
Weekly and monthly views derived from daily data
Different moving average periods. e.g. 50, 150, 200 on daily charts. 10, 30, 40 on weekly charts.

MVP Output - "Ideas Log" Clarification
When a pattern is detected and logged to ideas.log, the following information should be included -
Symbol, Date, Pattern Type, Key metrics (price, volume, RS), Confidence score, recommended trade (buy/sell), entry/exit rules (stop loss, take profit), rationales