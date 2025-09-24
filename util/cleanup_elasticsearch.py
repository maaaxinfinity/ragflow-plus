#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow ElasticSearch 清理工具
用于清理ElasticSearch中的RAGFlow相关索引和数据
"""

import os
import sys
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
from config_loader import get_elasticsearch_config

def get_elasticsearch_client(config):
    """创建ElasticSearch客户端"""
    try:
        # 构建连接URL
        scheme = 'https' if config['use_ssl'] else 'http'
        url = f"{scheme}://{config['host']}:{config['port']}"
        
        if config['username'] and config['password']:
            es = Elasticsearch(
                [url],
                basic_auth=(config['username'], config['password']),
                verify_certs=False,
                request_timeout=30
            )
        else:
            es = Elasticsearch(
                [url],
                verify_certs=False,
                request_timeout=30
            )
        
        # 测试连接
        if es.ping():
            print("ElasticSearch连接成功!")
            return es
        else:
            print("ElasticSearch连接失败!")
            return None
            
    except Exception as e:
        print(f"创建ElasticSearch客户端时出错: {e}")
        return None

def list_all_indices(es):
    """列出所有索引"""
    try:
        indices = es.indices.get_alias("*")
        return list(indices.keys())
    except Exception as e:
        print(f"获取索引列表时出错: {e}")
        return []

def get_ragflow_indices(es):
    """获取RAGFlow相关的索引（通常以tenant_id命名）"""
    all_indices = list_all_indices(es)
    
    # RAGFlow的索引通常是32位的tenant_id
    ragflow_indices = []
    for index in all_indices:
        # 过滤掉系统索引（以.开头）
        if not index.startswith('.') and len(index) == 32:
            ragflow_indices.append(index)
    
    return ragflow_indices

def count_documents_in_index(es, index_name):
    """统计索引中的文档数量"""
    try:
        result = es.count(index=index_name)
        return result['count']
    except Exception as e:
        print(f"统计索引 {index_name} 文档数量时出错: {e}")
        return 0

def delete_all_documents_in_index(es, index_name):
    """删除索引中的所有文档"""
    try:
        # 使用delete_by_query删除所有文档
        query = {
            "query": {
                "match_all": {}
            }
        }
        
        result = es.delete_by_query(
            index=index_name,
            body=query,
            wait_for_completion=True,
            refresh=True
        )
        
        return result.get('deleted', 0)
        
    except Exception as e:
        print(f"删除索引 {index_name} 中的文档时出错: {e}")
        return 0

def delete_index(es, index_name):
    """删除整个索引"""
    try:
        es.indices.delete(index=index_name)
        print(f"索引 {index_name} 已删除")
        return True
    except NotFoundError:
        print(f"索引 {index_name} 不存在")
        return False
    except Exception as e:
        print(f"删除索引 {index_name} 时出错: {e}")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RAGFlow ElasticSearch清理工具')
    parser.add_argument('--auto-confirm', action='store_true', 
                       help='自动确认所有操作，不需要用户交互')
    parser.add_argument('--operation', choices=['delete-docs', 'delete-indices'], 
                       default='delete-docs', help='清理操作类型')
    
    args = parser.parse_args()
    
    print("RAGFlow ElasticSearch清理工具")
    print("=" * 50)
    
    # 加载配置
    config = get_elasticsearch_config()
    print(f"ElasticSearch配置:")
    print(f"  主机: {config['host']}")
    print(f"  端口: {config['port']}")
    print(f"  SSL: {config['use_ssl']}")
    print()
    
    # 创建ES客户端
    es = get_elasticsearch_client(config)
    if not es:
        return
    
    # 获取RAGFlow相关索引
    ragflow_indices = get_ragflow_indices(es)
    
    if not ragflow_indices:
        print("未找到RAGFlow相关的索引")
        return
    
    print(f"找到 {len(ragflow_indices)} 个RAGFlow索引:")
    total_docs = 0
    for index in ragflow_indices:
        doc_count = count_documents_in_index(es, index)
        total_docs += doc_count
        print(f"  {index}: {doc_count} 个文档")
    
    print(f"\n总计: {total_docs} 个文档")
    
    if total_docs == 0:
        print("没有需要清理的文档")
        return
    
    if args.auto_confirm:
        # 自动确认模式
        if args.operation == 'delete-docs':
            print("\n自动执行: 删除所有文档但保留索引结构")
            print("\n开始清理文档...")
            total_deleted = 0
            for index in ragflow_indices:
                print(f"正在清理索引: {index}")
                deleted = delete_all_documents_in_index(es, index)
                total_deleted += deleted
                print(f"  已删除 {deleted} 个文档")
            
            print(f"\n清理完成! 总共删除了 {total_deleted} 个文档")
        else:
            print("\n自动执行: 删除整个索引")
            print("\n开始删除索引...")
            deleted_count = 0
            for index in ragflow_indices:
                print(f"正在删除索引: {index}")
                if delete_index(es, index):
                    deleted_count += 1
            
            print(f"\n删除完成! 总共删除了 {deleted_count} 个索引")
    else:
        # 交互模式
        print("\n清理选项:")
        print("1. 删除所有文档但保留索引结构")
        print("2. 删除整个索引（包括结构）")
        print("3. 取消操作")
        
        choice = input("\n请选择操作 (1/2/3): ").strip()
        
        if choice == '1':
            # 删除文档但保留索引
            confirm = input(f"确认删除 {total_docs} 个文档？(输入 'YES' 确认): ")
            if confirm != 'YES':
                print("操作已取消")
                return
            
            print("\n开始清理文档...")
            total_deleted = 0
            for index in ragflow_indices:
                print(f"正在清理索引: {index}")
                deleted = delete_all_documents_in_index(es, index)
                total_deleted += deleted
                print(f"  已删除 {deleted} 个文档")
            
            print(f"\n清理完成! 总共删除了 {total_deleted} 个文档")
        
        elif choice == '2':
            # 删除整个索引
            confirm = input(f"确认删除 {len(ragflow_indices)} 个索引？(输入 'YES' 确认): ")
            if confirm != 'YES':
                print("操作已取消")
                return
            
            print("\n开始删除索引...")
            deleted_count = 0
            for index in ragflow_indices:
                print(f"正在删除索引: {index}")
                if delete_index(es, index):
                    deleted_count += 1
            
            print(f"\n删除完成! 总共删除了 {deleted_count} 个索引")
        
        elif choice == '3':
            print("操作已取消")
            return
        
        else:
            print("无效选择")
            return
    
    # 验证清理结果
    print("\n验证清理结果...")
    remaining_indices = get_ragflow_indices(es)
    if remaining_indices:
        print(f"剩余索引: {len(remaining_indices)}")
        for index in remaining_indices:
            doc_count = count_documents_in_index(es, index)
            print(f"  {index}: {doc_count} 个文档")
    else:
        print("所有RAGFlow索引已清理完成")

if __name__ == "__main__":
    main()