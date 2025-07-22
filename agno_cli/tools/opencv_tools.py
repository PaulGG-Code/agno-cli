"""
OpenCV Tools - Computer Vision Operations

This module provides comprehensive computer vision capabilities with:
- Image processing and manipulation
- Object detection and recognition
- Face detection and recognition
- Image analysis and feature extraction
- Video processing and analysis
- Rich output formatting
- Multiple image formats and operations
- Advanced computer vision algorithms
"""

import os
import sys
import json
import time
import base64
import io
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.syntax import Syntax
from rich.text import Text
from rich.markdown import Markdown
import warnings

# Suppress OpenCV warnings
warnings.filterwarnings('ignore', category=UserWarning, module='cv2')
warnings.filterwarnings('ignore', category=FutureWarning, module='cv2')


@dataclass
class ImageInfo:
    """Image information and metadata"""
    width: int
    height: int
    channels: int
    dtype: str
    size_bytes: int
    format: str
    path: str


@dataclass
class DetectionResult:
    """Object detection result"""
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    center: Tuple[int, int]


@dataclass
class FaceResult:
    """Face detection result"""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    landmarks: Optional[List[Tuple[int, int]]] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    emotion: Optional[str] = None


@dataclass
class ImageProcessingResult:
    """Result of an image processing operation"""
    operation: str
    input_path: str
    output_path: Optional[str]
    success: bool
    processing_time: float
    image_info: Optional[ImageInfo] = None
    detections: Optional[List[DetectionResult]] = None
    faces: Optional[List[FaceResult]] = None
    error_message: Optional[str] = None


