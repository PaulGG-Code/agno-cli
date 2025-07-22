"""
Docker Tools - Container Management

This module provides Docker container management capabilities with:
- Container lifecycle management (create, start, stop, remove)
- Image management (build, pull, push, remove)
- Docker system monitoring and statistics
- Network and volume management
- Rich output formatting and progress tracking
- Safety features and validation
"""

import os
import sys
import json
import time
import subprocess
import shlex
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
import docker
from docker.errors import DockerException, ImageNotFound, ContainerError, APIError


@dataclass
class DockerContainer:
    """Docker container information"""
    id: str
    name: str
    image: str
    status: str
    ports: Dict[str, str]
    created: str
    size: str
    command: str
    labels: Dict[str, str]


@dataclass
class DockerImage:
    """Docker image information"""
    id: str
    repository: str
    tag: str
    created: str
    size: str
    labels: Dict[str, str]


@dataclass
class DockerNetwork:
    """Docker network information"""
    id: str
    name: str
    driver: str
    scope: str
    ipam_config: List[Dict[str, Any]]


@dataclass
class DockerVolume:
    """Docker volume information"""
    name: str
    driver: str
    mountpoint: str
    labels: Dict[str, str]


@dataclass
class DockerSystemInfo:
    """Docker system information"""
    containers: int
    images: int
    volumes: int
    networks: int
    disk_usage: Dict[str, Any]
    system_info: Dict[str, Any]


