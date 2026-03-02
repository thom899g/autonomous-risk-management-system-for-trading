"""
Firebase state manager for real-time risk monitoring and data persistence.
Handles all Firebase Firestore operations with proper error handling.
"""
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Optional, Dict, Any, List, Union
import logging
from datetime import datetime, timedelta
import json

from risk_manager.config import config

class FirebaseManager:
    """Manages all Firebase Firestore operations for the risk management system"""
    
    def __init__(self):
        self.app: Optional[firebase_admin.App] = None
        self.db: Optional[FirestoreClient] = None
        self._initialize_firebase()
        self.logger = logging.getLogger(__name__)
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase connection with error handling"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(config.firebase.credentials_path)
                self.app = firebase_admin.initialize_app(
                    cred,
                    {'projectId': config.firebase.project_id}
                )
            else:
                self.app = firebase_admin.get_app()
            
            self.db = firestore.client()
            self.logger.info("Firebase initialized successfully")
            
        except FileNotFoundError as e:
            self.logger.error(f"Firebase credentials not found: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def save_risk_metric(self, 
                        metric_name: str, 
                        value: float, 
                        timestamp: datetime,
                        metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save risk metric to Firestore with error handling
        
        Args:
            metric_name: Name of the risk metric
            value: Metric value
            timestamp: When the metric was recorded
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            if not self.db:
                self.logger.error("Firestore not initialized")
                return False
            
            doc_ref = self.db.collection(
                f"{config.firebase.collection_prefix}_metrics"
            ).document()
            
            data = {
                'metric': metric_name,
                'value': float(value),
                'timestamp': timestamp,
                'created_at': datetime.utcnow(),
                'metadata': metadata or {}
            }
            
            doc_ref.set(data)
            self.logger.debug(f"Saved metric {metric_name}: {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save metric {metric_name}: {e}")
            return False
    
    def get_recent_metrics(self, 
                          metric_name: str, 
                          hours: int = 24,
                          limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve recent metrics with time filtering
        
        Args:
            metric_name: Metric to retrieve
            hours: Hours to look back
            limit: Maximum documents to return
            
        Returns:
            List of metric documents
        """
        try:
            if not self.db:
                self.logger.error("Firestore not initialized")
                return []
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            query = (
                self.db.collection(f"{config.firebase.collection_prefix}_metrics")
                .where(filter=FieldFilter("metric", "==", metric_name))
                .where(filter=FieldFilter("timestamp", ">=", cutoff_time))
                .order_by("timestamp")
                .