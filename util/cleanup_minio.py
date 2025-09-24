#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow MinIO 存储桶清理工具
用于清空并删除所有MinIO存储桶
"""

import sys
from minio import Minio
from minio.error import S3Error
from minio.deleteobjects import DeleteObject
from config_loader import get_minio_config

def clear_all_buckets(auto_confirm=False):
    """
    连接到 MinIO，清空并删除所有存储桶。
    
    Args:
        auto_confirm: 是否自动确认删除操作，用于自动化脚本
    
    Returns:
        bool: 操作是否成功
    """
    try:
        # 1. 加载MinIO配置并初始化客户端
        minio_config = get_minio_config()
        
        minio_client = Minio(
            minio_config['endpoint'],
            access_key=minio_config['access_key'],
            secret_key=minio_config['secret_key'],
            secure=minio_config['secure']
        )
        print(f"✅ 成功连接到 MinIO: {minio_config['endpoint']}")

        # 2. 获取所有存储桶列表
        buckets = minio_client.list_buckets()
        bucket_names = [bucket.name for bucket in buckets]

        if not bucket_names:
            print("🟢 MinIO 中没有任何存储桶，无需操作。")
            return

        print(f"即将删除以下所有存储桶: {', '.join(bucket_names)}")
        
        # 在执行危险操作前，增加一个确认步骤
        if not auto_confirm:
            confirm = input("👉 请输入 'yes' 确认删除: ")
            if confirm.lower() != 'yes':
                print("❌ 操作已取消。")
                return False
        else:
            print("🤖 自动确认模式，跳过用户确认")
        
        # 3. 遍历并删除每一个存储桶
        for bucket_name in bucket_names:
            print(f"\n--- 正在处理存储桶: {bucket_name} ---")
            try:
                # 3.1 删除存储桶中的所有对象
                print(f"  - 正在清空对象...")
                objects_to_delete = minio_client.list_objects(bucket_name, recursive=True)
                # minio.remove_objects 需要一个 DeleteObject 列表
                delete_object_list = [DeleteObject(obj.object_name) for obj in objects_to_delete]
                
                # 如果列表不为空才执行删除
                if delete_object_list:
                    errors = minio_client.remove_objects(bucket_name, delete_object_list)
                    error_count = 0
                    for error in errors:
                        error_count += 1
                        print(f"  - 删除对象时出错: {error}")
                    if error_count == 0:
                        print(f"  - 成功清空存储桶 '{bucket_name}' 中的所有对象。")
                else:
                    print(f"  - 存储桶 '{bucket_name}' 本身就是空的。")

                # 3.2 删除空的存储桶
                minio_client.remove_bucket(bucket_name)
                print(f"  - ✅ 成功删除存储桶: {bucket_name}")

            except S3Error as exc:
                print(f"  - ❌ 处理存储桶 '{bucket_name}' 时出错: {exc}")

        print("\n🎉 所有MinIO存储桶清理完成！")
        return True

    except S3Error as exc:
        print(f"❌ 连接或操作 MinIO 时出错: {exc}")
        return False
    except Exception as exc:
        print(f"❌ 发生未知错误: {exc}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RAGFlow MinIO 存储桶清理工具')
    parser.add_argument('--auto-confirm', '-y', 
                       action='store_true',
                       help='自动确认删除操作，不需要用户输入')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("           RAGFlow MinIO 存储桶清理工具")
    print("=" * 60)
    print("⚠️  警告: 此操作将删除所有MinIO存储桶及其内容！")
    print("=" * 60)
    
    try:
        success = clear_all_buckets(auto_confirm=args.auto_confirm)
        
        if success:
            print("\n✅ 清理操作成功完成")
        else:
            print("\n❌ 清理操作失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
