"""
Screenshot Tools - Local and Webpage Screenshot Capabilities

This module provides comprehensive screenshot capabilities:
- Local screen capture (full screen, region, window)
- Webpage screenshots with browser automation
- Screenshot editing and annotation
- Screenshot management and organization
- Multiple output formats and quality settings
- Rich output formatting and CLI integration
"""

import os
import sys
import json
import time
import hashlib
import base64
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
import requests

# Screenshot imports
try:
    import pyautogui
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    import cv2
    import numpy as np
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    print("Warning: Screenshot libraries not available. Install with: pip install pyautogui pillow opencv-python")

# Web screenshot imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    WEB_SCREENSHOT_AVAILABLE = True
except ImportError:
    WEB_SCREENSHOT_AVAILABLE = False
    print("Warning: Web screenshot libraries not available. Install with: pip install selenium")


class ScreenshotType(Enum):
    """Screenshot types enumeration"""
    FULL_SCREEN = "full_screen"
    REGION = "region"
    WINDOW = "window"
    WEBPAGE = "webpage"
    ELEMENT = "element"
    SCROLLING = "scrolling"


class ScreenshotFormat(Enum):
    """Screenshot formats enumeration"""
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"


@dataclass
class ScreenshotConfig:
    """Screenshot configuration"""
    output_dir: str = "screenshots"
    format: str = "png"
    quality: int = 95
    delay: float = 0.0
    timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    viewport_width: int = 1920
    viewport_height: int = 1080
    full_page: bool = False
    wait_timeout: int = 10
    scroll_delay: float = 1.0
    include_background: bool = True
    show_scrollbars: bool = False
    width: Optional[int] = None
    height: Optional[int] = None
    wait_for_element: Optional[str] = None


@dataclass
class ScreenshotResult:
    """Screenshot result"""
    success: bool = False
    file_path: Optional[str] = None
    url: Optional[str] = None
    screenshot_type: str = ""
    width: int = 0
    height: int = 0
    file_size: int = 0
    format: str = "png"
    timestamp: str = ""
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class ScreenshotInfo:
    """Screenshot information"""
    name: str = ""
    file_path: str = ""
    screenshot_type: str = ""
    url: Optional[str] = None
    width: int = 0
    height: int = 0
    file_size: int = 0
    format: str = ""
    created_at: str = ""
    modified_at: str = ""
    metadata: Optional[Dict[str, Any]] = None


