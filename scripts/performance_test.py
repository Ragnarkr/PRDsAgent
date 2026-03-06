#!/usr/bin/env python3
"""
PRDsAgent 性能压测脚本
目标：500请求 + 20并发 + 10分钟模型
测量指标：P95/P99响应时间、成功率、5xx率、超时率
"""

import asyncio
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import statistics

import aiohttp
import requests
from tqdm import tqdm

# 配置参数
TEST_CONFIG = {
    "total_requests": 500,
    "concurrent_users": 20,
    "timeout_seconds": 30,
    "api_endpoint": "http://localhost:8080/analyze",  # 替换为实际API地址
    "test_files_dir": "./dataset/m1-v1/markdown",  # 测试文件目录
    "random_seed": 42,
    "max_test_duration_minutes": 10
}

class PerformanceTester:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = []
        self.start_time = None
        self.end_time = None
        self.random = random.Random(config["random_seed"])
        
        # 加载测试文件
        self.test_files = self._load_test_files()
        
    def _load_test_files(self) -> List[Path]:
        """加载测试文件列表"""
        files_dir = Path(self.config["test_files_dir"])
        if not files_dir.exists():
            raise FileNotFoundError(f"测试文件目录不存在: {files_dir}")
        
        # 支持多种格式
        markdown_files = list(files_dir.glob("*.md"))
        txt_files = list(files_dir.parent / "txt" / "*.txt")
        docx_files = list(files_dir.parent / "docx" / "*.docx")
        
        all_files = markdown_files + txt_files + docx_files
        if not all_files:
            raise FileNotFoundError(f"未找到测试文件: {files_dir}")
            
        return all_files
    
    async def send_request(self, session: aiohttp.ClientSession, file_path: Path) -> Dict[str, Any]:
        """发送单个请求并记录结果"""
        start_time = time.time()
        result = {
            "file": str(file_path),
            "start_time": start_time,
            "status_code": None,
            "response_time": None,
            "error": None,
            "is_timeout": False
        }
        
        try:
            # 读取文件内容
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # 构建请求
            data = aiohttp.FormData()
            data.add_field('file',
                          file_content,
                          filename=file_path.name,
                          content_type='application/octet-stream')
            
            # 发送请求
            async with session.post(
                self.config["api_endpoint"],
                data=data,
                timeout=aiohttp.ClientTimeout(total=self.config["timeout_seconds"])
            ) as response:
                result["status_code"] = response.status
                result["response_time"] = time.time() - start_time
                
                # 读取响应（可选）
                if response.status == 200:
                    try:
                        await response.json()
                    except:
                        pass  # 忽略响应解析错误
                        
        except asyncio.TimeoutError:
            result["is_timeout"] = True
            result["error"] = "timeout"
            result["response_time"] = time.time() - start_time
            
        except Exception as e:
            result["error"] = str(e)
            result["response_time"] = time.time() - start_time
            
        return result
    
    async def run_single_user(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """模拟单个用户的行为"""
        user_results = []
        requests_sent = 0
        
        while requests_sent < (self.config["total_requests"] // self.config["concurrent_users"]):
            # 随机选择一个测试文件
            file_path = self.random.choice(self.test_files)
            
            # 发送请求
            result = await self.send_request(session, file_path)
            user_results.append(result)
            requests_sent += 1
            
            # 随机延迟（模拟真实用户行为）
            await asyncio.sleep(self.random.uniform(0.1, 0.5))
            
        return user_results
    
    async def run_test(self) -> List[Dict[str, Any]]:
        """运行完整的性能测试"""
        print(f"开始性能测试...")
        print(f"总请求数: {self.config['total_requests']}")
        print(f"并发用户数: {self.config['concurrent_users']}")
        print(f"超时时间: {self.config['timeout_seconds']}秒")
        print(f"最大测试时长: {self.config['max_test_duration_minutes']}分钟")
        print("-" * 50)
        
        self.start_time = time.time()
        connector = aiohttp.TCPConnector(limit=self.config["concurrent_users"] * 2)
        timeout = aiohttp.ClientTimeout(total=self.config["timeout_seconds"])
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 创建并发任务
            tasks = [
                self.run_single_user(session)
                for _ in range(self.config["concurrent_users"])
            ]
            
            # 执行测试
            results = await asyncio.gather(*tasks)
            
        # 合并所有结果
        all_results = []
        for user_results in results:
            all_results.extend(user_results)
            
        self.end_time = time.time()
        self.results = all_results
        
        return all_results
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """计算性能指标"""
        if not self.results:
            return {}
            
        # 过滤有效响应时间
        valid_response_times = [
            r["response_time"] for r in self.results 
            if r["response_time"] is not None and not r["is_timeout"]
        ]
        
        # 计算成功率
        total_requests = len(self.results)
        successful_requests = len([
            r for r in self.results 
            if r["status_code"] and 200 <= r["status_code"] < 400
        ])
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        # 计算5xx错误率
        five_hundred_errors = len([
            r for r in self.results 
            if r["status_code"] and 500 <= r["status_code"] < 600
        ])
        five_hundred_rate = five_hundred_errors / total_requests if total_requests > 0 else 0
        
        # 计算超时率
        timeout_count = len([r for r in self.results if r["is_timeout"]])
        timeout_rate = timeout_count / total_requests if total_requests > 0 else 0
        
        # 计算响应时间百分位
        p95 = p99 = 0
        if valid_response_times:
            p95 = statistics.quantiles(valid_response_times, n=20)[-1]  # P95
            p99 = statistics.quantiles(valid_response_times, n=100)[-1]  # P99
        
        metrics = {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "five_hundred_errors": five_hundred_errors,
            "five_hundred_rate": five_hundred_rate,
            "timeout_count": timeout_count,
            "timeout_rate": timeout_rate,
            "p95_response_time": p95,
            "p99_response_time": p99,
            "test_duration_seconds": self.end_time - self.start_time,
            "requests_per_second": total_requests / (self.end_time - self.start_time) if self.end_time > self.start_time else 0
        }
        
        return metrics
    
    def print_report(self, metrics: Dict[str, Any]):
        """打印测试报告"""
        print("\n" + "="*60)
        print("性能测试报告")
        print("="*60)
        print(f"总请求数: {metrics['total_requests']}")
        print(f"测试时长: {metrics['test_duration_seconds']:.2f}秒")
        print(f"请求速率: {metrics['requests_per_second']:.2f} RPS")
        print()
        print(f"成功率: {metrics['success_rate']:.2%}")
        print(f"5xx错误率: {metrics['five_hundred_rate']:.2%}")
        print(f"超时率: {metrics['timeout_rate']:.2%}")
        print()
        print(f"P95响应时间: {metrics['p95_response_time']:.3f}秒")
        print(f"P99响应时间: {metrics['p99_response_time']:.3f}秒")
        print("="*60)
    
    def save_results(self, output_file: str = "performance_test_results.json"):
        """保存详细结果"""
        results_data = {
            "config": self.config,
            "metrics": self.calculate_metrics(),
            "results": self.results,
            "timestamp": time.time()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n详细结果已保存到: {output_file}")

async def main():
    """主函数"""
    tester = PerformanceTester(TEST_CONFIG)
    
    try:
        # 运行测试
        await tester.run_test()
        
        # 计算指标
        metrics = tester.calculate_metrics()
        
        # 打印报告
        tester.print_report(metrics)
        
        # 保存结果
        tester.save_results()
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())