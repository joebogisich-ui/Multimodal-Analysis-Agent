"""
反馈闭环模块

提供结果验证、错误检测、自我修正和策略调整功能，
实现 Agent 系统的自我检查和持续改进能力。
"""

import asyncio
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.core.exceptions import ValidationError

logger = get_logger(__name__)


class ResultStatus(str, Enum):
    """结果状态枚举"""
    PENDING = "pending"
    VALIDATING = "validating"
    PASSED = "passed"
    FAILED = "failed"
    CORRECTED = "corrected"
    RETRYING = "retrying"


class ValidationLevel(str, Enum):
    """验证级别枚举"""
    BASIC = "basic"           # 基础验证（数据格式、类型）
    INTERMEDIATE = "intermediate"  # 中级验证（完整性、一致性）
    ADVANCED = "advanced"      # 高级验证（语义、逻辑）


@dataclass
class ValidationRule:
    """验证规则"""
    name: str
    description: str
    level: ValidationLevel
    validator: Callable[[Any], tuple[bool, Optional[str]]]
    weight: float = 1.0  # 规则权重
    enabled: bool = True


@dataclass
class ValidationResult:
    """验证结果"""
    rule_name: str
    passed: bool
    message: Optional[str] = None
    severity: str = "error"  # error, warning, info
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeedbackContext:
    """反馈上下文"""
    task_id: str
    task_type: str
    input_data: Any
    output_data: Any
    parameters: Dict[str, Any]
    validation_results: List[ValidationResult] = field(default_factory=list)
    attempts: int = 1
    max_attempts: int = 3
    start_time: datetime = field(default_factory=datetime.now)
    corrections: List[Dict[str, Any]] = field(default_factory=list)
    status: ResultStatus = ResultStatus.PENDING


