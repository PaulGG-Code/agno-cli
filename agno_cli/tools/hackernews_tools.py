"""
Hacker News Tools - HN API Integration

This module provides comprehensive Hacker News API integration with:
- Story retrieval and filtering
- Comment threads and discussions
- User profiles and activity
- Real-time updates and trending
- Rich output formatting
- Caching and performance optimization
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown
from datetime import datetime, timedelta


@dataclass
class HNStory:
    """Hacker News story information"""
    id: int
    title: str
    url: Optional[str]
    text: Optional[str]
    score: int
    by: str
    time: int
    descendants: int
    kids: List[int]
    type: str
    deleted: bool
    dead: bool
    poll: Optional[int]
    parts: Optional[List[int]]


@dataclass
class HNComment:
    """Hacker News comment information"""
    id: int
    text: str
    by: str
    time: int
    kids: List[int]
    parent: int
    deleted: bool
    dead: bool
    type: str


@dataclass
class HNUser:
    """Hacker News user information"""
    id: str
    created: int
    karma: int
    about: Optional[str]
    submitted: List[int]
    delay: int


@dataclass
class HNJob:
    """Hacker News job posting information"""
    id: int
    title: str
    url: Optional[str]
    text: Optional[str]
    score: int
    by: str
    time: int
    type: str
    deleted: bool
    dead: bool


@dataclass
class HNAsk:
    """Hacker News ask HN information"""
    id: int
    title: str
    text: str
    score: int
    by: str
    time: int
    descendants: int
    kids: List[int]
    type: str
    deleted: bool
    dead: bool


class HackerNewsTools:
    """Core Hacker News API tools"""
    
    def __init__(self):
        self.console = Console()
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AgnoCLI/1.0 (https://github.com/agno-ai/agno-cli)'
        })
        
        # Cache for API responses
        self._cache = {}
        self._cache_timeout = 300  # 5 minutes
        
        # HN API endpoints
        self.endpoints = {
            'top_stories': 'topstories.json',
            'new_stories': 'newstories.json',
            'best_stories': 'beststories.json',
            'ask_stories': 'askstories.json',
            'show_stories': 'showstories.json',
            'job_stories': 'jobstories.json',
            'updates': 'updates.json',
            'item': 'item/{id}.json',
            'user': 'user/{username}.json'
        }
    
    def _get_url(self, endpoint: str, **kwargs) -> str:
        """Build API URL"""
        if kwargs:
            return f"{self.base_url}/{endpoint.format(**kwargs)}"
        return f"{self.base_url}/{endpoint}"
    
    def _make_request(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """Make API request with caching"""
        if use_cache and url in self._cache:
            cached_time, cached_data = self._cache[url]
            if time.time() - cached_time < self._cache_timeout:
                return cached_data
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if use_cache:
                self._cache[url] = (time.time(), data)
            
            return data
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_top_stories(self, limit: int = 20) -> List[int]:
        """Get top story IDs"""
        url = self._get_url(self.endpoints['top_stories'])
        story_ids = self._make_request(url)
        return story_ids[:limit]
    
    def get_new_stories(self, limit: int = 20) -> List[int]:
        """Get new story IDs"""
        url = self._get_url(self.endpoints['new_stories'])
        story_ids = self._make_request(url)
        return story_ids[:limit]
    
    def get_best_stories(self, limit: int = 20) -> List[int]:
        """Get best story IDs"""
        url = self._get_url(self.endpoints['best_stories'])
        story_ids = self._make_request(url)
        return story_ids[:limit]
    
    def get_ask_stories(self, limit: int = 20) -> List[int]:
        """Get ask HN story IDs"""
        url = self._get_url(self.endpoints['ask_stories'])
        story_ids = self._make_request(url)
        return story_ids[:limit]
    
    def get_show_stories(self, limit: int = 20) -> List[int]:
        """Get show HN story IDs"""
        url = self._get_url(self.endpoints['show_stories'])
        story_ids = self._make_request(url)
        return story_ids[:limit]
    
    def get_job_stories(self, limit: int = 20) -> List[int]:
        """Get job story IDs"""
        url = self._get_url(self.endpoints['job_stories'])
        story_ids = self._make_request(url)
        return story_ids[:limit]
    
    def get_story(self, story_id: int) -> HNStory:
        """Get story by ID"""
        url = self._get_url(self.endpoints['item'], id=story_id)
        data = self._make_request(url)
        
        return HNStory(
            id=data.get('id'),
            title=data.get('title', ''),
            url=data.get('url'),
            text=data.get('text'),
            score=data.get('score', 0),
            by=data.get('by', ''),
            time=data.get('time', 0),
            descendants=data.get('descendants', 0),
            kids=data.get('kids', []),
            type=data.get('type', 'story'),
            deleted=data.get('deleted', False),
            dead=data.get('dead', False),
            poll=data.get('poll'),
            parts=data.get('parts')
        )
    
    def get_comment(self, comment_id: int) -> HNComment:
        """Get comment by ID"""
        url = self._get_url(self.endpoints['item'], id=comment_id)
        data = self._make_request(url)
        
        return HNComment(
            id=data.get('id'),
            text=data.get('text', ''),
            by=data.get('by', ''),
            time=data.get('time', 0),
            kids=data.get('kids', []),
            parent=data.get('parent', 0),
            deleted=data.get('deleted', False),
            dead=data.get('dead', False),
            type=data.get('type', 'comment')
        )
    
    def get_user(self, username: str) -> HNUser:
        """Get user by username"""
        url = self._get_url(self.endpoints['user'], username=username)
        data = self._make_request(url)
        
        return HNUser(
            id=data.get('id', ''),
            created=data.get('created', 0),
            karma=data.get('karma', 0),
            about=data.get('about'),
            submitted=data.get('submitted', []),
            delay=data.get('delay', 0)
        )
    
    def get_job(self, job_id: int) -> HNJob:
        """Get job by ID"""
        url = self._get_url(self.endpoints['item'], id=job_id)
        data = self._make_request(url)
        
        return HNJob(
            id=data.get('id'),
            title=data.get('title', ''),
            url=data.get('url'),
            text=data.get('text'),
            score=data.get('score', 0),
            by=data.get('by', ''),
            time=data.get('time', 0),
            type=data.get('type', 'job'),
            deleted=data.get('deleted', False),
            dead=data.get('dead', False)
        )
    
    def get_ask(self, ask_id: int) -> HNAsk:
        """Get ask HN by ID"""
        url = self._get_url(self.endpoints['item'], id=ask_id)
        data = self._make_request(url)
        
        return HNAsk(
            id=data.get('id'),
            title=data.get('title', ''),
            text=data.get('text', ''),
            score=data.get('score', 0),
            by=data.get('by', ''),
            time=data.get('time', 0),
            descendants=data.get('descendants', 0),
            kids=data.get('kids', []),
            type=data.get('type', 'story'),
            deleted=data.get('deleted', False),
            dead=data.get('dead', False)
        )
    
    def get_stories_by_type(self, story_type: str, limit: int = 20) -> List[HNStory]:
        """Get stories by type (top, new, best, ask, show, job)"""
        type_methods = {
            'top': self.get_top_stories,
            'new': self.get_new_stories,
            'best': self.get_best_stories,
            'ask': self.get_ask_stories,
            'show': self.get_show_stories,
            'job': self.get_job_stories
        }
        
        if story_type not in type_methods:
            raise ValueError(f"Invalid story type: {story_type}")
        
        story_ids = type_methods[story_type](limit)
        stories = []
        
        for story_id in story_ids:
            try:
                story = self.get_story(story_id)
                stories.append(story)
            except Exception as e:
                # Skip problematic stories
                continue
        
        return stories
    
    def search_stories(self, query: str, limit: int = 20) -> List[HNStory]:
        """Search stories by title (simple text search)"""
        # Get top stories and filter by query
        story_ids = self.get_top_stories(limit * 2)  # Get more to filter
        matching_stories = []
        
        for story_id in story_ids:
            try:
                story = self.get_story(story_id)
                if query.lower() in story.title.lower():
                    matching_stories.append(story)
                    if len(matching_stories) >= limit:
                        break
            except Exception:
                continue
        
        return matching_stories
    
    def get_story_comments(self, story_id: int, max_depth: int = 3) -> List[HNComment]:
        """Get comments for a story with depth limit"""
        try:
            story = self.get_story(story_id)
            comments = []
            
            def get_comments_recursive(comment_ids: List[int], depth: int = 0):
                if depth >= max_depth:
                    return
                
                for comment_id in comment_ids:
                    try:
                        comment = self.get_comment(comment_id)
                        if not comment.deleted and not comment.dead:
                            comments.append(comment)
                            if comment.kids:
                                get_comments_recursive(comment.kids, depth + 1)
                    except Exception:
                        continue
            
            if story.kids:
                get_comments_recursive(story.kids)
            
            return comments
        except Exception as e:
            raise Exception(f"Failed to get comments: {str(e)}")
    
    def get_user_stories(self, username: str, limit: int = 20) -> List[HNStory]:
        """Get stories submitted by a user"""
        try:
            user = self.get_user(username)
            stories = []
            
            for story_id in user.submitted[:limit]:
                try:
                    story = self.get_story(story_id)
                    if story.type == 'story':
                        stories.append(story)
                except Exception:
                    continue
            
            return stories
        except Exception as e:
            raise Exception(f"Failed to get user stories: {str(e)}")
    
    def get_user_comments(self, username: str, limit: int = 20) -> List[HNComment]:
        """Get comments by a user"""
        try:
            user = self.get_user(username)
            comments = []
            
            for comment_id in user.submitted[:limit]:
                try:
                    comment = self.get_comment(comment_id)
                    if comment.type == 'comment':
                        comments.append(comment)
                except Exception:
                    continue
            
            return comments
        except Exception as e:
            raise Exception(f"Failed to get user comments: {str(e)}")
    
    def get_trending_stories(self, hours: int = 24, limit: int = 20) -> List[HNStory]:
        """Get trending stories from the last N hours"""
        cutoff_time = int(time.time()) - (hours * 3600)
        story_ids = self.get_top_stories(limit * 2)
        trending_stories = []
        
        for story_id in story_ids:
            try:
                story = self.get_story(story_id)
                if story.time >= cutoff_time:
                    trending_stories.append(story)
                    if len(trending_stories) >= limit:
                        break
            except Exception:
                continue
        
        return trending_stories
    
    def get_updates(self) -> Dict[str, Any]:
        """Get recent updates"""
        url = self._get_url(self.endpoints['updates'])
        return self._make_request(url, use_cache=False)  # Don't cache updates
    
    def format_time(self, timestamp: int) -> str:
        """Format timestamp to human-readable time"""
        dt = datetime.fromtimestamp(timestamp)
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "just now"
    
    def clear_cache(self):
        """Clear the cache"""
        self._cache.clear()


class HackerNewsToolsManager:
    """CLI integration for Hacker News tools"""
    
    def __init__(self):
        self.hn_tools = HackerNewsTools()
        self.console = Console()
    
    def get_stories(self, story_type: str = "top", limit: int = 20, format: str = "table"):
        """Get stories by type"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Fetching {story_type} stories...", total=None)
                stories = self.hn_tools.get_stories_by_type(story_type, limit)
            
            if format == "json":
                import json
                story_data = []
                for story in stories:
                    story_data.append({
                        'id': story.id,
                        'title': story.title,
                        'url': story.url,
                        'score': story.score,
                        'by': story.by,
                        'time': story.time,
                        'descendants': story.descendants,
                        'type': story.type
                    })
                self.console.print(json.dumps(story_data, indent=2))
                return
            
            # Create stories table
            table = Table(title=f"Hacker News {story_type.title()} Stories")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Score", style="green", justify="right")
            table.add_column("Author", style="yellow")
            table.add_column("Comments", style="blue", justify="right")
            table.add_column("Time", style="magenta")
            
            for story in stories:
                # Truncate title if too long
                title = story.title[:60] + "..." if len(story.title) > 60 else story.title
                
                # Format time
                time_str = self.hn_tools.format_time(story.time)
                
                table.add_row(
                    str(story.id),
                    title,
                    str(story.score),
                    story.by,
                    str(story.descendants),
                    time_str
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error fetching stories: {e}[/red]")
    
    def get_story(self, story_id: int, format: str = "table"):
        """Get story details"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Fetching story {story_id}...", total=None)
                story = self.hn_tools.get_story(story_id)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'id': story.id,
                    'title': story.title,
                    'url': story.url,
                    'text': story.text,
                    'score': story.score,
                    'by': story.by,
                    'time': story.time,
                    'descendants': story.descendants,
                    'type': story.type
                }, indent=2))
                return
            
            # Display story information
            self.console.print(Panel(f"[bold cyan]{story.title}[/bold cyan]", title="Story"))
            
            if story.url:
                self.console.print(Panel(f"[blue]{story.url}[/blue]", title="URL", border_style="blue"))
            
            if story.text:
                self.console.print(Panel(story.text, title="Text", border_style="green"))
            
            # Story stats
            stats_table = Table(title="Story Statistics")
            stats_table.add_column("Property", style="cyan")
            stats_table.add_column("Value", style="white")
            
            stats_table.add_row("ID", str(story.id))
            stats_table.add_row("Score", str(story.score))
            stats_table.add_row("Author", story.by)
            stats_table.add_row("Comments", str(story.descendants))
            stats_table.add_row("Type", story.type)
            stats_table.add_row("Time", self.hn_tools.format_time(story.time))
            
            self.console.print(stats_table)
            
        except Exception as e:
            self.console.print(f"[red]Error fetching story: {e}[/red]")
    
    def get_comments(self, story_id: int, max_depth: int = 3, format: str = "table"):
        """Get comments for a story"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Fetching comments for story {story_id}...", total=None)
                comments = self.hn_tools.get_story_comments(story_id, max_depth)
            
            if format == "json":
                import json
                comment_data = []
                for comment in comments:
                    comment_data.append({
                        'id': comment.id,
                        'text': comment.text,
                        'by': comment.by,
                        'time': comment.time,
                        'parent': comment.parent
                    })
                self.console.print(json.dumps(comment_data, indent=2))
                return
            
            if not comments:
                self.console.print("[yellow]No comments found[/yellow]")
                return
            
            # Create comments table
            table = Table(title=f"Comments for Story {story_id}")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Author", style="yellow")
            table.add_column("Text", style="white", no_wrap=True)
            table.add_column("Time", style="magenta")
            
            for comment in comments:
                # Truncate text if too long
                text = comment.text[:80] + "..." if len(comment.text) > 80 else comment.text
                
                # Format time
                time_str = self.hn_tools.format_time(comment.time)
                
                table.add_row(
                    str(comment.id),
                    comment.by,
                    text,
                    time_str
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error fetching comments: {e}[/red]")
    
    def get_user(self, username: str, format: str = "table"):
        """Get user information"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Fetching user {username}...", total=None)
                user = self.hn_tools.get_user(username)
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'id': user.id,
                    'created': user.created,
                    'karma': user.karma,
                    'about': user.about,
                    'submitted_count': len(user.submitted),
                    'delay': user.delay
                }, indent=2))
                return
            
            # Display user information
            self.console.print(Panel(f"[bold cyan]{user.id}[/bold cyan]", title="User"))
            
            if user.about:
                self.console.print(Panel(user.about, title="About", border_style="green"))
            
            # User stats
            stats_table = Table(title="User Statistics")
            stats_table.add_column("Property", style="cyan")
            stats_table.add_column("Value", style="white")
            
            stats_table.add_row("Username", user.id)
            stats_table.add_row("Karma", str(user.karma))
            stats_table.add_row("Created", self.hn_tools.format_time(user.created))
            stats_table.add_row("Submissions", str(len(user.submitted)))
            stats_table.add_row("Delay", str(user.delay))
            
            self.console.print(stats_table)
            
        except Exception as e:
            self.console.print(f"[red]Error fetching user: {e}[/red]")
    
    def get_user_stories(self, username: str, limit: int = 20, format: str = "table"):
        """Get stories by user"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Fetching stories by {username}...", total=None)
                stories = self.hn_tools.get_user_stories(username, limit)
            
            if format == "json":
                import json
                story_data = []
                for story in stories:
                    story_data.append({
                        'id': story.id,
                        'title': story.title,
                        'url': story.url,
                        'score': story.score,
                        'time': story.time,
                        'descendants': story.descendants
                    })
                self.console.print(json.dumps(story_data, indent=2))
                return
            
            if not stories:
                self.console.print("[yellow]No stories found for this user[/yellow]")
                return
            
            # Create user stories table
            table = Table(title=f"Stories by {username}")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Score", style="green", justify="right")
            table.add_column("Comments", style="blue", justify="right")
            table.add_column("Time", style="magenta")
            
            for story in stories:
                title = story.title[:60] + "..." if len(story.title) > 60 else story.title
                time_str = self.hn_tools.format_time(story.time)
                
                table.add_row(
                    str(story.id),
                    title,
                    str(story.score),
                    str(story.descendants),
                    time_str
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error fetching user stories: {e}[/red]")
    
    def search_stories(self, query: str, limit: int = 20, format: str = "table"):
        """Search stories"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Searching for '{query}'...", total=None)
                stories = self.hn_tools.search_stories(query, limit)
            
            if format == "json":
                import json
                story_data = []
                for story in stories:
                    story_data.append({
                        'id': story.id,
                        'title': story.title,
                        'url': story.url,
                        'score': story.score,
                        'by': story.by,
                        'time': story.time,
                        'descendants': story.descendants
                    })
                self.console.print(json.dumps(story_data, indent=2))
                return
            
            if not stories:
                self.console.print("[yellow]No stories found matching your query[/yellow]")
                return
            
            # Create search results table
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Score", style="green", justify="right")
            table.add_column("Author", style="yellow")
            table.add_column("Comments", style="blue", justify="right")
            table.add_column("Time", style="magenta")
            
            for story in stories:
                title = story.title[:60] + "..." if len(story.title) > 60 else story.title
                time_str = self.hn_tools.format_time(story.time)
                
                table.add_row(
                    str(story.id),
                    title,
                    str(story.score),
                    story.by,
                    str(story.descendants),
                    time_str
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error searching stories: {e}[/red]")
    
    def get_trending(self, hours: int = 24, limit: int = 20, format: str = "table"):
        """Get trending stories"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Fetching trending stories from last {hours}h...", total=None)
                stories = self.hn_tools.get_trending_stories(hours, limit)
            
            if format == "json":
                import json
                story_data = []
                for story in stories:
                    story_data.append({
                        'id': story.id,
                        'title': story.title,
                        'url': story.url,
                        'score': story.score,
                        'by': story.by,
                        'time': story.time,
                        'descendants': story.descendants
                    })
                self.console.print(json.dumps(story_data, indent=2))
                return
            
            if not stories:
                self.console.print("[yellow]No trending stories found[/yellow]")
                return
            
            # Create trending stories table
            table = Table(title=f"Trending Stories (Last {hours}h)")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white", no_wrap=True)
            table.add_column("Score", style="green", justify="right")
            table.add_column("Author", style="yellow")
            table.add_column("Comments", style="blue", justify="right")
            table.add_column("Time", style="magenta")
            
            for story in stories:
                title = story.title[:60] + "..." if len(story.title) > 60 else story.title
                time_str = self.hn_tools.format_time(story.time)
                
                table.add_row(
                    str(story.id),
                    title,
                    str(story.score),
                    story.by,
                    str(story.descendants),
                    time_str
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error fetching trending stories: {e}[/red]")
    
    def get_updates(self, format: str = "table"):
        """Get recent updates"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Fetching recent updates...", total=None)
                updates = self.hn_tools.get_updates()
            
            if format == "json":
                import json
                self.console.print(json.dumps(updates, indent=2))
                return
            
            # Display updates
            if 'items' in updates and updates['items']:
                items_table = Table(title="Updated Items")
                items_table.add_column("Item ID", style="cyan")
                
                for item_id in updates['items'][:20]:  # Show first 20
                    items_table.add_row(str(item_id))
                
                self.console.print(items_table)
            
            if 'profiles' in updates and updates['profiles']:
                profiles_table = Table(title="Updated Profiles")
                profiles_table.add_column("Username", style="cyan")
                
                for username in updates['profiles'][:20]:  # Show first 20
                    profiles_table.add_row(username)
                
                self.console.print(profiles_table)
            
        except Exception as e:
            self.console.print(f"[red]Error fetching updates: {e}[/red]")
    
    def clear_cache(self):
        """Clear the cache"""
        self.hn_tools.clear_cache()
        self.console.print("[green]Cache cleared successfully[/green]") 