class ScreenshotTools:
    """Core screenshot tools"""
    
    def __init__(self, config: Optional[ScreenshotConfig] = None):
        self.console = Console()
        self.config = config or ScreenshotConfig()
        
        # Create output directory
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Screenshot history
        self.screenshot_history: List[ScreenshotResult] = []
        
        # Web driver for webpage screenshots
        self.web_driver: Optional[webdriver.Chrome] = None
        
        # Check availability
        if not SCREENSHOT_AVAILABLE:
            raise ImportError("Screenshot libraries not available. Install with: pip install pyautogui pillow opencv-python")
    
    def _init_web_driver(self) -> bool:
        """Initialize web driver for webpage screenshots"""
        if not WEB_SCREENSHOT_AVAILABLE:
            return False
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--user-agent={self.config.user_agent}")
            chrome_options.add_argument(f"--window-size={self.config.viewport_width},{self.config.viewport_height}")
            
            if not self.config.show_scrollbars:
                chrome_options.add_argument("--hide-scrollbars")
            
            self.web_driver = webdriver.Chrome(options=chrome_options)
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error initializing web driver: {e}[/red]")
            return False
    
    def _cleanup_web_driver(self) -> None:
        """Clean up web driver"""
        if self.web_driver:
            try:
                self.web_driver.quit()
            except:
                pass
            self.web_driver = None
    
    def capture_full_screen(self, filename: Optional[str] = None) -> ScreenshotResult:
        """Capture full screen screenshot"""
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"fullscreen_{timestamp}.{self.config.format}"
            
            file_path = self.output_dir / filename
            
            # Capture screenshot
            screenshot = pyautogui.screenshot()
            
            # Resize if specified
            if self.config.width and self.config.height:
                screenshot = screenshot.resize((self.config.width, self.config.height))
            
            # Save screenshot
            screenshot.save(file_path, quality=self.config.quality)
            
            # Get file info
            file_size = file_path.stat().st_size
            width, height = screenshot.size
            
            result = ScreenshotResult(
                success=True,
                file_path=str(file_path),
                screenshot_type="full_screen",
                width=width,
                height=height,
                file_size=file_size,
                format=self.config.format,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "screen_size": pyautogui.size(),
                    "mouse_position": pyautogui.position()
                }
            )
            
            self.screenshot_history.append(result)
            return result
            
        except Exception as e:
            return ScreenshotResult(
                success=False,
                screenshot_type="full_screen",
                error_message=str(e)
            )
    
    def capture_region(self, x: int, y: int, width: int, height: int, 
                      filename: Optional[str] = None) -> ScreenshotResult:
        """Capture region screenshot"""
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"region_{x}_{y}_{width}_{height}_{timestamp}.{self.config.format}"
            
            file_path = self.output_dir / filename
            
            # Capture region screenshot
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # Save screenshot
            screenshot.save(file_path, quality=self.config.quality)
            
            # Get file info
            file_size = file_path.stat().st_size
            
            result = ScreenshotResult(
                success=True,
                file_path=str(file_path),
                screenshot_type="region",
                width=width,
                height=height,
                file_size=file_size,
                format=self.config.format,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "region": {"x": x, "y": y, "width": width, "height": height},
                    "screen_size": pyautogui.size()
                }
            )
            
            self.screenshot_history.append(result)
            return result
            
        except Exception as e:
            return ScreenshotResult(
                success=False,
                screenshot_type="region",
                error_message=str(e)
            )
    
    def capture_window(self, window_title: str, filename: Optional[str] = None) -> ScreenshotResult:
        """Capture specific window screenshot"""
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = "".join(c for c in window_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"window_{safe_title}_{timestamp}.{self.config.format}"
            
            file_path = self.output_dir / filename
            
            # Get window position and size
            try:
                import pygetwindow as gw
                window = gw.getWindowsWithTitle(window_title)[0]
                x, y, width, height = window.left, window.top, window.width, window.height
            except:
                # Fallback to full screen if window not found
                self.console.print(f"[yellow]Window '{window_title}' not found, capturing full screen[/yellow]")
                return self.capture_full_screen(filename)
            
            # Capture window screenshot
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # Save screenshot
            screenshot.save(file_path, quality=self.config.quality)
            
            # Get file info
            file_size = file_path.stat().st_size
            
            result = ScreenshotResult(
                success=True,
                file_path=str(file_path),
                screenshot_type="window",
                width=width,
                height=height,
                file_size=file_size,
                format=self.config.format,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "window_title": window_title,
                    "window_position": {"x": x, "y": y, "width": width, "height": height}
                }
            )
            
            self.screenshot_history.append(result)
            return result
            
        except Exception as e:
            return ScreenshotResult(
                success=False,
                screenshot_type="window",
                error_message=str(e)
            )
    
    def capture_webpage(self, url: str, filename: Optional[str] = None) -> ScreenshotResult:
        """Capture webpage screenshot"""
        if not WEB_SCREENSHOT_AVAILABLE:
            return ScreenshotResult(
                success=False,
                screenshot_type="webpage",
                error_message="Web screenshot libraries not available"
            )
        
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_url = url.replace("://", "_").replace("/", "_").replace(".", "_")
                filename = f"webpage_{safe_url}_{timestamp}.{self.config.format}"
            
            file_path = self.output_dir / filename
            
            # Initialize web driver
            if not self._init_web_driver():
                return ScreenshotResult(
                    success=False,
                    screenshot_type="webpage",
                    error_message="Failed to initialize web driver"
                )
            
            try:
                # Navigate to URL
                self.web_driver.get(url)
                
                # Wait for page to load
                time.sleep(self.config.delay)
                
                # Wait for specific element if specified
                if self.config.wait_for_element:
                    try:
                        WebDriverWait(self.web_driver, self.config.wait_timeout).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, self.config.wait_for_element))
                        )
                    except TimeoutException:
                        self.console.print(f"[yellow]Element '{self.config.wait_for_element}' not found within timeout[/yellow]")
                
                # Capture screenshot
                if self.config.full_page:
                    # Full page screenshot
                    total_height = self.web_driver.execute_script("return document.body.scrollHeight")
                    self.web_driver.set_window_size(self.config.viewport_width, total_height)
                    time.sleep(self.config.scroll_delay)
                
                self.web_driver.save_screenshot(str(file_path))
                
                # Get page info
                title = self.web_driver.title
                current_url = self.web_driver.current_url
                
                # Get file info
                file_size = file_path.stat().st_size
                image = Image.open(file_path)
                width, height = image.size
                
                result = ScreenshotResult(
                    success=True,
                    file_path=str(file_path),
                    url=url,
                    screenshot_type="webpage",
                    width=width,
                    height=height,
                    file_size=file_size,
                    format=self.config.format,
                    timestamp=datetime.now().isoformat(),
                    metadata={
                        "page_title": title,
                        "current_url": current_url,
                        "viewport_size": {"width": self.config.viewport_width, "height": self.config.viewport_height},
                        "full_page": self.config.full_page
                    }
                )
                
                self.screenshot_history.append(result)
                return result
                
            finally:
                self._cleanup_web_driver()
            
        except Exception as e:
            self._cleanup_web_driver()
            return ScreenshotResult(
                success=False,
                screenshot_type="webpage",
                error_message=str(e)
            )
    
    def capture_element(self, url: str, selector: str, filename: Optional[str] = None) -> ScreenshotResult:
        """Capture specific element screenshot"""
        if not WEB_SCREENSHOT_AVAILABLE:
            return ScreenshotResult(
                success=False,
                screenshot_type="element",
                error_message="Web screenshot libraries not available"
            )
        
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_selector = selector.replace("#", "").replace(".", "").replace(" ", "_")
                filename = f"element_{safe_selector}_{timestamp}.{self.config.format}"
            
            file_path = self.output_dir / filename
            
            # Initialize web driver
            if not self._init_web_driver():
                return ScreenshotResult(
                    success=False,
                    screenshot_type="element",
                    error_message="Failed to initialize web driver"
                )
            
            try:
                # Navigate to URL
                self.web_driver.get(url)
                
                # Wait for element
                element = WebDriverWait(self.web_driver, self.config.wait_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                # Get element location and size
                location = element.location
                size = element.size
                
                # Capture full page screenshot first
                temp_screenshot = self.output_dir / "temp_screenshot.png"
                self.web_driver.save_screenshot(str(temp_screenshot))
                
                # Crop to element
                full_img = Image.open(temp_screenshot)
                element_img = full_img.crop((
                    location['x'],
                    location['y'],
                    location['x'] + size['width'],
                    location['y'] + size['height']
                ))
                
                # Save element screenshot
                element_img.save(file_path, quality=self.config.quality)
                
                # Clean up temp file
                temp_screenshot.unlink()
                
                # Get file info
                file_size = file_path.stat().st_size
                width, height = element_img.size
                
                result = ScreenshotResult(
                    success=True,
                    file_path=str(file_path),
                    url=url,
                    screenshot_type="element",
                    width=width,
                    height=height,
                    file_size=file_size,
                    format=self.config.format,
                    timestamp=datetime.now().isoformat(),
                    metadata={
                        "selector": selector,
                        "element_location": location,
                        "element_size": size
                    }
                )
                
                self.screenshot_history.append(result)
                return result
                
            finally:
                self._cleanup_web_driver()
            
        except Exception as e:
            self._cleanup_web_driver()
            return ScreenshotResult(
                success=False,
                screenshot_type="element",
                error_message=str(e)
            )
    
    def capture_scrolling(self, url: str, filename: Optional[str] = None) -> ScreenshotResult:
        """Capture scrolling webpage screenshot"""
        if not WEB_SCREENSHOT_AVAILABLE:
            return ScreenshotResult(
                success=False,
                screenshot_type="scrolling",
                error_message="Web screenshot libraries not available"
            )
        
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_url = url.replace("://", "_").replace("/", "_").replace(".", "_")
                filename = f"scrolling_{safe_url}_{timestamp}.{self.config.format}"
            
            file_path = self.output_dir / filename
            
            # Initialize web driver
            if not self._init_web_driver():
                return ScreenshotResult(
                    success=False,
                    screenshot_type="scrolling",
                    error_message="Failed to initialize web driver"
                )
            
            try:
                # Navigate to URL
                self.web_driver.get(url)
                
                # Wait for page to load
                time.sleep(self.config.delay)
                
                # Get page dimensions
                total_height = self.web_driver.execute_script("return document.body.scrollHeight")
                viewport_height = self.web_driver.execute_script("return window.innerHeight")
                
                # Set window size
                self.web_driver.set_window_size(self.config.viewport_width, viewport_height)
                
                # Capture scrolling screenshot
                screenshots = []
                current_position = 0
                
                while current_position < total_height:
                    # Scroll to position
                    self.web_driver.execute_script(f"window.scrollTo(0, {current_position});")
                    time.sleep(self.config.scroll_delay)
                    
                    # Capture screenshot
                    temp_screenshot = self.output_dir / f"temp_scroll_{current_position}.png"
                    self.web_driver.save_screenshot(str(temp_screenshot))
                    screenshots.append((temp_screenshot, current_position))
                    
                    current_position += viewport_height
                
                # Combine screenshots
                if screenshots:
                    # Calculate total height
                    total_screenshots = len(screenshots)
                    combined_height = total_screenshots * viewport_height
                    
                    # Create combined image
                    first_img = Image.open(screenshots[0][0])
                    combined_img = Image.new('RGB', (self.config.viewport_width, combined_height))
                    
                    for i, (temp_file, position) in enumerate(screenshots):
                        img = Image.open(temp_file)
                        combined_img.paste(img, (0, i * viewport_height))
                        temp_file.unlink()  # Clean up temp file
                    
                    # Save combined screenshot
                    combined_img.save(file_path, quality=self.config.quality)
                    
                    # Get file info
                    file_size = file_path.stat().st_size
                    width, height = combined_img.size
                    
                    result = ScreenshotResult(
                        success=True,
                        file_path=str(file_path),
                        url=url,
                        screenshot_type="scrolling",
                        width=width,
                        height=height,
                        file_size=file_size,
                        format=self.config.format,
                        timestamp=datetime.now().isoformat(),
                        metadata={
                            "total_height": total_height,
                            "viewport_height": viewport_height,
                            "screenshots_combined": total_screenshots
                        }
                    )
                    
                    self.screenshot_history.append(result)
                    return result
                else:
                    return ScreenshotResult(
                        success=False,
                        screenshot_type="scrolling",
                        error_message="No screenshots captured"
                    )
                
            finally:
                self._cleanup_web_driver()
            
        except Exception as e:
            self._cleanup_web_driver()
            return ScreenshotResult(
                success=False,
                screenshot_type="scrolling",
                error_message=str(e)
            )
    
    def edit_screenshot(self, file_path: str, operations: List[Dict[str, Any]]) -> ScreenshotResult:
        """Edit screenshot with various operations"""
        try:
            # Load image
            image = Image.open(file_path)
            
            # Apply operations
            for operation in operations:
                op_type = operation.get("type")
                params = operation.get("params", {})
                
                if op_type == "resize":
                    width = params.get("width")
                    height = params.get("height")
                    if width and height:
                        image = image.resize((width, height))
                
                elif op_type == "crop":
                    left = params.get("left", 0)
                    top = params.get("top", 0)
                    right = params.get("right", image.width)
                    bottom = params.get("bottom", image.height)
                    image = image.crop((left, top, right, bottom))
                
                elif op_type == "rotate":
                    angle = params.get("angle", 0)
                    image = image.rotate(angle)
                
                elif op_type == "flip":
                    direction = params.get("direction", "horizontal")
                    if direction == "horizontal":
                        image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    elif direction == "vertical":
                        image = image.transpose(Image.FLIP_TOP_BOTTOM)
                
                elif op_type == "brightness":
                    factor = params.get("factor", 1.0)
                    enhancer = ImageEnhance.Brightness(image)
                    image = enhancer.enhance(factor)
                
                elif op_type == "contrast":
                    factor = params.get("factor", 1.0)
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(factor)
                
                elif op_type == "blur":
                    radius = params.get("radius", 2)
                    image = image.filter(ImageFilter.GaussianBlur(radius))
                
                elif op_type == "sharpen":
                    image = image.filter(ImageFilter.SHARPEN)
            
            # Save edited image
            edited_path = Path(file_path)
            edited_filename = f"edited_{edited_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{edited_path.suffix}"
            edited_path = self.output_dir / edited_filename
            
            image.save(edited_path, quality=self.config.quality)
            
            # Get file info
            file_size = edited_path.stat().st_size
            width, height = image.size
            
            result = ScreenshotResult(
                success=True,
                file_path=str(edited_path),
                screenshot_type="edited",
                width=width,
                height=height,
                file_size=file_size,
                format=self.config.format,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "original_file": file_path,
                    "operations_applied": operations
                }
            )
            
            self.screenshot_history.append(result)
            return result
            
        except Exception as e:
            return ScreenshotResult(
                success=False,
                screenshot_type="edited",
                error_message=str(e)
            )
    
    def list_screenshots(self) -> List[ScreenshotInfo]:
        """List all screenshots in output directory"""
        screenshots = []
        
        for file_path in self.output_dir.glob(f"*.{self.config.format}"):
            try:
                stat = file_path.stat()
                image = Image.open(file_path)
                width, height = image.size
                
                screenshot_info = ScreenshotInfo(
                    name=file_path.stem,
                    file_path=str(file_path),
                    screenshot_type="unknown",
                    width=width,
                    height=height,
                    file_size=stat.st_size,
                    format=file_path.suffix[1:],
                    created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat()
                )
                
                screenshots.append(screenshot_info)
                
            except Exception as e:
                self.console.print(f"[red]Error reading {file_path}: {e}[/red]")
        
        return sorted(screenshots, key=lambda x: x.modified_at, reverse=True)
    
    def get_screenshot_info(self, file_path: str) -> Optional[ScreenshotInfo]:
        """Get detailed information about a screenshot"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            image = Image.open(path)
            width, height = image.size
            
            return ScreenshotInfo(
                name=path.stem,
                file_path=str(path),
                screenshot_type="unknown",
                width=width,
                height=height,
                file_size=stat.st_size,
                format=path.suffix[1:],
                created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                metadata={
                    "mode": image.mode,
                    "format": image.format,
                    "dpi": image.info.get("dpi"),
                    "compression": image.info.get("compression")
                }
            )
            
        except Exception as e:
            self.console.print(f"[red]Error getting screenshot info: {e}[/red]")
            return None
    
    def delete_screenshot(self, file_path: str) -> bool:
        """Delete a screenshot file"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            self.console.print(f"[red]Error deleting screenshot: {e}[/red]")
            return False
    
    def clear_screenshots(self) -> int:
        """Clear all screenshots in output directory"""
        count = 0
        for file_path in self.output_dir.glob(f"*.{self.config.format}"):
            try:
                file_path.unlink()
                count += 1
            except Exception as e:
                self.console.print(f"[red]Error deleting {file_path}: {e}[/red]")
        return count


