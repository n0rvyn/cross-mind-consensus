"""
Analytics Manager for Cross-Mind Consensus System
Tracks model performance, response times, and consensus patterns
"""

import json
import logging
import sqlite3
import sys
import threading
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

sys.path.append("..")
from config import settings

logger = logging.getLogger(__name__)


@dataclass
class QueryAnalytics:
    """Analytics data for a single query"""

    query_id: str
    timestamp: datetime
    question: str
    model_ids: List[str]
    roles: List[str]
    method: str
    consensus_score: float
    response_time: float
    success: bool
    error_message: Optional[str] = None
    individual_scores: Optional[Dict[str, float]] = None
    chain_rounds: Optional[int] = None


@dataclass
class ModelPerformance:
    """Performance metrics for a model"""

    model_id: str
    total_queries: int
    avg_response_time: float
    avg_consensus_score: float
    success_rate: float
    error_count: int
    last_used: datetime


class AnalyticsManager:
    """Manages performance analytics and model statistics"""

    def __init__(self):
        self.db_path = f"{settings.log_directory}/analytics.db"
        self.lock = threading.Lock()
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS query_analytics (
                        query_id TEXT PRIMARY KEY,
                        timestamp TEXT,
                        question TEXT,
                        model_ids TEXT,
                        roles TEXT,
                        method TEXT,
                        consensus_score REAL,
                        response_time REAL,
                        success INTEGER,
                        error_message TEXT,
                        individual_scores TEXT,
                        chain_rounds INTEGER
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS model_performance (
                        model_id TEXT PRIMARY KEY,
                        total_queries INTEGER,
                        avg_response_time REAL,
                        avg_consensus_score REAL,
                        success_rate REAL,
                        error_count INTEGER,
                        last_used TEXT
                    )
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON query_analytics(timestamp)
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_model_ids ON query_analytics(model_ids)
                """
                )

                logger.info("Analytics database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize analytics database: {e}")

    def record_query(self, analytics: QueryAnalytics):
        """Record query analytics"""
        if not settings.enable_analytics:
            return

        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO query_analytics 
                        (query_id, timestamp, question, model_ids, roles, method, 
                         consensus_score, response_time, success, error_message, 
                         individual_scores, chain_rounds)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            analytics.query_id,
                            analytics.timestamp.isoformat(),
                            analytics.question,
                            json.dumps(analytics.model_ids),
                            json.dumps(analytics.roles),
                            analytics.method,
                            analytics.consensus_score,
                            analytics.response_time,
                            1 if analytics.success else 0,
                            analytics.error_message,
                            (
                                json.dumps(analytics.individual_scores)
                                if analytics.individual_scores
                                else None
                            ),
                            analytics.chain_rounds,
                        ),
                    )

                # Update model performance
                self._update_model_performance(analytics)

        except Exception as e:
            logger.error(f"Failed to record query analytics: {e}")

    def _update_model_performance(self, analytics: QueryAnalytics):
        """Update model performance metrics"""
        for model_id in analytics.model_ids:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Get current stats
                    cursor = conn.execute(
                        """
                        SELECT total_queries, avg_response_time, avg_consensus_score, 
                               success_rate, error_count 
                        FROM model_performance 
                        WHERE model_id = ?
                    """,
                        (model_id,),
                    )

                    row = cursor.fetchone()

                    if row:
                        (
                            total_queries,
                            avg_response_time,
                            avg_consensus_score,
                            success_rate,
                            error_count,
                        ) = row

                        # Update running averages
                        new_total = total_queries + 1
                        new_avg_time = (
                            (avg_response_time * total_queries)
                            + analytics.response_time
                        ) / new_total
                        new_avg_consensus = (
                            (avg_consensus_score * total_queries)
                            + analytics.consensus_score
                        ) / new_total

                        if not analytics.success:
                            error_count += 1

                        new_success_rate = ((new_total - error_count) / new_total) * 100

                    else:
                        # First record for this model
                        new_total = 1
                        new_avg_time = analytics.response_time
                        new_avg_consensus = analytics.consensus_score
                        error_count = 0 if analytics.success else 1
                        new_success_rate = 100.0 if analytics.success else 0.0

                    # Update or insert
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO model_performance 
                        (model_id, total_queries, avg_response_time, avg_consensus_score, 
                         success_rate, error_count, last_used)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            model_id,
                            new_total,
                            new_avg_time,
                            new_avg_consensus,
                            new_success_rate,
                            error_count,
                            analytics.timestamp.isoformat(),
                        ),
                    )

            except Exception as e:
                logger.error(f"Failed to update model performance for {model_id}: {e}")

    def get_model_performance(
        self, model_id: Optional[str] = None
    ) -> List[ModelPerformance]:
        """Get model performance metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if model_id:
                    cursor = conn.execute(
                        """
                        SELECT * FROM model_performance WHERE model_id = ?
                    """,
                        (model_id,),
                    )
                else:
                    cursor = conn.execute("SELECT * FROM model_performance")

                results = []
                for row in cursor.fetchall():
                    results.append(
                        ModelPerformance(
                            model_id=row[0],
                            total_queries=row[1],
                            avg_response_time=row[2],
                            avg_consensus_score=row[3],
                            success_rate=row[4],
                            error_count=row[5],
                            last_used=datetime.fromisoformat(row[6]),
                        )
                    )

                return results
        except Exception as e:
            logger.error(f"Failed to get model performance: {e}")
            return []

    def get_query_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[QueryAnalytics]:
        """Get query analytics within date range"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM query_analytics"
                params = []

                conditions = []
                if start_date:
                    conditions.append("timestamp >= ?")
                    params.append(start_date.isoformat())

                if end_date:
                    conditions.append("timestamp <= ?")
                    params.append(end_date.isoformat())

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)

                cursor = conn.execute(query, params)

                results = []
                for row in cursor.fetchall():
                    results.append(
                        QueryAnalytics(
                            query_id=row[0],
                            timestamp=datetime.fromisoformat(row[1]),
                            question=row[2],
                            model_ids=json.loads(row[3]),
                            roles=json.loads(row[4]),
                            method=row[5],
                            consensus_score=row[6],
                            response_time=row[7],
                            success=bool(row[8]),
                            error_message=row[9],
                            individual_scores=json.loads(row[10]) if row[10] else None,
                            chain_rounds=row[11],
                        )
                    )

                return results
        except Exception as e:
            logger.error(f"Failed to get query analytics: {e}")
            return []

    def get_consensus_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get consensus score trends over time"""
        try:
            start_date = datetime.now() - timedelta(days=days)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT DATE(timestamp) as date, 
                           AVG(consensus_score) as avg_score,
                           COUNT(*) as query_count
                    FROM query_analytics 
                    WHERE timestamp >= ? AND success = 1
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                """,
                    (start_date.isoformat(),),
                )

                trends = {"dates": [], "avg_scores": [], "query_counts": []}

                for row in cursor.fetchall():
                    trends["dates"].append(row[0])
                    trends["avg_scores"].append(row[1])
                    trends["query_counts"].append(row[2])

                return trends
        except Exception as e:
            logger.error(f"Failed to get consensus trends: {e}")
            return {"dates": [], "avg_scores": [], "query_counts": []}

    def get_model_comparison(self) -> Dict[str, Any]:
        """Get comparative analysis of all models"""
        performances = self.get_model_performance()

        if not performances:
            return {}

        comparison = {
            "models": [],
            "response_times": [],
            "consensus_scores": [],
            "success_rates": [],
            "query_counts": [],
        }

        for perf in performances:
            comparison["models"].append(perf.model_id)
            comparison["response_times"].append(perf.avg_response_time)
            comparison["consensus_scores"].append(perf.avg_consensus_score)
            comparison["success_rates"].append(perf.success_rate)
            comparison["query_counts"].append(perf.total_queries)

        return comparison

    def cleanup_old_data(self):
        """Clean up old analytics data based on retention policy"""
        try:
            cutoff_date = datetime.now() - timedelta(
                days=settings.analytics_retention_days
            )

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    DELETE FROM query_analytics 
                    WHERE timestamp < ?
                """,
                    (cutoff_date.isoformat(),),
                )

                logger.info(f"Cleaned up analytics data older than {cutoff_date}")
        except Exception as e:
            logger.error(f"Failed to cleanup old analytics data: {e}")

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT 
                        COUNT(*) as total_queries,
                        AVG(consensus_score) as avg_consensus,
                        AVG(response_time) as avg_response_time,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
                        COUNT(DISTINCT model_ids) as unique_model_combinations
                    FROM query_analytics
                """
                )

                row = cursor.fetchone()

                return {
                    "total_queries": row[0] or 0,
                    "avg_consensus_score": round(row[1] or 0, 3),
                    "avg_response_time": round(row[2] or 0, 2),
                    "success_rate": round(row[3] or 0, 1),
                    "unique_model_combinations": row[4] or 0,
                }
        except Exception as e:
            logger.error(f"Failed to get summary stats: {e}")
            return {}


# Global analytics manager instance
analytics_manager = AnalyticsManager()