class ResultValidator:
    """
    结果验证器

    提供多级别、多维度的结果验证功能，
    支持自定义验证规则和自动修复建议。
    """

    def __init__(self):
        """初始化验证器"""
        self.rules: Dict[ValidationLevel, List[ValidationRule]] = {
            ValidationLevel.BASIC: [],
            ValidationLevel.INTERMEDIATE: [],
            ValidationLevel.ADVANCED: [],
        }
        self._register_default_rules()
        logger.info("结果验证器初始化完成")

    def _register_default_rules(self):
        """注册默认验证规则"""
        # 基础验证规则
        self.add_rule(ValidationRule(
            name="data_not_none",
            description="输出数据不能为空",
            level=ValidationLevel.BASIC,
            validator=lambda x: (x is not None, "输出数据为空"),
            weight=1.0
        ))

        self.add_rule(ValidationRule(
            name="data_type_valid",
            description="数据类型有效性",
            level=ValidationLevel.BASIC,
            validator=self._validate_data_type,
            weight=1.0
        ))

        # 中级验证规则
        self.add_rule(ValidationRule(
            name="required_fields_present",
            description="必需字段完整性",
            level=ValidationLevel.INTERMEDIATE,
            validator=self._validate_required_fields,
            weight=0.8
        ))

        self.add_rule(ValidationRule(
            name="data_consistency",
            description="数据一致性检查",
            level=ValidationLevel.INTERMEDIATE,
            validator=self._validate_consistency,
            weight=0.7
        ))

        self.add_rule(ValidationRule(
            name="value_range_valid",
            description="数值范围有效性",
            level=ValidationLevel.INTERMEDIATE,
            validator=self._validate_value_range,
            weight=0.6
        ))

        # 高级验证规则
        self.add_rule(ValidationRule(
            name="semantic_validity",
            description="语义有效性检查",
            level=ValidationLevel.ADVANCED,
            validator=self._validate_semantic,
            weight=0.5
        ))

        self.add_rule(ValidationRule(
            name="logical_coherence",
            description="逻辑一致性检查",
            level=ValidationLevel.ADVANCED,
            validator=self._validate_logical,
            weight=0.5
        ))

    def add_rule(self, rule: ValidationRule):
        """添加验证规则"""
        self.rules[rule.level].append(rule)
        logger.info(f"添加验证规则: {rule.name} (级别: {rule.level.value})")

    def remove_rule(self, rule_name: str):
        """移除验证规则"""
        for level_rules in self.rules.values():
            level_rules[:] = [r for r in level_rules if r.name != rule_name]
        logger.info(f"移除验证规则: {rule_name}")

    async def validate(
        self,
        output_data: Any,
        task_type: str,
        level: ValidationLevel = ValidationLevel.INTERMEDIATE
    ) -> List[ValidationResult]:
        """
        执行验证

        Args:
            output_data: 待验证的数据
            task_type: 任务类型
            level: 验证级别

        Returns:
            验证结果列表
        """
        results = []
        levels_to_check = self._get_levels_to_check(level)

        for check_level in levels_to_check:
            for rule in self.rules[check_level]:
                if not rule.enabled:
                    continue

                try:
                    passed, message = rule.validator(output_data)
                    results.append(ValidationResult(
                        rule_name=rule.name,
                        passed=passed,
                        message=message,
                        severity="error" if not passed else "info"
                    ))
                except Exception as e:
                    results.append(ValidationResult(
                        rule_name=rule.name,
                        passed=False,
                        message=f"验证执行错误: {str(e)}",
                        severity="error"
                    ))

        return results

    def _get_levels_to_check(self, target_level: ValidationLevel) -> List[ValidationLevel]:
        """获取需要检查的验证级别"""
        level_order = [ValidationLevel.BASIC, ValidationLevel.INTERMEDIATE, ValidationLevel.ADVANCED]
        target_index = level_order.index(target_level)
        return level_order[:target_index + 1]

    def _validate_data_type(self, data: Any) -> tuple[bool, Optional[str]]:
        """验证数据类型"""
        if isinstance(data, dict):
            return True, None
        elif isinstance(data, (list, tuple)):
            return True, None
        elif isinstance(data, (int, float)):
            return True, None
        else:
            return False, f"不支持的数据类型: {type(data)}"

    def _validate_required_fields(self, data: Any) -> tuple[bool, Optional[str]]:
        """验证必需字段"""
        if not isinstance(data, dict):
            return True, None

        required_common = ["result", "status", "timestamp"]
        for field_name in required_common:
            if field_name not in data and field_name not in data.get("metadata", {}):
                return False, f"缺少必需字段: {field_name}"

        return True, None

    def _validate_consistency(self, data: Any) -> tuple[bool, Optional[str]]:
        """验证数据一致性"""
        if not isinstance(data, dict):
            return True, None

        # 检查描述性统计中的和是否一致
        if "descriptive" in data:
            for col_name, stats in data["descriptive"].items():
                if "count" in stats:
                    count = stats["count"]
                    if count <= 0:
                        return False, f"列 {col_name} 的计数无效: {count}"

        return True, None

    def _validate_value_range(self, data: Any) -> tuple[bool, Optional[str]]:
        """验证数值范围"""
        if not isinstance(data, dict):
            return True, None

        # 检查统计值是否在合理范围内
        if "descriptive" in data:
            for col_name, stats in stats.items():
                if "mean" in stats and "min" in stats and "max" in stats:
                    if stats["mean"] < stats["min"] or stats["mean"] > stats["max"]:
                        return False, f"列 {col_name} 的均值超出范围"

        return True, None

    def _validate_semantic(self, data: Any) -> tuple[bool, Optional[str]]:
        """验证语义有效性"""
        return True, None

    def _validate_logical(self, data: Any) -> tuple[bool, Optional[str]]:
        """验证逻辑一致性"""
        return True, None


class ErrorDetector:
    """
    错误检测器

    识别分析结果中的异常和错误模式，
    提供错误分类和严重程度评估。
    """

    def __init__(self):
        """初始化错误检测器"""
        self.error_patterns: Dict[str, Callable[[Any], Optional[Dict]]] = {}
        self._register_default_patterns()
        logger.info("错误检测器初始化完成")

    def _register_default_patterns(self):
        """注册默认错误模式"""
        self.register_pattern("null_values", self._detect_null_values)
        self.register_pattern("outliers", self._detect_outliers)
        self.register_pattern("missing_data", self._detect_missing_data)
        self.register_pattern("type_mismatch", self._detect_type_mismatch)
        self.register_pattern("empty_result", self._detect_empty_result)

    def register_pattern(self, pattern_name: str, detector: Callable[[Any], Optional[Dict]]):
        """注册错误检测模式"""
        self.error_patterns[pattern_name] = detector
        logger.info(f"注册错误检测模式: {pattern_name}")

    async def detect_errors(self, data: Any) -> List[Dict[str, Any]]:
        """
        检测错误

        Args:
            data: 待检测的数据

        Returns:
            检测到的错误列表
        """
        errors = []

        for pattern_name, detector in self.error_patterns.items():
            try:
                error_info = await asyncio.to_thread(detector, data)
                if error_info:
                    errors.append({
                        "pattern": pattern_name,
                        **error_info
                    })
            except Exception as e:
                logger.warning(f"错误模式 {pattern_name} 检测失败: {str(e)}")

        return errors

    def _detect_null_values(self, data: Any) -> Optional[Dict]:
        """检测空值"""
        if isinstance(data, dict):
            null_fields = []
            for key, value in data.items():
                if value is None or (isinstance(value, (list, dict)) and len(value) == 0):
                    null_fields.append(key)

            if null_fields:
                return {
                    "severity": "warning",
                    "message": f"发现 {len(null_fields)} 个空值字段",
                    "affected_fields": null_fields
                }

        return None

    def _detect_outliers(self, data: Any) -> Optional[Dict]:
        """检测异常值"""
        if isinstance(data, dict) and "outliers" in data:
            outliers = data["outliers"]
            if outliers:
                total_outliers = sum(len(v.get("indices", [])) for v in outliers.values())
                if total_outliers > 10:
                    return {
                        "severity": "warning",
                        "message": f"检测到大量异常值 ({total_outliers} 个)",
                        "affected_fields": list(outliers.keys())
                    }

        return None

    def _detect_missing_data(self, data: Any) -> Optional[Dict]:
        """检测缺失数据"""
        if isinstance(data, dict) and "summary" in data:
            summary = data["summary"]
            if "missing_values" in summary and summary["missing_values"] > 0:
                return {
                    "severity": "info",
                    "message": f"存在 {summary['missing_values']} 个缺失值",
                    "count": summary["missing_values"]
                }

        return None

    def _detect_type_mismatch(self, data: Any) -> Optional[Dict]:
        """检测类型不匹配"""
        return None

    def _detect_empty_result(self, data: Any) -> Optional[Dict]:
        """检测空结果"""
        if isinstance(data, dict):
            if not data or all(v is None or v == "" for v in data.values()):
                return {
                    "severity": "error",
                    "message": "结果为空"
                }

        if isinstance(data, list) and len(data) == 0:
            return {
                "severity": "warning",
                "message": "结果列表为空"
            }

        return None


