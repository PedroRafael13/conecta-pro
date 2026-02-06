# Sprint 04: Predictive Analytics

## 🎯 OBJETIVO
Implementar sistema avançado de analytics preditivo com machine learning para prever tendências de negócios, comportamento de clientes, detecção de fraudes, otimização de vendas e análise de risco, fornecendo insights acionáveis para tomada de decisão estratégica.

## 🔧 ESPECIFICAÇÕES TÉCNICAS

### Arquitetura de Analytics Preditivo
```
┌─────────────────────────────────────────────────────────┐
│                 PREDICTIVE ANALYTICS                     │
├─────────────────────────────────────────────────────────┤
│  ML/AI Engine                                           │
│  ├── Model Training Pipeline                            │
│  ├── Feature Engineering                                │
│  ├── Prediction Service                                 │
│  ├── Model Registry                                     │
│  └── Auto-ML Platform                                   │
├─────────────────────────────────────────────────────────┤
│  Prediction Models                                       │
│  ├── Customer Churn Prediction                          │
│  ├── Sales Forecasting                                  │
│  ├── Demand Planning                                    │
│  ├── Fraud Detection                                    │
│  ├── Lead Scoring                                       │
│  ├── Price Optimization                                 │
│  ├── Inventory Optimization                             │
│  └── Risk Assessment                                     │
├─────────────────────────────────────────────────────────┤
│  Data Processing                                         │
│  ├── Data Ingestion (Kafka/StreamSets)                  │
│  ├── Feature Store (PostgreSQL/Redis)                   │
│  ├── Data Warehouse (ClickHouse)                        │
│  ├── Real-time Streaming (Apache Spark)                 │
│  └── ETL Pipeline (Apache Airflow)                      │
├─────────────────────────────────────────────────────────┤
│  Analytics Layer                                         │
│  ├── Dashboard & Reports                                │
│  ├── Alerts & Notifications                             │
│  ├── Business Intelligence                              │
│  ├── A/B Testing Analytics                              │
│  └── Performance Monitoring                             │
└─────────────────────────────────────────────────────────┘
```

### Componentes Principais

