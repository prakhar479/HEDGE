"""
Common utility functions and constants.
"""
from typing import Any, Dict, List
import hashlib
import json

def compute_code_hash(code: str) -> str:
    """
    Compute MD5 hash of code string.
    
    Args:
        code: Source code string
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.md5(code.encode('utf-8')).hexdigest()

def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def format_metrics(metrics: Dict[str, float], precision: int = 4) -> Dict[str, str]:
    """
    Format metrics dictionary for display.
    
    Args:
        metrics: Dictionary of metric names to values
        precision: Number of decimal places
        
    Returns:
        Dictionary with formatted values
    """
    return {k: f"{v:.{precision}f}" for k, v in metrics.items()}

def safe_json_dump(obj: Any, **kwargs) -> str:
    """
    Safely dump object to JSON, handling non-serializable types.
    
    Args:
        obj: Object to serialize
        **kwargs: Additional arguments for json.dumps
        
    Returns:
        JSON string
    """
    def default_handler(o):
        if hasattr(o, '__dict__'):
            return o.__dict__
        return str(o)
    
    return json.dumps(obj, default=default_handler, **kwargs)
