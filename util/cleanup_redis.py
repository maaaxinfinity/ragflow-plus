#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow Redis缓存清理脚本
用于清理Redis中的所有缓存数据
"""

import sys
import time
from config_loader import get_redis_config

def print_banner():
    """打印横幅"""
    print("="*50)
    print("         RAGFlow Redis 缓存清理工具")
    print("="*50)
    print("此工具将清理Redis中的以下数据:")
    print("1. 临时文件缓存 (temp_file:*)")
    print("2. 文档处理队列 (rag_flow_svr_queue)")
    print("3. 任务执行器心跳数据 (TASKEXE, task_executor_*)")
    print("4. 文件缓存数据 (kb_id/location格式)")
    print("5. 其他应用缓存数据")
    print("="*50)
    print()

def get_redis_client():
    """获取Redis客户端"""
    try:
        import redis
    except ImportError:
        print("错误: 未安装redis模块")
        print("请运行: pip install redis")
        return None
    
    config = get_redis_config()
    
    try:
        client = redis.Redis(
            host=config['host'],
            port=config['port'],
            password=config['password'] if config['password'] else None,
            decode_responses=True,
            socket_timeout=10,
            socket_connect_timeout=10
        )
        
        # 测试连接
        client.ping()
        print(f"✓ 成功连接到Redis: {config['host']}:{config['port']}")
        return client
        
    except Exception as e:
        print(f"✗ 连接Redis失败: {e}")
        print(f"请检查Redis服务是否运行在 {config['host']}:{config['port']}")
        return None

def cleanup_redis_data(client, auto_confirm=False):
    """清理Redis数据"""
    print("\n开始清理Redis缓存数据...")
    
    if not auto_confirm:
        confirm = input("\n警告: 此操作将删除Redis中的所有缓存数据，是否继续？(输入 'YES' 确认): ")
        if confirm != 'YES':
            print("操作已取消")
            return False
    
    try:
        # 获取所有键
        all_keys = client.keys('*')
        total_keys = len(all_keys)
        
        if total_keys == 0:
            print("Redis中没有数据需要清理")
            return True
        
        print(f"\n发现 {total_keys} 个缓存键，开始清理...")
        
        # 分类统计
        categories = {
            'temp_files': [],
            'queues': [],
            'task_executors': [],
            'file_cache': [],
            'others': []
        }
        
        for key in all_keys:
            if key.startswith('temp_file:'):
                categories['temp_files'].append(key)
            elif 'queue' in key.lower():
                categories['queues'].append(key)
            elif key.startswith('TASKEXE') or key.startswith('task_executor_'):
                categories['task_executors'].append(key)
            elif '/' in key and not key.startswith('temp_file:'):
                categories['file_cache'].append(key)
            else:
                categories['others'].append(key)
        
        # 显示分类统计
        print("\n缓存数据分类统计:")
        print(f"  临时文件缓存: {len(categories['temp_files'])} 个")
        print(f"  队列数据: {len(categories['queues'])} 个")
        print(f"  任务执行器数据: {len(categories['task_executors'])} 个")
        print(f"  文件缓存数据: {len(categories['file_cache'])} 个")
        print(f"  其他缓存数据: {len(categories['others'])} 个")
        
        # 批量删除
        deleted_count = 0
        batch_size = 100
        
        for i in range(0, total_keys, batch_size):
            batch_keys = all_keys[i:i + batch_size]
            deleted = client.delete(*batch_keys)
            deleted_count += deleted
            print(f"已清理 {deleted_count}/{total_keys} 个缓存键...")
        
        print(f"\n✓ Redis缓存清理完成！共删除 {deleted_count} 个缓存键")
        
        # 验证清理结果
        remaining_keys = client.keys('*')
        if remaining_keys:
            print(f"警告: 仍有 {len(remaining_keys)} 个键未被清理")
            return False
        else:
            print("✓ 验证通过：Redis中已无缓存数据")
            return True
            
    except Exception as e:
        print(f"✗ 清理Redis数据时出错: {e}")
        return False

def get_redis_info(client):
    """获取Redis信息"""
    try:
        info = client.info()
        print("\nRedis服务器信息:")
        print(f"  版本: {info.get('redis_version', 'Unknown')}")
        print(f"  内存使用: {info.get('used_memory_human', 'Unknown')}")
        print(f"  连接数: {info.get('connected_clients', 'Unknown')}")
        print(f"  键总数: {info.get('db0', {}).get('keys', 0) if 'db0' in info else 0}")
        
        # 获取键空间信息
        keyspace_info = client.info('keyspace')
        if keyspace_info:
            print("\n键空间信息:")
            for db, stats in keyspace_info.items():
                if db.startswith('db'):
                    print(f"  {db}: {stats}")
        
    except Exception as e:
        print(f"获取Redis信息失败: {e}")

def main():
    """主函数"""
    print_banner()
    
    # 检查命令行参数
    auto_confirm = '--auto-confirm' in sys.argv
    
    # 获取Redis客户端
    client = get_redis_client()
    if not client:
        return
    
    # 显示Redis信息
    get_redis_info(client)
    
    # 执行清理
    success = cleanup_redis_data(client, auto_confirm)
    
    if success:
        print("\n" + "="*50)
        print("Redis缓存清理成功完成！")
        print("建议重启RAGFlow服务以确保缓存完全清理")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("Redis缓存清理失败，请检查错误信息")
        print("="*50)
        sys.exit(1)

if __name__ == "__main__":
    main()