class DockerTools:
    """Core Docker container management tools"""
    
    def __init__(self):
        self.console = Console()
        self.client = None
        self._connect()
    
    def _connect(self):
        """Connect to Docker daemon"""
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
        except DockerException as e:
            raise Exception(f"Failed to connect to Docker daemon: {str(e)}")
        except Exception as e:
            raise Exception(f"Docker connection error: {str(e)}")
    
    def list_containers(self, all_containers: bool = False) -> List[DockerContainer]:
        """List Docker containers"""
        try:
            containers = self.client.containers.list(all=all_containers)
            result = []
            
            for container in containers:
                # Get container stats
                try:
                    stats = container.stats(stream=False)
                    size = stats.get('memory_stats', {}).get('usage', 0)
                    size_str = self._format_bytes(size) if size else "N/A"
                except:
                    size_str = "N/A"
                
                # Get port mappings
                ports = {}
                if container.attrs.get('NetworkSettings', {}).get('Ports'):
                    for container_port, host_ports in container.attrs['NetworkSettings']['Ports'].items():
                        if host_ports:
                            ports[container_port] = host_ports[0]['HostPort']
                
                result.append(DockerContainer(
                    id=container.short_id,
                    name=container.name,
                    image=container.image.tags[0] if container.image.tags else container.image.id,
                    status=container.status,
                    ports=ports,
                    created=container.attrs['Created'][:19].replace('T', ' '),
                    size=size_str,
                    command=container.attrs['Config']['Cmd'][0] if container.attrs['Config']['Cmd'] else "N/A",
                    labels=container.attrs['Config'].get('Labels', {})
                ))
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to list containers: {str(e)}")
    
    def get_container_info(self, container_id: str) -> Dict[str, Any]:
        """Get detailed container information"""
        try:
            container = self.client.containers.get(container_id)
            attrs = container.attrs
            
            # Get container stats
            try:
                stats = container.stats(stream=False)
            except:
                stats = {}
            
            return {
                'id': container.short_id,
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else container.image.id,
                'status': container.status,
                'created': attrs['Created'][:19].replace('T', ' '),
                'command': attrs['Config']['Cmd'],
                'entrypoint': attrs['Config']['Entrypoint'],
                'working_dir': attrs['Config']['WorkingDir'],
                'user': attrs['Config']['User'],
                'environment': attrs['Config']['Env'],
                'ports': attrs['NetworkSettings']['Ports'],
                'volumes': attrs['Mounts'],
                'labels': attrs['Config'].get('Labels', {}),
                'network_settings': attrs['NetworkSettings'],
                'state': attrs['State'],
                'stats': stats
            }
            
        except Exception as e:
            raise Exception(f"Failed to get container info: {str(e)}")
    
    def start_container(self, container_id: str) -> bool:
        """Start a Docker container"""
        try:
            container = self.client.containers.get(container_id)
            container.start()
            return True
        except Exception as e:
            raise Exception(f"Failed to start container: {str(e)}")
    
    def stop_container(self, container_id: str, timeout: int = 10) -> bool:
        """Stop a Docker container"""
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            return True
        except Exception as e:
            raise Exception(f"Failed to stop container: {str(e)}")
    
    def restart_container(self, container_id: str, timeout: int = 10) -> bool:
        """Restart a Docker container"""
        try:
            container = self.client.containers.get(container_id)
            container.restart(timeout=timeout)
            return True
        except Exception as e:
            raise Exception(f"Failed to restart container: {str(e)}")
    
    def remove_container(self, container_id: str, force: bool = False, volumes: bool = False) -> bool:
        """Remove a Docker container"""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force, v=volumes)
            return True
        except Exception as e:
            raise Exception(f"Failed to remove container: {str(e)}")
    
    def create_container(self, image: str, name: Optional[str] = None, 
                        command: Optional[str] = None, ports: Optional[Dict[str, str]] = None,
                        volumes: Optional[Dict[str, str]] = None, environment: Optional[Dict[str, str]] = None,
                        detach: bool = True) -> str:
        """Create a new Docker container"""
        try:
            # Prepare container configuration
            container_config = {
                'image': image,
                'detach': detach
            }
            
            if name:
                container_config['name'] = name
            
            if command:
                container_config['command'] = shlex.split(command)
            
            if ports:
                container_config['ports'] = ports
            
            if volumes:
                container_config['volumes'] = volumes
            
            if environment:
                container_config['environment'] = environment
            
            # Create and start container
            container = self.client.containers.run(**container_config)
            return container.short_id
            
        except Exception as e:
            raise Exception(f"Failed to create container: {str(e)}")
    
    def execute_command(self, container_id: str, command: str, user: Optional[str] = None) -> Tuple[str, str]:
        """Execute command in a running container"""
        try:
            container = self.client.containers.get(container_id)
            exec_result = container.exec_run(command, user=user)
            return exec_result.output.decode('utf-8'), exec_result.exit_code
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")
    
    def get_container_logs(self, container_id: str, tail: int = 100, follow: bool = False) -> str:
        """Get container logs"""
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail, follow=follow, timestamps=True)
            return logs.decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to get container logs: {str(e)}")
    
    def list_images(self) -> List[DockerImage]:
        """List Docker images"""
        try:
            images = self.client.images.list()
            result = []
            
            for image in images:
                # Get image tags
                tags = image.tags if image.tags else [f"<none>:<none>"]
                
                for tag in tags:
                    if ':' in tag:
                        repo, tag_name = tag.rsplit(':', 1)
                    else:
                        repo, tag_name = tag, 'latest'
                    
                    # Handle Created field - it might be a string or integer
                    created_value = image.attrs.get('Created', 0)
                    if isinstance(created_value, str):
                        # Try to parse ISO format
                        try:
                            import datetime
                            created_time = datetime.datetime.fromisoformat(created_value.replace('Z', '+00:00'))
                            created_str = created_time.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            created_str = created_value[:19] if len(created_value) >= 19 else created_value
                    else:
                        # Integer timestamp
                        created_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created_value))
                    
                    result.append(DockerImage(
                        id=image.short_id,
                        repository=repo,
                        tag=tag_name,
                        created=created_str,
                        size=self._format_bytes(image.attrs.get('Size', 0)),
                        labels=image.attrs.get('Labels', {})
                    ))
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to list images: {str(e)}")
    
    def pull_image(self, image_name: str, tag: str = "latest") -> bool:
        """Pull a Docker image"""
        try:
            full_name = f"{image_name}:{tag}"
            self.client.images.pull(image_name, tag=tag)
            return True
        except Exception as e:
            raise Exception(f"Failed to pull image: {str(e)}")
    
    def remove_image(self, image_id: str, force: bool = False) -> bool:
        """Remove a Docker image"""
        try:
            image = self.client.images.get(image_id)
            self.client.images.remove(image.id, force=force)
            return True
        except Exception as e:
            raise Exception(f"Failed to remove image: {str(e)}")
    
    def build_image(self, path: str, tag: str, dockerfile: str = "Dockerfile") -> str:
        """Build a Docker image"""
        try:
            image, logs = self.client.images.build(
                path=path,
                tag=tag,
                dockerfile=dockerfile,
                decode=True
            )
            return image.short_id
        except Exception as e:
            raise Exception(f"Failed to build image: {str(e)}")
    
    def list_networks(self) -> List[DockerNetwork]:
        """List Docker networks"""
        try:
            networks = self.client.networks.list()
            result = []
            
            for network in networks:
                result.append(DockerNetwork(
                    id=network.short_id,
                    name=network.name,
                    driver=network.attrs['Driver'],
                    scope=network.attrs['Scope'],
                    ipam_config=network.attrs['IPAM']['Config']
                ))
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to list networks: {str(e)}")
    
    def list_volumes(self) -> List[DockerVolume]:
        """List Docker volumes"""
        try:
            volumes = self.client.volumes.list()
            result = []
            
            for volume in volumes:
                result.append(DockerVolume(
                    name=volume.name,
                    driver=volume.attrs['Driver'],
                    mountpoint=volume.attrs['Mountpoint'],
                    labels=volume.attrs.get('Labels', {})
                ))
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to list volumes: {str(e)}")
    
    def get_system_info(self) -> DockerSystemInfo:
        """Get Docker system information"""
        try:
            # Get container count
            containers = self.client.containers.list(all=True)
            
            # Get image count
            images = self.client.images.list()
            
            # Get volume count
            volumes = self.client.volumes.list()
            
            # Get network count
            networks = self.client.networks.list()
            
            # Get disk usage
            try:
                disk_usage = self.client.df()
            except:
                disk_usage = {}
            
            # Get system info
            try:
                system_info = self.client.info()
            except:
                system_info = {}
            
            return DockerSystemInfo(
                containers=len(containers),
                images=len(images),
                volumes=len(volumes),
                networks=len(networks),
                disk_usage=disk_usage,
                system_info=system_info
            )
            
        except Exception as e:
            raise Exception(f"Failed to get system info: {str(e)}")
    
    def prune_system(self, containers: bool = True, images: bool = True, 
                    volumes: bool = True, networks: bool = True) -> Dict[str, Any]:
        """Prune Docker system (remove unused resources)"""
        try:
            result = {}
            
            if containers:
                result['containers'] = self.client.containers.prune()
            
            if images:
                result['images'] = self.client.images.prune()
            
            if volumes:
                result['volumes'] = self.client.volumes.prune()
            
            if networks:
                result['networks'] = self.client.networks.prune()
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to prune system: {str(e)}")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"


