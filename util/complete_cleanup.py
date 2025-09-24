#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow完整数据清理脚本
整合MySQL数据库、ElasticSearch和MinIO的清理操作
"""

import os
import sys
import subprocess
import time
from config_loader import get_config_loader

def print_banner():
    """打印横幅"""
    print("="*60)
    print("           RAGFlow 完整数据清理工具")
    print("="*60)
    print("此工具将清理以下数据:")
    print("1. MySQL数据库中的文档、文件、任务等记录")
    print("2. ElasticSearch中的chunk数据")
    print("3. MinIO存储桶中的所有对象和存储桶")
    print("4. Redis缓存中的临时文件和队列数据")
    print("="*60)
    print()

def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    
    # 检查Python模块
    required_modules = ['mysql.connector', 'elasticsearch', 'minio', 'redis']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} 已安装")
        except ImportError:
            missing_modules.append(module)
            print(f"✗ {module} 未安装")
    
    if missing_modules:
        print(f"\n缺少依赖模块: {', '.join(missing_modules)}")
        print("请运行以下命令安装:")
        for module in missing_modules:
            if module == 'mysql.connector':
                print("  pip install mysql-connector-python")
            else:
                print(f"  pip install {module}")
        return False
    
    # 检查脚本文件
    required_files = [
        'cleanup_database.sql',
        'run_cleanup.py', 
        'cleanup_elasticsearch.py',
        'cleanup_minio.py',
        'cleanup_redis.py',
        'config_loader.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} 存在")
        else:
            print(f"✗ {file} 不存在")
            return False
    
    # 检查配置文件
    try:
        config_loader = get_config_loader()
        config_loader.print_config_summary()
        print("\n✓ 配置文件加载成功")
    except Exception as e:
        print(f"\n✗ 配置文件加载失败: {e}")
        return False
    
    print("\n所有依赖检查通过!\n")
    return True

def run_mysql_cleanup():
    """运行MySQL清理"""
    print("步骤 1: 清理MySQL数据库")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, 'run_cleanup.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("MySQL清理成功完成!")
            print(result.stdout)
            return True
        else:
            print("MySQL清理失败!")
            print("错误输出:", result.stderr)
            return False
            
    except Exception as e:
        print(f"运行MySQL清理脚本时出错: {e}")
        return False

def run_elasticsearch_cleanup():
    """运行ElasticSearch清理"""
    print("\n步骤 2: 清理ElasticSearch数据")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, 'cleanup_elasticsearch.py', '--auto-confirm'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("ElasticSearch清理成功完成!")
            print(result.stdout)
            return True
        else:
            print("ElasticSearch清理失败!")
            print("错误输出:", result.stderr)
            return False
            
    except Exception as e:
        print(f"运行ElasticSearch清理脚本时出错: {e}")
        return False

def run_minio_cleanup():
    """运行MinIO清理"""
    print("\n步骤 3: 清理MinIO存储桶")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, 'cleanup_minio.py', '--auto-confirm'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("MinIO清理成功完成!")
            print(result.stdout)
            return True
        else:
            print("MinIO清理失败!")
            print("错误输出:", result.stderr)
            return False
            
    except Exception as e:
        print(f"运行MinIO清理脚本时出错: {e}")
        return False

def run_redis_cleanup():
    """运行Redis清理"""
    print("\n步骤 4: 清理Redis缓存")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, 'cleanup_redis.py', '--auto-confirm'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("Redis清理成功完成!")
            print(result.stdout)
            return True
        else:
            print("Redis清理失败!")
            print("错误输出:", result.stderr)
            return False
            
    except Exception as e:
        print(f"运行Redis清理脚本时出错: {e}")
        return False

def interactive_cleanup():
    """交互式清理"""
    print("交互式清理模式")
    print("您可以选择要执行的清理步骤:\n")
    
    print("1. 仅清理MySQL数据库")
    print("2. 仅清理ElasticSearch")
    print("3. 仅清理MinIO存储桶")
    print("4. 仅清理Redis缓存")
    print("5. 清理数据库和搜索引擎（MySQL + ElasticSearch）")
    print("6. 清理存储和缓存（MinIO + Redis）")
    print("7. 清理所有数据（MySQL + ElasticSearch + MinIO + Redis）")
    print("8. 退出")
    
    choice = input("\n请选择操作 (1-8): ").strip()
    
    if choice == '1':
        return run_mysql_cleanup()
    elif choice == '2':
        return run_elasticsearch_cleanup()
    elif choice == '3':
        return run_minio_cleanup()
    elif choice == '4':
        return run_redis_cleanup()
    elif choice == '5':
        mysql_success = run_mysql_cleanup()
        if mysql_success:
            time.sleep(2)  # 等待2秒
            es_success = run_elasticsearch_cleanup()
            return mysql_success and es_success
        return False
    elif choice == '6':
        minio_success = run_minio_cleanup()
        if minio_success:
            time.sleep(2)
            redis_success = run_redis_cleanup()
            return minio_success and redis_success
        return False
    elif choice == '7':
        mysql_success = run_mysql_cleanup()
        if mysql_success:
            time.sleep(2)
            es_success = run_elasticsearch_cleanup()
            if es_success:
                time.sleep(2)
                minio_success = run_minio_cleanup()
                if minio_success:
                    time.sleep(2)
                    redis_success = run_redis_cleanup()
                    return mysql_success and es_success and minio_success and redis_success
        return False
    elif choice == '8':
        print("操作已取消")
        return False
    else:
        print("无效选择")
        return False

def automated_cleanup():
    """自动化清理（清理所有数据）"""
    print("自动化清理模式 - 将清理所有数据")
    
    confirm = input("\n警告: 此操作将删除所有文档和文件数据，是否继续？(输入 'YES' 确认): ")
    if confirm != 'YES':
        print("操作已取消")
        return False
    
    # 执行MySQL清理
    mysql_success = run_mysql_cleanup()
    if not mysql_success:
        print("MySQL清理失败，停止后续操作")
        return False
    
    time.sleep(2)  # 等待2秒
    
    # 执行ElasticSearch清理
    es_success = run_elasticsearch_cleanup()
    if not es_success:
        print("ElasticSearch清理失败，停止后续操作")
        return False
    
    time.sleep(2)  # 等待2秒
    
    # 执行MinIO清理
    minio_success = run_minio_cleanup()
    if not minio_success:
        print("MinIO清理失败，停止后续操作")
        return False
    
    time.sleep(2)  # 等待2秒
    
    # 执行Redis清理
    redis_success = run_redis_cleanup()
    
    return mysql_success and es_success and minio_success and redis_success

def print_cleanup_summary():
    """打印清理总结"""
    print("\n" + "="*60)
    print("                   清理完成总结")
    print("="*60)
    print("已完成的清理操作:")
    print("✓ MySQL数据库记录清理")
    print("✓ ElasticSearch chunk数据清理")
    print("✓ MinIO存储桶清理")
    print("✓ Redis缓存数据清理")
    print()
    print("建议的后续操作:")
    print("1. 重启RAGFlow服务以清理内存缓存")
    print("2. 验证系统功能是否正常")
    print("3. 重新上传和处理文档")
    print("4. 检查各服务连接状态")
    print("="*60)

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        print("\n请先安装缺少的依赖，然后重新运行此脚本")
        return
    
    # 选择运行模式
    print("运行模式:")
    print("1. 交互式清理（推荐）")
    print("2. 自动化清理（清理所有数据）")
    print("3. 退出")
    
    mode = input("\n请选择运行模式 (1-3): ").strip()
    
    success = False
    
    if mode == '1':
        success = interactive_cleanup()
    elif mode == '2':
        success = automated_cleanup()
    elif mode == '3':
        print("程序退出")
        return
    else:
        print("无效选择")
        return
    
    if success:
        print_cleanup_summary()
    else:
        print("\n清理过程中遇到错误，请检查日志并手动处理")

if __name__ == "__main__":
    main()