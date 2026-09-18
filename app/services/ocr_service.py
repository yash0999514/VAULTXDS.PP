"""OCR text extraction service with robust fallbacks and automated Windows binary discovery."""

import os
import shutil
from pathlib import Path
from typing import Optional


class OCRService:
    """Extracts searchable textual metadata from scanned documents, images, and PDFs."""

    def __init__(self):
        self.tesseract_available = False
        self.pypdf_available = False
        self.pil_available = False
        self.tesseract_binary_found = False
        self.tesseract_path: Optional[str] = None

        try:
            from PIL import Image
            self.Image = Image
            self.pil_available = True
        except ImportError:
            self.Image = None

        try:
            import pypdf
            self.pypdf = pypdf
            self.pypdf_available = True
        except ImportError:
            self.pypdf = None

        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.tesseract_available = True
            self._configure_tesseract_binary()
        except ImportError:
            self.pytesseract = None

    def _configure_tesseract_binary(self) -> None:
        """Automatically detect tesseract binary on PATH or standard Windows installation locations."""
        # 1. Check if 'tesseract' is accessible on system PATH
        which_path = shutil.which("tesseract")
        if which_path:
            self.tesseract_binary_found = True
            self.tesseract_path = which_path
            return

        # 2. Check standard Windows default install paths
        candidates = [
            Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
            Path(os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")),
            Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")),
        ]
        for candidate in candidates:
            if candidate.exists():
                self.pytesseract.pytesseract.tesseract_cmd = str(candidate)
                self.tesseract_binary_found = True
                self.tesseract_path = str(candidate)
                return

    def is_available(self) -> bool:
        """Check if image OCR capabilities and tesseract executable are ready."""
        return self.tesseract_available and self.pil_available and self.tesseract_binary_found

    def get_status_description(self) -> str:
        """Return human-readable status of OCR dependencies."""
        if self.is_available():
            return f"Active (Tesseract ready: {Path(self.tesseract_path).name})"
        if self.tesseract_available and not self.tesseract_binary_found:
            return "Pytesseract ready; tesseract.exe not detected on PATH"
        if self.pypdf_available:
            return "Partial (PDF extraction ready; install pytesseract for images)"
        return "Offline (Text files supported; install pytesseract & pypdf for scans)"

    def extract_text(self, file_path: str) -> str:
        """Extract searchable text from document file with fallback handling."""
        path = Path(file_path)
        if not path.exists():
            return ""

        suffix = path.suffix.lower()

        # 1. Plain text formats
        if suffix in [".txt", ".md", ".csv", ".json", ".log", ".xml", ".html", ".py", ".sql"]:
            try:
                return path.read_text(encoding="utf-8", errors="ignore")[:8000].strip()
            except Exception:
                return ""

        # 2. PDF text extraction (native python via pypdf)
        if suffix == ".pdf":
            if self.pypdf_available:
                try:
                    reader = self.pypdf.PdfReader(str(path))
                    extracted = []
                    for page in reader.pages[:8]:
                        txt = page.extract_text()
                        if txt:
                            extracted.append(txt)
                    full_txt = " ".join(extracted).strip()
                    if full_txt:
                        return full_txt[:10000]
                except Exception:
                    pass

        # 3. Image OCR (PNG, JPG, JPEG, BMP, TIFF, WEBP)
        if suffix in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]:
            if self.is_available():
                try:
                    img = self.Image.open(file_path)
                    text = self.pytesseract.image_to_string(img)
                    return text.strip()[:10000]
                except Exception:
                    return ""

        return ""
