#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow 统一配置加载模块
用于从docker/.env文件加载各种服务的配置信息
"""

import os
import sys
from typing import Dict, Optional

class ConfigLoader:
    """统一配置加载器"""
    
    def __init__(self, env_file_path: str = None):
        """初始化配置加载器
        
        Args:
            env_file_path: .env文件路径，默认为../docker/.env
        """
        if env_file_path is None:
            # 获取当前脚本所在目录的上级目录下的docker/.env
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            env_file_path = os.path.join(parent_dir, 'docker', '.env')
        
        self.env_file_path = env_file_path
        self._config = self._load_env_config()
    
    def _load_env_config(self) -> Dict[str, str]:
        """从.env文件加载配置"""
        if not os.path.exists(self.env_file_path):
            raise FileNotFoundError(f"配置文件不存在: {self.env_file_path}")
        
        config = {}
        try:
            with open(self.env_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    # 跳过空行和注释行
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析键值对
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 处理引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        config[key] = value
                    else:
                        print(f"警告: 第{line_num}行格式不正确: {line}")
        
        except Exception as e:
            raise Exception(f"读取配置文件失败: {e}")
        
        return config
    
    def get_mysql_config(self) -> Dict[str, any]:
        """获取MySQL配置"""
        return {
            'host': self._config.get('MYSQL_HOST', 'localhost'),
            'port': int(self._config.get('MYSQL_PORT', 3306)),
            'database': self._config.get('MYSQL_DBNAME', 'ragflow'),
            'user': self._config.get('MYSQL_USER', 'root'),
            'password': self._config.get('MYSQL_PASSWORD', '')
        }
    
    def get_minio_config(self) -> Dict[str, any]:
        """获取MinIO配置"""
        # 根据环境选择合适的主机地址
        minio_host = self._config.get('MINIO_HOST', 'localhost')
        minio_port = self._config.get('MINIO_PORT', '9000')
        
        # 如果是Docker环境中的服务名，转换为localhost用于本地访问
        if minio_host == 'minio':
            endpoint = f"localhost:{minio_port}"
        else:
            endpoint = f"{minio_host}:{minio_port}"
        
        return {
            'endpoint': endpoint,
            'access_key': self._config.get('MINIO_USER', 'rag_flow'),
            'secret_key': self._config.get('MINIO_PASSWORD', 'infini_rag_flow'),
            'secure': False  # 默认不使用HTTPS
        }
    
    def get_elasticsearch_config(self) -> Dict[str, any]:
        """获取ElasticSearch配置"""
        es_host = self._config.get('ES_HOST', 'localhost')
        es_port = self._config.get('ES_PORT', '9200')
        
        # 如果是Docker环境中的服务名，转换为localhost用于本地访问
        if es_host == 'es01':
            host = 'localhost'
        else:
            host = es_host
        
        return {
            'host': host,
            'port': int(es_port),
            'username': 'elastic',
            'password': self._config.get('ELASTIC_PASSWORD', 'infini_rag_flow'),
            'use_ssl': False,
            'verify_certs': False
        }
    
    def get_redis_config(self) -> Dict[str, any]:
        """获取Redis配置"""
        redis_host = self._config.get('REDIS_HOST', 'localhost')
        
        # 如果是Docker环境中的服务名，转换为localhost用于本地访问
        if redis_host == 'redis':
            host = 'localhost'
        else:
            host = redis_host
        
        return {
            'host': host,
            'port': int(self._config.get('REDIS_PORT', 6379)),
            'password': self._config.get('REDIS_PASSWORD', '')
        }
    
    def get_config_value(self, key: str, default: str = None) -> Optional[str]:
        """获取指定配置项的值
        
        Args:
            key: 配置项键名
            default: 默认值
            
        Returns:
            配置项的值，如果不存在则返回默认值
        """
        return self._config.get(key, default)
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("=" * 50)
        print("RAGFlow 配置摘要")
        print("=" * 50)
        print(f"配置文件: {self.env_file_path}")
        print()
        
        # MySQL配置
        mysql_config = self.get_mysql_config()
        print("MySQL配置:")
        print(f"  主机: {mysql_config['host']}:{mysql_config['port']}")
        print(f"  数据库: {mysql_config['database']}")
        print(f"  用户: {mysql_config['user']}")
        print()
        
        # MinIO配置
        minio_config = self.get_minio_config()
        print("MinIO配置:")
        print(f"  端点: {minio_config['endpoint']}")
        print(f"  用户: {minio_config['access_key']}")
        print()
        
        # ElasticSearch配置
        es_config = self.get_elasticsearch_config()
        print("ElasticSearch配置:")
        print(f"  主机: {es_config['host']}:{es_config['port']}")
        print(f"  用户: {es_config['username']}")
        print("=" * 50)


# 全局配置加载器实例
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """获取全局配置加载器实例"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


# 便捷函数
def get_mysql_config() -> Dict[str, any]:
    """获取MySQL配置的便捷函数"""
    return get_config_loader().get_mysql_config()

def get_minio_config() -> Dict[str, any]:
    """获取MinIO配置的便捷函数"""
    return get_config_loader().get_minio_config()

def get_elasticsearch_config() -> Dict[str, any]:
    """获取ElasticSearch配置的便捷函数"""
    return get_config_loader().get_elasticsearch_config()

def get_redis_config() -> Dict[str, any]:
    """获取Redis配置的便捷函数"""
    return get_config_loader().get_redis_config()


if __name__ == "__main__":
    # 测试配置加载
    try:
        config_loader = ConfigLoader()
        config_loader.print_config_summary()
    except Exception as e:
        print(f"配置加载失败: {e}")
        sys.exit(1)