"""
Search tools manager with support for multiple search engines
"""

import json
import requests
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class SearchResult:
    """Search result data structure"""
    title: str
    url: str
    snippet: str
    source: str
    rank: int
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'url': self.url,
            'snippet': self.snippet,
            'source': self.source,
            'rank': self.rank,
            'metadata': self.metadata or {}
        }


class SearchEngine(ABC):
    """Abstract base class for search engines"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    def search(self, query: str, num_results: int = 10, **kwargs) -> List[SearchResult]:
        """Perform a search and return results"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the search engine is available"""
        pass


class DuckDuckGoSearch(SearchEngine):
    """DuckDuckGo search engine implementation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("duckduckgo", config)
    
    def search(self, query: str, num_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search using DuckDuckGo"""
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=num_results)
                
                for i, result in enumerate(search_results):
                    results.append(SearchResult(
                        title=result.get('title', ''),
                        url=result.get('href', ''),
                        snippet=result.get('body', ''),
                        source='duckduckgo',
                        rank=i + 1,
                        metadata={'published': result.get('published')}
                    ))
            
            return results
            
        except ImportError:
            raise ImportError("duckduckgo-search package not installed. Install with: pip install duckduckgo-search")
        except Exception as e:
            raise Exception(f"DuckDuckGo search error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if DuckDuckGo search is available"""
        try:
            import duckduckgo_search
            return True
        except ImportError:
            return False


class GoogleSearch(SearchEngine):
    """Google Custom Search API implementation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("google", config)
        self.api_key = self.config.get('api_key')
        self.search_engine_id = self.config.get('search_engine_id')
    
    def search(self, query: str, num_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search using Google Custom Search API"""
        if not self.api_key or not self.search_engine_id:
            raise ValueError("Google search requires api_key and search_engine_id in config")
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)  # Google API limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for i, item in enumerate(data.get('items', [])):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('snippet', ''),
                    source='google',
                    rank=i + 1,
                    metadata={
                        'display_link': item.get('displayLink'),
                        'formatted_url': item.get('formattedUrl')
                    }
                ))
            
            return results
            
        except Exception as e:
            raise Exception(f"Google search error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Google search is available"""
        return bool(self.api_key and self.search_engine_id)


class SerpApiSearch(SearchEngine):
    """SerpApi search engine implementation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("serpapi", config)
        self.api_key = self.config.get('api_key')
    
    def search(self, query: str, num_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search using SerpApi"""
        if not self.api_key:
            raise ValueError("SerpApi search requires api_key in config")
        
        try:
            url = "https://serpapi.com/search"
            params = {
                'api_key': self.api_key,
                'q': query,
                'num': num_results,
                'engine': 'google'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for i, item in enumerate(data.get('organic_results', [])):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('snippet', ''),
                    source='serpapi',
                    rank=i + 1,
                    metadata={
                        'position': item.get('position'),
                        'displayed_link': item.get('displayed_link')
                    }
                ))
            
            return results
            
        except Exception as e:
            raise Exception(f"SerpApi search error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if SerpApi search is available"""
        return bool(self.api_key)


class BraveSearch(SearchEngine):
    """Brave Search API implementation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("brave", config)
        self.api_key = self.config.get('api_key')
    
    def search(self, query: str, num_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search using Brave Search API"""
        if not self.api_key:
            raise ValueError("Brave search requires api_key in config")
        
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'X-Subscription-Token': self.api_key
            }
            params = {
                'q': query,
                'count': num_results
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for i, item in enumerate(data.get('web', {}).get('results', [])):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    snippet=item.get('description', ''),
                    source='brave',
                    rank=i + 1,
                    metadata={
                        'age': item.get('age'),
                        'language': item.get('language')
                    }
                ))
            
            return results
            
        except Exception as e:
            raise Exception(f"Brave search error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Brave search is available"""
        return bool(self.api_key)


class SearxngSearch(SearchEngine):
    """SearXNG search engine implementation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("searxng", config)
        self.instance_url = self.config.get('instance_url', 'https://searx.be')
    
    def search(self, query: str, num_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search using SearXNG instance"""
        try:
            url = f"{self.instance_url}/search"
            params = {
                'q': query,
                'format': 'json',
                'engines': 'google,bing,duckduckgo'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for i, item in enumerate(data.get('results', [])[:num_results]):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    snippet=item.get('content', ''),
                    source='searxng',
                    rank=i + 1,
                    metadata={
                        'engine': item.get('engine'),
                        'category': item.get('category')
                    }
                ))
            
            return results
            
        except Exception as e:
            raise Exception(f"SearXNG search error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if SearXNG search is available"""
        try:
            response = requests.get(f"{self.instance_url}/stats", timeout=5)
            return response.status_code == 200
        except:
            return False


class BaiduSearch(SearchEngine):
    """Baidu search implementation (simplified)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("baidu", config)
    
    def search(self, query: str, num_results: int = 10, **kwargs) -> List[SearchResult]:
        """Search using Baidu (web scraping approach)"""
        # Note: This is a simplified implementation
        # In production, you'd want to use Baidu's official API
        try:
            import requests
            from bs4 import BeautifulSoup
            
            url = "https://www.baidu.com/s"
            params = {'wd': query}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse Baidu search results (simplified)
            result_divs = soup.find_all('div', class_='result')[:num_results]
            
            for i, div in enumerate(result_divs):
                title_elem = div.find('h3')
                link_elem = div.find('a')
                snippet_elem = div.find('span', class_='content-right_8Zs40')
                
                if title_elem and link_elem:
                    results.append(SearchResult(
                        title=title_elem.get_text(strip=True),
                        url=link_elem.get('href', ''),
                        snippet=snippet_elem.get_text(strip=True) if snippet_elem else '',
                        source='baidu',
                        rank=i + 1
                    ))
            
            return results
            
        except Exception as e:
            raise Exception(f"Baidu search error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Baidu search is available"""
        try:
            import requests
            from bs4 import BeautifulSoup
            return True
        except ImportError:
            return False


class SearchToolsManager:
    """Manages multiple search engines and provides unified search interface"""
    
    def __init__(self, config: Dict[str, Dict[str, Any]] = None):
        self.config = config or {}
        self.engines: Dict[str, SearchEngine] = {}
        self.default_engine = "duckduckgo"
        
        # Initialize available search engines
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize all available search engines"""
        engine_classes = {
            'duckduckgo': DuckDuckGoSearch,
            'google': GoogleSearch,
            'serpapi': SerpApiSearch,
            'brave': BraveSearch,
            'searxng': SearxngSearch,
            'baidu': BaiduSearch
        }
        
        for engine_name, engine_class in engine_classes.items():
            try:
                engine_config = self.config.get(engine_name, {})
                engine = engine_class(engine_config)
                
                if engine.is_available():
                    self.engines[engine_name] = engine
                    
            except Exception as e:
                print(f"Failed to initialize {engine_name} search engine: {e}")
    
    def get_available_engines(self) -> List[str]:
        """Get list of available search engines"""
        return list(self.engines.keys())
    
    def set_default_engine(self, engine_name: str) -> bool:
        """Set the default search engine"""
        if engine_name in self.engines:
            self.default_engine = engine_name
            return True
        return False
    
    def search(self, query: str, engine: str = None, num_results: int = 10, 
              **kwargs) -> List[SearchResult]:
        """Perform a search using specified or default engine"""
        engine_name = engine or self.default_engine
        
        if engine_name not in self.engines:
            available = ', '.join(self.engines.keys())
            raise ValueError(f"Search engine '{engine_name}' not available. Available engines: {available}")
        
        search_engine = self.engines[engine_name]
        return search_engine.search(query, num_results, **kwargs)
    
    def multi_search(self, query: str, engines: List[str] = None, 
                    num_results: int = 10) -> Dict[str, List[SearchResult]]:
        """Search using multiple engines and return combined results"""
        if engines is None:
            engines = list(self.engines.keys())
        
        results = {}
        
        for engine_name in engines:
            if engine_name in self.engines:
                try:
                    engine_results = self.search(query, engine_name, num_results)
                    results[engine_name] = engine_results
                except Exception as e:
                    print(f"Error searching with {engine_name}: {e}")
                    results[engine_name] = []
        
        return results
    
    def aggregate_results(self, multi_results: Dict[str, List[SearchResult]], 
                         max_results: int = 20) -> List[SearchResult]:
        """Aggregate and deduplicate results from multiple engines"""
        all_results = []
        seen_urls = set()
        
        # Collect all results
        for engine_results in multi_results.values():
            for result in engine_results:
                if result.url not in seen_urls:
                    all_results.append(result)
                    seen_urls.add(result.url)
        
        # Sort by relevance (using rank from original engine)
        all_results.sort(key=lambda x: x.rank)
        
        # Re-rank the aggregated results
        for i, result in enumerate(all_results[:max_results]):
            result.rank = i + 1
        
        return all_results[:max_results]
    
    def search_and_aggregate(self, query: str, engines: List[str] = None,
                           num_results_per_engine: int = 10,
                           max_final_results: int = 20) -> List[SearchResult]:
        """Perform multi-engine search and return aggregated results"""
        multi_results = self.multi_search(query, engines, num_results_per_engine)
        return self.aggregate_results(multi_results, max_final_results)
    
    def get_engine_info(self, engine_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific search engine"""
        if engine_name not in self.engines:
            return None
        
        engine = self.engines[engine_name]
        return {
            'name': engine.name,
            'available': engine.is_available(),
            'config_keys': list(engine.config.keys()) if engine.config else []
        }
    
    def get_all_engines_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all search engines"""
        return {
            name: self.get_engine_info(name) 
            for name in self.engines.keys()
        }
    
    def configure_engine(self, engine_name: str, config: Dict[str, Any]) -> bool:
        """Configure a search engine"""
        if engine_name not in self.engines:
            return False
        
        self.engines[engine_name].config.update(config)
        return True
    
    def test_engine(self, engine_name: str, test_query: str = "test") -> Dict[str, Any]:
        """Test a search engine with a simple query"""
        if engine_name not in self.engines:
            return {'success': False, 'error': f'Engine {engine_name} not available'}
        
        try:
            results = self.search(test_query, engine_name, num_results=3)
            return {
                'success': True,
                'results_count': len(results),
                'sample_result': results[0].to_dict() if results else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def export_results(self, results: List[SearchResult], format: str = "json") -> str:
        """Export search results in different formats"""
        if format == "json":
            return json.dumps([result.to_dict() for result in results], indent=2)
        
        elif format == "csv":
            lines = ["rank,title,url,snippet,source"]
            for result in results:
                # Escape commas and quotes in CSV
                title = result.title.replace('"', '""').replace(',', ';')
                snippet = result.snippet.replace('"', '""').replace(',', ';')
                lines.append(f'{result.rank},"{title}",{result.url},"{snippet}",{result.source}')
            return "\n".join(lines)
        
        elif format == "markdown":
            lines = ["# Search Results", ""]
            for result in results:
                lines.append(f"## {result.rank}. [{result.title}]({result.url})")
                lines.append(f"**Source:** {result.source}")
                lines.append(f"{result.snippet}")
                lines.append("")
            return "\n".join(lines)
        
        elif format == "text":
            lines = []
            for result in results:
                lines.append(f"{result.rank}. {result.title}")
                lines.append(f"   URL: {result.url}")
                lines.append(f"   Source: {result.source}")
                lines.append(f"   {result.snippet}")
                lines.append("")
            return "\n".join(lines)
        
        return ""