#### 1. ML Training Pipeline
```python
# ml/training/pipeline.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import roc_auc_score, mean_absolute_error, r2_score
import mlflow
import joblib
from typing import Dict, List, Tuple, Optional, Any

class MLTrainingPipeline:
    """Pipeline de treinamento de modelos ML."""

    def __init__(self):
        self.feature_store = FeatureStore()
        self.model_registry = ModelRegistry()
        self.data_validator = DataValidator()
        self.experiment_tracker = mlflow

    async def train_churn_prediction_model(
        self, 
        training_data_period: str = "12M",
        validation_split: float = 0.2
    ) -> Dict:
        """
        Treina modelo de previsão de churn.

        Args:
            training_data_period: Período dos dados de treino
            validation_split: Proporção para validação

        Returns:
            Métricas e metadados do modelo treinado
        """
        
        with mlflow.start_run(run_name="churn_prediction_training") as run:
            
            # 1. Preparar dados
            features_df = await self.prepare_churn_features(training_data_period)
            
            # 2. Validação de dados
            data_quality_report = await self.data_validator.validate_dataset(
                features_df, "churn_prediction"
            )
            
            if not data_quality_report["is_valid"]:
                raise ValueError(f"Data quality issues: {data_quality_report['issues']}")

            # 3. Feature engineering
            X, y = self.engineer_churn_features(features_df)
            
            # 4. Split dados
            split_idx = int(len(X) * (1 - validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]

            # 5. Treinar modelos candidatos
            models = {
                "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
                "gradient_boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
                "xgboost": XGBClassifier(n_estimators=100, random_state=42)
            }

            best_model = None
            best_score = 0
            model_results = {}

            for model_name, model in models.items():
                # Hyperparameter tuning
                tuned_model = await self.hyperparameter_tuning(
                    model, X_train, y_train, model_name
                )
                
                # Treinamento final
                tuned_model.fit(X_train, y_train)
                
                # Validação
                y_pred_proba = tuned_model.predict_proba(X_val)[:, 1]
                auc_score = roc_auc_score(y_val, y_pred_proba)
                
                model_results[model_name] = {
                    "auc_score": auc_score,
                    "model": tuned_model,
                    "feature_importance": self.get_feature_importance(tuned_model, X.columns)
                }
                
                # Logar métricas
                mlflow.log_metric(f"{model_name}_auc", auc_score)
                
                if auc_score > best_score:
                    best_score = auc_score
                    best_model = tuned_model
                    best_model_name = model_name

            # 6. Salvar melhor modelo
            model_version = await self.model_registry.save_model(
                model=best_model,
                model_name="churn_prediction",
                model_type="classification",
                metrics={"auc_score": best_score},
                features=list(X.columns),
                training_data_info={
                    "period": training_data_period,
                    "size": len(X_train),
                    "validation_size": len(X_val)
                }
            )

            # 7. Análise do modelo
            model_analysis = await self.analyze_model_performance(
                best_model, X_val, y_val, "churn_prediction"
            )

            return {
                "model_version": model_version,
                "best_model": best_model_name,
                "performance": model_results,
                "analysis": model_analysis,
                "data_quality": data_quality_report
            }

    async def prepare_churn_features(self, period: str) -> pd.DataFrame:
        """Prepara features para modelo de churn."""
        
        # Buscar dados históricos
        end_date = datetime.utcnow()
        start_date = end_date - pd.DateOffset(months=12)  # Ajustar baseado no period
        
        # Features de usuário
        user_features = await self.feature_store.get_user_features(
            start_date, end_date, include=[
                "tenure_days",
                "total_spent",
                "avg_order_value",
                "order_frequency",
                "last_activity_days",
                "support_tickets_count",
                "feature_adoption_score",
                "login_frequency",
                "mobile_usage_ratio"
            ]
        )

        # Features de engagement
        engagement_features = await self.feature_store.get_engagement_features(
            start_date, end_date, include=[
                "session_duration_avg",
                "pages_per_session",
                "bounce_rate",
                "notification_response_rate",
                "email_open_rate",
                "feature_usage_depth"
            ]
        )

        # Features de transação
        transaction_features = await self.feature_store.get_transaction_features(
            start_date, end_date, include=[
                "transaction_count_30d",
                "transaction_value_30d",
                "payment_method_diversity",
                "refund_rate",
                "discount_usage_rate"
            ]
        )

        # Target: churn nos próximos 30 dias
        churn_labels = await self.calculate_churn_labels(
            end_date, prediction_horizon_days=30
        )

        # Combinar todas as features
        features_df = user_features.merge(
            engagement_features, on="user_id", how="left"
        ).merge(
            transaction_features, on="user_id", how="left"
        ).merge(
            churn_labels, on="user_id", how="left"
        )

        return features_df.dropna()

    def engineer_churn_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Engineering de features para churn."""
        
        # Features derivadas
        df["avg_days_between_orders"] = df["tenure_days"] / (df["order_frequency"] + 1)
        df["revenue_per_day"] = df["total_spent"] / (df["tenure_days"] + 1)
        df["support_tickets_per_month"] = df["support_tickets_count"] / (df["tenure_days"] / 30 + 1)
        df["activity_recency_ratio"] = df["last_activity_days"] / (df["tenure_days"] + 1)
        
        # Features de engagement combinadas
        df["engagement_score"] = (
            df["session_duration_avg"] * df["login_frequency"] * 
            (1 - df["bounce_rate"]) * df["notification_response_rate"]
        )

        # Features de categoria
        df["user_segment"] = pd.cut(
            df["total_spent"], 
            bins=[0, 100, 500, 2000, float('inf')], 
            labels=["low", "medium", "high", "premium"]
        )
        
        # Encoding de variáveis categóricas
        categorical_columns = ["user_segment"]
        for col in categorical_columns:
            le = LabelEncoder()
            df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))

        # Separar features e target
        feature_columns = [col for col in df.columns if col not in ["user_id", "churn", "user_segment"]]
        X = df[feature_columns]
        y = df["churn"]

        # Normalização
        scaler = StandardScaler()
        X_scaled = pd.DataFrame(
            scaler.fit_transform(X),
            columns=X.columns,
            index=X.index
        )

        return X_scaled, y

    async def train_sales_forecasting_model(
        self,
        forecast_horizon: int = 30,  # dias
        granularity: str = "daily"  # daily, weekly, monthly
    ) -> Dict:
        """Treina modelo de previsão de vendas."""
        
        with mlflow.start_run(run_name="sales_forecasting_training") as run:
            
            # Preparar dados de séries temporais
            sales_data = await self.prepare_sales_time_series(granularity)
            
            # Feature engineering para séries temporais
            features_df = self.engineer_time_series_features(
                sales_data, forecast_horizon
            )
            
            # Split temporal (último 20% para validação)
            split_idx = int(len(features_df) * 0.8)
            train_data = features_df[:split_idx]
            val_data = features_df[split_idx:]

            # Modelos de séries temporais
            models = {
                "gradient_boosting": GradientBoostingRegressor(n_estimators=100),
                "random_forest": RandomForestRegressor(n_estimators=100),
                "prophet": Prophet(),  # Para séries temporais específicas
                "lstm": LSTMModel()    # Deep learning model
            }

            best_model = None
            best_mae = float('inf')
            model_results = {}

            for model_name, model in models.items():
                if model_name == "lstm":
                    # Processar dados para LSTM
                    result = await self.train_lstm_model(
                        train_data, val_data, forecast_horizon
                    )
                elif model_name == "prophet":
                    # Processar dados para Prophet
                    result = await self.train_prophet_model(
                        train_data, val_data, forecast_horizon
                    )
                else:
                    # Modelos tradicionais de ML
                    X_train = train_data.drop(["target"], axis=1)
                    y_train = train_data["target"]
                    X_val = val_data.drop(["target"], axis=1)
                    y_val = val_data["target"]
                    
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_val)
                    
                    mae = mean_absolute_error(y_val, y_pred)
                    r2 = r2_score(y_val, y_pred)
                    
                    result = {
                        "mae": mae,
                        "r2": r2,
                        "model": model
                    }

                model_results[model_name] = result
                mlflow.log_metric(f"{model_name}_mae", result["mae"])

                if result["mae"] < best_mae:
                    best_mae = result["mae"]
                    best_model = result["model"]
                    best_model_name = model_name

            # Salvar melhor modelo
            model_version = await self.model_registry.save_model(
                model=best_model,
                model_name="sales_forecasting",
                model_type="regression",
                metrics={"mae": best_mae},
                forecast_horizon=forecast_horizon,
                granularity=granularity
            )

            return {
                "model_version": model_version,
                "best_model": best_model_name,
                "performance": model_results,
                "forecast_horizon": forecast_horizon
            }

    def engineer_time_series_features(
        self, sales_data: pd.DataFrame, horizon: int
    ) -> pd.DataFrame:
        """Engineering de features para séries temporais."""
        
        df = sales_data.copy()
        
        # Features temporais
        df["day_of_week"] = df.index.dayofweek
        df["day_of_month"] = df.index.day
        df["month"] = df.index.month
        df["quarter"] = df.index.quarter
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        
        # Features de lag
        for lag in [1, 7, 14, 30]:
            df[f"sales_lag_{lag}"] = df["sales"].shift(lag)
        
        # Moving averages
        for window in [7, 14, 30]:
            df[f"sales_ma_{window}"] = df["sales"].rolling(window=window).mean()
            df[f"sales_std_{window}"] = df["sales"].rolling(window=window).std()
        
        # Trend features
        df["sales_trend_7d"] = df["sales"] - df["sales_ma_7"]
        df["sales_growth_rate"] = df["sales"].pct_change()
        
        # Seasonal features
        df["sales_seasonal_decomp"] = seasonal_decompose(
            df["sales"], model="additive", period=7
        ).seasonal
        
        # Target: vendas futuras
        df["target"] = df["sales"].shift(-horizon)
        
        # Features externas (se disponível)
        if "events" in df.columns:
            # One-hot encoding para eventos
            events_dummies = pd.get_dummies(df["events"], prefix="event")
            df = pd.concat([df, events_dummies], axis=1)
        
        return df.dropna()

    async def hyperparameter_tuning(
        self, model: Any, X_train: pd.DataFrame, y_train: pd.Series, model_name: str
    ) -> Any:
        """Tuning de hiperparâmetros com Grid Search."""
        
        param_grids = {
            "random_forest": {
                "n_estimators": [50, 100, 200],
                "max_depth": [10, 20, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4]
            },
            "gradient_boosting": {
                "n_estimators": [50, 100, 200],
                "learning_rate": [0.01, 0.1, 0.2],
                "max_depth": [3, 5, 7],
                "subsample": [0.8, 0.9, 1.0]
            },
            "xgboost": {
                "n_estimators": [50, 100, 200],
                "learning_rate": [0.01, 0.1, 0.2],
                "max_depth": [3, 5, 7],
                "colsample_bytree": [0.8, 0.9, 1.0]
            }
        }
        
        if model_name in param_grids:
            # Time series split para validação
            tscv = TimeSeriesSplit(n_splits=3)
            
            grid_search = GridSearchCV(
                model,
                param_grids[model_name],
                cv=tscv,
                scoring="roc_auc" if hasattr(model, "predict_proba") else "neg_mean_absolute_error",
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X_train, y_train)
            
            # Log melhores parâmetros
            mlflow.log_params(grid_search.best_params_)
            
            return grid_search.best_estimator_
        
        return model
```

