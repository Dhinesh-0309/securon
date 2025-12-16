"""ML Engine factory for creating ML Engine instances"""

from .engine import IsolationForestMLEngine
from ..interfaces.ml_engine import MLEngine


def create_ml_engine(
    contamination: float = 0.1,
    random_state: int = 42
) -> MLEngine:
    """
    Create an ML Engine instance with Isolation Forest
    
    Args:
        contamination: Expected proportion of anomalies in the data (default: 0.1)
        random_state: Random state for reproducible results (default: 42)
        
    Returns:
        MLEngine instance configured with Isolation Forest
    """
    return IsolationForestMLEngine(
        contamination=contamination,
        random_state=random_state
    )