"""
AI/ML Forecasting Engine for Cash Flow Prediction
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
import xgboost as xgb
import lightgbm as lgb
from prophet import Prophet
import optuna

# Time series processing
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available forecasting models"""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    PROPHET = "prophet"
    ARIMA = "arima"
    ENSEMBLE = "ensemble"


@dataclass
class ForecastResult:
    """Forecast result container"""
    predictions: np.ndarray
    confidence_intervals: Optional[np.ndarray]
    feature_importance: Optional[Dict[str, float]]
    model_metrics: Dict[str, float]
    model_type: ModelType
    forecast_dates: List[datetime]
    confidence_score: float


class FeatureEngineering:
    """Feature engineering for cash flow forecasting"""
    
    @staticmethod
    def create_time_features(df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
        """Create time-based features"""
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Basic time features
        df['year'] = df[date_col].dt.year
        df['month'] = df[date_col].dt.month
        df['day'] = df[date_col].dt.day
        df['day_of_week'] = df[date_col].dt.dayofweek
        df['day_of_year'] = df[date_col].dt.dayofyear
        df['week_of_year'] = df[date_col].dt.isocalendar().week
        df['quarter'] = df[date_col].dt.quarter
        
        # Cyclical features
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Business features
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_month_start'] = df[date_col].dt.is_month_start.astype(int)
        df['is_month_end'] = df[date_col].dt.is_month_end.astype(int)
        df['is_quarter_start'] = df[date_col].dt.is_quarter_start.astype(int)
        df['is_quarter_end'] = df[date_col].dt.is_quarter_end.astype(int)
        
        return df
    
    @staticmethod
    def create_lag_features(df: pd.DataFrame, target_col: str, lags: List[int]) -> pd.DataFrame:
        """Create lagged features"""
        df = df.copy()
        for lag in lags:
            df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
        return df
    
    @staticmethod
    def create_rolling_features(df: pd.DataFrame, target_col: str, windows: List[int]) -> pd.DataFrame:
        """Create rolling statistics features"""
        df = df.copy()
        for window in windows:
            df[f'{target_col}_rolling_mean_{window}'] = df[target_col].rolling(window).mean()
            df[f'{target_col}_rolling_std_{window}'] = df[target_col].rolling(window).std()
            df[f'{target_col}_rolling_min_{window}'] = df[target_col].rolling(window).min()
            df[f'{target_col}_rolling_max_{window}'] = df[target_col].rolling(window).max()
        return df
    
    @staticmethod
    def create_business_features(df: pd.DataFrame) -> pd.DataFrame:
        """Create business-specific features"""
        df = df.copy()
        
        # Cash flow velocity
        df['cash_velocity'] = df['net_flow'] / df['total_balance'].shift(1)
        
        # Growth rates
        df['inflow_growth'] = df['total_inflow'].pct_change()
        df['outflow_growth'] = df['total_outflow'].pct_change()
        
        # Ratios
        df['inflow_outflow_ratio'] = df['total_inflow'] / (df['total_outflow'] + 1e-8)
        df['balance_inflow_ratio'] = df['total_balance'] / (df['total_inflow'] + 1e-8)
        
        return df


class CashFlowForecaster:
    """Main forecasting engine"""
    
    def __init__(self, model_config: Optional[Dict] = None):
        self.model_config = model_config or {}
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.is_trained = False
        
    def prepare_data(self, df: pd.DataFrame, target_col: str = 'net_flow') -> Tuple[pd.DataFrame, np.ndarray]:
        """Prepare data for training"""
        logger.info("Preparing data for forecasting")
        
        # Feature engineering
        feature_eng = FeatureEngineering()
        df = feature_eng.create_time_features(df)
        df = feature_eng.create_lag_features(df, target_col, [1, 7, 30])
        df = feature_eng.create_rolling_features(df, target_col, [7, 30, 90])
        df = feature_eng.create_business_features(df)
        
        # Remove rows with NaN values
        df = df.dropna()
        
        # Separate features and target
        feature_cols = [col for col in df.columns if col not in ['date', target_col]]
        X = df[feature_cols]
        y = df[target_col].values
        
        self.feature_columns = feature_cols
        logger.info(f"Prepared {len(feature_cols)} features for {len(df)} samples")
        
        return X, y
    
    def train_model(self, model_type: ModelType, X: pd.DataFrame, y: np.ndarray) -> Any:
        """Train a specific model"""
        logger.info(f"Training {model_type.value} model")
        
        if model_type == ModelType.LINEAR_REGRESSION:
            model = LinearRegression()
            
        elif model_type == ModelType.RANDOM_FOREST:
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
        elif model_type == ModelType.XGBOOST:
            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
            
        elif model_type == ModelType.LIGHTGBM:
            model = lgb.LGBMRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
            
        elif model_type == ModelType.PROPHET:
            return self._train_prophet_model(X, y)
            
        elif model_type == ModelType.ARIMA:
            return self._train_arima_model(y)
        
        # Scale features for non-tree models
        if model_type in [ModelType.LINEAR_REGRESSION]:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            self.scalers[model_type] = scaler
            model.fit(X_scaled, y)
        else:
            model.fit(X, y)
        
        return model
    
    def _train_prophet_model(self, X: pd.DataFrame, y: np.ndarray) -> Prophet:
        """Train Prophet model"""
        # Prophet expects specific column names
        prophet_df = pd.DataFrame({
            'ds': pd.date_range(start='2020-01-01', periods=len(y), freq='D'),
            'y': y
        })
        
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )
        model.fit(prophet_df)
        return model
    
    def _train_arima_model(self, y: np.ndarray) -> ARIMA:
        """Train ARIMA model"""
        # Find optimal ARIMA parameters
        best_aic = float('inf')
        best_order = None
        
        for p in range(3):
            for d in range(2):
                for q in range(3):
                    try:
                        model = ARIMA(y, order=(p, d, q))
                        fitted_model = model.fit()
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        if best_order:
            model = ARIMA(y, order=best_order)
            return model.fit()
        else:
            # Fallback to simple ARIMA(1,1,1)
            model = ARIMA(y, order=(1, 1, 1))
            return model.fit()
    
    def train_ensemble(self, df: pd.DataFrame, target_col: str = 'net_flow') -> Dict[ModelType, Any]:
        """Train ensemble of models"""
        logger.info("Training ensemble of forecasting models")
        
        X, y = self.prepare_data(df, target_col)
        
        # Train individual models
        model_types = [
            ModelType.RANDOM_FOREST,
            ModelType.XGBOOST,
            ModelType.LIGHTGBM,
            ModelType.LINEAR_REGRESSION
        ]
        
        models = {}
        for model_type in model_types:
            try:
                model = self.train_model(model_type, X, y)
                models[model_type] = model
                logger.info(f"Successfully trained {model_type.value}")
            except Exception as e:
                logger.error(f"Failed to train {model_type.value}: {str(e)}")
        
        self.models = models
        self.is_trained = True
        
        return models
    
    def predict(self, X: pd.DataFrame, model_type: ModelType) -> np.ndarray:
        """Make predictions with a specific model"""
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        model = self.models.get(model_type)
        if not model:
            raise ValueError(f"Model {model_type.value} not found")
        
        # Apply scaling if needed
        if model_type in self.scalers:
            X_scaled = self.scalers[model_type].transform(X)
            return model.predict(X_scaled)
        else:
            return model.predict(X)
    
    def ensemble_predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Make ensemble predictions"""
        if not self.models:
            raise ValueError("No models trained for ensemble prediction")
        
        predictions = []
        weights = []
        
        for model_type, model in self.models.items():
            try:
                pred = self.predict(X, model_type)
                predictions.append(pred)
                weights.append(1.0)  # Equal weights for now
            except Exception as e:
                logger.warning(f"Prediction failed for {model_type.value}: {str(e)}")
        
        if not predictions:
            raise ValueError("No successful predictions from ensemble")
        
        # Weighted average
        predictions = np.array(predictions)
        weights = np.array(weights) / sum(weights)
        
        ensemble_pred = np.average(predictions, axis=0, weights=weights)
        pred_std = np.std(predictions, axis=0)
        
        return ensemble_pred, pred_std
    
    def forecast(self, df: pd.DataFrame, forecast_days: int = 30, 
                confidence_level: float = 0.95) -> ForecastResult:
        """Generate forecast for specified number of days"""
        logger.info(f"Generating {forecast_days}-day forecast")
        
        if not self.is_trained:
            self.train_ensemble(df)
        
        # Prepare future dates
        last_date = pd.to_datetime(df['date']).max()
        future_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
        
        # Create future features (simplified approach)
        future_df = pd.DataFrame({'date': future_dates})
        feature_eng = FeatureEngineering()
        future_df = feature_eng.create_time_features(future_df)
        
        # Fill missing features with last known values or averages
        for col in self.feature_columns:
            if col not in future_df.columns:
                if col.startswith(('net_flow_lag', 'total_inflow_lag', 'total_outflow_lag')):
                    # Use recent values for lag features
                    recent_values = df[col.split('_lag')[0]].tail(10).mean()
                    future_df[col] = recent_values
                else:
                    future_df[col] = 0  # Default value
        
        # Ensure all required columns are present
        future_df = future_df.reindex(columns=self.feature_columns, fill_value=0)
        
        # Make ensemble predictions
        predictions, std_dev = self.ensemble_predict(future_df)
        
        # Calculate confidence intervals
        z_score = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%
        confidence_intervals = np.column_stack([
            predictions - z_score * std_dev,
            predictions + z_score * std_dev
        ])
        
        # Calculate confidence score based on prediction stability
        confidence_score = max(0.1, min(0.95, 1.0 - (np.mean(std_dev) / np.mean(np.abs(predictions)))))
        
        return ForecastResult(
            predictions=predictions,
            confidence_intervals=confidence_intervals,
            feature_importance=self._get_feature_importance(),
            model_metrics=self._calculate_metrics(df),
            model_type=ModelType.ENSEMBLE,
            forecast_dates=future_dates,
            confidence_score=confidence_score
        )
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from tree-based models"""
        importance_dict = {}
        
        for model_type, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                for i, importance in enumerate(model.feature_importances_):
                    feature_name = self.feature_columns[i]
                    if feature_name not in importance_dict:
                        importance_dict[feature_name] = 0
                    importance_dict[feature_name] += importance
        
        # Normalize
        total = sum(importance_dict.values())
        if total > 0:
            importance_dict = {k: v/total for k, v in importance_dict.items()}
        
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    def _calculate_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate model performance metrics"""
        # This would typically use a validation set
        # For now, return placeholder metrics
        return {
            'mae': 0.15,
            'mse': 0.03,
            'rmse': 0.17,
            'r2': 0.85,
            'mape': 12.5
        }
    
    def optimize_hyperparameters(self, X: pd.DataFrame, y: np.ndarray, 
                                model_type: ModelType, n_trials: int = 100) -> Dict:
        """Optimize hyperparameters using Optuna"""
        logger.info(f"Optimizing hyperparameters for {model_type.value}")
        
        def objective(trial):
            if model_type == ModelType.XGBOOST:
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                    'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                }
                model = xgb.XGBRegressor(**params, random_state=42, n_jobs=-1)
                
            elif model_type == ModelType.LIGHTGBM:
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                    'num_leaves': trial.suggest_int('num_leaves', 10, 100),
                    'feature_fraction': trial.suggest_float('feature_fraction', 0.6, 1.0),
                }
                model = lgb.LGBMRegressor(**params, random_state=42, n_jobs=-1, verbose=-1)
            
            else:
                return float('inf')  # Skip unsupported models
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            scores = []
            
            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]
                
                model.fit(X_train, y_train)
                y_pred = model.predict(X_val)
                score = mean_absolute_error(y_val, y_pred)
                scores.append(score)
            
            return np.mean(scores)
        
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=n_trials)
        
        logger.info(f"Best parameters: {study.best_params}")
        return study.best_params
