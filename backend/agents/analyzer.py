"""
数据分析器模块

提供多类型的数据分析功能，包括统计分析、趋势分析、
聚类分析、关联分析等。
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import stats

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import AnalysisError, ValidationError

logger = get_logger(__name__)


class DataAnalyzer:
    """
    数据分析器

    提供全面的数据分析功能，支持多种分析方法和算法。
    """

    def __init__(self):
        """初始化数据分析器"""
        self.analysis_methods = {
            "statistics": self.statistical_analysis,
            "trend": self.trend_analysis,
            "clustering": self.clustering_analysis,
            "correlation": self.correlation_analysis,
            "regression": self.regression_analysis,
            "distribution": self.distribution_analysis,
        }
        logger.info("数据分析器初始化完成")

    async def analyze(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        analysis_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行数据分析

        Args:
            data: 输入数据
            analysis_type: 分析类型
            parameters: 分析参数

        Returns:
            分析结果
        """
        logger.info(f"开始执行 {analysis_type} 分析")

        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data

        method = self.analysis_methods.get(analysis_type)
        if not method:
            raise ValidationError(f"不支持的分析类型: {analysis_type}")

        try:
            result = await asyncio.to_thread(
                method,
                df,
                parameters or {}
            )
            logger.info(f"{analysis_type} 分析完成")
            return result
        except Exception as e:
            logger.error(f"分析失败: {str(e)}")
            raise AnalysisError(str(e), analysis_type)

    def statistical_analysis(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行统计分析

        Args:
            df: 数据框
            parameters: 参数

        Returns:
            统计分析结果
        """
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        results = {
            "summary": {},
            "descriptive": {},
            "outliers": {},
        }

        # 描述性统计
        for col in numeric_columns:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue

            results["descriptive"][col] = {
                "count": int(len(col_data)),
                "mean": float(col_data.mean()),
                "std": float(col_data.std()),
                "min": float(col_data.min()),
                "max": float(col_data.max()),
                "q25": float(col_data.quantile(0.25)),
                "q50": float(col_data.quantile(0.50)),
                "q75": float(col_data.quantile(0.75)),
                "skewness": float(col_data.skew()),
                "kurtosis": float(col_data.kurtosis()),
            }

            # 异常值检测
            q1, q3 = col_data.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]

            if len(outliers) > 0:
                results["outliers"][col] = {
                    "count": int(len(outliers)),
                    "indices": outliers.index.tolist()[:100],
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound),
                }

        # 数据概况
        results["summary"] = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(numeric_columns),
            "categorical_columns": len(df.select_dtypes(include=["object"]).columns),
            "missing_values": int(df.isnull().sum().sum()),
            "memory_usage": int(df.memory_usage(deep=True).sum()),
        }

        return results

    def trend_analysis(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行趋势分析

        Args:
            df: 数据框
            parameters: 参数

        Returns:
            趋势分析结果
        """
        forecast_periods = parameters.get("forecast_periods", 12)
        date_column = parameters.get("date_column")
        value_column = parameters.get("value_column")

        if not date_column or date_column not in df.columns:
            raise ValidationError("未指定有效的日期列")

        if not value_column or value_column not in df.columns:
            raise ValidationError("未指定有效的数值列")

        df_sorted = df.sort_values(date_column).copy()
        df_sorted["date"] = pd.to_datetime(df_sorted[date_column])

        values = df_sorted[value_column].values
        dates = df_sorted["date"]

        # 计算移动平均
        window_sizes = [3, 5, 7]
        moving_averages = {}
        for window in window_sizes:
            moving_averages[f"ma_{window}"] = (
                pd.Series(values)
                .rolling(window=window)
                .mean()
                .tolist()[-min(window, len(values)):]
            )

        # 简单线性回归趋势
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)

        # 趋势预测
        future_x = np.arange(len(values), len(values) + forecast_periods)
        forecast = slope * future_x + intercept

        # 季节性分析
        df_sorted["month"] = df_sorted["date"].dt.month
        monthly_avg = df_sorted.groupby("month")[value_column].mean().to_dict()

        results = {
            "trend": {
                "direction": "increasing" if slope > 0 else "decreasing",
                "slope": float(slope),
                "r_squared": float(r_value ** 2),
                "p_value": float(p_value),
                "significance": "significant" if p_value < 0.05 else "not_significant",
            },
            "moving_averages": moving_averages,
            "forecast": {
                "values": forecast.tolist(),
                "periods": forecast_periods,
            },
            "seasonality": {
                "detected": True,
                "monthly_averages": {str(k): float(v) for k, v in monthly_avg.items()},
            },
            "current_value": float(values[-1]) if len(values) > 0 else None,
            "min_value": float(values.min()),
            "max_value": float(values.max()),
        }

        return results

    def clustering_analysis(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行聚类分析

        Args:
            df: 数据框
            parameters: 参数

        Returns:
            聚类分析结果
        """
        from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
        from sklearn.preprocessing import StandardScaler

        features = parameters.get("features")
        if not features:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            features = numeric_cols

        available_features = [f for f in features if f in df.columns]
        if not available_features:
            raise ValidationError("没有可用的特征列进行聚类")

        X = df[available_features].fillna(0).values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        algorithm = parameters.get("algorithm", "kmeans")
        n_clusters = parameters.get("n_clusters", 3)

        if algorithm == "kmeans":
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        elif algorithm == "hierarchical":
            model = AgglomerativeClustering(n_clusters=n_clusters)
        elif algorithm == "dbscan":
            eps = parameters.get("eps", 0.5)
            min_samples = parameters.get("min_samples", 5)
            model = DBSCAN(eps=eps, min_samples=min_samples)
        else:
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)

        labels = model.fit_predict(X_scaled)

        # 计算聚类统计
        cluster_stats = {}
        for i in range(labels.max() + 1):
            cluster_mask = labels == i
            cluster_data = df[cluster_mask]
            cluster_stats[int(i)] = {
                "count": int(cluster_mask.sum()),
                "percentage": float(cluster_mask.sum() / len(labels) * 100),
                "features": {}
            }
            for feat in available_features:
                cluster_stats[int(i)]["features"][feat] = {
                    "mean": float(cluster_data[feat].mean()),
                    "std": float(cluster_data[feat].std()),
                }

        # 聚类质量评估
        from sklearn.metrics import silhouette_score, calinski_harabasz_score

        if len(np.unique(labels)) > 1:
            silhouette = silhouette_score(X_scaled, labels)
            calinski = calinski_harabasz_score(X_scaled, labels)
        else:
            silhouette = None
            calinski = None

        results = {
            "algorithm": algorithm,
            "n_clusters": len(np.unique(labels)),
            "labels": labels.tolist(),
            "cluster_stats": cluster_stats,
            "quality_metrics": {
                "silhouette_score": float(silhouette) if silhouette else None,
                "calinski_harabasz_score": float(calinski) if calinski else None,
            },
        }

        return results

    def correlation_analysis(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行相关性分析

        Args:
            df: 数据框
            parameters: 参数

        Returns:
            相关性分析结果
        """
        method = parameters.get("method", "pearson")

        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            raise ValidationError("没有数值列可供分析")

        # 计算相关矩阵
        if method == "pearson":
            corr_matrix = numeric_df.corr(method="pearson")
        elif method == "spearman":
            corr_matrix = numeric_df.corr(method="spearman")
        elif method == "kendall":
            corr_matrix = numeric_df.corr(method="kendall")
        else:
            corr_matrix = numeric_df.corr(method="pearson")

        # 找出强相关对
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= 0.7:
                    strong_correlations.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": float(corr_value),
                        "strength": "strong_positive" if corr_value > 0 else "strong_negative",
                    })

        # 部分相关性分析
        partial_corr = {}
        if len(corr_matrix.columns) >= 3:
            from sklearn.linear_model import LinearRegression
            for target in corr_matrix.columns:
                others = [c for c in corr_matrix.columns if c != target]
                X = numeric_df[others].values
                y = numeric_df[target].values
                mask = ~np.isnan(y)
                if mask.sum() > len(others):
                    model = LinearRegression()
                    residuals = np.zeros(len(y))
                    model.fit(X[mask], y[mask])
                    residuals[mask] = y[mask] - model.predict(X[mask])
                    partial_corr[target] = {
                        "mean_residual": float(np.mean(np.abs(residuals))),
                        "std_residual": float(np.std(residuals)),
                    }

        results = {
            "correlation_matrix": corr_matrix.to_dict(),
            "method": method,
            "strong_correlations": strong_correlations,
            "partial_correlations": partial_corr,
            "summary": {
                "n_variables": len(corr_matrix.columns),
                "n_strong_correlations": len(strong_correlations),
            },
        }

        return results

    def regression_analysis(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行回归分析

        Args:
            df: 数据框
            parameters: 参数

        Returns:
            回归分析结果
        """
        from sklearn.linear_model import LinearRegression, Ridge, Lasso
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

        target = parameters.get("target")
        if not target or target not in df.columns:
            raise ValidationError("未指定有效的目标列")

        features = parameters.get("features", [])
        available_features = [f for f in features if f in df.columns]
        if not available_features:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            available_features = [c for c in numeric_cols if c != target]

        X = df[available_features].fillna(0).values
        y = df[target].fillna(0).values

        test_size = parameters.get("test_size", 0.2)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        model_type = parameters.get("model_type", "linear")
        if model_type == "ridge":
            alpha = parameters.get("alpha", 1.0)
            model = Ridge(alpha=alpha)
        elif model_type == "lasso":
            alpha = parameters.get("alpha", 1.0)
            model = Lasso(alpha=alpha)
        else:
            model = LinearRegression()

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        results = {
            "model_type": model_type,
            "coefficients": {
                col: float(coef)
                for col, coef in zip(available_features, model.coef_)
            },
            "intercept": float(model.intercept_),
            "metrics": {
                "r2_score": float(r2_score(y_test, y_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
                "mae": float(mean_absolute_error(y_test, y_pred)),
            },
            "feature_importance": sorted(
                [
                    {"feature": col, "importance": float(abs(coef))}
                    for col, coef in zip(available_features, model.coef_)
                ],
                key=lambda x: x["importance"],
                reverse=True
            ),
        }

        return results

    def distribution_analysis(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行分布分析

        Args:
            df: 数据框
            parameters: 参数

        Returns:
            分布分析结果
        """
        from scipy.stats import shapiro, normaltest, anderson
        from scipy.stats import kstest, expon, uniform

        columns = parameters.get("columns")
        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        results = {"columns": {}}

        for col in columns:
            if col not in df.columns:
                continue

            data = df[col].dropna()
            if len(data) < 3:
                continue

            # 基本统计
            col_stats = {
                "mean": float(data.mean()),
                "median": float(data.median()),
                "mode": float(data.mode().iloc[0]) if not data.mode().empty else None,
                "std": float(data.std()),
                "skewness": float(data.skew()),
                "kurtosis": float(data.kurtosis()),
            }

            # 正态性检验
            if len(data) >= 5000:
                sample = data.sample(5000, random_state=42)
            else:
                sample = data

            if len(sample) >= 3:
                try:
                    normality_result = normaltest(sample)
                    col_stats["normality_test"] = {
                        "statistic": float(normality_result.statistic),
                        "p_value": float(normality_result.pvalue),
                        "is_normal": normality_result.pvalue > 0.05,
                    }
                except Exception:
                    pass

                try:
                    anderson_result = anderson(sample)
                    col_stats["anderson_test"] = {
                        "statistic": float(anderson_result.statistic),
                        "critical_values": anderson_result.critical_values.tolist(),
                        "significance_level": anderson_result.significance_level.tolist(),
                    }
                except Exception:
                    pass

            # 分位数
            quantiles = data.quantile([0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
            col_stats["quantiles"] = {str(k): float(v) for k, v in quantiles.items()}

            results["columns"][col] = col_stats

        return results
