"""
PubMed Tools - Medical Research Paper Search and Retrieval

This module provides PubMed medical research paper search capabilities with:
- Advanced paper search functionality
- Content retrieval and metadata extraction
- Medical abstracts and summaries
- Author and journal filtering
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
from Bio import Entrez


@dataclass
class PubMedPaper:
    """PubMed paper information"""
    pmid: str
    title: str
    authors: List[str]
    abstract: str
    journal: str
    publication_date: str
    publication_type: str
    mesh_terms: List[str]
    keywords: List[str]
    doi: Optional[str]
    issn: Optional[str]
    volume: Optional[str]
    issue: Optional[str]
    pages: Optional[str]
    language: str
    country: Optional[str]
    citation_count: Optional[int]


@dataclass
class PubMedSearchResult:
    """PubMed search result"""
    pmid: str
    title: str
    authors: List[str]
    abstract: str
    journal: str
    publication_date: str
    publication_type: str
    mesh_terms: List[str]


@dataclass
class PubMedAuthor:
    """PubMed author information"""
    name: str
    papers: List[str]
    journals: List[str]
    total_papers: int
    research_areas: List[str]


@dataclass
class PubMedJournal:
    """PubMed journal information"""
    name: str
    issn: str
    papers: List[str]
    total_papers: int
    impact_factor: Optional[float]


class PubMedTools:
    """Core PubMed medical research paper search tools"""
    
    def __init__(self, email: str = "agno-cli@example.com"):
        self.console = Console()
        self.email = email
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AgnoCLI/1.0 (https://github.com/agno-ai/agno-cli)'
        })
        
        # Set Entrez email for NCBI
        Entrez.email = email
        
        # Cache for search results and papers
        self._search_cache = {}
        self._paper_cache = {}
        self._cache_timeout = 3600  # 1 hour
        
        # PubMed databases
        self.databases = {
            'pubmed': 'PubMed',
            'pmc': 'PubMed Central',
            'gene': 'Gene',
            'protein': 'Protein',
            'nucleotide': 'Nucleotide'
        }
    
    def search(self, query: str, max_results: int = 10, database: str = "pubmed", 
               sort_by: str = "relevance", retmax: int = 50) -> List[PubMedSearchResult]:
        """Search PubMed papers"""
        try:
            # Check cache first
            cache_key = f"search_{query}_{max_results}_{database}_{sort_by}"
            if cache_key in self._search_cache:
                cached_time, cached_results = self._search_cache[cache_key]
                if time.time() - cached_time < self._cache_timeout:
                    return cached_results[:max_results]
            
            # Perform search
            handle = Entrez.esearch(db=database, term=query, retmax=retmax, sort=sort_by)
            record = Entrez.read(handle)
            handle.close()
            
            if not record['IdList']:
                return []
            
            # Get paper details using XML format
            handle = Entrez.efetch(db=database, id=record['IdList'], rettype="xml", retmode="text")
            records_data = Entrez.read(handle)
            handle.close()
            
            # Extract articles from the XML data
            records = []
            if 'PubmedArticle' in records_data:
                records = records_data['PubmedArticle']
            elif 'PubmedBookArticle' in records_data:
                records = records_data['PubmedBookArticle']
            
            results = []
            for record in records:
                if len(results) >= max_results:
                    break
                
                try:
                    # Extract data from XML structure
                    medline_citation = record.get('MedlineCitation', {})
                    article = medline_citation.get('Article', {})
                    
                    # Extract PMID
                    pmid = str(medline_citation.get('PMID', ''))
                    
                    # Extract title
                    title = article.get('ArticleTitle', 'No title available')
                    if isinstance(title, list):
                        title = ' '.join(title)
                    
                    # Extract authors
                    authors = []
                    author_list = article.get('AuthorList', [])
                    for author in author_list:
                        if 'LastName' in author and 'ForeName' in author:
                            authors.append(f"{author['ForeName']} {author['LastName']}")
                        elif 'LastName' in author:
                            authors.append(author['LastName'])
                    
                    # Extract abstract
                    abstract = 'No abstract available'
                    if 'Abstract' in article:
                        abstract_text = article['Abstract'].get('AbstractText', [])
                        if isinstance(abstract_text, list):
                            abstract = ' '.join([str(text) for text in abstract_text])
                        else:
                            abstract = str(abstract_text)
                    
                    # Extract journal
                    journal = 'Unknown journal'
                    if 'Journal' in article:
                        journal_info = article['Journal']
                        if 'Title' in journal_info:
                            journal = journal_info['Title']
                    
                    # Extract publication date
                    pub_date = 'Unknown date'
                    if 'Journal' in article and 'JournalIssue' in article['Journal']:
                        journal_issue = article['Journal']['JournalIssue']
                        if 'PubDate' in journal_issue:
                            pub_date_info = journal_issue['PubDate']
                            if 'Year' in pub_date_info:
                                pub_date = pub_date_info['Year']
                    
                    # Extract MeSH terms
                    mesh_terms = []
                    if 'MeshHeadingList' in medline_citation:
                        mesh_list = medline_citation['MeshHeadingList']
                        for mesh in mesh_list:
                            if 'DescriptorName' in mesh:
                                mesh_terms.append(mesh['DescriptorName'])
                    
                    # Extract publication type
                    pub_type = 'Journal Article'
                    if 'PublicationTypeList' in article:
                        pub_types = article['PublicationTypeList']
                        if pub_types:
                            pub_type = pub_types[0]
                    
                    results.append(PubMedSearchResult(
                        pmid=pmid,
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        journal=journal,
                        publication_date=pub_date,
                        publication_type=pub_type,
                        mesh_terms=mesh_terms
                    ))
                except Exception as e:
                    # Skip problematic records
                    continue
            
            # Cache results
            self._search_cache[cache_key] = (time.time(), results)
            
            return results
            
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    def get_paper(self, pmid: str) -> PubMedPaper:
        """Get detailed paper information"""
        try:
            # Check cache first
            cache_key = f"paper_{pmid}"
            if cache_key in self._paper_cache:
                cached_time, cached_paper = self._paper_cache[cache_key]
                if time.time() - cached_time < self._cache_timeout:
                    return cached_paper
            
            # Get paper details using XML format
            handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="text")
            records_data = Entrez.read(handle)
            handle.close()
            
            # Extract the article from the XML data
            if 'PubmedArticle' in records_data:
                record = records_data['PubmedArticle'][0]
            elif 'PubmedBookArticle' in records_data:
                record = records_data['PubmedBookArticle'][0]
            else:
                raise Exception("No article found")
            
            # Extract data from XML structure
            medline_citation = record.get('MedlineCitation', {})
            article = medline_citation.get('Article', {})
            
            # Extract PMID
            pmid = str(medline_citation.get('PMID', pmid))
            
            # Extract title
            title = article.get('ArticleTitle', 'No title available')
            if isinstance(title, list):
                title = ' '.join(title)
            
            # Extract authors
            authors = []
            author_list = article.get('AuthorList', [])
            for author in author_list:
                if 'LastName' in author and 'ForeName' in author:
                    authors.append(f"{author['ForeName']} {author['LastName']}")
                elif 'LastName' in author:
                    authors.append(author['LastName'])
            
            # Extract abstract
            abstract = 'No abstract available'
            if 'Abstract' in article:
                abstract_text = article['Abstract'].get('AbstractText', [])
                if isinstance(abstract_text, list):
                    abstract = ' '.join([str(text) for text in abstract_text])
                else:
                    abstract = str(abstract_text)
            
            # Extract journal
            journal = 'Unknown journal'
            if 'Journal' in article:
                journal_info = article['Journal']
                if 'Title' in journal_info:
                    journal = journal_info['Title']
            
            # Extract publication date
            publication_date = 'Unknown date'
            if 'Journal' in article and 'JournalIssue' in article['Journal']:
                journal_issue = article['Journal']['JournalIssue']
                if 'PubDate' in journal_issue:
                    pub_date_info = journal_issue['PubDate']
                    if 'Year' in pub_date_info:
                        publication_date = pub_date_info['Year']
            
            # Extract MeSH terms
            mesh_terms = []
            if 'MeshHeadingList' in medline_citation:
                mesh_list = medline_citation['MeshHeadingList']
                for mesh in mesh_list:
                    if 'DescriptorName' in mesh:
                        mesh_terms.append(mesh['DescriptorName'])
            
            # Extract keywords (same as MeSH terms for now)
            keywords = mesh_terms.copy()
            
            # Extract publication type
            publication_type = 'Journal Article'
            if 'PublicationTypeList' in article:
                pub_types = article['PublicationTypeList']
                if pub_types:
                    publication_type = pub_types[0]
            
            # Extract additional metadata (simplified for XML format)
            doi = None
            issn = None
            volume = None
            issue = None
            pages = None
            language = 'English'
            country = None
            
            paper = PubMedPaper(
                pmid=record.get('PMID', pmid),
                title=record.get('TI', 'No title available'),
                authors=authors,
                abstract=abstract,
                journal=journal,
                publication_date=publication_date,
                publication_type=publication_type,
                mesh_terms=mesh_terms,
                keywords=keywords,
                doi=doi,
                issn=issn,
                volume=volume,
                issue=issue,
                pages=pages,
                language=language,
                country=country,
                citation_count=None  # Would need additional API call
            )
            
            # Cache paper
            self._paper_cache[cache_key] = (time.time(), paper)
            
            return paper
            
        except Exception as e:
            raise Exception(f"Failed to get paper: {str(e)}")
    
    def search_by_author(self, author_name: str, max_results: int = 10) -> List[PubMedSearchResult]:
        """Search papers by author"""
        try:
            query = f"{author_name}[Author]"
            return self.search(query, max_results)
            
        except Exception as e:
            raise Exception(f"Author search failed: {str(e)}")
    
    def search_by_journal(self, journal_name: str, max_results: int = 20) -> List[PubMedSearchResult]:
        """Search papers by journal"""
        try:
            query = f"{journal_name}[Journal]"
            return self.search(query, max_results)
            
        except Exception as e:
            raise Exception(f"Journal search failed: {str(e)}")
    
    def search_by_date_range(self, start_date: str, end_date: str, 
                           query: str = "all", max_results: int = 50) -> List[PubMedSearchResult]:
        """Search papers by date range"""
        try:
            date_query = f"{start_date}:{end_date}[dp]"
            full_query = f"({query}) AND {date_query}"
            return self.search(full_query, max_results)
            
        except Exception as e:
            raise Exception(f"Date range search failed: {str(e)}")
    
    def search_by_mesh_term(self, mesh_term: str, max_results: int = 20) -> List[PubMedSearchResult]:
        """Search papers by MeSH term"""
        try:
            query = f"{mesh_term}[MeSH Terms]"
            return self.search(query, max_results)
            
        except Exception as e:
            raise Exception(f"MeSH term search failed: {str(e)}")
    
    def get_recent_papers(self, max_results: int = 20) -> List[PubMedSearchResult]:
        """Get recent papers"""
        try:
            # Search for papers from the last year
            current_year = time.strftime("%Y")
            query = f"{current_year}[dp]"
            return self.search(query, max_results, sort_by="date")
            
        except Exception as e:
            raise Exception(f"Recent papers search failed: {str(e)}")
    
    def get_related_papers(self, pmid: str, max_results: int = 10) -> List[PubMedSearchResult]:
        """Get papers related to a given paper"""
        try:
            # Get the main paper
            paper = self.get_paper(pmid)
            
            # Search for papers with similar MeSH terms
            if paper.mesh_terms:
                mesh_query = " OR ".join([f'"{term}"[MeSH Terms]' for term in paper.mesh_terms[:3]])
                return self.search(mesh_query, max_results)
            else:
                # Fallback to title-based search
                title_words = paper.title.split()[:5]
                title_query = " AND ".join([f'"{word}"[Title]' for word in title_words])
                return self.search(title_query, max_results)
            
        except Exception as e:
            raise Exception(f"Related papers search failed: {str(e)}")
    
    def get_author_info(self, author_name: str) -> PubMedAuthor:
        """Get information about an author"""
        try:
            papers = self.search_by_author(author_name, max_results=100)
            
            # Collect journals
            journals = []
            for paper in papers:
                if paper.journal not in journals:
                    journals.append(paper.journal)
            
            # Collect research areas from MeSH terms
            research_areas = []
            for paper in papers:
                research_areas.extend(paper.mesh_terms)
            
            # Get unique research areas
            unique_areas = list(set(research_areas))[:10]
            
            return PubMedAuthor(
                name=author_name,
                papers=[paper.pmid for paper in papers],
                journals=journals[:10],
                total_papers=len(papers),
                research_areas=unique_areas
            )
            
        except Exception as e:
            raise Exception(f"Author info search failed: {str(e)}")
    
    def get_journal_info(self, journal_name: str) -> PubMedJournal:
        """Get information about a journal"""
        try:
            papers = self.search_by_journal(journal_name, max_results=50)
            
            # Get ISSN if available
            issn = None
            if papers:
                # Try to get ISSN from first paper
                try:
                    paper_details = self.get_paper(papers[0].pmid)
                    issn = paper_details.issn
                except:
                    pass
            
            return PubMedJournal(
                name=journal_name,
                issn=issn or "Unknown",
                papers=[paper.pmid for paper in papers],
                total_papers=len(papers),
                impact_factor=None  # Would need additional API call
            )
            
        except Exception as e:
            raise Exception(f"Journal info search failed: {str(e)}")
    
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
                'we', 'study', 'research', 'analysis', 'results', 'method', 'approach',
                'patient', 'treatment', 'clinical', 'medical', 'health', 'disease'
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
    
    def get_databases(self) -> Dict[str, str]:
        """Get available PubMed databases"""
        return self.databases
    
    def clear_cache(self):
        """Clear the cache"""
        self._search_cache.clear()
        self._paper_cache.clear()


class PubMedToolsManager:
    """CLI integration for PubMed tools"""
    
    def __init__(self, email: str = "agno-cli@example.com"):
        self.pubmed_tools = PubMedTools(email)
        self.console = Console()
    
    def search(self, query: str, max_results: int = 10, database: str = "pubmed", 
               sort_by: str = "relevance", format: str = "table"):
        """Search PubMed papers"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Searching PubMed for '{query}'...", total=None)
                results = self.pubmed_tools.search(query, max_results, database, sort_by)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'pmid': r.pmid,
                    'title': r.title,
                    'authors': r.authors,
                    'abstract': r.abstract,
                    'journal': r.journal,
                    'publication_date': r.publication_date,
                    'publication_type': r.publication_type,
                    'mesh_terms': r.mesh_terms[:5]  # Limit for JSON
                } for r in results], indent=2))
                return
            
            # Create search results table
            table = Table(title=f"PubMed Search Results for '{query}'")
            table.add_column("PMID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Authors", style="yellow")
            table.add_column("Journal", style="green")
            table.add_column("Date", style="magenta")
            table.add_column("Type", style="blue")
            
            for result in results:
                # Truncate title if too long
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                
                # Format authors
                authors = ", ".join(result.authors[:2])  # Show first 2 authors
                if len(result.authors) > 2:
                    authors += f" et al. ({len(result.authors)} total)"
                
                # Truncate journal name
                journal = result.journal[:30] + "..." if len(result.journal) > 30 else result.journal
                
                table.add_row(
                    result.pmid,
                    title,
                    authors,
                    journal,
                    result.publication_date,
                    result.publication_type
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Search error: {e}[/red]")
    
    def get_paper(self, pmid: str, format: str = "table"):
        """Get detailed paper information"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Fetching paper '{pmid}'...", total=None)
                paper = self.pubmed_tools.get_paper(pmid)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'pmid': paper.pmid,
                    'title': paper.title,
                    'authors': paper.authors,
                    'abstract': paper.abstract,
                    'journal': paper.journal,
                    'publication_date': paper.publication_date,
                    'publication_type': paper.publication_type,
                    'mesh_terms': paper.mesh_terms[:10],
                    'keywords': paper.keywords[:10],
                    'doi': paper.doi,
                    'issn': paper.issn,
                    'language': paper.language,
                    'country': paper.country
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
            
            stats_table.add_row("PMID", paper.pmid)
            stats_table.add_row("Journal", paper.journal)
            stats_table.add_row("Publication Date", paper.publication_date)
            stats_table.add_row("Publication Type", paper.publication_type)
            stats_table.add_row("Language", paper.language)
            
            if paper.doi:
                stats_table.add_row("DOI", paper.doi)
            if paper.issn:
                stats_table.add_row("ISSN", paper.issn)
            if paper.volume:
                stats_table.add_row("Volume", paper.volume)
            if paper.issue:
                stats_table.add_row("Issue", paper.issue)
            if paper.pages:
                stats_table.add_row("Pages", paper.pages)
            if paper.country:
                stats_table.add_row("Country", paper.country)
            
            self.console.print(stats_table)
            
            # Authors
            if paper.authors:
                authors_text = ", ".join(paper.authors)
                self.console.print(Panel(authors_text, title="Authors", border_style="yellow"))
            
            # MeSH terms
            if paper.mesh_terms:
                mesh_text = ", ".join(paper.mesh_terms[:15])
                self.console.print(Panel(mesh_text, title="MeSH Terms", border_style="blue"))
            
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
                results = self.pubmed_tools.search_by_author(author_name, max_results)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'pmid': r.pmid,
                    'title': r.title,
                    'journal': r.journal,
                    'publication_date': r.publication_date,
                    'publication_type': r.publication_type
                } for r in results], indent=2))
                return
            
            # Create author papers table
            table = Table(title=f"Papers by {author_name}")
            table.add_column("PMID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Journal", style="green")
            table.add_column("Date", style="magenta")
            table.add_column("Type", style="blue")
            
            for result in results:
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                journal = result.journal[:30] + "..." if len(result.journal) > 30 else result.journal
                
                table.add_row(
                    result.pmid,
                    title,
                    journal,
                    result.publication_date,
                    result.publication_type
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Author search error: {e}[/red]")
    
    def search_by_journal(self, journal_name: str, max_results: int = 20, format: str = "table"):
        """Search papers by journal"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Searching papers in journal '{journal_name}'...", total=None)
                results = self.pubmed_tools.search_by_journal(journal_name, max_results)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'pmid': r.pmid,
                    'title': r.title,
                    'authors': r.authors,
                    'publication_date': r.publication_date,
                    'publication_type': r.publication_type
                } for r in results], indent=2))
                return
            
            # Create journal papers table
            table = Table(title=f"Papers in Journal: {journal_name}")
            table.add_column("PMID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Authors", style="yellow")
            table.add_column("Date", style="magenta")
            table.add_column("Type", style="blue")
            
            for result in results:
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                authors = ", ".join(result.authors[:2])
                if len(result.authors) > 2:
                    authors += f" et al. ({len(result.authors)} total)"
                
                table.add_row(
                    result.pmid,
                    title,
                    authors,
                    result.publication_date,
                    result.publication_type
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Journal search error: {e}[/red]")
    
    def get_recent_papers(self, max_results: int = 20, format: str = "table"):
        """Get recent papers"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Fetching recent papers...", total=None)
                results = self.pubmed_tools.get_recent_papers(max_results)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'pmid': r.pmid,
                    'title': r.title,
                    'authors': r.authors,
                    'journal': r.journal,
                    'publication_date': r.publication_date
                } for r in results], indent=2))
                return
            
            # Create recent papers table
            table = Table(title="Recent Papers")
            table.add_column("PMID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Authors", style="yellow")
            table.add_column("Journal", style="green")
            table.add_column("Date", style="magenta")
            
            for result in results:
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                authors = ", ".join(result.authors[:2])
                if len(result.authors) > 2:
                    authors += f" et al. ({len(result.authors)} total)"
                journal = result.journal[:30] + "..." if len(result.journal) > 30 else result.journal
                
                table.add_row(
                    result.pmid,
                    title,
                    authors,
                    journal,
                    result.publication_date
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Recent papers error: {e}[/red]")
    
    def get_related_papers(self, pmid: str, max_results: int = 10, format: str = "table"):
        """Get papers related to a given paper"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Finding papers related to '{pmid}'...", total=None)
                results = self.pubmed_tools.get_related_papers(pmid, max_results)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'pmid': r.pmid,
                    'title': r.title,
                    'authors': r.authors,
                    'journal': r.journal,
                    'publication_date': r.publication_date,
                    'mesh_terms': r.mesh_terms[:5]
                } for r in results], indent=2))
                return
            
            # Create related papers table
            table = Table(title=f"Papers Related to {pmid}")
            table.add_column("PMID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Authors", style="yellow")
            table.add_column("Journal", style="green")
            table.add_column("Date", style="magenta")
            table.add_column("MeSH Terms", style="blue")
            
            for result in results:
                title = result.title[:60] + "..." if len(result.title) > 60 else result.title
                authors = ", ".join(result.authors[:2])
                if len(result.authors) > 2:
                    authors += f" et al. ({len(result.authors)} total)"
                journal = result.journal[:30] + "..." if len(result.journal) > 30 else result.journal
                mesh_terms = ", ".join(result.mesh_terms[:3]) if result.mesh_terms else "None"
                
                table.add_row(
                    result.pmid,
                    title,
                    authors,
                    journal,
                    result.publication_date,
                    mesh_terms
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
                author = self.pubmed_tools.get_author_info(author_name)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'name': author.name,
                    'total_papers': author.total_papers,
                    'journals': author.journals[:10],
                    'research_areas': author.research_areas,
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
            stats_table.add_row("Journals", str(len(author.journals)))
            
            self.console.print(stats_table)
            
            # Journals
            if author.journals:
                journals_text = ", ".join(author.journals[:10])
                self.console.print(Panel(journals_text, title="Journals", border_style="yellow"))
            
            # Research areas
            if author.research_areas:
                areas_text = ", ".join(author.research_areas[:10])
                self.console.print(Panel(areas_text, title="Research Areas", border_style="blue"))
            
        except Exception as e:
            self.console.print(f"[red]Author info error: {e}[/red]")
    
    def get_databases(self, format: str = "table"):
        """Get available PubMed databases"""
        try:
            databases = self.pubmed_tools.get_databases()
            
            if format == "json":
                import json
                self.console.print(json.dumps(databases, indent=2))
                return
            
            # Create databases table
            table = Table(title="PubMed Databases")
            table.add_column("Code", style="cyan")
            table.add_column("Description", style="white")
            
            for code, description in databases.items():
                table.add_row(code, description)
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Databases error: {e}[/red]")
    
    def extract_keywords(self, text: str, max_keywords: int = 10, format: str = "table"):
        """Extract keywords from text"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Extracting keywords...", total=None)
                keywords = self.pubmed_tools.extract_keywords(text, max_keywords)
            
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
        self.pubmed_tools.clear_cache()
        self.console.print("[green]Cache cleared successfully[/green]") 