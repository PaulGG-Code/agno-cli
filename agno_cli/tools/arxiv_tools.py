"""
arXiv Tools - Academic Paper Search and Retrieval

This module provides arXiv academic paper search capabilities with:
- Advanced paper search functionality
- Content retrieval and metadata extraction
- Paper summaries and abstracts
- Author and category filtering
- Citation and reference analysis
- Rich output formatting
- Caching and performance optimization
"""

import os
import sys
import json
import time
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote, urlencode
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown
import arxiv


@dataclass
class ArxivPaper:
    """arXiv paper information"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: str
    updated_date: str
    pdf_url: str
    summary: str
    doi: Optional[str]
    journal_ref: Optional[str]
    primary_category: str
    comment: Optional[str]
    links: List[Dict[str, str]]


@dataclass
class ArxivSearchResult:
    """arXiv search result"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: str
    updated_date: str
    pdf_url: str
    summary: str
    primary_category: str


@dataclass
class ArxivAuthor:
    """arXiv author information"""
    name: str
    papers: List[str]
    categories: List[str]
    total_papers: int


@dataclass
class ArxivCategory:
    """arXiv category information"""
    name: str
    description: str
    paper_count: int
    recent_papers: List[str]


class ArxivTools:
    """Core arXiv academic paper search tools"""
    
    def __init__(self):
        self.console = Console()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AgnoCLI/1.0 (https://github.com/agno-ai/agno-cli)'
        })
        
        # Cache for search results and papers
        self._search_cache = {}
        self._paper_cache = {}
        self._cache_timeout = 3600  # 1 hour
        
        # arXiv categories
        self.categories = {
            'cs': 'Computer Science',
            'math': 'Mathematics',
            'physics': 'Physics',
            'quant-ph': 'Quantum Physics',
            'stat': 'Statistics',
            'eess': 'Electrical Engineering and Systems Science',
            'econ': 'Economics',
            'q-bio': 'Quantitative Biology',
            'q-fin': 'Quantitative Finance'
        }
    
    def search(self, query: str, max_results: int = 10, sort_by: str = "relevance", 
               sort_order: str = "descending", categories: Optional[List[str]] = None) -> List[ArxivSearchResult]:
        """Search arXiv papers"""
        try:
            # Check cache first
            cache_key = f"search_{query}_{max_results}_{sort_by}_{sort_order}_{str(categories)}"
            if cache_key in self._search_cache:
                cached_time, cached_results = self._search_cache[cache_key]
                if time.time() - cached_time < self._cache_timeout:
                    return cached_results
            
            # Build search query
            search_query = query
            if categories:
                category_filters = [f"cat:{cat}" for cat in categories]
                search_query = f"({query}) AND ({' OR '.join(category_filters)})"
            
            # Perform search
            search = arxiv.Search(
                query=search_query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion(sort_by),
                sort_order=arxiv.SortOrder(sort_order)
            )
            
            results = []
            for result in search.results():
                results.append(ArxivSearchResult(
                    id=result.entry_id,
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    categories=result.categories,
                    published_date=result.published.strftime('%Y-%m-%d') if result.published else '',
                    updated_date=result.updated.strftime('%Y-%m-%d') if result.updated else '',
                    pdf_url=result.pdf_url,
                    summary=result.summary,
                    primary_category=result.primary_category
                ))
            
            # Cache results
            self._search_cache[cache_key] = (time.time(), results)
            
            return results
            
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    def get_paper(self, paper_id: str) -> ArxivPaper:
        """Get detailed paper information"""
        try:
            # Check cache first
            cache_key = f"paper_{paper_id}"
            if cache_key in self._paper_cache:
                cached_time, cached_paper = self._paper_cache[cache_key]
                if time.time() - cached_time < self._cache_timeout:
                    return cached_paper
            
            # Get paper
            search = arxiv.Search(id_list=[paper_id])
            result = next(search.results())
            
            paper = ArxivPaper(
                id=result.entry_id,
                title=result.title,
                authors=[author.name for author in result.authors],
                abstract=result.summary,
                categories=result.categories,
                published_date=result.published.strftime('%Y-%m-%d %H:%M:%S') if result.published else '',
                updated_date=result.updated.strftime('%Y-%m-%d %H:%M:%S') if result.updated else '',
                pdf_url=result.pdf_url,
                summary=result.summary,
                doi=getattr(result, 'doi', None),
                journal_ref=getattr(result, 'journal_ref', None),
                primary_category=result.primary_category,
                comment=getattr(result, 'comment', None),
                links=[{'title': link.title, 'href': link.href} for link in result.links] if hasattr(result, 'links') else []
            )
            
            # Cache paper
            self._paper_cache[cache_key] = (time.time(), paper)
            
            return paper
            
        except Exception as e:
            raise Exception(f"Failed to get paper: {str(e)}")
    
    def search_by_author(self, author_name: str, max_results: int = 10) -> List[ArxivSearchResult]:
        """Search papers by author"""
        try:
            query = f"au:\"{author_name}\""
            return self.search(query, max_results)
            
        except Exception as e:
            raise Exception(f"Author search failed: {str(e)}")
    
    def search_by_category(self, category: str, max_results: int = 20) -> List[ArxivSearchResult]:
        """Search papers by category"""
        try:
            query = f"cat:{category}"
            return self.search(query, max_results)
            
        except Exception as e:
            raise Exception(f"Category search failed: {str(e)}")
    
    def get_recent_papers(self, category: Optional[str] = None, max_results: int = 20) -> List[ArxivSearchResult]:
        """Get recent papers"""
        try:
            if category:
                query = f"cat:{category}"
            else:
                query = "all:all"
            
            return self.search(query, max_results, sort_by="submittedDate", sort_order="descending")
            
        except Exception as e:
            raise Exception(f"Recent papers search failed: {str(e)}")
    
    def search_by_date_range(self, start_date: str, end_date: str, 
                           query: str = "all:all", max_results: int = 50) -> List[ArxivSearchResult]:
        """Search papers by date range"""
        try:
            date_query = f"submittedDate:[{start_date} TO {end_date}]"
            full_query = f"({query}) AND {date_query}"
            return self.search(full_query, max_results)
            
        except Exception as e:
            raise Exception(f"Date range search failed: {str(e)}")
    
    def get_paper_citations(self, paper_id: str) -> List[ArxivSearchResult]:
        """Get papers that cite a given paper"""
        try:
            # This is a simplified approach - in practice, you'd need to use
            # external citation databases or APIs
            paper = self.get_paper(paper_id)
            title_words = paper.title.split()[:3]  # Use first few words
            query = " AND ".join([f'"{word}"' for word in title_words])
            return self.search(query, max_results=20)
            
        except Exception as e:
            raise Exception(f"Citation search failed: {str(e)}")
    
    def get_related_papers(self, paper_id: str, max_results: int = 10) -> List[ArxivSearchResult]:
        """Get papers related to a given paper"""
        try:
            paper = self.get_paper(paper_id)
            
            # Build query from title and categories
            title_words = paper.title.split()[:5]  # Use first 5 words
            category_query = " OR ".join([f"cat:{cat}" for cat in paper.categories[:3]])
            title_query = " AND ".join([f'"{word}"' for word in title_words])
            
            query = f"({title_query}) OR ({category_query})"
            results = self.search(query, max_results)
            
            # Filter out the original paper
            return [r for r in results if r.id != paper_id]
            
        except Exception as e:
            raise Exception(f"Related papers search failed: {str(e)}")
    
    def get_author_info(self, author_name: str) -> ArxivAuthor:
        """Get information about an author"""
        try:
            papers = self.search_by_author(author_name, max_results=100)
            
            # Collect categories
            all_categories = []
            for paper in papers:
                all_categories.extend(paper.categories)
            
            # Count categories
            category_counts = {}
            for cat in all_categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            # Get top categories
            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return ArxivAuthor(
                name=author_name,
                papers=[paper.id for paper in papers],
                categories=[cat for cat, count in top_categories],
                total_papers=len(papers)
            )
            
        except Exception as e:
            raise Exception(f"Author info search failed: {str(e)}")
    
    def get_category_info(self, category: str) -> ArxivCategory:
        """Get information about a category"""
        try:
            papers = self.search_by_category(category, max_results=50)
            
            # Get recent papers
            recent_papers = [paper.title for paper in papers[:10]]
            
            return ArxivCategory(
                name=category,
                description=self.categories.get(category, "Unknown category"),
                paper_count=len(papers),
                recent_papers=recent_papers
            )
            
        except Exception as e:
            raise Exception(f"Category info search failed: {str(e)}")
    
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
                'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
                'we', 'paper', 'study', 'propose', 'present', 'show', 'demonstrate',
                'results', 'method', 'approach', 'algorithm', 'model', 'system'
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
    
    def get_categories(self) -> Dict[str, str]:
        """Get available arXiv categories"""
        return self.categories
    
    def clear_cache(self):
        """Clear the cache"""
        self._search_cache.clear()
        self._paper_cache.clear()