#### 2. Fraud Detection System
```python
# ml/fraud_detection/fraud_detector.py
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.cluster import DBSCAN

class FraudDetectionSystem:
    """Sistema de detecção de fraudes em tempo real."""

    def __init__(self):
        self.anomaly_models = {
            "isolation_forest": IsolationForest(contamination=0.1),
            "one_class_svm": OneClassSVM(nu=0.1),
            "dbscan": DBSCAN(eps=0.5, min_samples=5)
        }
        self.rule_engine = FraudRuleEngine()
        self.feature_extractor = FraudFeatureExtractor()

    async def detect_fraud_real_time(
        self,
        transaction: Dict,
        user_context: Dict
    ) -> Dict:
        """
        Detecta fraude em tempo real para uma transação.

        Args:
            transaction: Dados da transação
            user_context: Contexto do usuário

        Returns:
            Resultado da análise de fraude
        """
        
        fraud_result = {
            "transaction_id": transaction["id"],
            "risk_score": 0.0,
            "fraud_probability": 0.0,
            "risk_level": "low",
            "alerts": [],
            "recommendations": [],
            "analysis_timestamp": datetime.utcnow()
        }

        # 1. Extração de features
        features = await self.feature_extractor.extract_transaction_features(
            transaction, user_context
        )

        # 2. Análise por regras de negócio
        rule_analysis = await self.rule_engine.analyze_transaction(
            transaction, user_context, features
        )
        
        fraud_result["rule_alerts"] = rule_analysis["alerts"]
        fraud_result["risk_score"] += rule_analysis["risk_score"]

        # 3. Detecção de anomalias por ML
        anomaly_analysis = await self.detect_anomalies(features)
        
        fraud_result["anomaly_score"] = anomaly_analysis["anomaly_score"]
        fraud_result["risk_score"] += anomaly_analysis["anomaly_score"]

        # 4. Análise de padrões comportamentais
        behavioral_analysis = await self.analyze_behavioral_patterns(
            transaction, user_context
        )
        
        fraud_result["behavioral_score"] = behavioral_analysis["risk_score"]
        fraud_result["risk_score"] += behavioral_analysis["risk_score"]

        # 5. Análise de rede/relacionamentos
        network_analysis = await self.analyze_network_patterns(
            transaction, user_context
        )
        
        fraud_result["network_score"] = network_analysis["risk_score"]
        fraud_result["risk_score"] += network_analysis["risk_score"]

        # 6. Calcular probabilidade final de fraude
        fraud_result["fraud_probability"] = self.calculate_fraud_probability(
            fraud_result["risk_score"]
        )

        # 7. Determinar nível de risco
        fraud_result["risk_level"] = self.determine_risk_level(
            fraud_result["fraud_probability"]
        )

        # 8. Gerar recomendações
        fraud_result["recommendations"] = self.generate_recommendations(
            fraud_result
        )

        # 9. Salvar análise para auditoria
        await self.save_fraud_analysis(fraud_result)

        return fraud_result

    async def detect_anomalies(self, features: Dict) -> Dict:
        """Detecta anomalias usando múltiplos algoritmos."""
        
        # Converter features para array
        feature_vector = np.array(list(features.values())).reshape(1, -1)
        
        anomaly_scores = []
        
        # Testar cada modelo de anomalia
        for model_name, model in self.anomaly_models.items():
            try:
                if model_name == "dbscan":
                    # DBSCAN precisa de múltiplos pontos, usar apenas para análise histórica
                    score = 0.0
                else:
                    # Isolation Forest e One-Class SVM
                    anomaly_score = model.decision_function(feature_vector)[0]
                    # Normalizar para 0-1
                    normalized_score = max(0, min(1, (1 - anomaly_score) / 2))
                    anomaly_scores.append(normalized_score)
                    
            except Exception as e:
                logger.warning(f"Erro no modelo {model_name}: {e}")
                anomaly_scores.append(0.0)

        # Score médio de anomalia
        avg_anomaly_score = np.mean(anomaly_scores) if anomaly_scores else 0.0

        return {
            "anomaly_score": avg_anomaly_score,
            "individual_scores": dict(zip(self.anomaly_models.keys(), anomaly_scores))
        }

    async def analyze_behavioral_patterns(
        self, transaction: Dict, user_context: Dict
    ) -> Dict:
        """Analisa padrões comportamentais suspeitos."""
        
        risk_score = 0.0
        patterns = []

        user_id = transaction["user_id"]
        transaction_amount = transaction["amount"]
        transaction_time = transaction["timestamp"]

        # Histórico recente do usuário
        recent_transactions = await get_user_recent_transactions(
            user_id, days=30
        )

        # 1. Análise de quantidade
        if recent_transactions:
            avg_amount = np.mean([t["amount"] for t in recent_transactions])
            std_amount = np.std([t["amount"] for t in recent_transactions])
            
            # Transação muito acima da média
            if transaction_amount > avg_amount + 3 * std_amount:
                risk_score += 0.3
                patterns.append("unusual_amount")

        # 2. Análise temporal
        if recent_transactions:
            # Horários usuais do usuário
            usual_hours = [t["timestamp"].hour for t in recent_transactions]
            current_hour = transaction_time.hour
            
            # Transação fora do horário usual
            if usual_hours and current_hour not in usual_hours:
                risk_score += 0.2
                patterns.append("unusual_time")

        # 3. Frequência de transações
        today_transactions = [
            t for t in recent_transactions 
            if t["timestamp"].date() == transaction_time.date()
        ]
        
        if len(today_transactions) > 10:  # Muitas transações em um dia
            risk_score += 0.25
            patterns.append("high_frequency")

        # 4. Localização geográfica (se disponível)
        if "location" in transaction and "usual_locations" in user_context:
            current_location = transaction["location"]
            usual_locations = user_context["usual_locations"]
            
            if current_location not in usual_locations:
                risk_score += 0.4
                patterns.append("unusual_location")

        # 5. Dispositivo/IP
        if "device_fingerprint" in transaction:
            device_fp = transaction["device_fingerprint"]
            known_devices = user_context.get("known_devices", [])
            
            if device_fp not in known_devices:
                risk_score += 0.3
                patterns.append("new_device")

        return {
            "risk_score": min(1.0, risk_score),
            "suspicious_patterns": patterns
        }

    async def analyze_network_patterns(
        self, transaction: Dict, user_context: Dict
    ) -> Dict:
        """Analisa padrões de rede suspeitos."""
        
        risk_score = 0.0
        network_alerts = []

        user_id = transaction["user_id"]
        
        # 1. Análise de IP
        if "ip_address" in transaction:
            ip_address = transaction["ip_address"]
            
            # Verificar se IP está em lista de IPs suspeitos
            if await self.is_suspicious_ip(ip_address):
                risk_score += 0.5
                network_alerts.append("suspicious_ip")
            
            # Verificar geolocalização do IP
            ip_location = await get_ip_geolocation(ip_address)
            if ip_location and ip_location["country"] in ["high_risk_countries"]:
                risk_score += 0.3
                network_alerts.append("high_risk_country")

        # 2. Análise de relacionamentos entre usuários
        connected_users = await find_connected_users(user_id)
        for connected_user in connected_users:
            if await has_recent_fraud_activity(connected_user):
                risk_score += 0.2
                network_alerts.append("connected_to_fraudster")

        # 3. Análise de merchant/destinatário
        if "recipient" in transaction:
            recipient = transaction["recipient"]
            
            if await is_suspicious_recipient(recipient):
                risk_score += 0.4
                network_alerts.append("suspicious_recipient")

        return {
            "risk_score": min(1.0, risk_score),
            "network_alerts": network_alerts
        }

class FraudRuleEngine:
    """Motor de regras de negócio para detecção de fraudes."""

    def __init__(self):
        self.rules = self.load_fraud_rules()

    async def analyze_transaction(
        self, transaction: Dict, user_context: Dict, features: Dict
    ) -> Dict:
        """Aplica regras de negócio para detecção de fraude."""
        
        alerts = []
        risk_score = 0.0

        # Regra 1: Valor muito alto
        if transaction["amount"] > 10000:
            alerts.append("high_value_transaction")
            risk_score += 0.3

        # Regra 2: Múltiplas transações em sequência
        recent_count = await count_recent_transactions(
            transaction["user_id"], minutes=10
        )
        if recent_count > 5:
            alerts.append("rapid_successive_transactions")
            risk_score += 0.4

        # Regra 3: Primeiro uso de método de pagamento
        if await is_first_time_payment_method(
            transaction["user_id"], transaction["payment_method"]
        ):
            alerts.append("new_payment_method")
            risk_score += 0.2

        # Regra 4: Transação fora do horário comercial
        if transaction["timestamp"].hour < 6 or transaction["timestamp"].hour > 23:
            alerts.append("off_hours_transaction")
            risk_score += 0.15

        # Regra 5: Conta recém-criada
        account_age = datetime.utcnow() - user_context["created_at"]
        if account_age.days < 7:
            alerts.append("new_account")
            risk_score += 0.25

        return {
            "alerts": alerts,
            "risk_score": min(1.0, risk_score)
        }
```

