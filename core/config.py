"""
Configuration System - 配置管理系统

负责加载、验证和管理系统配置。
支持 YAML 格式配置文件，提供类型安全和默认值管理。

设计原则:
- 单一职责：只负责配置相关操作
- 开闭原则：支持通过扩展添加新的配置源
- 依赖倒置：不依赖具体配置存储格式
"""

import os
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class ConfigError(Exception):
    """配置相关异常"""
    pass


class Config:
    """
    配置容器类
    
    提供字典式的配置访问接口，支持嵌套配置和默认值。
    
    Attributes:
        data: 存储配置数据的字典
    """
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """
        初始化配置对象
        
        Args:
            data: 初始配置数据字典
        """
        self._data = data or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        支持点分隔的嵌套键访问，如 "model.name"
        
        Args:
            key: 配置键，支持嵌套访问
            default: 默认值，当键不存在时返回
            
        Returns:
            配置值或默认值
            
        Example:
            >>> config = Config({"model": {"name": "deepseek"}})
            >>> config.get("model.name")
            'deepseek'
            >>> config.get("model.temperature", 0.7)
            0.7
        """
        keys = key.split(".")
        value = self._data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持嵌套访问
            value: 配置值
            
        Example:
            >>> config.set("model.temperature", 0.8)
        """
        keys = key.split(".")
        data = self._data
        
        # 导航到倒数第二层
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        # 设置最后一层的值
        data[keys[-1]] = value
    
    def has(self, key: str) -> bool:
        """
        检查配置键是否存在
        
        Args:
            key: 配置键
            
        Returns:
            是否存在
        """
        try:
            keys = key.split(".")
            value = self._data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return False
            
            return True
        except (KeyError, TypeError):
            return False
    
    def validate(self, schema: Dict[str, Any]) -> bool:
        """
        根据 schema 验证配置
        
        Args:
            schema: 验证 schema，定义必需字段和类型
            
        Returns:
            验证是否通过
            
        Raises:
            ConfigError: 验证失败时抛出异常
        """
        errors = []
        
        for field, spec in schema.items():
            required = spec.get("required", False)
            field_type = spec.get("type")
            
            value = self.get(field)
            
            # 检查必需字段
            if required and value is None:
                errors.append(f"Missing required field: {field}")
                continue
            
            # 检查类型
            if value is not None and field_type is not None:
                if not isinstance(value, field_type):
                    errors.append(
                        f"Field '{field}' should be {field_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
        
        if errors:
            raise ConfigError("Validation failed: " + "; ".join(errors))
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            配置数据字典
        """
        return self._data.copy()
    
    def __repr__(self) -> str:
        return f"Config({self._data})"


class ConfigLoader:
    """
    配置加载器
    
    支持从多种来源加载配置：
    - YAML 文件
    - 字典
    - 环境变量
    
    Static Methods:
        from_yaml: 从 YAML 文件加载
        from_dict: 从字典创建
        from_env: 从环境变量加载
    """
    
    @staticmethod
    def from_yaml(path: Union[str, Path]) -> Config:
        """
        从 YAML 文件加载配置
        
        Args:
            path: YAML 文件路径
            
        Returns:
            Config 对象
            
        Raises:
            ConfigError: 文件不存在或解析失败时抛出
            
        Example:
            >>> config = ConfigLoader.from_yaml("config/interview.yaml")
        """
        path = Path(path)
        
        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")
        
        if not path.is_file():
            raise ConfigError(f"Config path is not a file: {path}")
        
        try:
            import yaml
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if data is None:
                data = {}
            
            return Config(data)
        
        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse YAML: {e}")
        except IOError as e:
            raise ConfigError(f"Failed to read file: {e}")
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Config:
        """
        从字典创建配置
        
        Args:
            data: 配置数据字典
            
        Returns:
            Config 对象
            
        Example:
            >>> config = ConfigLoader.from_dict({
            ...     "model": {"name": "deepseek"}
            ... })
        """
        if not isinstance(data, dict):
            raise ConfigError("Config data must be a dictionary")
        
        return Config(data)
    
    @staticmethod
    def from_env(prefix: str = "INTERVIEW_") -> Config:
        """
        从环境变量加载配置
        
        Args:
            prefix: 环境变量前缀
            
        Returns:
            Config 对象
            
        Example:
            >>> # 环境变量 INTERVIEW_MODEL_NAME=deepseek
            >>> config = ConfigLoader.from_env("INTERVIEW_")
            >>> config.get("model_name")  # "deepseek"
        """
        data = {}
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # 移除前缀并转换为小写
                config_key = key[len(prefix):].lower()
                data[config_key] = value
        
        return Config(data)
    
    @staticmethod
    def merge(*configs: Config) -> Config:
        """
        合并多个配置对象
        
        后面的配置会覆盖前面的同名配置
        
        Args:
            *configs: 要合并的配置对象列表
            
        Returns:
            合并后的 Config 对象
            
        Example:
            >>> config = ConfigLoader.merge(base_config, override_config)
        """
        result = {}
        
        for config in configs:
            result = ConfigLoader._deep_merge(result, config.to_dict())
        
        return Config(result)
    
    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> Dict:
        """深度合并两个字典"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigLoader._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result


# 默认配置
DEFAULT_CONFIG = {
    "model": {
        "name": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 2048,
    },
    "dialogue": {
        "max_turns": 10,
        "timeout_seconds": 300,
    },
    "agent": {
        "interviewer": {
            "style": "friendly",
            "domain": "general",
        },
    },
}
