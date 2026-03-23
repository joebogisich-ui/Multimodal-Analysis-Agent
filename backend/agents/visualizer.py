"""
可视化生成器模块

提供图表和仪表盘生成功能，支持多种可视化类型和交互操作。
"""

import base64
import io
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import VisualizationError, ValidationError

logger = get_logger(__name__)


class ChartVisualizer:
    """
    图表可视化器

    提供丰富的图表生成功能，包括折线图、柱状图、散点图、热力图等。
    """

    def __init__(self):
        """初始化可视化器"""
        self.chart_types = {
            "line": self.create_line_chart,
            "bar": self.create_bar_chart,
            "scatter": self.create_scatter_chart,
            "pie": self.create_pie_chart,
            "histogram": self.create_histogram,
            "box": self.create_box_plot,
            "heatmap": self.create_heatmap,
            "radar": self.create_radar_chart,
            "treemap": self.create_treemap,
            "wordcloud": self.create_wordcloud,
        }
        self.theme = settings.visualization.default_theme
        self.color_scheme = settings.visualization.color_schemes
        logger.info("可视化生成器初始化完成")

    async def generate_chart(
        self,
        data: Union[pd.DataFrame, Dict[str, Any]],
        chart_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成图表

        Args:
            data: 输入数据
            chart_type: 图表类型
            parameters: 图表参数

        Returns:
            图表配置和数据
        """
        logger.info(f"开始生成 {chart_type} 图表")

        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data

        creator = self.chart_types.get(chart_type)
        if not creator:
            raise ValidationError(f"不支持的图表类型: {chart_type}")

        try:
            result = await creator(df, parameters or {})
            logger.info(f"图表 {chart_type} 生成完成")
            return result
        except Exception as e:
            logger.error(f"图表生成失败: {str(e)}")
            raise VisualizationError(str(e), chart_type)

    def create_line_chart(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建折线图"""
        x_col = parameters.get("x", df.columns[0] if len(df.columns) > 0 else None)
        y_cols = parameters.get("y", df.columns[1:3].tolist() if len(df.columns) > 1 else [])

        if not x_col or x_col not in df.columns:
            raise ValidationError("未指定有效的X轴列")

        fig = go.Figure()

        colors = px.colors.qualitative.Plotly

        for i, y_col in enumerate(y_cols):
            if y_col not in df.columns:
                continue

            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode="lines+markers",
                name=y_col,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6),
            ))

        title = parameters.get("title", f"{', '.join(y_cols)} 趋势图")
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            xaxis_title=x_col,
            yaxis_title=parameters.get("y_title", ""),
            template="plotly_white" if self.theme == "light" else "plotly_dark",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )

        return self._export_figure(fig, parameters)

    def create_bar_chart(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建柱状图"""
        x_col = parameters.get("x", df.columns[0] if len(df.columns) > 0 else None)
        y_col = parameters.get("y", df.columns[1] if len(df.columns) > 1 else None)
        orientation = parameters.get("orientation", "v")

        if not x_col or x_col not in df.columns:
            raise ValidationError("未指定有效的X轴列")

        if not y_col or y_col not in df.columns:
            raise ValidationError("未指定有效的Y轴列")

        fig = go.Figure()

        if orientation == "h":
            fig.add_trace(go.Bar(
                y=df[x_col],
                x=df[y_col],
                orientation="h",
                marker_color=px.colors.qualitative.Set2,
            ))
        else:
            fig.add_trace(go.Bar(
                x=df[x_col],
                y=df[y_col],
                marker_color=px.colors.qualitative.Set2,
            ))

        title = parameters.get("title", f"{y_col} 柱状图")
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            template="plotly_white" if self.theme == "light" else "plotly_dark",
        )

        return self._export_figure(fig, parameters)

    def create_scatter_chart(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建散点图"""
        x_col = parameters.get("x", df.columns[0] if len(df.columns) > 0 else None)
        y_col = parameters.get("y", df.columns[1] if len(df.columns) > 1 else None)
        size_col = parameters.get("size")
        color_col = parameters.get("color")

        if not x_col or x_col not in df.columns:
            raise ValidationError("未指定有效的X轴列")

        if not y_col or y_col not in df.columns:
            raise ValidationError("未指定有效的Y轴列")

        fig = go.Figure()

        marker_config = dict(size=10, opacity=0.7)

        if size_col and size_col in df.columns:
            marker_config["size"] = df[size_col].values
            marker_config["sizemin"] = 5

        if color_col and color_col in df.columns:
            if df[color_col].dtype in ["object", "category"]:
                marker_config["color"] = df[color_col]
                marker_config["colorscale"] = self.color_scheme.get("categorical", "Viridis")
            else:
                marker_config["color"] = df[color_col]
                marker_config["colorscale"] = self.color_scheme.get("sequential", "Blues")

        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="markers",
            marker=marker_config,
            text=df.apply(lambda row: f"{x_col}: {row[x_col]}<br>{y_col}: {row[y_col]}", axis=1),
            hoverinfo="text",
        ))

        title = parameters.get("title", f"{x_col} vs {y_col}")
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            xaxis_title=x_col,
            yaxis_title=y_col,
            template="plotly_white" if self.theme == "light" else "plotly_dark",
        )

        return self._export_figure(fig, parameters)

    def create_pie_chart(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建饼图"""
        names_col = parameters.get("names", df.columns[0] if len(df.columns) > 0 else None)
        values_col = parameters.get("values", df.columns[1] if len(df.columns) > 1 else None)

        if not names_col or names_col not in df.columns:
            raise ValidationError("未指定有效的名称列")

        if not values_col or values_col not in df.columns:
            raise ValidationError("未指定有效的数值列")

        fig = go.Figure()

        fig.add_trace(go.Pie(
            labels=df[names_col],
            values=df[values_col],
            hole=parameters.get("hole", 0.4),
            textinfo="label+percent",
            textposition="inside",
            marker=dict(colors=px.colors.qualitative.Set3),
        ))

        title = parameters.get("title", f"{values_col} 分布")
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            template="plotly_white" if self.theme == "light" else "plotly_dark",
        )

        return self._export_figure(fig, parameters)

    def create_histogram(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建直方图"""
        x_col = parameters.get("x", df.columns[0] if len(df.columns) > 0 else None)

        if not x_col or x_col not in df.columns:
            raise ValidationError("未指定有效的列")

        nbinsx = parameters.get("nbins", 30)

        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=df[x_col],
            nbinsx=nbinsx,
            marker_color=px.colors.qualitative.Plotly[0],
            opacity=0.8,
        ))

        title = parameters.get("title", f"{x_col} 分布直方图")
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            xaxis_title=x_col,
            yaxis_title="频数",
            template="plotly_white" if self.theme == "light" else "plotly_dark",
            bargap=0.1,
        )

        return self._export_figure(fig, parameters)

    def create_box_plot(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建箱线图"""
        y_cols = parameters.get("y", df.select_dtypes(include=[np.number]).columns.tolist())

        fig = go.Figure()

        for i, y_col in enumerate(y_cols):
            if y_col not in df.columns:
                continue

            fig.add_trace(go.Box(
                y=df[y_col],
                name=y_col,
                boxpoints="outliers",
                marker_color=px.colors.qualitative.Set2[i % len(px.colors.qualitative.Set2)],
            ))

        title = parameters.get("title", "箱线图")
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            template="plotly_white" if self.theme == "light" else "plotly_dark",
        )

        return self._export_figure(fig, parameters)

    def create_heatmap(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建热力图"""
        columns = parameters.get("columns", df.select_dtypes(include=[np.number]).columns.tolist())
        available_cols = [c for c in columns if c in df.columns]

        if len(available_cols) < 2:
            raise ValidationError("热力图需要至少两个数值列")

        corr_matrix = df[available_cols].corr()

        fig = go.Figure()

        fig.add_trace(go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale=self.color_scheme.get("diverging", "RdBu"),
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False,
        ))

        title = parameters.get("title", "相关性热力图")
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            template="plotly_white" if self.theme == "light" else "plotly_dark",
        )

        return self._export_figure(fig, parameters)

    def create_radar_chart(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建雷达图"""
        categories_col = parameters.get("categories", df.columns[0] if len(df.columns) > 0 else None)
        value_cols = parameters.get("values", df.select_dtypes(include=[np.number]).columns.tolist()[:5])

        if not categories_col or categories_col not in df.columns:
            raise ValidationError("未指定有效的类别列")

        available_values = [c for c in value_cols if c in df.columns]
        if not available_values:
            raise ValidationError("未指定有效的数值列")

        fig = go.Figure()

        colors = px.colors.qualitative.Plotly

        for i, (_, row) in enumerate(df.iterrows()):
            fig.add_trace(go.Scatterpolar(
                r=[row[col] for col in available_values],
                theta=available_values,
                fill="toself",
                name=row[categories_col],
                line_color=colors[i % len(colors)],
                fillcolor=colors[i % len(colors)],
                opacity=0.6,
            ))

        title = parameters.get("title", "雷达图")
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            polar=dict(radialaxis=dict(visible=True)),
            template="plotly_white" if self.theme == "light" else "plotly_dark",
            showlegend=True,
        )

        return self._export_figure(fig, parameters)

    def create_treemap(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建树形图"""
        labels_col = parameters.get("labels", df.columns[0] if len(df.columns) > 0 else None)
        values_col = parameters.get("values", df.columns[1] if len(df.columns) > 1 else None)
        parents_col = parameters.get("parents")

        if not labels_col or labels_col not in df.columns:
            raise ValidationError("未指定有效的标签列")

        if not values_col or values_col not in df.columns:
            raise ValidationError("未指定有效的数值列")

        fig = go.Figure()

        if parents_col and parents_col in df.columns:
            fig.add_trace(go.Treemap(
                labels=df[labels_col],
                values=df[values_col],
                parents=df[parents_col],
                marker_colors=px.colors.qualitative.Set3,
            ))
        else:
            fig.add_trace(go.Treemap(
                labels=df[labels_col],
                values=df[values_col],
                marker_colors=px.colors.qualitative.Set3,
            ))

        title = parameters.get("title", "树形图")
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20)),
            template="plotly_white" if self.theme == "light" else "plotly_dark",
        )

        return self._export_figure(fig, parameters)

    def create_wordcloud(
        self,
        df: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建词云图"""
        text_col = parameters.get("text", df.columns[0] if len(df.columns) > 0 else None)
        weight_col = parameters.get("weight", None)

        if not text_col or text_col not in df.columns:
            raise ValidationError("未指定有效的文本列")

        from wordcloud import WordCloud
        import matplotlib.pyplot as plt

        if weight_col and weight_col in df.columns:
            word_freq = dict(zip(df[text_col].astype(str), df[weight_col]))
        else:
            text = " ".join(df[text_col].astype(str).tolist())
            word_freq = None

        wc = WordCloud(
            width=parameters.get("width", 800),
            height=parameters.get("height", 400),
            background_color="white" if self.theme == "light" else "black",
            max_words=parameters.get("max_words", 200),
            colormap=self.color_scheme.get("categorical", "viridis"),
        )

        if word_freq:
            wc.generate_from_frequencies(word_freq)
        else:
            wc.generate(text)

        img_buffer = io.BytesIO()
        wc.to_image().save(img_buffer, format="PNG")
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

        return {
            "type": "wordcloud",
            "image": f"data:image/png;base64,{img_base64}",
            "width": parameters.get("width", 800),
            "height": parameters.get("height", 400),
        }

    def _export_figure(
        self,
        fig: go.Figure,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """导出图表为不同格式"""
        export_format = parameters.get("format", "html")

        result = {
            "type": "plotly",
            "chart_type": parameters.get("chart_type", "line"),
        }

        if export_format == "html":
            result["html"] = fig.to_html(full_html=False, include_plotlyjs="cdn")
        elif export_format == "json":
            result["config"] = fig.to_json()
        elif export_format == "png":
            img_bytes = fig.to_image(format="png", width=parameters.get("width", 800), height=parameters.get("height", 600))
            result["image"] = f"data:image/png;base64,{base64.b64encode(img_bytes).decode()}"
        elif export_format == "svg":
            img_bytes = fig.to_image(format="svg")
            result["image"] = f"data:image/svg+xml;base64,{base64.b64encode(img_bytes).decode()}"

        result["data"] = fig.to_dict()
        return result


class DashboardGenerator:
    """
    仪表盘生成器

    提供多图表仪表盘的组合生成功能。
    """

    def __init__(self, chart_visualizer: ChartVisualizer):
        """
        初始化仪表盘生成器

        Args:
            chart_visualizer: 图表可视化器实例
        """
        self.chart_visualizer = chart_visualizer

    async def generate_dashboard(
        self,
        chart_configs: List[Dict[str, Any]],
        layout: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成仪表盘

        Args:
            chart_configs: 图表配置列表
            layout: 布局配置

        Returns:
            仪表盘数据
        """
        charts = []

        for config in chart_configs:
            chart_type = config.get("type", "line")
            data = config.get("data", {})
            params = config.get("parameters", {})

            chart = await self.chart_visualizer.generate_chart(
                data=data,
                chart_type=chart_type,
                parameters=params
            )

            chart["title"] = config.get("title", "")
            chart["position"] = config.get("position", {"x": 0, "y": 0, "w": 6, "h": 4})
            charts.append(chart)

        default_layout = {
            "columns": 12,
            "row_height": 100,
            "theme": self.chart_visualizer.theme,
        }

        return {
            "charts": charts,
            "layout": {**default_layout, **(layout or {})},
            "created_at": datetime.now().isoformat(),
        }
