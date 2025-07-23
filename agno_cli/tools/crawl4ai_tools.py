"""
Crawl4AI Tools - Web Crawling and Data Extraction

This module provides comprehensive web crawling and data extraction capabilities:
- Web page crawling and scraping
- Data extraction and parsing
- Content analysis and processing
- Link discovery and following
- Image and media extraction
- Form handling and interaction
- Rate limiting and politeness
- Rich output formatting
- Multiple crawling strategies
- Advanced data processing
"""

import os
import sys
import json
import time
import hashlib
import urllib.parse
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown
from rich.tree import Tree
from rich.align import Align
from rich.layout import Layout
import requests
from bs4 import BeautifulSoup
import lxml.html
from urllib.robotparser import RobotFileParser
import re
import threading
from queue import Queue
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor


class CrawlStrategy(Enum):
    """Crawling strategies enumeration"""
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    PRIORITY_BASED = "priority_based"
    RANDOM = "random"
    FOCUSED = "focused"


class ContentType(Enum):
    """Content types enumeration"""
    HTML = "html"
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    IMAGE = "image"
    PDF = "pdf"
    DOCUMENT = "document"
    MEDIA = "media"


@dataclass
class CrawlRequest:
    """Crawl request configuration"""
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, Any]] = None
    timeout: int = 30
    retry_attempts: int = 3
    follow_redirects: bool = True
    verify_ssl: bool = True
    user_agent: Optional[str] = None


@dataclass
class CrawlResponse:
    """Crawl response data"""
    url: str
    status_code: int
    headers: Dict[str, str]
    content: str
    content_type: str
    encoding: str
    size: int
    response_time: float
    timestamp: str
    redirected_from: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ExtractedData:
    """Extracted data from web page"""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    text_content: Optional[str] = None
    links: Optional[List[str]] = None
    images: Optional[List[str]] = None
    forms: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    structured_data: Optional[Dict[str, Any]] = None
    extracted_at: str = None
    
    def __post_init__(self):
        if self.extracted_at is None:
            self.extracted_at = datetime.now().isoformat()


@dataclass
class CrawlJob:
    """Crawl job configuration"""
    id: str
    name: str
    description: str
    start_url: str
    strategy: str
    max_depth: int = 3
    max_pages: int = 100
    allowed_domains: Optional[List[str]] = None
    excluded_patterns: Optional[List[str]] = None
    included_patterns: Optional[List[str]] = None
    delay_between_requests: float = 1.0
    respect_robots_txt: bool = True
    user_agent: str = "Crawl4AI Bot/1.0"
    created_at: str = None
    status: str = "pending"  # pending, running, completed, failed
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class CrawlResult:
    """Crawl job result"""
    job_id: str
    total_pages: int
    successful_pages: int
    failed_pages: int
    total_size: int
    total_time: float
    start_time: str
    end_time: str
    extracted_data: List[ExtractedData]
    errors: List[Dict[str, Any]]
    statistics: Dict[str, Any]


@dataclass
class WebPage:
    """Web page representation"""
    url: str
    title: str
    content: str
    links: List[str]
    images: List[str]
    metadata: Dict[str, Any]
    crawled_at: str
    response_time: float
    status_code: int