class ArxivToolsManager:
    """CLI integration for arXiv tools"""
    
    def __init__(self):
        self.arxiv_tools = ArxivTools()
        self.console = Console()
    
    def search(self, query: str, max_results: int = 10, sort_by: str = "relevance", 
               sort_order: str = "descending", categories: Optional[List[str]] = None, format: str = "table"):
        """Search arXiv papers"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Searching arXiv for '{query}'...", total=None)
                results = self.arxiv_tools.search(query, max_results, sort_by, sort_order, categories)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'id': r.id,
                    'title': r.title,
                    'authors': r.authors,
                    'abstract': r.abstract,
                    'categories': r.categories,
                    'published_date': r.published_date,
                    'pdf_url': r.pdf_url,
                    'primary_category': r.primary_category
                } for r in results], indent=2))
                return
            
            # Create search results table
            table = Table(title=f"arXiv Search Results for '{query}'")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Authors", style="yellow")
            table.add_column("Categories", style="green")
            table.add_column("Published", style="magenta")
            table.add_column("PDF URL", style="blue", no_wrap=True)
            
            for result in results:
                # Truncate title if too long
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                
                # Format authors
                authors = ", ".join(result.authors[:2])  # Show first 2 authors
                if len(result.authors) > 2:
                    authors += f" et al. ({len(result.authors)} total)"
                
                # Format categories
                categories = ", ".join(result.categories[:3]) if result.categories else "None"
                
                table.add_row(
                    result.id,
                    title,
                    authors,
                    categories,
                    result.published_date,
                    result.pdf_url
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Search error: {e}[/red]")
    
    def get_paper(self, paper_id: str, format: str = "table"):
        """Get detailed paper information"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Fetching paper '{paper_id}'...", total=None)
                paper = self.arxiv_tools.get_paper(paper_id)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'id': paper.id,
                    'title': paper.title,
                    'authors': paper.authors,
                    'abstract': paper.abstract,
                    'categories': paper.categories,
                    'published_date': paper.published_date,
                    'updated_date': paper.updated_date,
                    'pdf_url': paper.pdf_url,
                    'doi': paper.doi,
                    'journal_ref': paper.journal_ref,
                    'primary_category': paper.primary_category,
                    'comment': paper.comment
                }, indent=2))
                return
            
            # Display paper information
            self.console.print(Panel(f"[bold cyan]{paper.title}[/bold cyan]", title="Paper"))
            
            # Abstract
            self.console.print(Panel(paper.abstract, title="Abstract", border_style="green"))
            
            # Paper stats
            stats_table = Table(title="Paper Statistics")
            stats_table.add_column("Property", style="cyan")
            stats_table.add_column("Value", style="white")
            
            stats_table.add_row("ID", paper.id)
            stats_table.add_row("Primary Category", paper.primary_category)
            stats_table.add_row("Published", paper.published_date)
            stats_table.add_row("Updated", paper.updated_date)
            stats_table.add_row("PDF URL", paper.pdf_url)
            
            if paper.doi:
                stats_table.add_row("DOI", paper.doi)
            if paper.journal_ref:
                stats_table.add_row("Journal Ref", paper.journal_ref)
            if paper.comment:
                stats_table.add_row("Comment", paper.comment)
            
            self.console.print(stats_table)
            
            # Authors
            authors_text = ", ".join(paper.authors)
            self.console.print(Panel(authors_text, title="Authors", border_style="yellow"))
            
            # Categories
            if paper.categories:
                categories_text = ", ".join(paper.categories)
                self.console.print(Panel(categories_text, title="Categories", border_style="blue"))
            
        except Exception as e:
            self.console.print(f"[red]Paper error: {e}[/red]")
    
    def search_by_author(self, author_name: str, max_results: int = 10, format: str = "table"):
        """Search papers by author"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Searching papers by '{author_name}'...", total=None)
                results = self.arxiv_tools.search_by_author(author_name, max_results)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'id': r.id,
                    'title': r.title,
                    'categories': r.categories,
                    'published_date': r.published_date,
                    'pdf_url': r.pdf_url
                } for r in results], indent=2))
                return
            
            # Create author papers table
            table = Table(title=f"Papers by {author_name}")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Categories", style="green")
            table.add_column("Published", style="magenta")
            table.add_column("PDF URL", style="blue", no_wrap=True)
            
            for result in results:
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                categories = ", ".join(result.categories[:3]) if result.categories else "None"
                
                table.add_row(
                    result.id,
                    title,
                    categories,
                    result.published_date,
                    result.pdf_url
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Author search error: {e}[/red]")
    
    def search_by_category(self, category: str, max_results: int = 20, format: str = "table"):
        """Search papers by category"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Searching papers in category '{category}'...", total=None)
                results = self.arxiv_tools.search_by_category(category, max_results)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'id': r.id,
                    'title': r.title,
                    'authors': r.authors,
                    'published_date': r.published_date,
                    'pdf_url': r.pdf_url
                } for r in results], indent=2))
                return
            
            # Create category papers table
            table = Table(title=f"Papers in Category: {category}")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Authors", style="yellow")
            table.add_column("Published", style="magenta")
            table.add_column("PDF URL", style="blue", no_wrap=True)
            
            for result in results:
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                authors = ", ".join(result.authors[:2])
                if len(result.authors) > 2:
                    authors += f" et al. ({len(result.authors)} total)"
                
                table.add_row(
                    result.id,
                    title,
                    authors,
                    result.published_date,
                    result.pdf_url
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Category search error: {e}[/red]")
    
    def get_recent_papers(self, category: Optional[str] = None, max_results: int = 20, format: str = "table"):
        """Get recent papers"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Fetching recent papers...", total=None)
                results = self.arxiv_tools.get_recent_papers(category, max_results)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'id': r.id,
                    'title': r.title,
                    'authors': r.authors,
                    'published_date': r.published_date,
                    'pdf_url': r.pdf_url
                } for r in results], indent=2))
                return
            
            # Create recent papers table
            title = f"Recent Papers{f' in {category}' if category else ''}"
            table = Table(title=title)
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Authors", style="yellow")
            table.add_column("Published", style="magenta")
            table.add_column("PDF URL", style="blue", no_wrap=True)
            
            for result in results:
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                authors = ", ".join(result.authors[:2])
                if len(result.authors) > 2:
                    authors += f" et al. ({len(result.authors)} total)"
                
                table.add_row(
                    result.id,
                    title,
                    authors,
                    result.published_date,
                    result.pdf_url
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Recent papers error: {e}[/red]")
    
    def get_related_papers(self, paper_id: str, max_results: int = 10, format: str = "table"):
        """Get papers related to a given paper"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Finding papers related to '{paper_id}'...", total=None)
                results = self.arxiv_tools.get_related_papers(paper_id, max_results)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'id': r.id,
                    'title': r.title,
                    'authors': r.authors,
                    'categories': r.categories,
                    'published_date': r.published_date,
                    'pdf_url': r.pdf_url
                } for r in results], indent=2))
                return
            
            # Create related papers table
            table = Table(title=f"Papers Related to {paper_id}")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Authors", style="yellow")
            table.add_column("Categories", style="green")
            table.add_column("Published", style="magenta")
            table.add_column("PDF URL", style="blue", no_wrap=True)
            
            for result in results:
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                authors = ", ".join(result.authors[:2])
                if len(result.authors) > 2:
                    authors += f" et al. ({len(result.authors)} total)"
                categories = ", ".join(result.categories[:3]) if result.categories else "None"
                
                table.add_row(
                    result.id,
                    title,
                    authors,
                    categories,
                    result.published_date,
                    result.pdf_url
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Related papers error: {e}[/red]")
    
    def get_author_info(self, author_name: str, format: str = "table"):
        """Get information about an author"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Getting info for author '{author_name}'...", total=None)
                author = self.arxiv_tools.get_author_info(author_name)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'name': author.name,
                    'total_papers': author.total_papers,
                    'categories': author.categories,
                    'papers': author.papers[:10]  # Limit for JSON
                }, indent=2))
                return
            
            # Display author information
            self.console.print(Panel(f"[bold cyan]{author.name}[/bold cyan]", title="Author Information"))
            
            # Author stats
            stats_table = Table(title="Author Statistics")
            stats_table.add_column("Property", style="cyan")
            stats_table.add_column("Value", style="white")
            
            stats_table.add_row("Total Papers", str(author.total_papers))
            stats_table.add_row("Top Categories", ", ".join(author.categories[:5]))
            
            self.console.print(stats_table)
            
            # Recent papers
            if author.papers:
                papers_text = ", ".join(author.papers[:10])
                self.console.print(Panel(papers_text, title="Recent Papers", border_style="yellow"))
            
        except Exception as e:
            self.console.print(f"[red]Author info error: {e}[/red]")
    
    def get_categories(self, format: str = "table"):
        """Get available arXiv categories"""
        try:
            categories = self.arxiv_tools.get_categories()
            
            if format == "json":
                import json
                self.console.print(json.dumps(categories, indent=2))
                return
            
            # Create categories table
            table = Table(title="arXiv Categories")
            table.add_column("Code", style="cyan")
            table.add_column("Description", style="white")
            
            for code, description in categories.items():
                table.add_row(code, description)
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Categories error: {e}[/red]")
    
    def extract_keywords(self, text: str, max_keywords: int = 10, format: str = "table"):
        """Extract keywords from text"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Extracting keywords...", total=None)
                keywords = self.arxiv_tools.extract_keywords(text, max_keywords)
            
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
        self.arxiv_tools.clear_cache()
        self.console.print("[green]Cache cleared successfully[/green]") 