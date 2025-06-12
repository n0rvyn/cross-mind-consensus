"""
Data Science Module for Cross-Mind Consensus System
Advanced analytics, model evaluation, and statistical analysis
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any, Tuple
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.append('..')
from analytics_manager import analytics_manager

class ConsensusDataScientist:
    """Advanced data science analysis for consensus patterns"""
    
    def __init__(self):
        self.analytics_manager = analytics_manager
        
    def get_consensus_distribution_analysis(self) -> Dict[str, Any]:
        """Analyze the distribution of consensus scores"""
        queries = self.analytics_manager.get_query_analytics(limit=1000)
        
        if not queries:
            return {"error": "No data available"}
        
        scores = [q.consensus_score for q in queries if q.success]
        
        if not scores:
            return {"error": "No successful queries found"}
        
        # Statistical analysis
        analysis = {
            "descriptive_stats": {
                "mean": np.mean(scores),
                "median": np.median(scores),
                "std": np.std(scores),
                "min": np.min(scores),
                "max": np.max(scores),
                "q25": np.percentile(scores, 25),
                "q75": np.percentile(scores, 75),
                "iqr": np.percentile(scores, 75) - np.percentile(scores, 25)
            },
            "distribution_tests": {
                "shapiro_wilk_p": stats.shapiro(scores)[1],
                "jarque_bera_p": stats.jarque_bera(scores)[1],
                "is_normal": stats.shapiro(scores)[1] > 0.05
            },
            "outlier_analysis": self._detect_outliers(scores),
            "sample_size": len(scores)
        }
        
        return analysis
    
    def _detect_outliers(self, data: List[float]) -> Dict[str, Any]:
        """Detect outliers using multiple methods"""
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        # IQR method
        iqr_lower = q1 - 1.5 * iqr
        iqr_upper = q3 + 1.5 * iqr
        iqr_outliers = [x for x in data if x < iqr_lower or x > iqr_upper]
        
        # Z-score method
        z_scores = np.abs(stats.zscore(data))
        zscore_outliers = [data[i] for i, z in enumerate(z_scores) if z > 3]
        
        return {
            "iqr_outliers": len(iqr_outliers),
            "zscore_outliers": len(zscore_outliers),
            "outlier_percentage": (len(iqr_outliers) / len(data)) * 100,
            "outlier_threshold_iqr": {"lower": iqr_lower, "upper": iqr_upper}
        }
    
    def model_performance_clustering(self) -> Dict[str, Any]:
        """Cluster models based on performance characteristics"""
        performances = self.analytics_manager.get_model_performance()
        
        if len(performances) < 3:
            return {"error": "Need at least 3 models for clustering"}
        
        # Prepare feature matrix
        features = []
        model_names = []
        
        for perf in performances:
            features.append([
                perf.avg_response_time,
                perf.avg_consensus_score,
                perf.success_rate,
                perf.total_queries
            ])
            model_names.append(perf.model_id)
        
        features = np.array(features)
        
        # Normalize features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Optimal number of clusters
        silhouette_scores = []
        k_range = range(2, min(len(performances), 6))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            cluster_labels = kmeans.fit_predict(features_scaled)
            silhouette_avg = silhouette_score(features_scaled, cluster_labels)
            silhouette_scores.append(silhouette_avg)
        
        optimal_k = k_range[np.argmax(silhouette_scores)]
        
        # Final clustering
        kmeans = KMeans(n_clusters=optimal_k, random_state=42)
        cluster_labels = kmeans.fit_predict(features_scaled)
        
        # PCA for visualization
        pca = PCA(n_components=2)
        features_pca = pca.fit_transform(features_scaled)
        
        return {
            "optimal_clusters": optimal_k,
            "silhouette_score": max(silhouette_scores),
            "cluster_assignments": dict(zip(model_names, cluster_labels.tolist())),
            "pca_explained_variance": pca.explained_variance_ratio_.tolist(),
            "cluster_centers": kmeans.cluster_centers_.tolist(),
            "feature_names": ["response_time", "consensus_score", "success_rate", "total_queries"],
            "pca_coordinates": {
                "models": model_names,
                "x": features_pca[:, 0].tolist(),
                "y": features_pca[:, 1].tolist(),
                "clusters": cluster_labels.tolist()
            }
        }
    
    def consensus_time_series_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Advanced time series analysis of consensus patterns"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        queries = self.analytics_manager.get_query_analytics(
            start_date=start_date, 
            end_date=end_date, 
            limit=10000
        )
        
        if not queries:
            return {"error": "No data in specified time range"}
        
        # Create time series dataframe
        df = pd.DataFrame([
            {
                "timestamp": q.timestamp,
                "consensus_score": q.consensus_score,
                "response_time": q.response_time,
                "method": q.method,
                "success": q.success,
                "model_count": len(q.model_ids)
            }
            for q in queries if q.success
        ])
        
        if df.empty:
            return {"error": "No successful queries in time range"}
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Resample to hourly data
        hourly_stats = df.resample('H').agg({
            'consensus_score': ['mean', 'std', 'count'],
            'response_time': ['mean', 'std'],
            'model_count': 'mean'
        }).fillna(0)
        
        # Trend analysis
        from scipy.stats import linregress
        
        hourly_scores = hourly_stats[('consensus_score', 'mean')].dropna()
        if len(hourly_scores) > 1:
            time_numeric = np.arange(len(hourly_scores))
            slope, intercept, r_value, p_value, std_err = linregress(time_numeric, hourly_scores)
            
            trend_analysis = {
                "slope": slope,
                "r_squared": r_value**2,
                "p_value": p_value,
                "trend_direction": "improving" if slope > 0 else "declining" if slope < 0 else "stable",
                "trend_significance": "significant" if p_value < 0.05 else "not_significant"
            }
        else:
            trend_analysis = {"error": "Insufficient data for trend analysis"}
        
        # Seasonality detection (if enough data)
        seasonality_analysis = {}
        if len(hourly_scores) >= 48:  # At least 2 days of hourly data
            # Simple hour-of-day analysis
            df['hour'] = df.index.hour
            hourly_patterns = df.groupby('hour')['consensus_score'].agg(['mean', 'std', 'count'])
            
            seasonality_analysis = {
                "hourly_patterns": hourly_patterns.to_dict(),
                "peak_performance_hour": hourly_patterns['mean'].idxmax(),
                "lowest_performance_hour": hourly_patterns['mean'].idxmin(),
                "hourly_variance": hourly_patterns['mean'].var()
            }
        
        return {
            "time_series_stats": {
                "total_queries": len(df),
                "date_range": {
                    "start": df.index.min().isoformat(),
                    "end": df.index.max().isoformat()
                },
                "hourly_query_rate": len(df) / ((df.index.max() - df.index.min()).total_seconds() / 3600)
            },
            "trend_analysis": trend_analysis,
            "seasonality_analysis": seasonality_analysis,
            "summary_statistics": {
                "avg_consensus_score": df['consensus_score'].mean(),
                "consensus_volatility": df['consensus_score'].std(),
                "avg_response_time": df['response_time'].mean(),
                "response_time_volatility": df['response_time'].std()
            }
        }
    
    def model_consensus_correlation_matrix(self) -> Dict[str, Any]:
        """Analyze correlations between different model pairs in consensus"""
        queries = self.analytics_manager.get_query_analytics(limit=1000)
        
        # Extract individual model scores
        model_scores = {}
        
        for query in queries:
            if query.success and query.individual_scores:
                for model_id, score in query.individual_scores.items():
                    if model_id not in model_scores:
                        model_scores[model_id] = []
                    model_scores[model_id].append(score)
        
        if len(model_scores) < 2:
            return {"error": "Need at least 2 models with individual scores"}
        
        # Create correlation matrix
        models = list(model_scores.keys())
        correlation_matrix = []
        
        for i, model1 in enumerate(models):
            row = []
            for j, model2 in enumerate(models):
                if i == j:
                    corr = 1.0
                else:
                    # Find common queries
                    min_len = min(len(model_scores[model1]), len(model_scores[model2]))
                    if min_len > 1:
                        corr = np.corrcoef(
                            model_scores[model1][:min_len],
                            model_scores[model2][:min_len]
                        )[0, 1]
                        if np.isnan(corr):
                            corr = 0.0
                    else:
                        corr = 0.0
                row.append(corr)
            correlation_matrix.append(row)
        
        return {
            "models": models,
            "correlation_matrix": correlation_matrix,
            "strongest_correlation": {
                "models": self._find_strongest_correlation(models, correlation_matrix),
                "value": self._get_max_correlation(correlation_matrix)
            },
            "model_sample_sizes": {model: len(scores) for model, scores in model_scores.items()}
        }
    
    def _find_strongest_correlation(self, models: List[str], matrix: List[List[float]]) -> Tuple[str, str]:
        """Find the pair with strongest correlation (excluding self-correlation)"""
        max_corr = -1
        best_pair = ("", "")
        
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                if abs(matrix[i][j]) > max_corr:
                    max_corr = abs(matrix[i][j])
                    best_pair = (models[i], models[j])
        
        return best_pair
    
    def _get_max_correlation(self, matrix: List[List[float]]) -> float:
        """Get maximum correlation value (excluding self-correlation)"""
        max_corr = -1
        
        for i in range(len(matrix)):
            for j in range(i + 1, len(matrix)):
                if abs(matrix[i][j]) > max_corr:
                    max_corr = abs(matrix[i][j])
        
        return max_corr
    
    def generate_consensus_quality_score(self) -> Dict[str, Any]:
        """Generate an overall consensus quality score for the system"""
        queries = self.analytics_manager.get_query_analytics(limit=1000)
        
        if not queries:
            return {"error": "No data available"}
        
        successful_queries = [q for q in queries if q.success]
        
        if not successful_queries:
            return {"error": "No successful queries"}
        
        # Calculate various quality metrics
        consensus_scores = [q.consensus_score for q in successful_queries]
        response_times = [q.response_time for q in successful_queries]
        
        # Quality components
        avg_consensus = np.mean(consensus_scores)
        consensus_consistency = 1 - np.std(consensus_scores)  # Higher consistency = lower std
        speed_score = max(0, 1 - (np.mean(response_times) / 30))  # Normalized to 30s max
        reliability_score = len(successful_queries) / len(queries)
        
        # Weights for different aspects
        weights = {
            "consensus_quality": 0.4,
            "consistency": 0.25,
            "speed": 0.2,
            "reliability": 0.15
        }
        
        # Calculate overall score
        overall_score = (
            avg_consensus * weights["consensus_quality"] +
            consensus_consistency * weights["consistency"] +
            speed_score * weights["speed"] +
            reliability_score * weights["reliability"]
        )
        
        return {
            "overall_quality_score": round(overall_score, 3),
            "components": {
                "consensus_quality": round(avg_consensus, 3),
                "consistency_score": round(consensus_consistency, 3),
                "speed_score": round(speed_score, 3),
                "reliability_score": round(reliability_score, 3)
            },
            "weights": weights,
            "recommendations": self._generate_quality_recommendations(
                avg_consensus, consensus_consistency, speed_score, reliability_score
            ),
            "sample_size": len(successful_queries),
            "data_quality": "good" if len(successful_queries) > 100 else "limited"
        }
    
    def _generate_quality_recommendations(self, consensus: float, consistency: float, 
                                        speed: float, reliability: float) -> List[str]:
        """Generate actionable recommendations based on quality metrics"""
        recommendations = []
        
        if consensus < 0.8:
            recommendations.append("Consider fine-tuning model prompts to improve consensus quality")
        
        if consistency < 0.7:
            recommendations.append("High variability detected - review model selection strategy")
        
        if speed < 0.6:
            recommendations.append("Response times are high - consider caching optimization")
        
        if reliability < 0.9:
            recommendations.append("Error rate is concerning - review error handling and model stability")
        
        if not recommendations:
            recommendations.append("System performing well across all quality metrics")
        
        return recommendations

# Global data scientist instance
consensus_data_scientist = ConsensusDataScientist() 