#### 3. Lead Scoring System
```python
# ml/lead_scoring/lead_scorer.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class LeadScoringSystem:
    """Sistema de pontuação de leads com ML."""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = {}
        self.load_trained_model()

    async def score_lead(self, lead_data: Dict) -> Dict:
        """
        Calcula score de qualidade do lead.

        Args:
            lead_data: Dados do lead

        Returns:
            Score e insights do lead
        """
        
        # Extrair features
        features = await self.extract_lead_features(lead_data)
        
        # Preparar dados para predição
        feature_vector = self.prepare_features_for_prediction(features)
        
        # Calcular score usando modelo ML
        ml_score = self.model.predict_proba(feature_vector)[0][1]
        
        # Calcular score usando regras de negócio
        rule_score = await self.calculate_rule_based_score(lead_data, features)
        
        # Combinar scores
        final_score = (ml_score * 0.7 + rule_score * 0.3)
        
        # Determinar categoria
        lead_category = self.categorize_lead(final_score)
        
        # Gerar insights
        insights = await self.generate_lead_insights(
            lead_data, features, final_score
        )
        
        return {
            "lead_id": lead_data["id"],
            "score": final_score,
            "ml_score": ml_score,
            "rule_score": rule_score,
            "category": lead_category,
            "confidence": self.calculate_confidence(final_score),
            "insights": insights,
            "next_best_action": self.recommend_next_action(final_score, features),
            "estimated_conversion_time": self.estimate_conversion_time(features),
            "estimated_deal_value": self.estimate_deal_value(features)
        }

    async def extract_lead_features(self, lead_data: Dict) -> Dict:
        """Extrai features relevantes do lead."""
        
        features = {}
        
        # Features demográficas
        features["company_size"] = lead_data.get("company_size", 0)
        features["industry_score"] = await self.get_industry_score(
            lead_data.get("industry", "")
        )
        features["job_title_score"] = self.get_job_title_score(
            lead_data.get("job_title", "")
        )
        
        # Features geográficas
        features["location_score"] = await self.get_location_score(
            lead_data.get("country", ""), 
            lead_data.get("city", "")
        )
        
        # Features comportamentais
        if "email" in lead_data:
            email_domain = lead_data["email"].split("@")[1]
            features["email_domain_score"] = await self.get_email_domain_score(email_domain)
        
        # Features de origem
        features["source_score"] = self.get_source_score(lead_data.get("source", ""))
        features["campaign_score"] = await self.get_campaign_score(
            lead_data.get("campaign_id", "")
        )
        
        # Features temporais
        features["hour_of_day"] = datetime.now().hour
        features["day_of_week"] = datetime.now().weekday()
        features["is_business_hours"] = self.is_business_hours()
        
        # Features de engagement (se disponível)
        if "website_visits" in lead_data:
            features["website_engagement"] = self.calculate_website_engagement(
                lead_data["website_visits"]
            )
        
        # Features de completude dos dados
        features["data_completeness"] = self.calculate_data_completeness(lead_data)
        
        return features

    async def calculate_rule_based_score(
        self, lead_data: Dict, features: Dict
    ) -> float:
        """Calcula score baseado em regras de negócio."""
        
        score = 0.0
        
        # Pontuação por tamanho da empresa
        company_size = features.get("company_size", 0)
        if company_size > 1000:
            score += 0.3
        elif company_size > 100:
            score += 0.2
        elif company_size > 10:
            score += 0.1
        
        # Pontuação por cargo
        job_title_score = features.get("job_title_score", 0)
        score += job_title_score * 0.2
        
        # Pontuação por indústria
        industry_score = features.get("industry_score", 0)
        score += industry_score * 0.15
        
        # Pontuação por origem
        source_score = features.get("source_score", 0)
        score += source_score * 0.1
        
        # Pontuação por completude dos dados
        data_completeness = features.get("data_completeness", 0)
        score += data_completeness * 0.1
        
        # Pontuação por horário (leads em horário comercial pontuam mais)
        if features.get("is_business_hours", False):
            score += 0.05
        
        # Pontuação por engagement no website
        website_engagement = features.get("website_engagement", 0)
        score += website_engagement * 0.1
        
        return min(1.0, score)

    def categorize_lead(self, score: float) -> str:
        """Categoriza lead baseado no score."""
        
        if score >= 0.8:
            return "hot"
        elif score >= 0.6:
            return "warm"
        elif score >= 0.4:
            return "cold"
        else:
            return "unqualified"

    async def generate_lead_insights(
        self, lead_data: Dict, features: Dict, score: float
    ) -> List[Dict]:
        """Gera insights sobre o lead."""
        
        insights = []
        
        # Insight sobre score
        if score >= 0.8:
            insights.append({
                "type": "high_priority",
                "message": "Lead de alta prioridade - contato imediato recomendado",
                "confidence": "high"
            })
        elif score < 0.3:
            insights.append({
                "type": "low_priority",
                "message": "Lead de baixa qualidade - nurturing recomendado",
                "confidence": "high"
            })
        
        # Insight sobre empresa
        company_size = features.get("company_size", 0)
        if company_size > 1000:
            insights.append({
                "type": "company_size",
                "message": "Empresa de grande porte - potencial de alto valor",
                "confidence": "medium"
            })
        
        # Insight sobre cargo
        job_title_score = features.get("job_title_score", 0)
        if job_title_score > 0.8:
            insights.append({
                "type": "decision_maker",
                "message": "Provável tomador de decisão - abordagem direta",
                "confidence": "high"
            })
        
        # Insight sobre timing
        if features.get("is_business_hours", False):
            insights.append({
                "type": "timing",
                "message": "Lead gerado em horário comercial - maior probabilidade de conversão",
                "confidence": "medium"
            })
        
        # Insight sobre engagement
        website_engagement = features.get("website_engagement", 0)
        if website_engagement > 0.7:
            insights.append({
                "type": "engagement",
                "message": "Alto engagement no website - interesse demonstrado",
                "confidence": "high"
            })
        
        return insights

    def recommend_next_action(self, score: float, features: Dict) -> str:
        """Recomenda próxima ação baseada no score."""
        
        if score >= 0.8:
            return "immediate_call"
        elif score >= 0.6:
            return "priority_email"
        elif score >= 0.4:
            return "nurturing_campaign"
        else:
            return "qualification_needed"

    def estimate_conversion_time(self, features: Dict) -> int:
        """Estima tempo para conversão em dias."""
        
        base_time = 30  # dias base
        
        # Ajustar por tamanho da empresa
        company_size = features.get("company_size", 0)
        if company_size > 1000:
            base_time += 45  # Empresas grandes demoram mais
        elif company_size < 10:
            base_time -= 10  # Empresas pequenas são mais rápidas
        
        # Ajustar por cargo
        job_title_score = features.get("job_title_score", 0)
        if job_title_score > 0.8:
            base_time -= 15  # Tomadores de decisão são mais rápidos
        
        # Ajustar por engagement
        website_engagement = features.get("website_engagement", 0)
        if website_engagement > 0.7:
            base_time -= 10  # Alto engagement acelera conversão
        
        return max(1, base_time)

    def estimate_deal_value(self, features: Dict) -> float:
        """Estima valor potencial do deal."""
        
        base_value = 5000.0  # Valor base
        
        # Ajustar por tamanho da empresa
        company_size = features.get("company_size", 0)
        if company_size > 1000:
            base_value *= 10
        elif company_size > 100:
            base_value *= 3
        elif company_size > 10:
            base_value *= 1.5
        
        # Ajustar por indústria
        industry_score = features.get("industry_score", 0.5)
        base_value *= (1 + industry_score)
        
        return base_value
```

