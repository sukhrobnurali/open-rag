import logging
import sys
from pathlib import Path
from app.config import settings

def setup_logging():
    """Setup application logging"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configure specific loggers
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    
    # Suppress some noisy loggers in production
    if not settings.debug:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)