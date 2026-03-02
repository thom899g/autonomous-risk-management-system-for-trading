"""
Configuration management for the Risk Management System.
Centralizes all configuration parameters and Firebase settings.
"""
import os
from dataclasses import dataclass
from typing import Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    project_id: str = os.getenv("FIREBASE_PROJECT_ID", "trading-risk-manager")
    credentials_path: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./credentials.json")
    collection_prefix: str = "risk_system"

@dataclass
class ExchangeConfig:
    """Exchange API configuration"""
    api_key: Optional[str] = os.getenv("EXCHANGE_API_KEY")
    api_secret: Optional[str] = os.getenv("EXCHANGE_API_SECRET")
    timeout: int = 30
    retry_attempts: int = 3

@dataclass
class RiskThresholds:
    """Risk threshold configuration"""
    max_position_size: float = 0.1  # Max 10% of portfolio per position
    max_daily_loss: float = 0.02   # Max 2% daily loss
    max_drawdown: float = 0.15     # Max 15% drawdown
    volatility_threshold: float = 0.3  # Annualized volatility threshold
    correlation_threshold: float = 0.7  # Maximum allowed correlation

@dataclass
class MLConfig:
    """Machine learning configuration"""
    model_update_frequency: int = 3600  # Update model every hour
    training_window_days: int = 30      # Use last 30 days for training
    prediction_confidence: float = 0.85  # Minimum confidence threshold

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: int = logging.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "./logs/risk_manager.log"

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.firebase = FirebaseConfig()
        self.exchange = ExchangeConfig()
        self.risk_thresholds = RiskThresholds()
        self.ml = MLConfig()
        self.logging = LoggingConfig()
        
        # Validate critical configurations
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate essential configuration parameters"""
        if not self.exchange.api_key or not self.exchange.api_secret:
            logging.warning("Exchange API credentials not configured")
        
        if not os.path.exists(self.firebase.credentials_path):
            logging.warning(f"Firebase credentials not found at {self.firebase.credentials_path}")
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.logging.file_path), exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return os.getenv("ENVIRONMENT", "development") == "production"

# Global configuration instance
config = Config()