## 🗃️ ESTRUTURAS DE DADOS

### 1. Prediction Models
```python
# models/analytics/predictions.py
class PredictionModel(Base):
    """Modelo de predições."""
    __tablename__ = "prediction_models"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(200), nullable=False, unique=True)
    model_type = Column(String(50), nullable=False)  # classification, regression, clustering
    version = Column(String(20), nullable=False)
    
    # Configuração do modelo
    algorithm = Column(String(100), nullable=False)
    hyperparameters = Column(JSON)
    features = Column(JSON)  # Lista de features utilizadas
    target_variable = Column(String(100))
    
    # Métricas de performance
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_roc = Column(Float)
    mae = Column(Float)  # Para regressão
    rmse = Column(Float)  # Para regressão
    
    # Dados de treinamento
    training_start_date = Column(DateTime)
    training_end_date = Column(DateTime)
    training_samples = Column(Integer)
    validation_samples = Column(Integer)
    
    # Status e metadados
    status = Column(String(20), default="training")  # training, active, deprecated
    model_file_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_retrained = Column(DateTime)
    next_retrain_date = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relacionamentos
    creator = relationship("User")
    predictions = relationship("Prediction", back_populates="model")

class Prediction(Base):
    """Predições individuais."""
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    model_id = Column(String, ForeignKey("prediction_models.id"), nullable=False)
    entity_type = Column(String(50), nullable=False)  # user, transaction, lead, etc.
    entity_id = Column(String, nullable=False)
    
    # Resultado da predição
    prediction_value = Column(Float)
    prediction_class = Column(String(100))
    confidence_score = Column(Float)
    probability_scores = Column(JSON)  # Para classificação multi-classe
    
    # Features utilizadas
    input_features = Column(JSON)
    feature_importance = Column(JSON)
    
    # Metadados
    prediction_date = Column(DateTime, default=datetime.utcnow)
    actual_outcome = Column(Float)  # Para calcular accuracy posterior
    outcome_date = Column(DateTime)
    is_correct = Column(Boolean)
    
    # Contexto
    context_data = Column(JSON)
    batch_id = Column(String)  # Para predições em lote

    # Relacionamentos
    model = relationship("PredictionModel", back_populates="predictions")

class FraudAnalysis(Base):
    """Análises de fraude."""
    __tablename__ = "fraud_analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    transaction_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Scores de risco
    overall_risk_score = Column(Float, nullable=False)
    fraud_probability = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Componentes do score
    rule_based_score = Column(Float)
    ml_anomaly_score = Column(Float)
    behavioral_score = Column(Float)
    network_score = Column(Float)
    
    # Alertas e padrões
    triggered_rules = Column(JSON)  # Regras que dispararam
    suspicious_patterns = Column(JSON)
    anomaly_indicators = Column(JSON)
    
    # Ações tomadas
    action_taken = Column(String(50))  # approved, rejected, manual_review, escalated
    auto_decision = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    review_notes = Column(Text)
    
    # Features utilizadas
    analysis_features = Column(JSON)
    transaction_context = Column(JSON)
    
    # Resultado final
    is_fraud = Column(Boolean)  # Resultado confirmado
    false_positive = Column(Boolean)
    feedback_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LeadScore(Base):
    """Scores de leads."""
    __tablename__ = "lead_scores"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False, unique=True)
    
    # Scores
    overall_score = Column(Float, nullable=False)
    ml_score = Column(Float)
    rule_based_score = Column(Float)
    confidence = Column(Float)
    
    # Categorização
    category = Column(String(20), nullable=False)  # hot, warm, cold, unqualified
    priority_level = Column(Integer, default=0)  # 1-10
    
    # Estimativas
    estimated_conversion_probability = Column(Float)
    estimated_deal_value = Column(Float)
    estimated_conversion_days = Column(Integer)
    
    # Features e insights
    scoring_features = Column(JSON)
    insights = Column(JSON)
    recommendations = Column(JSON)
    
    # Resultado real
    converted = Column(Boolean)
    conversion_date = Column(DateTime)
    actual_deal_value = Column(Float)
    days_to_conversion = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    lead = relationship("Lead")
```