class Crawl4AITools:
    """Core web crawling and data extraction tools"""
    
    def __init__(self):
        self.console = Console()
        self.crawls_dir = Path("crawls")
        self.crawls_dir.mkdir(exist_ok=True)
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Crawl4AI Bot/1.0 (https://github.com/your-repo)'
        })
        
        # Crawl jobs and results
        self.crawl_jobs: Dict[str, CrawlJob] = {}
        self.crawl_results: Dict[str, CrawlResult] = {}
        
        # Robots.txt cache
        self.robots_cache: Dict[str, RobotFileParser] = {}
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 1.0
        
        # Common user agents
        self.user_agents = {
            'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        }
    
    def crawl_page(self, url: str, request_config: Optional[CrawlRequest] = None) -> CrawlResponse:
        """Crawl a single web page"""
        if request_config is None:
            request_config = CrawlRequest(url=url)
        
        # Rate limiting
        self._respect_rate_limit()
        
        try:
            # Prepare request
            headers = request_config.headers or {}
            if request_config.user_agent:
                headers['User-Agent'] = request_config.user_agent
            
            # Make request
            start_time = time.time()
            response = self.session.request(
                method=request_config.method,
                url=url,
                headers=headers,
                data=request_config.data,
                timeout=request_config.timeout,
                allow_redirects=request_config.follow_redirects,
                verify=request_config.verify_ssl
            )
            response_time = time.time() - start_time
            
            # Create crawl response
            crawl_response = CrawlResponse(
                url=url,
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.text,
                content_type=response.headers.get('content-type', 'text/html'),
                encoding=response.encoding,
                size=len(response.content),
                response_time=response_time,
                timestamp=datetime.now().isoformat()
            )
            
            return crawl_response
            
        except Exception as e:
            return CrawlResponse(
                url=url,
                status_code=0,
                headers={},
                content="",
                content_type="",
                encoding="",
                size=0,
                response_time=0,
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def extract_data(self, response: CrawlResponse) -> ExtractedData:
        """Extract structured data from web page response"""
        try:
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            title = soup.find('title')
            title_text = title.get_text().strip() if title else None
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content') if meta_desc else None
            
            # Extract keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            keywords = []
            if meta_keywords and meta_keywords.get('content'):
                keywords = [kw.strip() for kw in meta_keywords.get('content').split(',')]
            
            # Extract text content
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    links.append(href)
                elif href.startswith('/'):
                    # Convert relative URLs to absolute
                    base_url = response.url
                    if '#' in base_url:
                        base_url = base_url.split('#')[0]
                    links.append(urllib.parse.urljoin(base_url, href))
            
            # Extract images
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src.startswith('http'):
                    images.append(src)
                elif src.startswith('/'):
                    base_url = response.url
                    if '#' in base_url:
                        base_url = base_url.split('#')[0]
                    images.append(urllib.parse.urljoin(base_url, src))
            
            # Extract forms
            forms = []
            for form in soup.find_all('form'):
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET'),
                    'inputs': []
                }
                
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    input_data = {
                        'type': input_tag.get('type', input_tag.name),
                        'name': input_tag.get('name', ''),
                        'value': input_tag.get('value', ''),
                        'required': input_tag.get('required') is not None
                    }
                    form_data['inputs'].append(input_data)
                
                forms.append(form_data)
            
            # Extract metadata
            metadata = {
                'language': soup.find('html').get('lang') if soup.find('html') else None,
                'viewport': soup.find('meta', attrs={'name': 'viewport'}),
                'robots': soup.find('meta', attrs={'name': 'robots'}),
                'author': soup.find('meta', attrs={'name': 'author'}),
                'charset': soup.find('meta', attrs={'charset': True}),
            }
            
            # Extract structured data (JSON-LD, Microdata, RDFa)
            structured_data = []
            
            # JSON-LD
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string)
                    structured_data.append({
                        'type': 'json-ld',
                        'data': data
                    })
                except:
                    pass
            
            # Microdata
            for item in soup.find_all(attrs={'itemtype': True}):
                microdata = {
                    'type': 'microdata',
                    'itemtype': item.get('itemtype'),
                    'properties': {}
                }
                
                for prop in item.find_all(attrs={'itemprop': True}):
                    prop_name = prop.get('itemprop')
                    prop_value = prop.get('content') or prop.get_text().strip()
                    microdata['properties'][prop_name] = prop_value
                
                structured_data.append(microdata)
            
            return ExtractedData(
                url=response.url,
                title=title_text,
                description=description,
                keywords=keywords,
                text_content=text_content,
                links=links,
                images=images,
                forms=forms,
                metadata=metadata,
                structured_data=structured_data
            )
            
        except Exception as e:
            return ExtractedData(
                url=response.url,
                error_message=str(e)
            )
    
    def create_crawl_job(self, name: str, description: str, start_url: str,
                        strategy: str = "breadth_first", max_depth: int = 3,
                        max_pages: int = 100, allowed_domains: Optional[List[str]] = None,
                        delay_between_requests: float = 1.0) -> CrawlJob:
        """Create a new crawl job"""
        job_id = hashlib.md5(f"{name}_{time.time()}".encode()).hexdigest()[:8]
        
        # Extract domain from start URL
        if not allowed_domains:
            parsed_url = urllib.parse.urlparse(start_url)
            allowed_domains = [parsed_url.netloc]
        
        job = CrawlJob(
            id=job_id,
            name=name,
            description=description,
            start_url=start_url,
            strategy=strategy,
            max_depth=max_depth,
            max_pages=max_pages,
            allowed_domains=allowed_domains,
            delay_between_requests=delay_between_requests
        )
        
        self.crawl_jobs[job_id] = job
        self._save_crawl_job(job)
        
        return job
    
    def execute_crawl_job(self, job_id: str) -> CrawlResult:
        """Execute a crawl job"""
        if job_id not in self.crawl_jobs:
            raise ValueError(f"Crawl job not found: {job_id}")
        
        job = self.crawl_jobs[job_id]
        job.status = "running"
        
        start_time = time.time()
        visited_urls = set()
        extracted_data = []
        errors = []
        queue = Queue()
        queue.put((job.start_url, 0))  # (url, depth)
        
        while not queue.empty() and len(visited_urls) < job.max_pages:
            current_url, depth = queue.get()
            
            if current_url in visited_urls or depth > job.max_depth:
                continue
            
            # Check if URL is allowed
            if not self._is_url_allowed(current_url, job.allowed_domains):
                continue
            
            # Check robots.txt
            if job.respect_robots_txt and not self._can_fetch(current_url):
                continue
            
            visited_urls.add(current_url)
            
            try:
                # Crawl the page
                response = self.crawl_page(current_url)
                
                if response.status_code == 200:
                    # Extract data
                    data = self.extract_data(response)
                    extracted_data.append(data)
                    
                    # Add new links to queue if within depth limit
                    if depth < job.max_depth and data.links:
                        for link in data.links:
                            if link not in visited_urls:
                                queue.put((link, depth + 1))
                
                else:
                    errors.append({
                        'url': current_url,
                        'error': f"HTTP {response.status_code}",
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Rate limiting
                time.sleep(job.delay_between_requests)
                
            except Exception as e:
                errors.append({
                    'url': current_url,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        total_size = sum(len(data.text_content or '') for data in extracted_data)
        statistics = {
            'total_urls_visited': len(visited_urls),
            'successful_extractions': len(extracted_data),
            'failed_extractions': len(errors),
            'average_response_time': total_time / len(visited_urls) if visited_urls else 0,
            'total_data_size': total_size,
            'unique_domains': len(set(urllib.parse.urlparse(url).netloc for url in visited_urls))
        }
        
        result = CrawlResult(
            job_id=job_id,
            total_pages=len(visited_urls),
            successful_pages=len(extracted_data),
            failed_pages=len(errors),
            total_size=total_size,
            total_time=total_time,
            start_time=datetime.fromtimestamp(start_time).isoformat(),
            end_time=datetime.fromtimestamp(end_time).isoformat(),
            extracted_data=extracted_data,
            errors=errors,
            statistics=statistics
        )
        
        job.status = "completed"
        self.crawl_results[job_id] = result
        self._save_crawl_result(result)
        
        return result
    
    def _is_url_allowed(self, url: str, allowed_domains: List[str]) -> bool:
        """Check if URL is in allowed domains"""
        parsed_url = urllib.parse.urlparse(url)
        return parsed_url.netloc in allowed_domains
    
    def _can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc
        
        if domain not in self.robots_cache:
            try:
                robots_url = f"https://{domain}/robots.txt"
                robots_response = self.session.get(robots_url, timeout=10)
                rp = RobotFileParser()
                rp.read(robots_response.text.splitlines())
                self.robots_cache[domain] = rp
            except:
                # If robots.txt is not accessible, assume it's allowed
                return True
        
        return self.robots_cache[domain].can_fetch(self.user_agents['chrome'], url)
    
    def _respect_rate_limit(self):
        """Respect rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            time.sleep(self.min_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _save_crawl_job(self, job: CrawlJob) -> bool:
        """Save crawl job to file"""
        try:
            job_file = self.crawls_dir / f"job_{job.id}.json"
            with open(job_file, 'w') as f:
                json.dump(asdict(job), f, indent=2, default=str)
            return True
        except Exception as e:
            self.console.print(f"[red]Error saving crawl job: {e}[/red]")
            return False
    
    def _save_crawl_result(self, result: CrawlResult) -> bool:
        """Save crawl result to file"""
        try:
            result_file = self.crawls_dir / f"result_{result.job_id}.json"
            with open(result_file, 'w') as f:
                json.dump(asdict(result), f, indent=2, default=str)
            return True
        except Exception as e:
            self.console.print(f"[red]Error saving crawl result: {e}[/red]")
            return False
    
    def get_crawl_job(self, job_id: str) -> Optional[CrawlJob]:
        """Get crawl job by ID"""
        return self.crawl_jobs.get(job_id)
    
    def list_crawl_jobs(self) -> List[CrawlJob]:
        """List all crawl jobs"""
        return list(self.crawl_jobs.values())
    
    def get_crawl_result(self, job_id: str) -> Optional[CrawlResult]:
        """Get crawl result by job ID"""
        return self.crawl_results.get(job_id)
    
    def delete_crawl_job(self, job_id: str) -> bool:
        """Delete crawl job"""
        if job_id in self.crawl_jobs:
            del self.crawl_jobs[job_id]
            
            # Delete file
            job_file = self.crawls_dir / f"job_{job_id}.json"
            if job_file.exists():
                job_file.unlink()
            
            return True
        return False
    
    def search_content(self, text: str, pattern: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for patterns in text content"""
        flags = 0 if case_sensitive else re.IGNORECASE
        matches = []
        
        for match in re.finditer(pattern, text, flags):
            matches.append({
                'start': match.start(),
                'end': match.end(),
                'match': match.group(),
                'groups': match.groups()
            })
        
        return matches
    
    def extract_links_from_text(self, text: str, base_url: str) -> List[str]:
        """Extract links from text content"""
        # Simple regex for URL extraction
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Also look for relative URLs
        relative_pattern = r'/[^\s<>"{}|\\^`\[\]]+'
        relative_urls = re.findall(relative_pattern, text)
        
        # Convert relative URLs to absolute
        absolute_urls = []
        for rel_url in relative_urls:
            absolute_urls.append(urllib.parse.urljoin(base_url, rel_url))
        
        return urls + absolute_urls


class Crawl4AIToolsManager:
    """CLI integration for crawl4ai tools"""
    
    def __init__(self):
        self.crawl4ai_tools = Crawl4AITools()
        self.console = Console()
    
    def crawl_page(self, url: str, user_agent: Optional[str] = None,
                  timeout: int = 30, format: str = "table") -> None:
        """Crawl a single web page"""
        try:
            request_config = CrawlRequest(
                url=url,
                timeout=timeout,
                user_agent=user_agent
            )
            
            response = self.crawl4ai_tools.crawl_page(url, request_config)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(response), indent=2, default=str))
            else:
                # Show crawl response
                response_panel = Panel(
                    f"[bold blue]URL:[/bold blue] {response.url}\n"
                    f"[bold green]Status:[/bold green] {response.status_code}\n"
                    f"[bold yellow]Size:[/bold yellow] {response.size:,} bytes\n"
                    f"[bold cyan]Time:[/bold cyan] {response.response_time:.3f}s\n"
                    f"[bold white]Type:[/bold white] {response.content_type}",
                    title="Page Crawl Result",
                    border_style="green" if response.status_code == 200 else "red"
                )
                self.console.print(response_panel)
                
                if response.status_code == 200:
                    # Extract and show data
                    data = self.crawl4ai_tools.extract_data(response)
                    
                    data_panel = Panel(
                        f"[bold blue]Title:[/bold blue] {data.title or 'N/A'}\n"
                        f"[bold green]Description:[/bold green] {data.description or 'N/A'}\n"
                        f"[bold yellow]Links:[/bold yellow] {len(data.links or [])}\n"
                        f"[bold cyan]Images:[/bold cyan] {len(data.images or [])}\n"
                        f"[bold white]Forms:[/bold white] {len(data.forms or [])}",
                        title="Extracted Data",
                        border_style="blue"
                    )
                    self.console.print(data_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error crawling page: {e}[/red]")
    
    def create_job(self, name: str, description: str, start_url: str,
                  strategy: str = "breadth_first", max_depth: int = 3,
                  max_pages: int = 100, delay: float = 1.0,
                  format: str = "table") -> None:
        """Create a new crawl job"""
        try:
            job = self.crawl4ai_tools.create_crawl_job(
                name=name,
                description=description,
                start_url=start_url,
                strategy=strategy,
                max_depth=max_depth,
                max_pages=max_pages,
                delay_between_requests=delay
            )
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(job), indent=2, default=str))
            else:
                job_panel = Panel(
                    f"[bold blue]Job ID:[/bold blue] {job.id}\n"
                    f"[bold green]Name:[/bold green] {job.name}\n"
                    f"[bold yellow]Start URL:[/bold yellow] {job.start_url}\n"
                    f"[bold cyan]Strategy:[/bold cyan] {job.strategy}\n"
                    f"[bold white]Max Depth:[/bold white] {job.max_depth}\n"
                    f"[bold magenta]Max Pages:[/bold magenta] {job.max_pages}",
                    title="Crawl Job Created",
                    border_style="green"
                )
                self.console.print(job_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error creating crawl job: {e}[/red]")
    
    def execute_job(self, job_id: str, format: str = "table") -> None:
        """Execute a crawl job"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task("Crawling...", total=None)
                
                result = self.crawl4ai_tools.execute_crawl_job(job_id)
                
                progress.update(task, completed=True)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2, default=str))
            else:
                # Show crawl result
                result_panel = Panel(
                    f"[bold blue]Job ID:[/bold blue] {result.job_id}\n"
                    f"[bold green]Total Pages:[/bold green] {result.total_pages}\n"
                    f"[bold yellow]Successful:[/bold yellow] {result.successful_pages}\n"
                    f"[bold cyan]Failed:[/bold cyan] {result.failed_pages}\n"
                    f"[bold white]Total Time:[/bold white] {result.total_time:.2f}s\n"
                    f"[bold magenta]Total Size:[/bold magenta] {result.total_size:,} bytes",
                    title="Crawl Job Result",
                    border_style="green"
                )
                self.console.print(result_panel)
                
                # Show statistics
                stats_table = Table(title="Crawl Statistics")
                stats_table.add_column("Metric", style="cyan")
                stats_table.add_column("Value", style="white")
                
                for key, value in result.statistics.items():
                    if isinstance(value, float):
                        value_str = f"{value:.2f}"
                    else:
                        value_str = str(value)
                    stats_table.add_row(key.replace('_', ' ').title(), value_str)
                
                self.console.print(stats_table)
                
        except Exception as e:
            self.console.print(f"[red]Error executing crawl job: {e}[/red]")
    
    def list_jobs(self, format: str = "table") -> None:
        """List all crawl jobs"""
        try:
            jobs = self.crawl4ai_tools.list_crawl_jobs()
            
            if format == "json":
                import json
                self.console.print(json.dumps([asdict(job) for job in jobs], indent=2, default=str))
            else:
                if not jobs:
                    self.console.print("[yellow]No crawl jobs found[/yellow]")
                    return
                
                jobs_table = Table(title="Crawl Jobs")
                jobs_table.add_column("ID", style="cyan")
                jobs_table.add_column("Name", style="white")
                jobs_table.add_column("Start URL", style="blue")
                jobs_table.add_column("Strategy", style="green")
                jobs_table.add_column("Status", style="yellow")
                jobs_table.add_column("Created", style="red")
                
                for job in jobs:
                    status_color = "green" if job.status == "completed" else "yellow" if job.status == "running" else "red"
                    jobs_table.add_row(
                        job.id,
                        job.name,
                        job.start_url[:50] + "..." if len(job.start_url) > 50 else job.start_url,
                        job.strategy,
                        f"[{status_color}]{job.status}[/{status_color}]",
                        job.created_at[:10]
                    )
                
                self.console.print(jobs_table)
                
        except Exception as e:
            self.console.print(f"[red]Error listing jobs: {e}[/red]")
    
    def show_job(self, job_id: str, format: str = "table") -> None:
        """Show crawl job details"""
        try:
            job = self.crawl4ai_tools.get_crawl_job(job_id)
            if not job:
                self.console.print(f"[red]Crawl job not found: {job_id}[/red]")
                return
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(job), indent=2, default=str))
            else:
                # Show job details
                job_table = Table(title=f"Crawl Job: {job.name}")
                job_table.add_column("Property", style="cyan")
                job_table.add_column("Value", style="white")
                
                job_table.add_row("ID", job.id)
                job_table.add_row("Name", job.name)
                job_table.add_row("Description", job.description)
                job_table.add_row("Start URL", job.start_url)
                job_table.add_row("Strategy", job.strategy)
                job_table.add_row("Max Depth", str(job.max_depth))
                job_table.add_row("Max Pages", str(job.max_pages))
                job_table.add_row("Delay", f"{job.delay_between_requests}s")
                job_table.add_row("Status", job.status)
                job_table.add_row("Created", job.created_at)
                job_table.add_row("Allowed Domains", ", ".join(job.allowed_domains or []))
                
                self.console.print(job_table)
                
                # Show result if available
                result = self.crawl4ai_tools.get_crawl_result(job_id)
                if result:
                    result_panel = Panel(
                        f"[bold green]Total Pages:[/bold green] {result.total_pages}\n"
                        f"[bold yellow]Successful:[/bold yellow] {result.successful_pages}\n"
                        f"[bold cyan]Failed:[/bold cyan] {result.failed_pages}\n"
                        f"[bold white]Total Time:[/bold white] {result.total_time:.2f}s",
                        title="Job Result",
                        border_style="green"
                    )
                    self.console.print(result_panel)
                
        except Exception as e:
            self.console.print(f"[red]Error showing job: {e}[/red]")
    
    def delete_job(self, job_id: str) -> None:
        """Delete crawl job"""
        try:
            success = self.crawl4ai_tools.delete_crawl_job(job_id)
            if success:
                self.console.print(f"[green]Crawl job deleted: {job_id}[/green]")
            else:
                self.console.print(f"[red]Crawl job not found: {job_id}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error deleting job: {e}[/red]")
    
    def search_content(self, text: str, pattern: str, case_sensitive: bool = False,
                      format: str = "table") -> None:
        """Search for patterns in text content"""
        try:
            matches = self.crawl4ai_tools.search_content(text, pattern, case_sensitive)
            
            if format == "json":
                import json
                self.console.print(json.dumps(matches, indent=2))
            else:
                if not matches:
                    self.console.print("[yellow]No matches found[/yellow]")
                    return
                
                matches_table = Table(title=f"Search Results for: {pattern}")
                matches_table.add_column("Position", style="cyan")
                matches_table.add_column("Match", style="white")
                matches_table.add_column("Groups", style="blue")
                
                for match in matches:
                    groups_str = ", ".join(match['groups']) if match['groups'] else "N/A"
                    matches_table.add_row(
                        f"{match['start']}-{match['end']}",
                        match['match'][:50] + "..." if len(match['match']) > 50 else match['match'],
                        groups_str
                    )
                
                self.console.print(matches_table)
                
        except Exception as e:
            self.console.print(f"[red]Error searching content: {e}[/red]") 