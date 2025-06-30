#!/usr/bin/env python3
"""
FightHub ML Training Pipeline
Trains models for fight outcome prediction and fighter analytics
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
import joblib
import mlflow
import mlflow.sklearn
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.processors.fight_data_processor import FightDataProcessor
from models.fight_predictor import FightPredictor
from utils.ml_utils import setup_logging, save_model_metrics

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def main():
    """Main training pipeline"""
    logger.info("Starting FightHub ML training pipeline")
    
    # Initialize MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("fighthub-fight-prediction")
    
    try:
        # Load and preprocess data
        logger.info("Loading and preprocessing fight data...")
        data_processor = FightDataProcessor()
        
        # Load historical fight data
        fight_data = data_processor.load_fight_data()
        if fight_data.empty:
            logger.error("No fight data available for training")
            return
        
        logger.info(f"Loaded {len(fight_data)} fight records")
        
        # Preprocess features
        X, y = data_processor.prepare_features(fight_data)
        logger.info(f"Prepared features: {X.shape}, targets: {y.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train multiple models
        models = {
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(random_state=42),
            'xgboost': xgb.XGBClassifier(random_state=42, eval_metric='logloss')
        }
        
        best_model = None
        best_score = 0
        
        for model_name, model in models.items():
            logger.info(f"Training {model_name}...")
            
            with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
                # Train model
                model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                # Cross-validation
                cv_scores = cross_val_score(model, X_train, y_train, cv=5)
                cv_mean = cv_scores.mean()
                cv_std = cv_scores.std()
                
                # Log metrics
                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("cv_mean", cv_mean)
                mlflow.log_metric("cv_std", cv_std)
                
                # Log model
                mlflow.sklearn.log_model(model, model_name)
                
                # Save detailed metrics
                save_model_metrics(model_name, model, X_test, y_test, y_pred, accuracy, cv_mean, cv_std)
                
                logger.info(f"{model_name} - Accuracy: {accuracy:.4f}, CV: {cv_mean:.4f} (+/- {cv_std*2:.4f})")
                
                # Track best model
                if accuracy > best_score:
                    best_score = accuracy
                    best_model = model_name
        
        # Save best model
        if best_model:
            logger.info(f"Best model: {best_model} with accuracy: {best_score:.4f}")
            
            # Save model to disk
            model_path = f"models/{best_model}_best.joblib"
            os.makedirs("models", exist_ok=True)
            
            best_model_instance = models[best_model]
            joblib.dump(best_model_instance, model_path)
            
            # Save feature names for inference
            feature_names = X.columns.tolist()
            joblib.dump(feature_names, "models/feature_names.joblib")
            
            logger.info(f"Best model saved to {model_path}")
        
        # Train additional specialized models
        logger.info("Training specialized models...")
        
        # Method prediction model
        method_predictor = FightPredictor()
        method_predictor.train_method_model(fight_data)
        
        # Round prediction model
        round_predictor = FightPredictor()
        round_predictor.train_round_model(fight_data)
        
        logger.info("ML training pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Error in training pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    main() 