### 2. Analytics Dashboards
```python
# models/analytics/dashboards.py
class AnalyticsDashboard(Base):
    """Dashboards de analytics."""
    __tablename__ = "analytics_dashboards"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    dashboard_type = Column(String(50), nullable=False)  # predictive, descriptive, prescriptive
    
    # Configuração
    widgets = Column(JSON)  # Configuração dos widgets
    filters = Column(JSON)  # Filtros padrão
    refresh_interval = Column(Integer, default=300)  # segundos
    
    # Permissões
    is_public = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_with = Column(JSON)  # Lista de usuários/grupos
    
    # Metadados
    usage_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    creator = relationship("User")

class AnalyticsAlert(Base):
    """Alertas de analytics."""
    __tablename__ = "analytics_alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Condição do alerta
    metric_name = Column(String(100), nullable=False)
    threshold_type = Column(String(20), nullable=False)  # above, below, equals, change
    threshold_value = Column(Float, nullable=False)
    comparison_period = Column(String(20))  # for change alerts: 1d, 1w, 1m
    
    # Configuração
    is_active = Column(Boolean, default=True)
    check_frequency = Column(String(20), default="hourly")  # hourly, daily, weekly
    notification_channels = Column(JSON)  # email, slack, webhook
    
    # Status
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    last_checked = Column(DateTime)
    current_value = Column(Float)
    
    # Metadados
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    creator = relationship("User")
```

