
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow MinIO 存储桶检查工具
用于检查指定存储桶是否存在，并列出所有存储桶
"""

import os
import sys
from minio import Minio
from minio.error import S3Error
from config_loader import get_minio_config

# 要检查的存储桶名称（可以通过命令行参数指定）
DEFAULT_CHECK_BUCKET = 'aa2b7ed2979a11f09d05febcb89061f6'

def check_minio_buckets(check_bucket_name=None):
    """
    检查MinIO存储桶状态
    
    Args:
        check_bucket_name: 要检查的特定存储桶名称
    """
    try:
        # 加载MinIO配置
        minio_config = get_minio_config()
        
        # 初始化 MinIO 客户端
        minio_client = Minio(
            minio_config['endpoint'],
            access_key=minio_config['access_key'],
            secret_key=minio_config['secret_key'],
            secure=minio_config['secure']
        )
        print(f"✅ 成功连接到 MinIO 服务: {minio_config['endpoint']}")

        # 1. 检查指定的存储桶是否存在
        if check_bucket_name:
            print(f"\n--- 检查指定存储桶 ---")
            exists = minio_client.bucket_exists(check_bucket_name)
            if exists:
                print(f"🟢 存储桶 '{check_bucket_name}' 存在。")
            else:
                print(f"🟡 存储桶 '{check_bucket_name}' 不存在。")

        # 2. 列出所有可见的存储桶
        print("\n--- 列出所有存储桶 ---")
        buckets = minio_client.list_buckets()
        
        # 将生成器转换为列表以检查是否为空
        bucket_list = list(buckets)
        
        if not bucket_list:
            print("  - 未找到任何存储桶。")
        else:
            print("所有存储桶列表:")
            for bucket in bucket_list:
                print(f'  - {bucket.name} (创建时间: {bucket.creation_date})')
        
        return True

    except S3Error as exc:
        # 捕获S3相关的错误，例如认证失败
        if "AccessDenied" in str(exc):
            print(f"❌ 连接 MinIO 失败: 访问被拒绝。请检查配置文件中的 MINIO_USER 和 MINIO_PASSWORD 是否正确。")
        else:
            print(f"❌ 连接或操作 MinIO 时发生 S3 错误: {exc}")
        return False
    except Exception as exc:
        print(f"❌ 发生未知错误，请检查 MinIO 服务是否正在运行以及网络是否可达: {exc}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RAGFlow MinIO 存储桶检查工具')
    parser.add_argument('--bucket', '-b', 
                       help='要检查的存储桶名称', 
                       default=DEFAULT_CHECK_BUCKET)
    parser.add_argument('--list-only', '-l', 
                       action='store_true',
                       help='仅列出所有存储桶，不检查特定存储桶')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("           RAGFlow MinIO 存储桶检查工具")
    print("=" * 60)
    
    try:
        # 检查存储桶
        bucket_to_check = None if args.list_only else args.bucket
        success = check_minio_buckets(bucket_to_check)
        
        if success:
            print("\n✅ 检查完成")
        else:
            print("\n❌ 检查失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()