import inspect
from typing import Dict, List, Callable
import hashlib

from datetime import datetime


class CoreFunctionality:
    """基础功能核心类"""

    def __init__(self):
        self.function_registry: Dict[str, Callable] = {}
        self.code_versions: Dict[str, List[str]] = {}
        self.performance_metrics: Dict[str, Dict] = {}

    def register_function(self, func: Callable) -> str:
        """注册新功能函数"""
        func_hash = self._generate_function_hash(func)
        self.function_registry[func_hash] = func
        self._track_code_version(func, func_hash)
        return func_hash

    def execute_function(self, func_hash: str, *args, **kwargs):
        """执行注册的功能"""
        if func_hash not in self.function_registry:
            raise ValueError(f"Function {func_hash} not registered")

        start_time = datetime.now()
        try:
            result = self.function_registry[func_hash](*args, **kwargs)
            status = "success"
        except Exception as e:
            result = str(e)
            status = "failed"

        self._record_performance(
            func_hash,
            duration=(datetime.now() - start_time).total_seconds(),
            status=status
        )
        return result

    def _generate_function_hash(self, func: Callable) -> str:
        """生成函数唯一哈希"""
        source = inspect.getsource(func)
        return hashlib.md5(source.encode()).hexdigest()

    def _track_code_version(self, func: Callable, func_hash: str):
        """跟踪代码版本变化"""
        func_name = func.__name__
        if func_name not in self.code_versions:
            self.code_versions[func_name] = []

        source = inspect.getsource(func)
        if not self.code_versions[func_name] or self.code_versions[func_name][-1] != source:
            self.code_versions[func_name].append(source)

    def _record_performance(self, func_hash: str, **metrics):
        """记录性能指标"""
        if func_hash not in self.performance_metrics:
            self.performance_metrics[func_hash] = []
        self.performance_metrics[func_hash].append({
            "timestamp": datetime.now().isoformat(),
            **metrics
        })

    def auto_optimize(self):
        """基于性能数据自动优化"""
        for func_hash, metrics in self.performance_metrics.items():
            avg_time = sum(m['duration'] for m in metrics) / len(metrics)
            success_rate = sum(1 for m in metrics if m['status'] == "success") / len(metrics)

            if avg_time > 1.0 or success_rate < 0.9:
                print(f"Optimization needed for {func_hash} (avg: {avg_time:.2f}s, success: {success_rate:.1%})")
                # 这里可以添加自动优化逻辑


# 基础API功能
class CoreAPI:
    """核心API管理"""

    def __init__(self, core: CoreFunctionality):
        self.core = core
        self._register_builtin_functions()

    def _register_builtin_functions(self):
        """注册内置功能"""
        self.core.register_function(self.execute_code)
        self.core.register_function(self.analyze_performance)

    def execute_code(self, code: str, language: str = "python") -> dict:
        """执行代码的基础功能"""
        if language == "python":
            try:
                locals_dict = {}
                exec(code, globals(), locals_dict)
                return {
                    "status": "success",
                    "result": locals_dict.get('result', None),
                    "output": locals_dict
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e)
                }
        else:
            return {
                "status": "error",
                "error": f"Unsupported language: {language}"
            }

    def analyze_performance(self) -> dict:
        """分析性能数据"""
        return {
            "function_count": len(self.core.function_registry),
            "performance_metrics": self.core.performance_metrics
        }