class OpenCVTools:
    """Core computer vision tools"""
    
    def __init__(self):
        self.console = Console()
        self.output_dir = Path("opencv_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize OpenCV models and classifiers
        self.face_cascade = None
        self.eye_cascade = None
        self.body_cascade = None
        self.car_cascade = None
        
        # Load pre-trained models
        self._load_cascades()
        
        # Color maps for visualization
        self.color_maps = {
            'viridis': cv2.COLORMAP_VIRIDIS,
            'plasma': cv2.COLORMAP_PLASMA,
            'inferno': cv2.COLORMAP_INFERNO,
            'magma': cv2.COLORMAP_MAGMA,
            'hot': cv2.COLORMAP_HOT,
            'cool': cv2.COLORMAP_COOL,
            'spring': cv2.COLORMAP_SPRING,
            'summer': cv2.COLORMAP_SUMMER,
            'autumn': cv2.COLORMAP_AUTUMN,
            'winter': cv2.COLORMAP_WINTER
        }
    
    def _load_cascades(self):
        """Load OpenCV cascade classifiers"""
        try:
            # Get OpenCV data path
            opencv_data_path = cv2.data.haarcascades
            
            # Load face cascade
            face_cascade_path = os.path.join(opencv_data_path, 'haarcascade_frontalface_default.xml')
            if os.path.exists(face_cascade_path):
                self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
            
            # Load eye cascade
            eye_cascade_path = os.path.join(opencv_data_path, 'haarcascade_eye.xml')
            if os.path.exists(eye_cascade_path):
                self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            # Load body cascade
            body_cascade_path = os.path.join(opencv_data_path, 'haarcascade_fullbody.xml')
            if os.path.exists(body_cascade_path):
                self.body_cascade = cv2.CascadeClassifier(body_cascade_path)
            
            # Load car cascade
            car_cascade_path = os.path.join(opencv_data_path, 'haarcascade_cars.xml')
            if os.path.exists(car_cascade_path):
                self.car_cascade = cv2.CascadeClassifier(car_cascade_path)
                
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load some cascade classifiers: {e}[/yellow]")
    
    def _create_output_path(self, operation: str, filename: Optional[str] = None) -> Path:
        """Create output file path"""
        if filename:
            return self.output_dir / f"{filename}"
        else:
            timestamp = int(time.time())
            return self.output_dir / f"{operation}_{timestamp}.jpg"
    
    def _get_image_info(self, image: np.ndarray, path: str) -> ImageInfo:
        """Get image information"""
        height, width = image.shape[:2]
        channels = 1 if len(image.shape) == 2 else image.shape[2]
        dtype = str(image.dtype)
        size_bytes = image.nbytes
        format_ext = Path(path).suffix.lower()
        
        return ImageInfo(
            width=width,
            height=height,
            channels=channels,
            dtype=dtype,
            size_bytes=size_bytes,
            format=format_ext,
            path=path
        )
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image from file"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            return image
            
        except Exception as e:
            self.console.print(f"[red]Error loading image: {e}[/red]")
            return None
    
    def save_image(self, image: np.ndarray, output_path: str) -> bool:
        """Save image to file"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save image
            success = cv2.imwrite(output_path, image)
            if not success:
                raise ValueError(f"Could not save image to: {output_path}")
            
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error saving image: {e}[/red]")
            return False
    
    def resize_image(self, image: np.ndarray, width: Optional[int] = None, 
                    height: Optional[int] = None, scale: Optional[float] = None) -> np.ndarray:
        """Resize image"""
        h, w = image.shape[:2]
        
        if scale is not None:
            new_width = int(w * scale)
            new_height = int(h * scale)
        elif width is not None and height is not None:
            new_width, new_height = width, height
        elif width is not None:
            aspect_ratio = w / h
            new_width = width
            new_height = int(width / aspect_ratio)
        elif height is not None:
            aspect_ratio = w / h
            new_height = height
            new_width = int(height * aspect_ratio)
        else:
            return image
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    def convert_color(self, image: np.ndarray, conversion: str) -> np.ndarray:
        """Convert image color space"""
        conversions = {
            'bgr2rgb': cv2.COLOR_BGR2RGB,
            'bgr2gray': cv2.COLOR_BGR2GRAY,
            'bgr2hsv': cv2.COLOR_BGR2HSV,
            'bgr2lab': cv2.COLOR_BGR2LAB,
            'rgb2bgr': cv2.COLOR_RGB2BGR,
            'rgb2gray': cv2.COLOR_RGB2GRAY,
            'rgb2hsv': cv2.COLOR_RGB2HSV,
            'gray2bgr': cv2.COLOR_GRAY2BGR,
            'gray2rgb': cv2.COLOR_GRAY2RGB,
            'hsv2bgr': cv2.COLOR_HSV2BGR,
            'hsv2rgb': cv2.COLOR_HSV2RGB
        }
        
        if conversion in conversions:
            return cv2.cvtColor(image, conversions[conversion])
        else:
            raise ValueError(f"Unsupported color conversion: {conversion}")
    
    def apply_filter(self, image: np.ndarray, filter_type: str, **kwargs) -> np.ndarray:
        """Apply various filters to image"""
        if filter_type == "blur":
            kernel_size = kwargs.get('kernel_size', 5)
            return cv2.blur(image, (kernel_size, kernel_size))
        
        elif filter_type == "gaussian_blur":
            kernel_size = kwargs.get('kernel_size', 5)
            sigma = kwargs.get('sigma', 1.0)
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)
        
        elif filter_type == "median_blur":
            kernel_size = kwargs.get('kernel_size', 5)
            return cv2.medianBlur(image, kernel_size)
        
        elif filter_type == "bilateral":
            d = kwargs.get('d', 9)
            sigma_color = kwargs.get('sigma_color', 75)
            sigma_space = kwargs.get('sigma_space', 75)
            return cv2.bilateralFilter(image, d, sigma_color, sigma_space)
        
        elif filter_type == "sharpen":
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            return cv2.filter2D(image, -1, kernel)
        
        elif filter_type == "emboss":
            kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
            return cv2.filter2D(image, -1, kernel)
        
        elif filter_type == "edge":
            return cv2.Canny(image, 100, 200)
        
        else:
            raise ValueError(f"Unsupported filter type: {filter_type}")
    
    def adjust_brightness_contrast(self, image: np.ndarray, brightness: float = 0, 
                                 contrast: float = 1.0) -> np.ndarray:
        """Adjust brightness and contrast"""
        adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
        return adjusted
    
    def apply_color_map(self, image: np.ndarray, color_map: str) -> np.ndarray:
        """Apply color map to image"""
        if color_map in self.color_maps:
            return cv2.applyColorMap(image, self.color_maps[color_map])
        else:
            raise ValueError(f"Unsupported color map: {color_map}")
    
    def detect_faces(self, image: np.ndarray) -> List[FaceResult]:
        """Detect faces in image"""
        if self.face_cascade is None:
            raise ValueError("Face cascade classifier not loaded")
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        face_results = []
        for (x, y, w, h) in faces:
            face_results.append(FaceResult(
                bbox=(x, y, w, h),
                confidence=0.8  # Default confidence for cascade
            ))
        
        return face_results
    
    def detect_eyes(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect eyes in image"""
        if self.eye_cascade is None:
            raise ValueError("Eye cascade classifier not loaded")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect eyes
        eyes = self.eye_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20)
        )
        
        eye_results = []
        for (x, y, w, h) in eyes:
            eye_results.append(DetectionResult(
                class_name="eye",
                confidence=0.8,
                bbox=(x, y, w, h),
                center=(x + w//2, y + h//2)
            ))
        
        return eye_results
    
    def detect_bodies(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect human bodies in image"""
        if self.body_cascade is None:
            raise ValueError("Body cascade classifier not loaded")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect bodies
        bodies = self.body_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 100)
        )
        
        body_results = []
        for (x, y, w, h) in bodies:
            body_results.append(DetectionResult(
                class_name="body",
                confidence=0.8,
                bbox=(x, y, w, h),
                center=(x + w//2, y + h//2)
            ))
        
        return body_results
    
    def detect_cars(self, image: np.ndarray) -> List[DetectionResult]:
        """Detect cars in image"""
        if self.car_cascade is None:
            raise ValueError("Car cascade classifier not loaded")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect cars
        cars = self.car_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )
        
        car_results = []
        for (x, y, w, h) in cars:
            car_results.append(DetectionResult(
                class_name="car",
                confidence=0.8,
                bbox=(x, y, w, h),
                center=(x + w//2, y + h//2)
            ))
        
        return car_results
    
    def draw_detections(self, image: np.ndarray, detections: List[DetectionResult], 
                       color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """Draw detection bounding boxes on image"""
        result_image = image.copy()
        
        for detection in detections:
            x, y, w, h = detection.bbox
            cv2.rectangle(result_image, (x, y), (x + w, y + h), color, thickness)
            
            # Add label
            label = f"{detection.class_name}: {detection.confidence:.2f}"
            cv2.putText(result_image, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
        
        return result_image
    
    def draw_faces(self, image: np.ndarray, faces: List[FaceResult], 
                  color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """Draw face bounding boxes on image"""
        result_image = image.copy()
        
        for face in faces:
            x, y, w, h = face.bbox
            cv2.rectangle(result_image, (x, y), (x + w, y + h), color, thickness)
            
            # Add face label
            label = f"Face: {face.confidence:.2f}"
            cv2.putText(result_image, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
        
        return result_image
    
    def extract_features(self, image: np.ndarray, feature_type: str) -> Dict[str, Any]:
        """Extract image features"""
        features = {}
        
        if feature_type == "basic":
            # Basic image statistics
            features['mean'] = np.mean(image, axis=(0, 1)).tolist()
            features['std'] = np.std(image, axis=(0, 1)).tolist()
            features['min'] = np.min(image, axis=(0, 1)).tolist()
            features['max'] = np.max(image, axis=(0, 1)).tolist()
            
            # Histogram
            if len(image.shape) == 3:
                hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                features['histogram'] = hist.flatten().tolist()
            else:
                hist = cv2.calcHist([image], [0], None, [256], [0, 256])
                features['histogram'] = hist.flatten().tolist()
        
        elif feature_type == "edges":
            # Edge detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            edges = cv2.Canny(gray, 100, 200)
            features['edge_density'] = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        elif feature_type == "corners":
            # Corner detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            corners = cv2.goodFeaturesToTrack(gray, 25, 0.01, 10)
            features['corner_count'] = len(corners) if corners is not None else 0
        
        return features
    
    def create_thumbnail(self, image: np.ndarray, max_size: int = 200) -> np.ndarray:
        """Create thumbnail of image"""
        h, w = image.shape[:2]
        
        if h > w:
            new_h = max_size
            new_w = int(w * max_size / h)
        else:
            new_w = max_size
            new_h = int(h * max_size / w)
        
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    def rotate_image(self, image: np.ndarray, angle: float, center: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """Rotate image by angle"""
        h, w = image.shape[:2]
        
        if center is None:
            center = (w // 2, h // 2)
        
        # Get rotation matrix
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Perform rotation
        rotated = cv2.warpAffine(image, matrix, (w, h))
        
        return rotated
    
    def crop_image(self, image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Crop image to specified region"""
        return image[y:y+height, x:x+width]
    
    def flip_image(self, image: np.ndarray, direction: str) -> np.ndarray:
        """Flip image horizontally or vertically"""
        if direction == "horizontal":
            return cv2.flip(image, 1)
        elif direction == "vertical":
            return cv2.flip(image, 0)
        else:
            raise ValueError("Direction must be 'horizontal' or 'vertical'")
    
    def add_text(self, image: np.ndarray, text: str, position: Tuple[int, int], 
                font_scale: float = 1.0, color: Tuple[int, int, int] = (255, 255, 255), 
                thickness: int = 2) -> np.ndarray:
        """Add text to image"""
        result_image = image.copy()
        cv2.putText(result_image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                   font_scale, color, thickness)
        return result_image
    
    def create_montage(self, images: List[np.ndarray], cols: int = 3, max_size: int = 200) -> np.ndarray:
        """Create image montage"""
        if not images:
            raise ValueError("No images provided")
        
        # Create thumbnails
        thumbnails = [self.create_thumbnail(img, max_size) for img in images]
        
        # Calculate grid dimensions
        n_images = len(thumbnails)
        rows = (n_images + cols - 1) // cols
        
        # Get thumbnail dimensions
        thumb_h, thumb_w = thumbnails[0].shape[:2]
        
        # Create montage canvas
        if len(thumbnails[0].shape) == 3:
            montage = np.zeros((thumb_h * rows, thumb_w * cols, 3), dtype=np.uint8)
        else:
            montage = np.zeros((thumb_h * rows, thumb_w * cols), dtype=np.uint8)
        
        # Place thumbnails in grid
        for i, thumb in enumerate(thumbnails):
            row = i // cols
            col = i % cols
            y_start = row * thumb_h
            y_end = y_start + thumb_h
            x_start = col * thumb_w
            x_end = x_start + thumb_w
            
            montage[y_start:y_end, x_start:x_end] = thumb
        
        return montage
    
    def get_image_info(self, image_path: str) -> Optional[ImageInfo]:
        """Get detailed image information"""
        try:
            image = self.load_image(image_path)
            if image is None:
                return None
            
            return self._get_image_info(image, image_path)
            
        except Exception as e:
            self.console.print(f"[red]Error getting image info: {e}[/red]")
            return None


class OpenCVToolsManager:
    """CLI integration for OpenCV tools"""
    
    def __init__(self):
        self.opencv_tools = OpenCVTools()
        self.console = Console()
    
    def process_image(self, image_path: str, operation: str, output_path: Optional[str] = None,
                     **kwargs) -> None:
        """Process image with specified operation"""
        try:
            start_time = time.time()
            
            # Load image
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Loading image...", total=None)
                image = self.opencv_tools.load_image(image_path)
            
            if image is None:
                self.console.print(f"[red]Failed to load image: {image_path}[/red]")
                return
            
            # Get image info
            image_info = self.opencv_tools._get_image_info(image, image_path)
            
            # Process image based on operation
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Processing {operation}...", total=None)
                
                if operation == "resize":
                    width = kwargs.get('width')
                    height = kwargs.get('height')
                    scale = kwargs.get('scale')
                    result_image = self.opencv_tools.resize_image(image, width, height, scale)
                
                elif operation == "convert_color":
                    conversion = kwargs.get('conversion', 'bgr2rgb')
                    result_image = self.opencv_tools.convert_color(image, conversion)
                
                elif operation == "filter":
                    filter_type = kwargs.get('filter_type', 'blur')
                    # Remove filter_type from kwargs to avoid duplicate argument
                    filter_kwargs = {k: v for k, v in kwargs.items() if k != 'filter_type'}
                    result_image = self.opencv_tools.apply_filter(image, filter_type, **filter_kwargs)
                
                elif operation == "brightness_contrast":
                    brightness = kwargs.get('brightness', 0)
                    contrast = kwargs.get('contrast', 1.0)
                    result_image = self.opencv_tools.adjust_brightness_contrast(image, brightness, contrast)
                
                elif operation == "color_map":
                    color_map = kwargs.get('color_map', 'viridis')
                    result_image = self.opencv_tools.apply_color_map(image, color_map)
                
                elif operation == "rotate":
                    angle = kwargs.get('angle', 90)
                    result_image = self.opencv_tools.rotate_image(image, angle)
                
                elif operation == "flip":
                    direction = kwargs.get('direction', 'horizontal')
                    result_image = self.opencv_tools.flip_image(image, direction)
                
                elif operation == "crop":
                    x = kwargs.get('x', 0)
                    y = kwargs.get('y', 0)
                    width = kwargs.get('width', image.shape[1] // 2)
                    height = kwargs.get('height', image.shape[0] // 2)
                    result_image = self.opencv_tools.crop_image(image, x, y, width, height)
                
                elif operation == "add_text":
                    text = kwargs.get('text', 'OpenCV Text')
                    position = kwargs.get('position', (50, 50))
                    result_image = self.opencv_tools.add_text(image, text, position)
                
                else:
                    self.console.print(f"[red]Unknown operation: {operation}[/red]")
                    return
            
            # Save result
            if output_path is None:
                output_path = str(self.opencv_tools._create_output_path(operation))
            
            success = self.opencv_tools.save_image(result_image, output_path)
            
            processing_time = time.time() - start_time
            
            if success:
                self.console.print(f"[green]Image processed successfully![/green]")
                self.console.print(f"[blue]Output saved to: {output_path}[/blue]")
                
                # Show result info
                result_info = self.opencv_tools._get_image_info(result_image, output_path)
                
                info_table = Table(title="Processing Result")
                info_table.add_column("Property", style="cyan")
                info_table.add_column("Value", style="white")
                
                info_table.add_row("Operation", operation)
                info_table.add_row("Input Path", image_path)
                info_table.add_row("Output Path", output_path)
                info_table.add_row("Processing Time", f"{processing_time:.2f}s")
                info_table.add_row("Input Size", f"{image_info.width}x{image_info.height}")
                info_table.add_row("Output Size", f"{result_info.width}x{result_info.height}")
                info_table.add_row("Input Format", image_info.format)
                info_table.add_row("Output Format", result_info.format)
                
                self.console.print(info_table)
            else:
                self.console.print(f"[red]Failed to save processed image[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Image processing error: {e}[/red]")
    
    def detect_objects(self, image_path: str, object_type: str, output_path: Optional[str] = None,
                      draw_boxes: bool = True) -> None:
        """Detect objects in image"""
        try:
            start_time = time.time()
            
            # Load image
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Loading image...", total=None)
                image = self.opencv_tools.load_image(image_path)
            
            if image is None:
                self.console.print(f"[red]Failed to load image: {image_path}[/red]")
                return
            
            # Detect objects
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Detecting {object_type}...", total=None)
                
                if object_type == "faces":
                    detections = self.opencv_tools.detect_faces(image)
                    detection_results = [DetectionResult(
                        class_name="face",
                        confidence=face.confidence,
                        bbox=face.bbox,
                        center=(face.bbox[0] + face.bbox[2]//2, face.bbox[1] + face.bbox[3]//2)
                    ) for face in detections]
                
                elif object_type == "eyes":
                    detection_results = self.opencv_tools.detect_eyes(image)
                
                elif object_type == "bodies":
                    detection_results = self.opencv_tools.detect_bodies(image)
                
                elif object_type == "cars":
                    detection_results = self.opencv_tools.detect_cars(image)
                
                else:
                    self.console.print(f"[red]Unknown object type: {object_type}[/red]")
                    return
            
            # Draw detections if requested
            if draw_boxes and detection_results:
                result_image = self.opencv_tools.draw_detections(image, detection_results)
            else:
                result_image = image
            
            # Save result
            if output_path is None:
                output_path = str(self.opencv_tools._create_output_path(f"{object_type}_detection"))
            
            success = self.opencv_tools.save_image(result_image, output_path)
            
            processing_time = time.time() - start_time
            
            if success:
                self.console.print(f"[green]Object detection completed![/green]")
                self.console.print(f"[blue]Output saved to: {output_path}[/blue]")
                
                # Show detection results
                info_table = Table(title=f"{object_type.title()} Detection Results")
                info_table.add_column("Property", style="cyan")
                info_table.add_column("Value", style="white")
                
                info_table.add_row("Object Type", object_type)
                info_table.add_row("Detections Found", str(len(detection_results)))
                info_table.add_row("Processing Time", f"{processing_time:.2f}s")
                info_table.add_row("Output Path", output_path)
                
                if detection_results:
                    avg_confidence = sum(d.confidence for d in detection_results) / len(detection_results)
                    info_table.add_row("Average Confidence", f"{avg_confidence:.2f}")
                
                self.console.print(info_table)
                
                # Show individual detections
                if detection_results:
                    detections_table = Table(title="Detections")
                    detections_table.add_column("Index", style="cyan")
                    detections_table.add_column("Class", style="white")
                    detections_table.add_column("Confidence", style="yellow")
                    detections_table.add_column("Bounding Box", style="green")
                    detections_table.add_column("Center", style="blue")
                    
                    for i, detection in enumerate(detection_results):
                        detections_table.add_row(
                            str(i + 1),
                            detection.class_name,
                            f"{detection.confidence:.2f}",
                            str(detection.bbox),
                            str(detection.center)
                        )
                    
                    self.console.print(detections_table)
            else:
                self.console.print(f"[red]Failed to save detection result[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Object detection error: {e}[/red]")
    
    def extract_features(self, image_path: str, feature_type: str, format: str = "table") -> None:
        """Extract features from image"""
        try:
            # Load image
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Loading image...", total=None)
                image = self.opencv_tools.load_image(image_path)
            
            if image is None:
                self.console.print(f"[red]Failed to load image: {image_path}[/red]")
                return
            
            # Extract features
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Extracting {feature_type} features...", total=None)
                features = self.opencv_tools.extract_features(image, feature_type)
            
            if format == "json":
                import json
                self.console.print(json.dumps(features, indent=2))
            else:
                # Show features table
                features_table = Table(title=f"{feature_type.title()} Features")
                features_table.add_column("Feature", style="cyan")
                features_table.add_column("Value", style="white")
                
                for key, value in features.items():
                    if isinstance(value, list) and len(value) > 10:
                        features_table.add_row(key, f"List with {len(value)} elements")
                    else:
                        features_table.add_row(key, str(value))
                
                self.console.print(features_table)
                
        except Exception as e:
            self.console.print(f"[red]Feature extraction error: {e}[/red]")
    
    def get_image_info(self, image_path: str, format: str = "table") -> None:
        """Get detailed image information"""
        try:
            image_info = self.opencv_tools.get_image_info(image_path)
            
            if image_info is None:
                self.console.print(f"[red]Failed to get image info: {image_path}[/red]")
                return
            
            if format == "json":
                import json
                self.console.print(json.dumps({
                    'width': image_info.width,
                    'height': image_info.height,
                    'channels': image_info.channels,
                    'dtype': image_info.dtype,
                    'size_bytes': image_info.size_bytes,
                    'format': image_info.format,
                    'path': image_info.path
                }, indent=2))
            else:
                # Show image info table
                info_table = Table(title="Image Information")
                info_table.add_column("Property", style="cyan")
                info_table.add_column("Value", style="white")
                
                info_table.add_row("Path", image_info.path)
                info_table.add_row("Dimensions", f"{image_info.width}x{image_info.height}")
                info_table.add_row("Channels", str(image_info.channels))
                info_table.add_row("Data Type", image_info.dtype)
                info_table.add_row("Size (bytes)", f"{image_info.size_bytes:,}")
                info_table.add_row("Size (MB)", f"{image_info.size_bytes / (1024*1024):.2f}")
                info_table.add_row("Format", image_info.format)
                
                self.console.print(info_table)
                
        except Exception as e:
            self.console.print(f"[red]Error getting image info: {e}[/red]")
    
    def list_operations(self, format: str = "table") -> None:
        """List available image processing operations"""
        operations = {
            'resize': 'Resize image to specified dimensions or scale',
            'convert_color': 'Convert between color spaces (BGR, RGB, HSV, etc.)',
            'filter': 'Apply filters (blur, gaussian, median, bilateral, sharpen, emboss, edge)',
            'brightness_contrast': 'Adjust brightness and contrast',
            'color_map': 'Apply color maps for visualization',
            'rotate': 'Rotate image by specified angle',
            'flip': 'Flip image horizontally or vertically',
            'crop': 'Crop image to specified region',
            'add_text': 'Add text overlay to image'
        }
        
        if format == "json":
            import json
            self.console.print(json.dumps(operations, indent=2))
        else:
            # Show operations table
            operations_table = Table(title="Available Image Processing Operations")
            operations_table.add_column("Operation", style="cyan")
            operations_table.add_column("Description", style="white")
            
            for operation, description in operations.items():
                operations_table.add_row(operation, description)
            
            self.console.print(operations_table)
    
    def list_object_types(self, format: str = "table") -> None:
        """List available object detection types"""
        object_types = {
            'faces': 'Detect human faces using Haar cascade',
            'eyes': 'Detect human eyes using Haar cascade',
            'bodies': 'Detect human bodies using Haar cascade',
            'cars': 'Detect cars using Haar cascade'
        }
        
        if format == "json":
            import json
            self.console.print(json.dumps(object_types, indent=2))
        else:
            # Show object types table
            object_types_table = Table(title="Available Object Detection Types")
            object_types_table.add_column("Object Type", style="cyan")
            object_types_table.add_column("Description", style="white")
            
            for obj_type, description in object_types.items():
                object_types_table.add_row(obj_type, description)
            
            self.console.print(object_types_table)
    
    def list_feature_types(self, format: str = "table") -> None:
        """List available feature extraction types"""
        feature_types = {
            'basic': 'Basic image statistics (mean, std, histogram)',
            'edges': 'Edge detection and edge density',
            'corners': 'Corner detection and corner count'
        }
        
        if format == "json":
            import json
            self.console.print(json.dumps(feature_types, indent=2))
        else:
            # Show feature types table
            feature_types_table = Table(title="Available Feature Extraction Types")
            feature_types_table.add_column("Feature Type", style="cyan")
            feature_types_table.add_column("Description", style="white")
            
            for feature_type, description in feature_types.items():
                feature_types_table.add_row(feature_type, description)
            
            self.console.print(feature_types_table) 