## 🚀 IMPLEMENTAÇÃO

### Fase 1: Infraestrutura ML (Sprint 1-2)
1. **ML Pipeline Setup**
   - Feature store
   - Model registry
   - Training pipeline
   - Data validation

2. **Core Models**
   - Churn prediction
   - Sales forecasting
   - Basic fraud detection
   - Lead scoring

### Fase 2: Advanced Analytics (Sprint 3-4)
1. **Fraud Detection**
   - Real-time detection
   - Rule engine
   - Network analysis
   - Behavioral patterns

2. **Predictive Models**
   - Demand forecasting
   - Price optimization
   - Inventory planning
   - Risk assessment

### Fase 3: Real-time Analytics (Sprint 5)
1. **Streaming Analytics**
   - Real-time processing
   - Stream processing (Kafka/Spark)
   - Live dashboards
   - Alert system

2. **AutoML Platform**
   - Automated model selection
   - Hyperparameter tuning
   - Model monitoring
   - Performance tracking

### Fase 4: Business Intelligence (Sprint 6)
1. **Advanced Dashboards**
   - Interactive visualizations
   - Custom reports
   - Executive dashboards
   - Mobile analytics

2. **AI-Powered Insights**
   - Natural language insights
   - Anomaly detection
   - Trend analysis
   - Recommendation engine

## 📊 MÉTRICAS E MONITORAMENTO

### Model Performance Monitoring
```python
# monitoring/ml_monitoring.py
class MLModelMonitoring:
    """Monitoramento de performance de modelos ML."""

    def __init__(self):
        self.metrics_tracker = MetricsTracker()
        self.drift_detector = DataDriftDetector()

    async def monitor_model_performance(self, model_name: str) -> Dict:
        """Monitora performance de modelo em produção."""
        
        # Buscar predições recentes
        recent_predictions = await get_recent_predictions(model_name, days=7)
        
        # Calcular métricas de performance
        performance_metrics = await self.calculate_performance_metrics(
            recent_predictions
        )
        
        # Detectar data drift
        drift_analysis = await self.drift_detector.analyze_drift(
            model_name, recent_predictions
        )
        
        # Verificar model decay
        decay_analysis = await self.analyze_model_decay(
            model_name, recent_predictions
        )
        
        # Gerar alertas se necessário
        alerts = self.generate_performance_alerts(
            performance_metrics, drift_analysis, decay_analysis
        )
        
        return {
            "model_name": model_name,
            "performance": performance_metrics,
            "drift_analysis": drift_analysis,
            "decay_analysis": decay_analysis,
            "alerts": alerts,
            "recommendation": self.get_maintenance_recommendation(
                performance_metrics, drift_analysis
            )
        }

    async def calculate_performance_metrics(
        self, predictions: List[Dict]
    ) -> Dict:
        """Calcula métricas de performance do modelo."""
        
        # Filtrar predições com outcome conhecido
        validated_predictions = [
            p for p in predictions 
            if p["actual_outcome"] is not None
        ]
        
        if not validated_predictions:
            return {"status": "insufficient_data"}

        # Calcular métricas baseado no tipo de modelo
        model_type = validated_predictions[0]["model_type"]
        
        if model_type == "classification":
            return self.calculate_classification_metrics(validated_predictions)
        elif model_type == "regression":
            return self.calculate_regression_metrics(validated_predictions)
        else:
            return {"status": "unsupported_model_type"}

    def calculate_classification_metrics(self, predictions: List[Dict]) -> Dict:
        """Calcula métricas para modelos de classificação."""
        
        y_true = [p["actual_outcome"] for p in predictions]
        y_pred = [p["prediction_class"] for p in predictions]
        y_proba = [p["confidence_score"] for p in predictions]
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average="weighted"),
            "recall": recall_score(y_true, y_pred, average="weighted"),
            "f1_score": f1_score(y_true, y_pred, average="weighted"),
            "auc_roc": roc_auc_score(y_true, y_proba),
            "sample_size": len(predictions)
        }

    def calculate_regression_metrics(self, predictions: List[Dict]) -> Dict:
        """Calcula métricas para modelos de regressão."""
        
        y_true = [p["actual_outcome"] for p in predictions]
        y_pred = [p["prediction_value"] for p in predictions]
        
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        
        return {
            "mae": mean_absolute_error(y_true, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
            "r2_score": r2_score(y_true, y_pred),
            "mape": np.mean(np.abs((y_true - y_pred) / y_true)) * 100,
            "sample_size": len(predictions)
        }
```

