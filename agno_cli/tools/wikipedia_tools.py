"""
Wikipedia Tools - Research and Knowledge Retrieval

This module provides Wikipedia research capabilities with:
- Advanced search functionality
- Content retrieval and parsing
- Article summaries and extracts
- Related articles discovery
- Language support
- Rich output formatting
- Caching and performance optimization
"""

import os
import sys
import json
import time
import re
import html
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown
import wikipedia
from wikipedia.exceptions import WikipediaException, DisambiguationError, PageError


@dataclass
class WikipediaSearchResult:
    """Wikipedia search result"""
    title: str
    pageid: int
    snippet: str
    url: str
    wordcount: int
    timestamp: str
    categories: List[str]
    links: List[str]


@dataclass
class WikipediaArticle:
    """Wikipedia article information"""
    title: str
    pageid: int
    url: str
    summary: str
    content: str
    categories: List[str]
    links: List[str]
    references: List[str]
    images: List[str]
    wordcount: int
    last_modified: str
    language: str


@dataclass
class WikipediaSummary:
    """Wikipedia article summary"""
    title: str
    summary: str
    url: str
    wordcount: int
    categories: List[str]
    related_topics: List[str]


class WikipediaTools:
    """Core Wikipedia research tools"""
    
    def __init__(self, language: str = "en"):
        self.console = Console()
        self.language = language
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AgnoCLI/1.0 (https://github.com/agno-ai/agno-cli)'
        })
        
        # Set Wikipedia language
        wikipedia.set_lang(language)
        
        # Cache for search results and articles
        self._search_cache = {}
        self._article_cache = {}
        self._cache_timeout = 3600  # 1 hour
    
    def search(self, query: str, limit: int = 10, suggestion: bool = True) -> List[WikipediaSearchResult]:
        """Search Wikipedia articles"""
        try:
            # Check cache first
            cache_key = f"search_{query}_{limit}_{self.language}"
            if cache_key in self._search_cache:
                cached_time, cached_results = self._search_cache[cache_key]
                if time.time() - cached_time < self._cache_timeout:
                    return cached_results
            
            # Perform search
            search_results = wikipedia.search(query, results=limit, suggestion=suggestion)
            
            if isinstance(search_results, tuple):
                results, suggestion = search_results
            else:
                results = search_results
                suggestion = None
            
            # Convert to our format
            formatted_results = []
            for result in results:
                try:
                    # Get page info
                    page = wikipedia.page(result, auto_suggest=False)
                    
                    # Extract categories
                    categories = []
                    try:
                        categories = page.categories[:10]  # Limit to first 10
                    except:
                        pass
                    
                    # Extract links
                    links = []
                    try:
                        links = list(page.links)[:20]  # Limit to first 20
                    except:
                        pass
                    
                    formatted_results.append(WikipediaSearchResult(
                        title=page.title,
                        pageid=page.pageid,
                        snippet=page.summary[:200] + "..." if len(page.summary) > 200 else page.summary,
                        url=page.url,
                        wordcount=getattr(page, 'wordcount', 0),
                        timestamp=getattr(page, 'timestamp', ''),
                        categories=categories,
                        links=links
                    ))
                except (PageError, DisambiguationError):
                    # Skip problematic pages
                    continue
            
            # Cache results
            self._search_cache[cache_key] = (time.time(), formatted_results)
            
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    def get_article(self, title: str, auto_suggest: bool = True) -> WikipediaArticle:
        """Get full Wikipedia article"""
        try:
            # Check cache first
            cache_key = f"article_{title}_{self.language}"
            if cache_key in self._article_cache:
                cached_time, cached_article = self._article_cache[cache_key]
                if time.time() - cached_time < self._cache_timeout:
                    return cached_article
            
            # Get page
            page = wikipedia.page(title, auto_suggest=auto_suggest)
            
            # Extract content
            content = page.content
            
            # Extract categories
            categories = []
            try:
                categories = page.categories[:20]  # Limit to first 20
            except:
                pass
            
            # Extract links
            links = []
            try:
                links = list(page.links)[:50]  # Limit to first 50
            except:
                pass
            
            # Extract references
            references = []
            try:
                references = page.references[:20]  # Limit to first 20
            except:
                pass
            
            # Extract images
            images = []
            try:
                images = page.images[:10]  # Limit to first 10
            except:
                pass
            
            article = WikipediaArticle(
                title=page.title,
                pageid=page.pageid,
                url=page.url,
                summary=page.summary,
                content=content,
                categories=categories,
                links=links,
                references=references,
                images=images,
                wordcount=getattr(page, 'wordcount', 0),
                last_modified=getattr(page, 'timestamp', ''),
                language=self.language
            )
            
            # Cache article
            self._article_cache[cache_key] = (time.time(), article)
            
            return article
            
        except PageError:
            raise Exception(f"Article '{title}' not found")
        except DisambiguationError as e:
            # Handle disambiguation pages
            options = e.options[:10]  # Limit to first 10 options
            raise Exception(f"Disambiguation page. Options: {', '.join(options)}")
        except Exception as e:
            raise Exception(f"Failed to get article: {str(e)}")
    
    def get_summary(self, title: str, sentences: int = 3, auto_suggest: bool = True) -> WikipediaSummary:
        """Get article summary"""
        try:
            # Get summary
            summary = wikipedia.summary(title, sentences=sentences, auto_suggest=auto_suggest)
            
            # Get page for additional info
            page = wikipedia.page(title, auto_suggest=auto_suggest)
            
            # Extract categories
            categories = []
            try:
                categories = page.categories[:10]
            except:
                pass
            
            # Get related topics (first few links)
            related_topics = []
            try:
                related_topics = list(page.links)[:15]
            except:
                pass
            
            return WikipediaSummary(
                title=page.title,
                summary=summary,
                url=page.url,
                wordcount=getattr(page, 'wordcount', 0),
                categories=categories,
                related_topics=related_topics
            )
            
        except PageError:
            raise Exception(f"Article '{title}' not found")
        except DisambiguationError as e:
            options = e.options[:10]
            raise Exception(f"Disambiguation page. Options: {', '.join(options)}")
        except Exception as e:
            raise Exception(f"Failed to get summary: {str(e)}")
    
    def get_random_article(self, language: Optional[str] = None) -> WikipediaArticle:
        """Get a random Wikipedia article"""
        try:
            if language:
                wikipedia.set_lang(language)
            
            # Get random page title
            random_title = wikipedia.random(1)[0]
            
            # Get the article
            return self.get_article(random_title)
            
        except Exception as e:
            raise Exception(f"Failed to get random article: {str(e)}")
    
    def get_related_articles(self, title: str, limit: int = 10) -> List[WikipediaSearchResult]:
        """Get articles related to a given title"""
        try:
            # Get the main article
            article = self.get_article(title)
            
            # Get related articles from links
            related = []
            for link in article.links[:limit]:
                try:
                    # Get basic info for each link
                    page = wikipedia.page(link, auto_suggest=False)
                    
                    related.append(WikipediaSearchResult(
                        title=page.title,
                        pageid=page.pageid,
                        snippet=page.summary[:150] + "..." if len(page.summary) > 150 else page.summary,
                        url=page.url,
                        wordcount=getattr(page, 'wordcount', 0),
                        timestamp=getattr(page, 'timestamp', ''),
                        categories=page.categories[:5] if hasattr(page, 'categories') else [],
                        links=[]
                    ))
                except (PageError, DisambiguationError):
                    continue
            
            return related
            
        except Exception as e:
            raise Exception(f"Failed to get related articles: {str(e)}")
    
    def get_article_categories(self, title: str) -> List[str]:
        """Get categories for an article"""
        try:
            page = wikipedia.page(title, auto_suggest=True)
            return page.categories[:20]  # Limit to first 20
            
        except Exception as e:
            raise Exception(f"Failed to get categories: {str(e)}")
    
    def get_category_articles(self, category: str, limit: int = 20) -> List[WikipediaSearchResult]:
        """Get articles in a category"""
        try:
            # Search for category
            category_page = wikipedia.page(f"Category:{category}", auto_suggest=False)
            
            # Extract article links from category page
            articles = []
            for link in category_page.links:
                if not link.startswith('Category:') and not link.startswith('Template:'):
                    try:
                        page = wikipedia.page(link, auto_suggest=False)
                        
                        articles.append(WikipediaSearchResult(
                            title=page.title,
                            pageid=page.pageid,
                            snippet=page.summary[:150] + "..." if len(page.summary) > 150 else page.summary,
                            url=page.url,
                            wordcount=getattr(page, 'wordcount', 0),
                            timestamp=getattr(page, 'timestamp', ''),
                            categories=page.categories[:5] if hasattr(page, 'categories') else [],
                            links=[]
                        ))
                        
                        if len(articles) >= limit:
                            break
                            
                    except (PageError, DisambiguationError):
                        continue
            
            return articles
            
        except Exception as e:
            raise Exception(f"Failed to get category articles: {str(e)}")
    
    def search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """Get search suggestions for a query"""
        try:
            # Use Wikipedia's search with suggestions
            results, suggestions = wikipedia.search(query, results=limit, suggestion=True)
            
            if suggestions:
                return [suggestions] + results[:limit-1]
            else:
                return results[:limit]
                
        except Exception as e:
            raise Exception(f"Failed to get suggestions: {str(e)}")
    
    def get_language_versions(self, title: str) -> Dict[str, str]:
        """Get available language versions of an article"""
        try:
            page = wikipedia.page(title, auto_suggest=True)
            
            # Get language links
            lang_links = {}
            try:
                for lang, link in page.langlinks.items():
                    lang_links[lang] = link
            except:
                pass
            
            return lang_links
            
        except Exception as e:
            raise Exception(f"Failed to get language versions: {str(e)}")
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text"""
        try:
            # Simple keyword extraction (can be enhanced with NLP libraries)
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
                'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
                'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
            }
            
            # Filter and count words
            word_counts = {}
            for word in words:
                if len(word) > 3 and word not in stop_words:
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            # Sort by frequency and return top keywords
            sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            return [word for word, count in sorted_words[:max_keywords]]
            
        except Exception as e:
            raise Exception(f"Failed to extract keywords: {str(e)}")
    
    def clear_cache(self):
        """Clear the cache"""
        self._search_cache.clear()
        self._article_cache.clear()
    
    def set_language(self, language: str):
        """Set Wikipedia language"""
        self.language = language
        wikipedia.set_lang(language)
        # Clear cache when language changes
        self.clear_cache()


class WikipediaToolsManager:
    """CLI integration for Wikipedia tools"""
    
    def __init__(self, language: str = "en"):
        self.wikipedia_tools = WikipediaTools(language)
        self.console = Console()
    
    def search(self, query: str, limit: int = 10, format: str = "table"):
        """Search Wikipedia articles"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Searching for '{query}'...", total=None)
                results = self.wikipedia_tools.search(query, limit)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'title': r.title,
                    'pageid': r.pageid,
                    'snippet': r.snippet,
                    'url': r.url,
                    'wordcount': r.wordcount,
                    'categories': r.categories[:5]  # Limit for JSON
                } for r in results], indent=2))
                return
            
            # Create search results table
            table = Table(title=f"Wikipedia Search Results for '{query}'")
            table.add_column("Title", style="cyan", no_wrap=True)
            table.add_column("Snippet", style="white")
            table.add_column("Word Count", style="yellow", justify="right")
            table.add_column("Categories", style="green")
            table.add_column("URL", style="blue", no_wrap=True)
            
            for result in results:
                # Truncate snippet if too long
                snippet = result.snippet[:100] + "..." if len(result.snippet) > 100 else result.snippet
                
                # Format categories
                categories = ", ".join(result.categories[:3]) if result.categories else "None"
                categories = categories[:50] + "..." if len(categories) > 50 else categories
                
                table.add_row(
                    result.title,
                    snippet,
                    str(result.wordcount),
                    categories,
                    result.url
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Search error: {e}[/red]")
    
    def get_article(self, title: str, format: str = "table"):
        """Get full Wikipedia article"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Fetching article '{title}'...", total=None)
                article = self.wikipedia_tools.get_article(title)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'title': article.title,
                    'pageid': article.pageid,
                    'url': article.url,
                    'summary': article.summary,
                    'wordcount': article.wordcount,
                    'categories': article.categories[:10],
                    'links': article.links[:20],
                    'references': article.references[:10],
                    'images': article.images[:5]
                }, indent=2))
                return
            
            # Display article information
            self.console.print(Panel(f"[bold cyan]{article.title}[/bold cyan]", title="Article"))
            
            # Summary
            self.console.print(Panel(article.summary, title="Summary", border_style="green"))
            
            # Article stats
            stats_table = Table(title="Article Statistics")
            stats_table.add_column("Property", style="cyan")
            stats_table.add_column("Value", style="white")
            
            stats_table.add_row("Page ID", str(article.pageid))
            stats_table.add_row("Word Count", str(article.wordcount))
            stats_table.add_row("Language", article.language)
            stats_table.add_row("Last Modified", article.last_modified)
            stats_table.add_row("URL", article.url)
            
            self.console.print(stats_table)
            
            # Categories
            if article.categories:
                categories_text = ", ".join(article.categories[:15])
                self.console.print(Panel(categories_text, title="Categories", border_style="yellow"))
            
            # Related links
            if article.links:
                links_text = ", ".join(article.links[:20])
                self.console.print(Panel(links_text, title="Related Articles", border_style="blue"))
            
        except Exception as e:
            self.console.print(f"[red]Article error: {e}[/red]")
    
    def get_summary(self, title: str, sentences: int = 3, format: str = "table"):
        """Get article summary"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Getting summary for '{title}'...", total=None)
                summary = self.wikipedia_tools.get_summary(title, sentences)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'title': summary.title,
                    'summary': summary.summary,
                    'url': summary.url,
                    'wordcount': summary.wordcount,
                    'categories': summary.categories[:5],
                    'related_topics': summary.related_topics[:10]
                }, indent=2))
                return
            
            # Display summary
            self.console.print(Panel(f"[bold cyan]{summary.title}[/bold cyan]", title="Article"))
            self.console.print(Panel(summary.summary, title="Summary", border_style="green"))
            
            # Article info
            info_table = Table(title="Article Information")
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="white")
            
            info_table.add_row("Word Count", str(summary.wordcount))
            info_table.add_row("URL", summary.url)
            
            self.console.print(info_table)
            
            # Related topics
            if summary.related_topics:
                topics_text = ", ".join(summary.related_topics[:15])
                self.console.print(Panel(topics_text, title="Related Topics", border_style="blue"))
            
        except Exception as e:
            self.console.print(f"[red]Summary error: {e}[/red]")
    
    def get_random_article(self, format: str = "table"):
        """Get a random Wikipedia article"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Finding random article...", total=None)
                article = self.wikipedia_tools.get_random_article()
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'title': article.title,
                    'summary': article.summary,
                    'url': article.url,
                    'wordcount': article.wordcount
                }, indent=2))
                return
            
            # Display random article
            self.console.print(Panel(f"[bold cyan]🎲 Random Article: {article.title}[/bold cyan]", title="Random Article"))
            self.console.print(Panel(article.summary, title="Summary", border_style="green"))
            
            # Quick info
            info_table = Table(title="Quick Info")
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="white")
            
            info_table.add_row("Word Count", str(article.wordcount))
            info_table.add_row("URL", article.url)
            
            self.console.print(info_table)
            
        except Exception as e:
            self.console.print(f"[red]Random article error: {e}[/red]")
    
    def get_related_articles(self, title: str, limit: int = 10, format: str = "table"):
        """Get articles related to a given title"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Finding articles related to '{title}'...", total=None)
                related = self.wikipedia_tools.get_related_articles(title, limit)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'title': r.title,
                    'snippet': r.snippet,
                    'url': r.url,
                    'wordcount': r.wordcount
                } for r in related], indent=2))
                return
            
            # Create related articles table
            table = Table(title=f"Articles Related to '{title}'")
            table.add_column("Title", style="cyan", no_wrap=True)
            table.add_column("Snippet", style="white")
            table.add_column("Word Count", style="yellow", justify="right")
            table.add_column("URL", style="blue", no_wrap=True)
            
            for result in related:
                snippet = result.snippet[:100] + "..." if len(result.snippet) > 100 else result.snippet
                
                table.add_row(
                    result.title,
                    snippet,
                    str(result.wordcount),
                    result.url
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Related articles error: {e}[/red]")
    
    def get_suggestions(self, query: str, limit: int = 5, format: str = "table"):
        """Get search suggestions"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Getting suggestions for '{query}'...", total=None)
                suggestions = self.wikipedia_tools.search_suggestions(query, limit)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'query': query,
                    'suggestions': suggestions
                }, indent=2))
                return
            
            # Display suggestions
            suggestions_text = "\n".join([f"• {suggestion}" for suggestion in suggestions])
            self.console.print(Panel(suggestions_text, title=f"Search Suggestions for '{query}'", border_style="yellow"))
            
        except Exception as e:
            self.console.print(f"[red]Suggestions error: {e}[/red]")
    
    def extract_keywords(self, text: str, max_keywords: int = 10, format: str = "table"):
        """Extract keywords from text"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Extracting keywords...", total=None)
                keywords = self.wikipedia_tools.extract_keywords(text, max_keywords)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'text_length': len(text),
                    'keywords': keywords
                }, indent=2))
                return
            
            # Display keywords
            keywords_text = ", ".join(keywords)
            self.console.print(Panel(keywords_text, title=f"Keywords (from {len(text)} characters)", border_style="green"))
            
        except Exception as e:
            self.console.print(f"[red]Keyword extraction error: {e}[/red]")
    
    def clear_cache(self):
        """Clear the cache"""
        self.wikipedia_tools.clear_cache()
        self.console.print("[green]Cache cleared successfully[/green]")
    
    def set_language(self, language: str):
        """Set Wikipedia language"""
        self.wikipedia_tools.set_language(language)
        self.console.print(f"[green]Language set to: {language}[/green]") 