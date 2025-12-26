import os
import shutil
from pathlib import Path
from typing import List, Optional


def ensure_upload_dir(user_id: str) -> Path:
    """Ensure upload directory exists for user."""
    upload_dir = Path("data/uploads") / user_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def save_uploads(user_id: str, files: Optional[List]) -> List[str]:
    """
    Save uploaded files to data/uploads/<user_id>/.
    
    Args:
        user_id: User identifier
        files: List of file paths from Gradio file upload
        
    Returns:
        List of saved file paths (relative to project root)
    """
    if not files:
        return []
    
    upload_dir = ensure_upload_dir(user_id)
    saved_paths = []
    
    for file_path in files:
        if not file_path:
            continue
            
        source = Path(file_path)
        if not source.exists():
            continue
            
        # Generate unique filename to avoid conflicts
        filename = source.name
        counter = 1
        dest = upload_dir / filename
        while dest.exists():
            stem = source.stem
            suffix = source.suffix
            dest = upload_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        # Copy file
        shutil.copy2(source, dest)
        saved_paths.append(str(dest))
    
    return saved_paths