### Business KPIs
- **Model Accuracy:** Churn > 85%, Fraud > 95%, Lead Scoring > 80%
- **Performance:** Prediction latency < 100ms, Batch processing < 1h
- **Business Impact:** 20% reduction in churn, 40% improvement in lead conversion
- **ROI:** 300% return on investment in 12 months

## 🔒 PRIVACY E COMPLIANCE

### Data Privacy & LGPD Compliance
```python
# privacy/ml_privacy.py
class MLPrivacyManager:
    """Gerencia privacidade em ML."""

    def __init__(self):
        self.anonymizer = DataAnonymizer()
        self.consent_manager = ConsentManager()

    async def ensure_ml_privacy_compliance(
        self, dataset: pd.DataFrame, purpose: str
    ) -> pd.DataFrame:
        """Garante compliance de privacidade em datasets ML."""
        
        # 1. Verificar consentimento para uso em ML
        consented_users = await self.get_consented_users(purpose)
        dataset = dataset[dataset["user_id"].isin(consented_users)]
        
        # 2. Anonimizar dados sensíveis
        dataset = await self.anonymizer.anonymize_for_ml(dataset)
        
        # 3. Aplicar differential privacy se necessário
        if purpose == "research":
            dataset = self.apply_differential_privacy(dataset)
        
        # 4. Remover identificadores diretos
        dataset = self.remove_direct_identifiers(dataset)
        
        return dataset

    async def get_consented_users(self, purpose: str) -> List[int]:
        """Obtém lista de usuários que consentiram para uso em ML."""
        
        consent_type = f"ml_analytics_{purpose}"
        consented_users = await self.consent_manager.get_consented_users(
            consent_type
        )
        
        return consented_users

    def apply_differential_privacy(self, dataset: pd.DataFrame) -> pd.DataFrame:
        """Aplica differential privacy ao dataset."""
        
        # Implementar técnicas de differential privacy
        # para proteger privacidade individual
        
        epsilon = 0.1  # Privacy budget
        
        # Adicionar ruído laplaciano a features numéricas
        numeric_columns = dataset.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            sensitivity = dataset[col].max() - dataset[col].min()
            noise = np.random.laplace(0, sensitivity / epsilon, len(dataset))
            dataset[col] += noise
        
        return dataset
```

## 📋 CHECKLIST DE ENTREGA

### ✅ ML Infrastructure
- [ ] Feature Store implementado
- [ ] Model Registry configurado
- [ ] Training Pipeline automatizado
- [ ] Data Validation framework
- [ ] Model Versioning
- [ ] A/B Testing para modelos
- [ ] Performance Monitoring
- [ ] Model Serving API
- [ ] Batch Prediction Pipeline

### ✅ Predictive Models
- [ ] Customer Churn Prediction (>85% accuracy)
- [ ] Sales Forecasting (>80% accuracy)  
- [ ] Lead Scoring (>80% accuracy)
- [ ] Fraud Detection (>95% accuracy)
- [ ] Demand Forecasting
- [ ] Price Optimization
- [ ] Inventory Optimization
- [ ] Risk Assessment Models

### ✅ Real-time Analytics
- [ ] Streaming Data Pipeline (Kafka/Spark)
- [ ] Real-time Dashboards
- [ ] Alert System
- [ ] Anomaly Detection
- [ ] Live Model Serving
- [ ] Event-driven Predictions
- [ ] Performance Monitoring
- [ ] Auto-scaling Infrastructure

### ✅ Business Intelligence
- [ ] Executive Dashboards
- [ ] Custom Report Builder
- [ ] Mobile Analytics
- [ ] Natural Language Insights
- [ ] Automated Report Generation
- [ ] Data Export Tools
- [ ] Visualization Library
- [ ] Drill-down Capabilities

## 🎯 CRITÉRIOS DE SUCESSO

### Technical Performance
- Model accuracy > 85% for all models
- Prediction latency < 100ms
- System uptime > 99.9%
- Data pipeline SLA > 99%

### Business Impact
- 20% reduction in customer churn
- 40% improvement in lead conversion
- 30% increase in sales forecast accuracy
- 60% reduction in fraud losses

### User Adoption
- 90% of managers using dashboards
- 80% of sales team using lead scores
- 95% of transactions processed by fraud detection
- 50+ custom reports created

### ROI Metrics
- 300% ROI in 12 months
- k+ annual savings from churn reduction
- k+ additional revenue from lead optimization
- M+ prevented fraud losses

---

**📅 Duração Estimada:** 6 sprints (12 semanas)
**👥 Equipe Necessária:** 3 data scientists + 2 ML engineers + 2 backend developers + 1 DevOps
**💰 Investimento:** R$ 300.000 - R$ 400.000
**🚀 Impacto Esperado:** Plataforma de analytics preditivo de classe mundial com IA avançada e insights acionáveis para tomada de decisão estratégica