class SelfCorrector:
    """
    自我修正器

    根据错误检测结果自动调整参数，
    提供修正建议和自动修复能力。
    """

    def __init__(self):
        """初始化自我修正器"""
        self.correction_strategies: Dict[str, Callable[[Any, Dict], Dict]] = {}
        self._register_default_strategies()
        logger.info("自我修正器初始化完成")

    def _register_default_strategies(self):
        """注册默认修正策略"""
        self.register_strategy("retry_with_params", self._retry_strategy)
        self.register_strategy("adjust_threshold", self._threshold_strategy)
        self.register_strategy("use_alternative_method", self._method_strategy)
        self.register_strategy("reduce_data_volume", self._data_reduction_strategy)

    def register_strategy(self, strategy_name: str, strategy_func: Callable):
        """注册修正策略"""
        self.correction_strategies[strategy_name] = strategy_func
        logger.info(f"注册修正策略: {strategy_name}")

    async def correct(
        self,
        context: FeedbackContext,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        执行修正

        Args:
            context: 反馈上下文
            errors: 检测到的错误列表

        Returns:
            修正建议
        """
        corrections = []

        for error in errors:
            pattern = error.get("pattern")
            severity = error.get("severity")

            if severity == "error":
                strategy = self._select_strategy(pattern, context)
                if strategy:
                    correction = strategy(context, error)
                    corrections.append(correction)
                    context.corrections.append(correction)

        return {
            "total_errors": len(errors),
            "corrections_applied": len(corrections),
            "correction_details": corrections,
            "new_parameters": context.parameters.copy()
        }

    def _select_strategy(self, pattern: Optional[str], context: FeedbackContext) -> Optional[Callable]:
        """选择修正策略"""
        if pattern == "empty_result":
            return self.correction_strategies.get("retry_with_params")
        elif pattern == "outliers":
            return self.correction_strategies.get("adjust_threshold")
        elif pattern == "type_mismatch":
            return self.correction_strategies.get("use_alternative_method")
        else:
            return self.correction_strategies.get("retry_with_params")

    def _retry_strategy(self, context: FeedbackContext, error: Dict) -> Dict:
        """重试策略"""
        return {
            "strategy": "retry_with_params",
            "original_attempts": context.attempts,
            "suggested_action": "重新执行分析",
            "reason": error.get("message", "未知错误"),
            "suggested_params": context.parameters.copy()
        }

    def _threshold_strategy(self, context: FeedbackContext, error: Dict) -> Dict:
        """阈值调整策略"""
        new_params = context.parameters.copy()
        if "threshold" not in new_params:
            new_params["threshold"] = 0.5

        return {
            "strategy": "adjust_threshold",
            "original_threshold": new_params.get("threshold"),
            "suggested_threshold": 0.7,
            "suggested_action": "提高异常值检测阈值",
            "new_parameters": new_params
        }

    def _method_strategy(self, context: FeedbackContext, error: Dict) -> Dict:
        """方法替换策略"""
        current_method = context.parameters.get("method", "pearson")
        alternative_methods = {
            "pearson": "spearman",
            "spearman": "kendall",
            "kendall": "pearson"
        }

        return {
            "strategy": "use_alternative_method",
            "original_method": current_method,
            "suggested_method": alternative_methods.get(current_method, "pearson"),
            "suggested_action": "使用替代分析方法",
            "new_parameters": {**context.parameters, "method": alternative_methods.get(current_method)}
        }

    def _data_reduction_strategy(self, context: FeedbackContext, error: Dict) -> Dict:
        """数据缩减策略"""
        return {
            "strategy": "reduce_data_volume",
            "suggested_action": "减少数据量或进行采样",
            "suggested_params": {
                **context.parameters,
                "sample_size": min(1000, context.parameters.get("sample_size", 10000)),
                "use_sampling": True
            }
        }


class FeedbackLoop:
    """
    反馈闭环管理器

    协调验证器、错误检测器和自我修正器，
    实现完整的反馈控制循环。
    """

    def __init__(self):
        """初始化反馈闭环"""
        self.validator = ResultValidator()
        self.error_detector = ErrorDetector()
        self.self_corrector = SelfCorrector()
        self.contexts: Dict[str, FeedbackContext] = {}
        self.performance_metrics: Dict[str, List[float]] = defaultdict(list)
        self.strategy_success_rates: Dict[str, float] = defaultdict(float)
        logger.info("反馈闭环管理器初始化完成")

    async def execute(
        self,
        task_id: str,
        task_type: str,
        input_data: Any,
        output_data: Any,
        parameters: Dict[str, Any],
        max_attempts: int = 3
    ) -> Dict[str, Any]:
        """
        执行反馈闭环

        Args:
            task_id: 任务ID
            task_type: 任务类型
            input_data: 输入数据
            output_data: 输出数据
            parameters: 参数
            max_attempts: 最大尝试次数

        Returns:
            处理结果
        """
        context = FeedbackContext(
            task_id=task_id,
            task_type=task_type,
            input_data=input_data,
            output_data=output_data,
            parameters=parameters,
            max_attempts=max_attempts
        )

        self.contexts[task_id] = context

        while context.attempts <= max_attempts:
            # 验证结果
            context.status = ResultStatus.VALIDATING
            validation_results = await self.validator.validate(
                output_data,
                task_type,
                ValidationLevel.INTERMEDIATE
            )
            context.validation_results.extend(validation_results)

            passed_validations = sum(1 for r in validation_results if r.passed)
            failed_validations = [r for r in validation_results if not r.passed]

            # 检测错误
            errors = await self.error_detector.detect_errors(output_data)

            if passed_validations == len(validation_results) and not errors:
                context.status = ResultStatus.PASSED
                self._record_success(context)
                break

            # 尝试修正
            if context.attempts < max_attempts:
                context.status = ResultStatus.RETRYING
                correction_result = await self.self_corrector.correct(context, failed_validations + errors)

                # 更新参数
                if correction_result.get("new_parameters"):
                    context.parameters.update(correction_result["new_parameters"])

                context.attempts += 1
                logger.info(f"任务 {task_id} 第 {context.attempts} 次尝试修正")
            else:
                context.status = ResultStatus.FAILED
                self._record_failure(context)
                break

        return self._generate_report(context)

    def _record_success(self, context: FeedbackContext):
        """记录成功"""
        duration = (datetime.now() - context.start_time).total_seconds()
        self.performance_metrics["success_rate"].append(1.0)
        self.performance_metrics["duration"].append(duration)
        logger.info(f"任务 {context.task_id} 验证通过")

    def _record_failure(self, context: FeedbackContext):
        """记录失败"""
        self.performance_metrics["success_rate"].append(0.0)
        logger.warning(f"任务 {context.task_id} 验证失败")

    def _generate_report(self, context: FeedbackContext) -> Dict[str, Any]:
        """生成报告"""
        return {
            "task_id": context.task_id,
            "status": context.status.value,
            "attempts": context.attempts,
            "validation_results": [
                {
                    "rule": r.rule_name,
                    "passed": r.passed,
                    "message": r.message,
                    "severity": r.severity
                }
                for r in context.validation_results
            ],
            "corrections": context.corrections,
            "final_parameters": context.parameters,
            "duration_seconds": (datetime.now() - context.start_time).total_seconds()
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        metrics = {}
        for metric_name, values in self.performance_metrics.items():
            if values:
                metrics[metric_name] = {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "latest": values[-1]
                }

        return {
            "performance": metrics,
            "strategy_success_rates": dict(self.strategy_success_rates)
        }


# 全局反馈闭环实例
feedback_loop = FeedbackLoop()