class DockerToolsManager:
    """CLI integration for Docker tools"""
    
    def __init__(self):
        self.docker_tools = DockerTools()
        self.console = Console()
    
    def list_containers(self, all_containers: bool = False, format: str = "table"):
        """List Docker containers"""
        try:
            containers = self.docker_tools.list_containers(all_containers)
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'id': c.id,
                    'name': c.name,
                    'image': c.image,
                    'status': c.status,
                    'ports': c.ports,
                    'created': c.created,
                    'size': c.size
                } for c in containers], indent=2))
                return
            
            # Create containers table
            table = Table(title="Docker Containers")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("Image", style="yellow")
            table.add_column("Status", style="green")
            table.add_column("Ports", style="blue")
            table.add_column("Created", style="magenta")
            table.add_column("Size", style="red")
            
            for container in containers:
                # Color status
                status_color = "green" if container.status == "running" else "red"
                status_text = f"[{status_color}]{container.status}[/{status_color}]"
                
                # Format ports
                ports_text = ", ".join([f"{k}->{v}" for k, v in container.ports.items()]) if container.ports else "-"
                
                table.add_row(
                    container.id,
                    container.name,
                    container.image,
                    status_text,
                    ports_text,
                    container.created,
                    container.size
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error listing containers: {e}[/red]")
    
    def show_container_info(self, container_id: str, format: str = "table"):
        """Show detailed container information"""
        try:
            info = self.docker_tools.get_container_info(container_id)
            
            if format == "json":
                import json
                self.console.print(json.dumps(info, indent=2))
                return
            
            # Create info table
            table = Table(title=f"Container Information - {container_id}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            
            # Basic info
            table.add_row("ID", info['id'])
            table.add_row("Name", info['name'])
            table.add_row("Image", info['image'])
            table.add_row("Status", info['status'])
            table.add_row("Created", info['created'])
            table.add_row("Command", str(info['command']))
            table.add_row("Working Directory", info['working_dir'])
            table.add_row("User", info['user'])
            
            # Network info
            if info['ports']:
                ports_text = ", ".join([f"{k}->{v[0]['HostPort']}" for k, v in info['ports'].items() if v])
                table.add_row("Ports", ports_text)
            
            # Environment variables
            if info['environment']:
                env_text = "\n".join(info['environment'][:5])  # Show first 5
                if len(info['environment']) > 5:
                    env_text += f"\n... and {len(info['environment']) - 5} more"
                table.add_row("Environment", env_text)
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error getting container info: {e}[/red]")
    
    def start_container(self, container_id: str):
        """Start a container"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Starting container...", total=None)
                success = self.docker_tools.start_container(container_id)
                
            if success:
                self.console.print(f"[green]Container {container_id} started successfully[/green]")
            else:
                self.console.print(f"[red]Failed to start container {container_id}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error starting container: {e}[/red]")
    
    def stop_container(self, container_id: str, timeout: int = 10):
        """Stop a container"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Stopping container...", total=None)
                success = self.docker_tools.stop_container(container_id, timeout)
                
            if success:
                self.console.print(f"[green]Container {container_id} stopped successfully[/green]")
            else:
                self.console.print(f"[red]Failed to stop container {container_id}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error stopping container: {e}[/red]")
    
    def restart_container(self, container_id: str, timeout: int = 10):
        """Restart a container"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Restarting container...", total=None)
                success = self.docker_tools.restart_container(container_id, timeout)
                
            if success:
                self.console.print(f"[green]Container {container_id} restarted successfully[/green]")
            else:
                self.console.print(f"[red]Failed to restart container {container_id}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error restarting container: {e}[/red]")
    
    def remove_container(self, container_id: str, force: bool = False, volumes: bool = False):
        """Remove a container"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Removing container...", total=None)
                success = self.docker_tools.remove_container(container_id, force, volumes)
                
            if success:
                self.console.print(f"[green]Container {container_id} removed successfully[/green]")
            else:
                self.console.print(f"[red]Failed to remove container {container_id}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error removing container: {e}[/red]")
    
    def create_container(self, image: str, name: Optional[str] = None, 
                        command: Optional[str] = None, ports: Optional[str] = None,
                        volumes: Optional[str] = None, environment: Optional[str] = None,
                        detach: bool = True):
        """Create a new container"""
        try:
            # Parse ports
            ports_dict = None
            if ports:
                ports_dict = {}
                for port_mapping in ports.split(','):
                    if ':' in port_mapping:
                        host_port, container_port = port_mapping.split(':')
                        ports_dict[container_port] = host_port
            
            # Parse volumes
            volumes_dict = None
            if volumes:
                volumes_dict = {}
                for volume_mapping in volumes.split(','):
                    if ':' in volume_mapping:
                        host_path, container_path = volume_mapping.split(':')
                        volumes_dict[host_path] = container_path
            
            # Parse environment
            env_dict = None
            if environment:
                env_dict = {}
                for env_var in environment.split(','):
                    if '=' in env_var:
                        key, value = env_var.split('=', 1)
                        env_dict[key] = value
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Creating container...", total=None)
                container_id = self.docker_tools.create_container(
                    image, name, command, ports_dict, volumes_dict, env_dict, detach
                )
                
            self.console.print(f"[green]Container created successfully with ID: {container_id}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error creating container: {e}[/red]")
    
    def execute_command(self, container_id: str, command: str, user: Optional[str] = None):
        """Execute command in container"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Executing command...", total=None)
                output, exit_code = self.docker_tools.execute_command(container_id, command, user)
                
            self.console.print(f"[bold blue]Command Output (Exit Code: {exit_code}):[/bold blue]")
            syntax = Syntax(output, "bash", theme="monokai")
            self.console.print(Panel(syntax, title="Command Output"))
            
        except Exception as e:
            self.console.print(f"[red]Error executing command: {e}[/red]")
    
    def show_logs(self, container_id: str, tail: int = 100, follow: bool = False):
        """Show container logs"""
        try:
            logs = self.docker_tools.get_container_logs(container_id, tail, follow)
            
            if follow:
                # Live log display
                with Live(Panel("Loading logs...", title="Container Logs"), refresh_per_second=4) as live:
                    live.update(Panel(logs, title=f"Container Logs - {container_id}"))
            else:
                # Static log display
                syntax = Syntax(logs, "bash", theme="monokai")
                self.console.print(Panel(syntax, title=f"Container Logs - {container_id}"))
                
        except Exception as e:
            self.console.print(f"[red]Error getting logs: {e}[/red]")
    
    def list_images(self, format: str = "table"):
        """List Docker images"""
        try:
            images = self.docker_tools.list_images()
            
            if format == "json":
                import json
                self.console.print(json.dumps([{
                    'id': img.id,
                    'repository': img.repository,
                    'tag': img.tag,
                    'created': img.created,
                    'size': img.size
                } for img in images], indent=2))
                return
            
            # Create images table
            table = Table(title="Docker Images")
            table.add_column("ID", style="cyan")
            table.add_column("Repository", style="white")
            table.add_column("Tag", style="yellow")
            table.add_column("Created", style="magenta")
            table.add_column("Size", style="red")
            
            for image in images:
                table.add_row(
                    image.id,
                    image.repository,
                    image.tag,
                    image.created,
                    image.size
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error listing images: {e}[/red]")
    
    def pull_image(self, image_name: str, tag: str = "latest"):
        """Pull a Docker image"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Pulling {image_name}:{tag}...", total=None)
                success = self.docker_tools.pull_image(image_name, tag)
                
            if success:
                self.console.print(f"[green]Image {image_name}:{tag} pulled successfully[/green]")
            else:
                self.console.print(f"[red]Failed to pull image {image_name}:{tag}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error pulling image: {e}[/red]")
    
    def remove_image(self, image_id: str, force: bool = False):
        """Remove a Docker image"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Removing image...", total=None)
                success = self.docker_tools.remove_image(image_id, force)
                
            if success:
                self.console.print(f"[green]Image {image_id} removed successfully[/green]")
            else:
                self.console.print(f"[red]Failed to remove image {image_id}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error removing image: {e}[/red]")
    
    def build_image(self, path: str, tag: str, dockerfile: str = "Dockerfile"):
        """Build a Docker image"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Building {tag}...", total=None)
                image_id = self.docker_tools.build_image(path, tag, dockerfile)
                
            self.console.print(f"[green]Image built successfully with ID: {image_id}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Error building image: {e}[/red]")
    
    def show_system_info(self, format: str = "table"):
        """Show Docker system information"""
        try:
            info = self.docker_tools.get_system_info()
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'containers': info.containers,
                    'images': info.images,
                    'volumes': info.volumes,
                    'networks': info.networks,
                    'disk_usage': info.disk_usage,
                    'system_info': info.system_info
                }, indent=2))
                return
            
            # Create system info table
            table = Table(title="Docker System Information")
            table.add_column("Category", style="cyan")
            table.add_column("Count", style="white")
            
            table.add_row("Containers", str(info.containers))
            table.add_row("Images", str(info.images))
            table.add_row("Volumes", str(info.volumes))
            table.add_row("Networks", str(info.networks))
            
            # Disk usage
            if info.disk_usage:
                for resource, usage in info.disk_usage.items():
                    if isinstance(usage, dict) and 'Size' in usage:
                        size = self.docker_tools._format_bytes(usage['Size'])
                        table.add_row(f"{resource.title()} Size", size)
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Error getting system info: {e}[/red]")
    
    def prune_system(self, containers: bool = True, images: bool = True, 
                    volumes: bool = True, networks: bool = True):
        """Prune Docker system"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Pruning system...", total=None)
                result = self.docker_tools.prune_system(containers, images, volumes, networks)
                
            self.console.print("[green]System pruning completed[/green]")
            
            # Show results
            for resource, data in result.items():
                if 'SpaceReclaimed' in data:
                    space = self.docker_tools._format_bytes(data['SpaceReclaimed'])
                    self.console.print(f"[yellow]Reclaimed {space} from {resource}[/yellow]")
                    
        except Exception as e:
            self.console.print(f"[red]Error pruning system: {e}[/red]")
    
    def close(self):
        """Clean up resources"""
        if self.docker_tools.client:
            self.docker_tools.client.close() 