class ScreenshotToolsManager:
    """CLI integration for screenshot tools"""
    
    def __init__(self):
        self.screenshot_tools = ScreenshotTools()
        self.console = Console()
    
    def capture_full_screen(self, filename: Optional[str] = None, format: str = "table") -> None:
        """Capture full screen screenshot"""
        try:
            with Progress() as progress:
                task = progress.add_task("Capturing full screen...", total=None)
                result = self.screenshot_tools.capture_full_screen(filename)
                progress.update(task, completed=True)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2))
            else:
                if result.success:
                    self.console.print(f"[green]✓ Full screen screenshot saved: {result.file_path}[/green]")
                    self.console.print(f"  Size: {result.width}x{result.height} pixels")
                    self.console.print(f"  File size: {result.file_size} bytes")
                else:
                    self.console.print(f"[red]✗ Failed to capture screenshot: {result.error_message}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error capturing full screen: {e}[/red]")
    
    def capture_region(self, x: int, y: int, width: int, height: int, 
                      filename: Optional[str] = None, format: str = "table") -> None:
        """Capture region screenshot"""
        try:
            with Progress() as progress:
                task = progress.add_task(f"Capturing region ({x},{y},{width},{height})...", total=None)
                result = self.screenshot_tools.capture_region(x, y, width, height, filename)
                progress.update(task, completed=True)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2))
            else:
                if result.success:
                    self.console.print(f"[green]✓ Region screenshot saved: {result.file_path}[/green]")
                    self.console.print(f"  Region: ({x},{y},{width},{height})")
                    self.console.print(f"  File size: {result.file_size} bytes")
                else:
                    self.console.print(f"[red]✗ Failed to capture region: {result.error_message}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error capturing region: {e}[/red]")
    
    def capture_window(self, window_title: str, filename: Optional[str] = None, format: str = "table") -> None:
        """Capture window screenshot"""
        try:
            with Progress() as progress:
                task = progress.add_task(f"Capturing window '{window_title}'...", total=None)
                result = self.screenshot_tools.capture_window(window_title, filename)
                progress.update(task, completed=True)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2))
            else:
                if result.success:
                    self.console.print(f"[green]✓ Window screenshot saved: {result.file_path}[/green]")
                    self.console.print(f"  Window: {window_title}")
                    self.console.print(f"  Size: {result.width}x{result.height} pixels")
                else:
                    self.console.print(f"[red]✗ Failed to capture window: {result.error_message}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error capturing window: {e}[/red]")
    
    def capture_webpage(self, url: str, filename: Optional[str] = None, 
                       full_page: bool = False, wait_element: Optional[str] = None,
                       format: str = "table") -> None:
        """Capture webpage screenshot"""
        try:
            # Update config
            self.screenshot_tools.config.full_page = full_page
            if wait_element:
                self.screenshot_tools.config.wait_for_element = wait_element
            
            with Progress() as progress:
                task = progress.add_task(f"Capturing webpage '{url}'...", total=None)
                result = self.screenshot_tools.capture_webpage(url, filename)
                progress.update(task, completed=True)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2))
            else:
                if result.success:
                    self.console.print(f"[green]✓ Webpage screenshot saved: {result.file_path}[/green]")
                    self.console.print(f"  URL: {url}")
                    self.console.print(f"  Size: {result.width}x{result.height} pixels")
                    if result.metadata and "page_title" in result.metadata:
                        self.console.print(f"  Title: {result.metadata['page_title']}")
                else:
                    self.console.print(f"[red]✗ Failed to capture webpage: {result.error_message}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error capturing webpage: {e}[/red]")
    
    def capture_element(self, url: str, selector: str, filename: Optional[str] = None, format: str = "table") -> None:
        """Capture element screenshot"""
        try:
            with Progress() as progress:
                task = progress.add_task(f"Capturing element '{selector}' from '{url}'...", total=None)
                result = self.screenshot_tools.capture_element(url, selector, filename)
                progress.update(task, completed=True)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2))
            else:
                if result.success:
                    self.console.print(f"[green]✓ Element screenshot saved: {result.file_path}[/green]")
                    self.console.print(f"  URL: {url}")
                    self.console.print(f"  Selector: {selector}")
                    self.console.print(f"  Size: {result.width}x{result.height} pixels")
                else:
                    self.console.print(f"[red]✗ Failed to capture element: {result.error_message}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error capturing element: {e}[/red]")
    
    def capture_scrolling(self, url: str, filename: Optional[str] = None, format: str = "table") -> None:
        """Capture scrolling webpage screenshot"""
        try:
            with Progress() as progress:
                task = progress.add_task(f"Capturing scrolling webpage '{url}'...", total=None)
                result = self.screenshot_tools.capture_scrolling(url, filename)
                progress.update(task, completed=True)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(result), indent=2))
            else:
                if result.success:
                    self.console.print(f"[green]✓ Scrolling screenshot saved: {result.file_path}[/green]")
                    self.console.print(f"  URL: {url}")
                    self.console.print(f"  Size: {result.width}x{result.height} pixels")
                    if result.metadata and "screenshots_combined" in result.metadata:
                        self.console.print(f"  Screenshots combined: {result.metadata['screenshots_combined']}")
                else:
                    self.console.print(f"[red]✗ Failed to capture scrolling: {result.error_message}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error capturing scrolling: {e}[/red]")
    
    def list_screenshots(self, format: str = "table") -> None:
        """List all screenshots"""
        try:
            screenshots = self.screenshot_tools.list_screenshots()
            
            if format == "json":
                import json
                self.console.print(json.dumps([asdict(s) for s in screenshots], indent=2))
            else:
                if not screenshots:
                    self.console.print("[yellow]No screenshots found[/yellow]")
                    return
                
                screenshots_table = Table(title="Screenshots")
                screenshots_table.add_column("Name", style="cyan")
                screenshots_table.add_column("Type", style="blue")
                screenshots_table.add_column("Size", style="green")
                screenshots_table.add_column("Dimensions", style="yellow")
                screenshots_table.add_column("File Size", style="red")
                screenshots_table.add_column("Created", style="white")
                
                for screenshot in screenshots:
                    file_size_mb = screenshot.file_size / (1024 * 1024)
                    created_date = datetime.fromisoformat(screenshot.created_at).strftime("%Y-%m-%d %H:%M")
                    
                    screenshots_table.add_row(
                        screenshot.name,
                        screenshot.screenshot_type,
                        screenshot.format.upper(),
                        f"{screenshot.width}x{screenshot.height}",
                        f"{file_size_mb:.2f} MB",
                        created_date
                    )
                
                self.console.print(screenshots_table)
                
        except Exception as e:
            self.console.print(f"[red]Error listing screenshots: {e}[/red]")
    
    def show_screenshot_info(self, file_path: str, format: str = "table") -> None:
        """Show screenshot information"""
        try:
            info = self.screenshot_tools.get_screenshot_info(file_path)
            
            if format == "json":
                import json
                self.console.print(json.dumps(asdict(info) if info else {}, indent=2))
            else:
                if info:
                    info_table = Table(title=f"Screenshot Info: {info.name}")
                    info_table.add_column("Property", style="cyan")
                    info_table.add_column("Value", style="white")
                    
                    info_table.add_row("File Path", info.file_path)
                    info_table.add_row("Type", info.screenshot_type)
                    info_table.add_row("Dimensions", f"{info.width}x{info.height}")
                    info_table.add_row("Format", info.format.upper())
                    info_table.add_row("File Size", f"{info.file_size} bytes")
                    info_table.add_row("Created", info.created_at)
                    info_table.add_row("Modified", info.modified_at)
                    
                    if info.metadata:
                        for key, value in info.metadata.items():
                            info_table.add_row(key.title(), str(value))
                    
                    self.console.print(info_table)
                else:
                    self.console.print(f"[red]Screenshot not found: {file_path}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error showing screenshot info: {e}[/red]")
    
    def delete_screenshot(self, file_path: str) -> None:
        """Delete a screenshot"""
        try:
            if self.screenshot_tools.delete_screenshot(file_path):
                self.console.print(f"[green]✓ Screenshot deleted: {file_path}[/green]")
            else:
                self.console.print(f"[red]✗ Screenshot not found: {file_path}[/red]")
        except Exception as e:
            self.console.print(f"[red]Error deleting screenshot: {e}[/red]")
    
    def clear_screenshots(self) -> None:
        """Clear all screenshots"""
        try:
            count = self.screenshot_tools.clear_screenshots()
            self.console.print(f"[green]✓ Cleared {count} screenshots[/green]")
        except Exception as e:
            self.console.print(f"[red]Error clearing screenshots: {e}[/red]")
    
    def get_screen_info(self) -> None:
        """Get screen information"""
        try:
            screen_size = pyautogui.size()
            mouse_position = pyautogui.position()
            
            info_table = Table(title="Screen Information")
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="white")
            
            info_table.add_row("Screen Size", f"{screen_size.width}x{screen_size.height}")
            info_table.add_row("Mouse Position", f"({mouse_position.x}, {mouse_position.y})")
            info_table.add_row("Screenshot Output", str(self.screenshot_tools.output_dir))
            info_table.add_row("Default Format", self.screenshot_tools.config.format.upper())
            info_table.add_row("Quality", str(self.screenshot_tools.config.quality))
            
            self.console.print(info_table)
            
        except Exception as e:
            self.console.print(f"[red]Error getting screen info: {e}[/red]")


# Global instance
screenshot_tools = ScreenshotToolsManager() 