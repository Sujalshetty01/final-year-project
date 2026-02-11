"""
Baseline machine learning models for malware classification comparison
Includes Random Forest, SVM, and Gradient Boosting models
"""

import numpy as np
from typing import Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)

# Try to import sklearn
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available - baseline models disabled")


class BaselineModelEnsemble:
    """
    Ensemble of traditional ML models for malware classification
    Includes Random Forest, SVM, and Gradient Boosting
    """
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.is_fitted = False
    
    def _initialize_models(self):
        """Initialize baseline models"""
        if not SKLEARN_AVAILABLE:
            logger.warning("sklearn not available, baseline models cannot be used")
            return
        
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                random_state=42,
                n_jobs=-1
            ),
            'svm': SVC(
                kernel='rbf',
                C=1.0,
                probability=True,
                random_state=42
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=10,
                learning_rate=0.1,
                random_state=42
            )
        }
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Fit all baseline models
        
        Args:
            X: Feature matrix [num_samples, num_features]
            y: Labels [num_samples]
        """
        if not SKLEARN_AVAILABLE:
            logger.warning("Cannot fit models - sklearn not available")
            return
        
        self._initialize_models()
        
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train each model
            for model_name, model in self.models.items():
                logger.info(f"Training {model_name}...")
                model.fit(X_scaled, y)
            
            self.is_fitted = True
            logger.info("All baseline models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training baseline models: {str(e)}")
            raise
    
    def predict(self, X: np.ndarray) -> Dict[str, Dict[str, Any]]:
        """
        Get predictions from all baseline models
        
        Args:
            X: Feature matrix [num_samples, num_features]
            
        Returns:
            Dictionary with predictions and probabilities from each model
        """
        if not self.is_fitted:
            logger.warning("Models not fitted, using dummy predictions")
            return self._dummy_predictions(X)
        
        try:
            X_scaled = self.scaler.transform(X)
            
            results = {}
            for model_name, model in self.models.items():
                try:
                    pred = model.predict(X_scaled)[0]
                    probs = model.predict_proba(X_scaled)[0]
                    
                    results[model_name] = {
                        'prediction': int(pred),
                        'probabilities': {
                            '0': float(probs[0]),
                            '1': float(probs[1])
                        }
                    }
                except Exception as e:
                    logger.error(f"Error predicting with {model_name}: {str(e)}")
                    results[model_name] = {
                        'prediction': 0,
                        'probabilities': {'0': 0.5, '1': 0.5}
                    }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in predict: {str(e)}")
            return self._dummy_predictions(X)
    
    def _dummy_predictions(self, X: np.ndarray) -> Dict[str, Dict[str, Any]]:
        """Return dummy predictions when models aren't available"""
        return {
            'random_forest': {'prediction': 0, 'probabilities': {'0': 0.5, '1': 0.5}},
            'svm': {'prediction': 0, 'probabilities': {'0': 0.5, '1': 0.5}},
            'gradient_boosting': {'prediction': 0, 'probabilities': {'0': 0.5, '1': 0.5}}
        }
    
    def save(self, path: str):
        """Save models (requires joblib)"""
        if not SKLEARN_AVAILABLE:
            logger.warning("Cannot save models - sklearn not available")
            return
        
        try:
            import joblib
            joblib.dump({
                'models': self.models,
                'scaler': self.scaler
            }, path)
            logger.info(f"Baseline models saved to {path}")
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
    
    def load(self, path: str):
        """Load models (requires joblib)"""
        if not SKLEARN_AVAILABLE:
            logger.warning("Cannot load models - sklearn not available")
            return
        
        try:
            import joblib
            data = joblib.load(path)
            self.models = data['models']
            self.scaler = data['scaler']
            self.is_fitted = True
            logger.info(f"Baseline models loaded from {path}")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")


def create_dummy_baseline_predictions() -> Dict[str, Dict[str, Any]]:
    """Create dummy predictions for testing"""
    return {
        'random_forest': {
            'model_name': 'Random Forest',
            'predicted_label': 'benign',
            'confidence': 0.72,
            'probabilities': {'benign': 0.72, 'malware': 0.28}
        },
        'svm': {
            'model_name': 'SVM',
            'predicted_label': 'benign',
            'confidence': 0.65,
            'probabilities': {'benign': 0.65, 'malware': 0.35}
        },
        'gradient_boosting': {
            'model_name': 'Gradient Boosting',
            'predicted_label': 'benign',
            'confidence': 0.68,
            'probabilities': {'benign': 0.68, 'malware': 0.32}
        }
    }
