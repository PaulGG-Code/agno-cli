"""
Financial tools manager with yfinance and other financial data sources
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class StockInfo:
    """Stock information data structure"""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': self.price,
            'change': self.change,
            'change_percent': self.change_percent,
            'volume': self.volume,
            'market_cap': self.market_cap,
            'pe_ratio': self.pe_ratio,
            'dividend_yield': self.dividend_yield,
            'fifty_two_week_high': self.fifty_two_week_high,
            'fifty_two_week_low': self.fifty_two_week_low
        }


@dataclass
class NewsItem:
    """Financial news item"""
    title: str
    summary: str
    url: str
    published: datetime
    source: str
    sentiment: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'summary': self.summary,
            'url': self.url,
            'published': self.published.isoformat(),
            'source': self.source,
            'sentiment': self.sentiment
        }


class FinancialToolsManager:
    """Manager for financial data tools and analysis"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required dependencies are available"""
        try:
            import yfinance as yf
            self.yf = yf
        except ImportError:
            raise ImportError("yfinance package not installed. Install with: pip install yfinance")
        
        try:
            import pandas as pd
            self.pd = pd
        except ImportError:
            raise ImportError("pandas package not installed. Install with: pip install pandas")
    
    def get_stock_info(self, symbol: str) -> Optional[StockInfo]:
        """Get current stock information"""
        try:
            ticker = self.yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'regularMarketPrice' not in info:
                return None
            
            current_price = info.get('regularMarketPrice', 0)
            previous_close = info.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close != 0 else 0
            
            return StockInfo(
                symbol=symbol.upper(),
                name=info.get('longName', symbol),
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=info.get('regularMarketVolume', 0),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
                fifty_two_week_low=info.get('fiftyTwoWeekLow')
            )
            
        except Exception as e:
            print(f"Error getting stock info for {symbol}: {e}")
            return None
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Optional[StockInfo]]:
        """Get information for multiple stocks"""
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_stock_info(symbol)
        return results
    
    def get_historical_data(self, symbol: str, period: str = "1y", 
                          interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get historical stock data"""
        try:
            ticker = self.yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return None
            
            return data
            
        except Exception as e:
            print(f"Error getting historical data for {symbol}: {e}")
            return None
    
    def get_stock_news(self, symbol: str, limit: int = 10) -> List[NewsItem]:
        """Get recent news for a stock"""
        try:
            ticker = self.yf.Ticker(symbol)
            news = ticker.news
            
            news_items = []
            for item in news[:limit]:
                published = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                
                news_items.append(NewsItem(
                    title=item.get('title', ''),
                    summary=item.get('summary', ''),
                    url=item.get('link', ''),
                    published=published,
                    source=item.get('publisher', '')
                ))
            
            return news_items
            
        except Exception as e:
            print(f"Error getting news for {symbol}: {e}")
            return []
    
    def get_analyst_recommendations(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get analyst recommendations for a stock"""
        try:
            ticker = self.yf.Ticker(symbol)
            recommendations = ticker.recommendations
            
            if recommendations is None or recommendations.empty:
                return None
            
            # Get the most recent recommendations
            recent = recommendations.tail(1).iloc[0]
            
            return {
                'symbol': symbol.upper(),
                'date': recent.name.strftime('%Y-%m-%d'),
                'strong_buy': int(recent.get('strongBuy', 0)),
                'buy': int(recent.get('buy', 0)),
                'hold': int(recent.get('hold', 0)),
                'sell': int(recent.get('sell', 0)),
                'strong_sell': int(recent.get('strongSell', 0)),
                'total_analysts': int(recent.sum())
            }
            
        except Exception as e:
            print(f"Error getting recommendations for {symbol}: {e}")
            return None
    
    def get_financial_statements(self, symbol: str, statement_type: str = "income") -> Optional[pd.DataFrame]:
        """Get financial statements (income, balance, cashflow)"""
        try:
            ticker = self.yf.Ticker(symbol)
            
            if statement_type.lower() == "income":
                return ticker.financials
            elif statement_type.lower() == "balance":
                return ticker.balance_sheet
            elif statement_type.lower() == "cashflow":
                return ticker.cashflow
            else:
                raise ValueError("statement_type must be 'income', 'balance', or 'cashflow'")
                
        except Exception as e:
            print(f"Error getting {statement_type} statement for {symbol}: {e}")
            return None
    
    def calculate_returns(self, symbol: str, period: str = "1y") -> Optional[Dict[str, float]]:
        """Calculate various return metrics"""
        try:
            data = self.get_historical_data(symbol, period)
            if data is None or data.empty:
                return None
            
            # Calculate returns
            first_price = data['Close'].iloc[0]
            last_price = data['Close'].iloc[-1]
            total_return = (last_price - first_price) / first_price
            
            # Calculate daily returns
            daily_returns = data['Close'].pct_change().dropna()
            
            # Calculate volatility (annualized)
            volatility = daily_returns.std() * (252 ** 0.5)  # 252 trading days
            
            # Calculate Sharpe ratio (assuming 0% risk-free rate)
            sharpe_ratio = daily_returns.mean() / daily_returns.std() * (252 ** 0.5)
            
            # Calculate max drawdown
            cumulative = (1 + daily_returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            return {
                'symbol': symbol.upper(),
                'period': period,
                'total_return': total_return,
                'annualized_return': (1 + total_return) ** (365 / len(data)) - 1,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'best_day': daily_returns.max(),
                'worst_day': daily_returns.min()
            }
            
        except Exception as e:
            print(f"Error calculating returns for {symbol}: {e}")
            return None
    
    def compare_stocks(self, symbols: List[str], period: str = "1y") -> Optional[Dict[str, Any]]:
        """Compare multiple stocks"""
        try:
            comparison_data = {}
            
            for symbol in symbols:
                stock_info = self.get_stock_info(symbol)
                returns = self.calculate_returns(symbol, period)
                
                if stock_info and returns:
                    comparison_data[symbol] = {
                        'current_price': stock_info.price,
                        'market_cap': stock_info.market_cap,
                        'pe_ratio': stock_info.pe_ratio,
                        'total_return': returns['total_return'],
                        'volatility': returns['volatility'],
                        'sharpe_ratio': returns['sharpe_ratio'],
                        'max_drawdown': returns['max_drawdown']
                    }
            
            if not comparison_data:
                return None
            
            # Create comparison DataFrame
            df = self.pd.DataFrame(comparison_data).T
            
            # Add rankings
            rankings = {}
            for metric in ['total_return', 'sharpe_ratio']:
                if metric in df.columns:
                    rankings[f'{metric}_rank'] = df[metric].rank(ascending=False)
            
            for metric in ['volatility', 'max_drawdown']:
                if metric in df.columns:
                    rankings[f'{metric}_rank'] = df[metric].rank(ascending=True)
            
            ranking_df = self.pd.DataFrame(rankings)
            
            return {
                'comparison_data': df.to_dict('index'),
                'rankings': ranking_df.to_dict('index'),
                'period': period,
                'best_performer': df['total_return'].idxmax() if 'total_return' in df.columns else None,
                'lowest_volatility': df['volatility'].idxmin() if 'volatility' in df.columns else None
            }
            
        except Exception as e:
            print(f"Error comparing stocks: {e}")
            return None
    
    def get_sector_performance(self, sector_etfs: Dict[str, str] = None) -> Dict[str, Any]:
        """Get sector performance using sector ETFs"""
        if sector_etfs is None:
            sector_etfs = {
                'Technology': 'XLK',
                'Healthcare': 'XLV',
                'Financials': 'XLF',
                'Consumer Discretionary': 'XLY',
                'Communication Services': 'XLC',
                'Industrials': 'XLI',
                'Consumer Staples': 'XLP',
                'Energy': 'XLE',
                'Utilities': 'XLU',
                'Real Estate': 'XLRE',
                'Materials': 'XLB'
            }
        
        sector_data = {}
        
        for sector, etf_symbol in sector_etfs.items():
            stock_info = self.get_stock_info(etf_symbol)
            if stock_info:
                sector_data[sector] = {
                    'symbol': etf_symbol,
                    'price': stock_info.price,
                    'change_percent': stock_info.change_percent,
                    'volume': stock_info.volume
                }
        
        return sector_data
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get overall market summary"""
        market_indices = {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC',
            'Russell 2000': '^RUT',
            'VIX': '^VIX'
        }
        
        market_data = {}
        
        for index_name, symbol in market_indices.items():
            stock_info = self.get_stock_info(symbol)
            if stock_info:
                market_data[index_name] = {
                    'symbol': symbol,
                    'price': stock_info.price,
                    'change': stock_info.change,
                    'change_percent': stock_info.change_percent
                }
        
        return market_data
    
    def screen_stocks(self, criteria: Dict[str, Any], symbols: List[str] = None) -> List[Dict[str, Any]]:
        """Screen stocks based on criteria"""
        if symbols is None:
            # Use S&P 500 symbols as default (simplified list)
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B', 'JNJ', 'V']
        
        screened_stocks = []
        
        for symbol in symbols:
            stock_info = self.get_stock_info(symbol)
            if not stock_info:
                continue
            
            # Check criteria
            passes_screen = True
            
            if 'min_price' in criteria and stock_info.price < criteria['min_price']:
                passes_screen = False
            
            if 'max_price' in criteria and stock_info.price > criteria['max_price']:
                passes_screen = False
            
            if 'min_market_cap' in criteria and (not stock_info.market_cap or stock_info.market_cap < criteria['min_market_cap']):
                passes_screen = False
            
            if 'max_pe_ratio' in criteria and (not stock_info.pe_ratio or stock_info.pe_ratio > criteria['max_pe_ratio']):
                passes_screen = False
            
            if 'min_dividend_yield' in criteria and (not stock_info.dividend_yield or stock_info.dividend_yield < criteria['min_dividend_yield']):
                passes_screen = False
            
            if passes_screen:
                screened_stocks.append(stock_info.to_dict())
        
        return screened_stocks
    
    def get_options_data(self, symbol: str, expiration_date: str = None) -> Optional[Dict[str, Any]]:
        """Get options data for a stock"""
        try:
            ticker = self.yf.Ticker(symbol)
            
            # Get available expiration dates
            expirations = ticker.options
            if not expirations:
                return None
            
            # Use first available expiration if none specified
            if expiration_date is None:
                expiration_date = expirations[0]
            elif expiration_date not in expirations:
                return None
            
            # Get options chain
            options_chain = ticker.option_chain(expiration_date)
            
            return {
                'symbol': symbol.upper(),
                'expiration_date': expiration_date,
                'calls': options_chain.calls.to_dict('records'),
                'puts': options_chain.puts.to_dict('records'),
                'available_expirations': list(expirations)
            }
            
        except Exception as e:
            print(f"Error getting options data for {symbol}: {e}")
            return None
    
    def export_data(self, data: Any, format: str = "json") -> str:
        """Export financial data in different formats"""
        if format == "json":
            if isinstance(data, pd.DataFrame):
                return data.to_json(indent=2, date_format='iso')
            else:
                return json.dumps(data, indent=2, default=str)
        
        elif format == "csv":
            if isinstance(data, pd.DataFrame):
                return data.to_csv()
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                df = self.pd.DataFrame(data)
                return df.to_csv(index=False)
            else:
                return str(data)
        
        elif format == "markdown":
            if isinstance(data, pd.DataFrame):
                return data.to_markdown()
            elif isinstance(data, dict):
                lines = ["# Financial Data", ""]
                for key, value in data.items():
                    lines.append(f"## {key}")
                    if isinstance(value, dict):
                        for k, v in value.items():
                            lines.append(f"- **{k}**: {v}")
                    else:
                        lines.append(f"{value}")
                    lines.append("")
                return "\n".join(lines)
        
        return str(data)
    
    def create_portfolio_analysis(self, holdings: Dict[str, float], period: str = "1y") -> Dict[str, Any]:
        """Analyze a portfolio of stocks with weights"""
        try:
            portfolio_data = {}
            total_weight = sum(holdings.values())
            
            # Normalize weights
            normalized_weights = {symbol: weight/total_weight for symbol, weight in holdings.items()}
            
            # Get data for each holding
            portfolio_returns = []
            portfolio_value = 0
            
            for symbol, weight in normalized_weights.items():
                stock_info = self.get_stock_info(symbol)
                returns = self.calculate_returns(symbol, period)
                
                if stock_info and returns:
                    portfolio_data[symbol] = {
                        'weight': weight,
                        'current_price': stock_info.price,
                        'total_return': returns['total_return'],
                        'contribution': weight * returns['total_return']
                    }
                    
                    portfolio_returns.append(returns['total_return'] * weight)
                    portfolio_value += weight * stock_info.price
            
            # Calculate portfolio metrics
            portfolio_return = sum(portfolio_returns)
            
            return {
                'holdings': portfolio_data,
                'portfolio_return': portfolio_return,
                'portfolio_value': portfolio_value,
                'period': period,
                'best_performer': max(portfolio_data.items(), key=lambda x: x[1]['total_return'])[0] if portfolio_data else None,
                'worst_performer': min(portfolio_data.items(), key=lambda x: x[1]['total_return'])[0] if portfolio_data else None
            }
            
        except Exception as e:
            print(f"Error analyzing portfolio: {e}")
            return {}

