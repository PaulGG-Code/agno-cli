"""
Local File System Operations Tool for Agno CLI
Provides comprehensive file and directory operations
"""

import os
import json
import shutil
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


@dataclass
class FileInfo:
    """File information structure"""
    name: str
    path: str
    size: int
    type: str  # 'file' or 'directory'
    modified: datetime
    permissions: str
    mime_type: Optional[str] = None
    extension: Optional[str] = None
    is_hidden: bool = False
    is_symlink: bool = False
    symlink_target: Optional[str] = None


@dataclass
class FileOperationResult:
    """Result of file operations"""
    success: bool
    message: str
    operation: str
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'error': self.error,
            'operation': self.operation,
            'timestamp': self.timestamp.isoformat()
        }


class FileSystemTools:
    """Comprehensive file system operations tool"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.supported_text_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', 
            '.csv', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            '.log', '.sql', '.sh', '.bat', '.ps1', '.r', '.java', '.cpp',
            '.c', '.h', '.php', '.rb', '.go', '.rs', '.swift', '.kt'
        }
    
    def _ensure_safe_path(self, path: Union[str, Path]) -> Path:
        """Ensure path is safe and within allowed directory"""
        path = Path(path)
        
        # Resolve relative paths
        if not path.is_absolute():
            path = self.base_path / path
        
        # Ensure path is within base directory for security
        try:
            path = path.resolve()
            if not str(path).startswith(str(self.base_path.resolve())):
                raise ValueError(f"Path {path} is outside allowed directory")
        except (RuntimeError, ValueError) as e:
            raise ValueError(f"Invalid path: {e}")
        
        return path
    
    def _get_file_info(self, path: Path) -> FileInfo:
        """Get detailed file information"""
        stat = path.stat()
        
        # Determine file type
        if path.is_dir():
            file_type = 'directory'
            mime_type = 'inode/directory'
        else:
            file_type = 'file'
            mime_type = mimetypes.guess_type(str(path))[0]
        
        # Get permissions
        mode = stat.st_mode
        permissions = oct(mode)[-3:]
        
        # Check if hidden
        is_hidden = path.name.startswith('.')
        
        # Check if symlink
        is_symlink = path.is_symlink()
        symlink_target = None
        if is_symlink:
            try:
                symlink_target = str(path.readlink())
            except OSError:
                symlink_target = "broken"
        
        return FileInfo(
            name=path.name,
            path=str(path),
            size=stat.st_size,
            type=file_type,
            modified=datetime.fromtimestamp(stat.st_mtime),
            permissions=permissions,
            mime_type=mime_type,
            extension=path.suffix if path.is_file() else None,
            is_hidden=is_hidden,
            is_symlink=is_symlink,
            symlink_target=symlink_target
        )
    
    def list_directory(self, path: str = ".", show_hidden: bool = False, 
                      recursive: bool = False, max_depth: int = 3) -> FileOperationResult:
        """List directory contents"""
        try:
            target_path = self._ensure_safe_path(path)
            
            if not target_path.exists():
                return FileOperationResult(
                    success=False,
                    message=f"Path does not exist: {path}",
                    error="PathNotFound",
                    operation="list_directory"
                )
            
            if not target_path.is_dir():
                return FileOperationResult(
                    success=False,
                    message=f"Path is not a directory: {path}",
                    error="NotDirectory",
                    operation="list_directory"
                )
            
            items = []
            
            def scan_directory(current_path: Path, depth: int = 0):
                if depth > max_depth:
                    return
                
                try:
                    for item in current_path.iterdir():
                        # Skip hidden files unless requested
                        if not show_hidden and item.name.startswith('.'):
                            continue
                        
                        file_info = self._get_file_info(item)
                        items.append(file_info)
                        
                        # Recursive scan for directories
                        if recursive and item.is_dir() and depth < max_depth:
                            scan_directory(item, depth + 1)
                            
                except PermissionError:
                    pass  # Skip directories we can't access
            
            scan_directory(target_path)
            
            return FileOperationResult(
                success=True,
                message=f"Found {len(items)} items in {path}",
                data=[asdict(item) for item in items],
                operation="list_directory"
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                message=f"Error listing directory: {str(e)}",
                error=str(e),
                operation="list_directory"
            )
    
    def read_file(self, path: str, encoding: str = "utf-8", 
                  max_size: int = 10 * 1024 * 1024) -> FileOperationResult:  # 10MB limit
        """Read file contents"""
        try:
            target_path = self._ensure_safe_path(path)
            
            if not target_path.exists():
                return FileOperationResult(
                    success=False,
                    message=f"File does not exist: {path}",
                    error="FileNotFound",
                    operation="read_file"
                )
            
            if not target_path.is_file():
                return FileOperationResult(
                    success=False,
                    message=f"Path is not a file: {path}",
                    error="NotFile",
                    operation="read_file"
                )
            
            # Check file size
            file_size = target_path.stat().st_size
            if file_size > max_size:
                return FileOperationResult(
                    success=False,
                    message=f"File too large ({file_size} bytes). Max size: {max_size} bytes",
                    error="FileTooLarge",
                    operation="read_file"
                )
            
            # Read file content
            try:
                with open(target_path, 'r', encoding=encoding) as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(target_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    return FileOperationResult(
                        success=False,
                        message=f"Cannot read file (binary or encoding issue): {str(e)}",
                        error="EncodingError",
                        operation="read_file"
                    )
            
            file_info = self._get_file_info(target_path)
            
            return FileOperationResult(
                success=True,
                message=f"Successfully read file: {path}",
                data={
                    'content': content,
                    'file_info': asdict(file_info),
                    'encoding': encoding,
                    'size': file_size
                },
                operation="read_file"
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                message=f"Error reading file: {str(e)}",
                error=str(e),
                operation="read_file"
            )
    
    def write_file(self, path: str, content: str, encoding: str = "utf-8", 
                   overwrite: bool = True, create_dirs: bool = True) -> FileOperationResult:
        """Write content to file"""
        try:
            target_path = self._ensure_safe_path(path)
            
            # Check if file exists and overwrite flag
            if target_path.exists() and not overwrite:
                return FileOperationResult(
                    success=False,
                    message=f"File already exists and overwrite=False: {path}",
                    error="FileExists",
                    operation="write_file"
                )
            
            # Create parent directories if needed
            if create_dirs:
                target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(target_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            file_info = self._get_file_info(target_path)
            
            return FileOperationResult(
                success=True,
                message=f"Successfully wrote file: {path}",
                data={
                    'file_info': asdict(file_info),
                    'size': len(content.encode(encoding)),
                    'encoding': encoding
                },
                operation="write_file"
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                message=f"Error writing file: {str(e)}",
                error=str(e),
                operation="write_file"
            )
    
    def delete_file(self, path: str, recursive: bool = False) -> FileOperationResult:
        """Delete file or directory"""
        try:
            target_path = self._ensure_safe_path(path)
            
            if not target_path.exists():
                return FileOperationResult(
                    success=False,
                    message=f"Path does not exist: {path}",
                    error="PathNotFound",
                    operation="delete_file"
                )
            
            # Get file info before deletion
            file_info = self._get_file_info(target_path)
            
            if target_path.is_dir():
                if recursive:
                    shutil.rmtree(target_path)
                else:
                    return FileOperationResult(
                        success=False,
                        message=f"Directory not empty. Use recursive=True to delete: {path}",
                        error="DirectoryNotEmpty",
                        operation="delete_file"
                    )
            else:
                target_path.unlink()
            
            return FileOperationResult(
                success=True,
                message=f"Successfully deleted: {path}",
                data={
                    'deleted_info': asdict(file_info),
                    'recursive': recursive
                },
                operation="delete_file"
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                message=f"Error deleting file: {str(e)}",
                error=str(e),
                operation="delete_file"
            )
    
    def copy_file(self, source: str, destination: str, overwrite: bool = False) -> FileOperationResult:
        """Copy file or directory"""
        try:
            source_path = self._ensure_safe_path(source)
            dest_path = self._ensure_safe_path(destination)
            
            if not source_path.exists():
                return FileOperationResult(
                    success=False,
                    message=f"Source does not exist: {source}",
                    error="SourceNotFound",
                    operation="copy_file"
                )
            
            if dest_path.exists() and not overwrite:
                return FileOperationResult(
                    success=False,
                    message=f"Destination exists and overwrite=False: {destination}",
                    error="DestinationExists",
                    operation="copy_file"
                )
            
            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_dir():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
            
            dest_info = self._get_file_info(dest_path)
            
            return FileOperationResult(
                success=True,
                message=f"Successfully copied {source} to {destination}",
                data={
                    'destination_info': asdict(dest_info)
                },
                operation="copy_file"
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                message=f"Error copying file: {str(e)}",
                error=str(e),
                operation="copy_file"
            )
    
    def move_file(self, source: str, destination: str, overwrite: bool = False) -> FileOperationResult:
        """Move file or directory"""
        try:
            source_path = self._ensure_safe_path(source)
            dest_path = self._ensure_safe_path(destination)
            
            if not source_path.exists():
                return FileOperationResult(
                    success=False,
                    message=f"Source does not exist: {source}",
                    error="SourceNotFound",
                    operation="move_file"
                )
            
            if dest_path.exists() and not overwrite:
                return FileOperationResult(
                    success=False,
                    message=f"Destination exists and overwrite=False: {destination}",
                    error="DestinationExists",
                    operation="move_file"
                )
            
            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if dest_path.exists() and overwrite:
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            
            shutil.move(str(source_path), str(dest_path))
            
            dest_info = self._get_file_info(dest_path)
            
            return FileOperationResult(
                success=True,
                message=f"Successfully moved {source} to {destination}",
                data={
                    'destination_info': asdict(dest_info)
                },
                operation="move_file"
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                message=f"Error moving file: {str(e)}",
                error=str(e),
                operation="move_file"
            )
    
    def create_directory(self, path: str, parents: bool = True) -> FileOperationResult:
        """Create directory"""
        try:
            target_path = self._ensure_safe_path(path)
            
            if target_path.exists():
                if target_path.is_dir():
                    return FileOperationResult(
                        success=False,
                        message=f"Directory already exists: {path}",
                        error="DirectoryExists",
                        operation="create_directory"
                    )
                else:
                    return FileOperationResult(
                        success=False,
                        message=f"Path exists but is not a directory: {path}",
                        error="PathExists",
                        operation="create_directory"
                    )
            
            target_path.mkdir(parents=parents, exist_ok=True)
            
            dir_info = self._get_file_info(target_path)
            
            return FileOperationResult(
                success=True,
                message=f"Successfully created directory: {path}",
                data={
                    'directory_info': asdict(dir_info)
                },
                operation="create_directory"
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                message=f"Error creating directory: {str(e)}",
                error=str(e),
                operation="create_directory"
            )
    
    def get_file_info(self, path: str) -> FileOperationResult:
        """Get detailed file information"""
        try:
            target_path = self._ensure_safe_path(path)
            
            if not target_path.exists():
                return FileOperationResult(
                    success=False,
                    message=f"Path does not exist: {path}",
                    error="PathNotFound",
                    operation="get_file_info"
                )
            
            file_info = self._get_file_info(target_path)
            
            return FileOperationResult(
                success=True,
                message=f"File information retrieved: {path}",
                data=asdict(file_info),
                operation="get_file_info"
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                message=f"Error getting file info: {str(e)}",
                error=str(e),
                operation="get_file_info"
            )
    
    def search_files(self, pattern: str, directory: str = ".", 
                    recursive: bool = True, case_sensitive: bool = False) -> FileOperationResult:
        """Search for files matching pattern"""
        try:
            target_dir = self._ensure_safe_path(directory)
            
            if not target_dir.exists() or not target_dir.is_dir():
                return FileOperationResult(
                    success=False,
                    message=f"Directory does not exist: {directory}",
                    error="DirectoryNotFound",
                    operation="search_files"
                )
            
            import fnmatch
            
            matches = []
            
            def search_recursive(current_path: Path):
                try:
                    for item in current_path.iterdir():
                        # Check if name matches pattern
                        name = item.name
                        if not case_sensitive:
                            name = name.lower()
                            pattern_lower = pattern.lower()
                        else:
                            pattern_lower = pattern
                        
                        if fnmatch.fnmatch(name, pattern_lower):
                            file_info = self._get_file_info(item)
                            matches.append(asdict(file_info))
                        
                        # Recursive search
                        if recursive and item.is_dir():
                            search_recursive(item)
                            
                except PermissionError:
                    pass  # Skip directories we can't access
            
            search_recursive(target_dir)
            
            return FileOperationResult(
                success=True,
                message=f"Found {len(matches)} files matching '{pattern}' in {directory}",
                data=matches,
                operation="search_files"
            )
            
        except Exception as e:
            return FileOperationResult(
                success=False,
                message=f"Error searching files: {str(e)}",
                error=str(e),
                operation="search_files"
            )
    
    def display_directory_tree(self, path: str = ".", max_depth: int = 3, 
                              show_hidden: bool = False) -> str:
        """Generate a tree-like display of directory structure"""
        try:
            target_path = self._ensure_safe_path(path)
            
            if not target_path.exists():
                return f"Path does not exist: {path}"
            
            if not target_path.is_dir():
                return f"Path is not a directory: {path}"
            
            tree_lines = []
            
            def build_tree(current_path: Path, prefix: str = "", depth: int = 0):
                if depth > max_depth:
                    return
                
                try:
                    items = list(current_path.iterdir())
                    items.sort(key=lambda x: (x.is_file(), x.name.lower()))
                    
                    for i, item in enumerate(items):
                        # Skip hidden files unless requested
                        if not show_hidden and item.name.startswith('.'):
                            continue
                        
                        is_last = i == len(items) - 1
                        current_prefix = "└── " if is_last else "├── "
                        next_prefix = "    " if is_last else "│   "
                        
                        # Add file/directory indicator
                        if item.is_dir():
                            indicator = "📁"
                        elif item.is_symlink():
                            indicator = "🔗"
                        else:
                            indicator = "📄"
                        
                        tree_lines.append(f"{prefix}{current_prefix}{indicator} {item.name}")
                        
                        # Recursive for directories
                        if item.is_dir() and depth < max_depth:
                            build_tree(item, prefix + next_prefix, depth + 1)
                            
                except PermissionError:
                    tree_lines.append(f"{prefix}└── [Permission Denied]")
            
            tree_lines.append(f"📁 {target_path.name or '.'}")
            build_tree(target_path)
            
            return "\n".join(tree_lines)
            
        except Exception as e:
            return f"Error generating tree: {str(e)}"


class FileSystemToolsManager:
    """Manager class for file system operations with CLI integration"""
    
    def __init__(self, base_path: str = None):
        self.fs_tools = FileSystemTools(base_path)
        self.console = Console()
    
    def list_directory(self, path: str = ".", show_hidden: bool = False, 
                      recursive: bool = False, max_depth: int = 3, 
                      format: str = "table") -> None:
        """List directory with rich formatting"""
        result = self.fs_tools.list_directory(path, show_hidden, recursive, max_depth)
        
        if not result.success:
            self.console.print(f"[red]{result.message}[/red]")
            return
        
        if format == "table":
            self._display_directory_table(result.data, path)
        elif format == "tree":
            tree = self.fs_tools.display_directory_tree(path, max_depth, show_hidden)
            self.console.print(Panel(tree, title=f"Directory Tree: {path}", border_style="green"))
        else:
            self.console.print(result.data)
    
    def _display_directory_table(self, items: List[Dict], path: str) -> None:
        """Display directory contents in a rich table"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Size", style="blue")
        table.add_column("Modified", style="yellow")
        table.add_column("Permissions", style="red")
        
        for item in items:
            # Format size
            size = item['size']
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            
            # Format modified date
            if isinstance(item['modified'], str):
                modified = datetime.fromisoformat(item['modified'])
            else:
                modified = item['modified']
            modified_str = modified.strftime("%Y-%m-%d %H:%M")
            
            # Add indicators
            name = item['name']
            if item['is_hidden']:
                name = f"• {name}"
            if item['is_symlink']:
                name = f"🔗 {name}"
            elif item['type'] == 'directory':
                name = f"📁 {name}"
            else:
                name = f"📄 {name}"
            
            table.add_row(
                name,
                item['type'],
                size_str,
                modified_str,
                item['permissions']
            )
        
        self.console.print(table)
    
    def read_file(self, path: str, encoding: str = "utf-8", 
                  max_size: int = 10 * 1024 * 1024, format: str = "text") -> None:
        """Read and display file contents"""
        result = self.fs_tools.read_file(path, encoding, max_size)
        
        if not result.success:
            self.console.print(f"[red]{result.message}[/red]")
            return
        
        content = result.data['content']
        file_info = result.data['file_info']
        
        if format in ["text", "table"]:
            # Display file info
            # Format modified date for display
            if isinstance(file_info['modified'], str):
                modified_display = file_info['modified']
            else:
                modified_display = file_info['modified'].strftime("%Y-%m-%d %H:%M:%S")
            
            info_text = f"""
**File:** {file_info['name']}
**Path:** {file_info['path']}
**Size:** {file_info['size']} bytes
**Type:** {file_info['mime_type'] or 'Unknown'}
**Modified:** {modified_display}
**Permissions:** {file_info['permissions']}
"""
            
            self.console.print(Panel(
                Markdown(info_text),
                title="File Information",
                border_style="blue"
            ))
            
            # Display content
            if file_info['extension'] in ['.md', '.txt']:
                self.console.print(Panel(
                    Markdown(content),
                    title="File Content",
                    border_style="green"
                ))
            else:
                self.console.print(Panel(
                    content,
                    title="File Content",
                    border_style="green"
                ))
        
        elif format == "json":
            # Convert datetime objects to strings for JSON serialization
            json_data = result.data.copy()
            if 'file_info' in json_data and 'modified' in json_data['file_info']:
                if not isinstance(json_data['file_info']['modified'], str):
                    json_data['file_info']['modified'] = json_data['file_info']['modified'].isoformat()
            self.console.print(json.dumps(json_data, indent=2))
    
    def write_file(self, path: str, content: str, encoding: str = "utf-8", 
                   overwrite: bool = True, create_dirs: bool = True) -> None:
        """Write content to file with feedback"""
        result = self.fs_tools.write_file(path, content, encoding, overwrite, create_dirs)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            file_info = result.data['file_info']
            self.console.print(f"📄 File: {file_info['name']} ({file_info['size']} bytes)")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def delete_file(self, path: str, recursive: bool = False, confirm: bool = True) -> None:
        """Delete file with confirmation"""
        if confirm:
            if not self.console.input(f"Are you sure you want to delete '{path}'? (y/N): ").lower().startswith('y'):
                self.console.print("[yellow]Deletion cancelled[/yellow]")
                return
        
        result = self.fs_tools.delete_file(path, recursive)
        
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
            deleted_info = result.data['deleted_info']
            self.console.print(f"🗑️  Deleted: {deleted_info['name']} ({deleted_info['type']})")
        else:
            self.console.print(f"[red]{result.message}[/red]")
    
    def get_file_info(self, path: str, format: str = "table") -> None:
        """Get and display file information"""
        result = self.fs_tools.get_file_info(path)
        
        if not result.success:
            self.console.print(f"[red]{result.message}[/red]")
            return
        
        file_info = result.data
        
        if format == "table":
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Name", file_info['name'])
            table.add_row("Path", file_info['path'])
            table.add_row("Type", file_info['type'])
            table.add_row("Size", f"{file_info['size']} bytes")
            # Format modified date for display
            if isinstance(file_info['modified'], str):
                modified_display = file_info['modified']
            else:
                modified_display = file_info['modified'].strftime("%Y-%m-%d %H:%M:%S")
            table.add_row("Modified", modified_display)
            table.add_row("Permissions", file_info['permissions'])
            table.add_row("MIME Type", file_info['mime_type'] or "Unknown")
            table.add_row("Extension", file_info['extension'] or "None")
            table.add_row("Hidden", "Yes" if file_info['is_hidden'] else "No")
            table.add_row("Symlink", "Yes" if file_info['is_symlink'] else "No")
            
            if file_info['is_symlink'] and file_info['symlink_target']:
                table.add_row("Symlink Target", file_info['symlink_target'])
            
            self.console.print(table)
        
        elif format == "json":
            self.console.print(json.dumps(file_info, indent=2, default=str))
    
    def search_files(self, pattern: str, directory: str = ".", 
                    recursive: bool = True, case_sensitive: bool = False) -> None:
        """Search for files and display results"""
        result = self.fs_tools.search_files(pattern, directory, recursive, case_sensitive)
        
        if not result.success:
            self.console.print(f"[red]{result.message}[/red]")
            return
        
        if not result.data:
            self.console.print(f"[yellow]No files found matching '{pattern}' in {directory}[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Path", style="blue")
        table.add_column("Type", style="green")
        table.add_column("Size", style="yellow")
        table.add_column("Modified", style="red")
        
        for item in result.data:
            # Format size
            size = item['size']
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            
            # Format modified date
            if isinstance(item['modified'], str):
                modified = datetime.fromisoformat(item['modified'])
            else:
                modified = item['modified']
            modified_str = modified.strftime("%Y-%m-%d %H:%M")
            
            # Add indicators
            name = item['name']
            if item['type'] == 'directory':
                name = f"📁 {name}"
            else:
                name = f"📄 {name}"
            
            table.add_row(
                name,
                item['path'],
                item['type'],
                size_str,
                modified_str
            )
        
        self.console.print(table) 