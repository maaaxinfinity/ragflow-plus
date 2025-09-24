#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow数据库清理执行脚本
用于连接MySQL数据库并执行清理SQL脚本
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from config_loader import get_mysql_config

def execute_sql_file(connection, sql_file):
    """执行SQL文件"""
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句（以分号分隔）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        cursor = connection.cursor()
        results = []
        
        for i, statement in enumerate(sql_statements):
            if statement.upper().startswith('--') or not statement:
                continue
                
            try:
                print(f"执行语句 {i+1}/{len(sql_statements)}: {statement[:50]}...")
                cursor.execute(statement)
                
                # 如果是SELECT语句，获取结果
                if statement.upper().strip().startswith('SELECT'):
                    result = cursor.fetchall()
                    if result:
                        print(f"结果: {result}")
                        results.append(result)
                else:
                    # 对于其他语句，显示影响的行数
                    if cursor.rowcount >= 0:
                        print(f"影响行数: {cursor.rowcount}")
                
                connection.commit()
                
            except Error as e:
                print(f"执行语句时出错: {e}")
                print(f"问题语句: {statement}")
                connection.rollback()
                continue
        
        cursor.close()
        return results
        
    except Exception as e:
        print(f"读取或执行SQL文件时出错: {e}")
        return None

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RAGFlow数据库清理工具')
    parser.add_argument('--auto-confirm', '-y', 
                       action='store_true',
                       help='自动确认清理操作，不需要用户输入')
    parser.add_argument('--sql-file', '-f',
                       default='cleanup_database.sql',
                       help='要执行的SQL清理脚本文件路径')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("           RAGFlow数据库清理工具")
    print("=" * 60)
    
    try:
        # 加载配置
        config = get_mysql_config()
        
        print(f"数据库配置:")
        print(f"  主机: {config['host']}:{config['port']}")
        print(f"  数据库: {config['database']}")
        print(f"  用户: {config['user']}")
        print()
        
        # 确认操作
        print("⚠️  警告: 此操作将删除数据库中的所有文档、文件和相关数据!")
        if not args.auto_confirm:
            confirm = input("请输入 'YES' 确认继续: ")
            if confirm != 'YES':
                print("操作已取消")
                return False
        else:
            print("🤖 自动确认模式，跳过用户确认")
    
    except Exception as e:
        print(f"配置加载失败: {e}")
        return False
    
    # 连接数据库
    try:
        print("正在连接数据库...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("数据库连接成功!")
            
            # 执行清理SQL
            sql_file = args.sql_file
            if not os.path.exists(sql_file):
                print(f"错误: 找不到SQL文件 {sql_file}")
                return False
            
            print(f"\n开始执行清理脚本: {sql_file}")
            print("-" * 50)
            
            results = execute_sql_file(connection, sql_file)
            
            print("-" * 50)
            print("清理脚本执行完成!")
            
            if results:
                print("\n执行结果摘要:")
                for result in results:
                    print(result)
            
            print("\n✅ 数据库清理操作成功完成")
            return True
    
    except Error as e:
        print(f"❌ 数据库连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")
        return False
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("\n数据库连接已关闭")

if __name__ == "__main__":
    main()