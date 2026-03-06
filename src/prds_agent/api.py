"""
PRDsAgent API Service
开发工程师: 王浩然
任务: 实现基于FastAPI的Web服务，集成现有规则引擎

技术难点识别:
1. 文件上传处理 - 需要支持多格式文件
2. 异步处理 - 避免大文件阻塞服务
3. 错误处理 - 统一的错误响应格式
4. 性能优化 - 满足P95≤6s的性能要求

开发约束条件:
- Python 3.8+
- FastAPI框架
- 必须复用现有的规则引擎代码
- 必须符合API接口规范v0.1
"""

import tempfile
import traceback
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from prds_agent.parsers import DocumentParser
from prds_agent.rules import RuleEngine
from prds_agent.rules.models import RuleReport

# 应用配置
app = FastAPI(
    title="PRDsAgent API",
    description="需求文档质量分析服务",
    version="0.1.0"
)

# CORS配置（开发阶段）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局配置
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_EXTENSIONS = {".md", ".markdown", ".txt", ".docx"}

class APIError(Exception):
    """API自定义异常"""
    def __init__(self, code: int, message: str, details: Optional[str] = None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

@app.exception_handler(APIError)
async def api_error_handler(request, exc: APIError):
    """API错误处理器"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """全局异常处理器"""
    print(f"Unexpected error: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 5000,
            "message": "Internal server error",
            "details": str(exc)
        }
    )

@app.get("/health")
async def health_check():
    """
    健康检查端点
    返回服务状态和版本信息
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": "2026-03-06T00:03:00Z"
    }

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """
    分析需求文档
    
    支持格式: .md, .markdown, .txt, .docx
    最大文件大小: 10MB
    
    Args:
        file: 上传的需求文档文件
        
    Returns:
        JSON格式的分析报告
        
    Raises:
        APIError: 文件类型不支持、文件过大等错误
    """
    # 1. 验证文件类型
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in SUPPORTED_EXTENSIONS:
        raise APIError(
            code=1001,
            message="Invalid file type",
            details=f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    
    # 2. 验证文件大小
    # 注意: FastAPI会将小文件加载到内存，大文件需要流式处理
    # 这里简化处理，实际生产环境需要更复杂的文件大小检查
    try:
        # 读取文件内容
        content = await file.read()
        
        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise APIError(
                code=1002,
                message="File too large",
                details=f"Maximum size: {MAX_FILE_SIZE} bytes"
            )
            
        # 3. 保存临时文件
        with tempfile.NamedTemporaryFile(
            suffix=file_extension, 
            delete=False,
            dir="/tmp"
        ) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
            
        # 4. 解析文档
        try:
            parser = DocumentParser()
            parsed_doc = parser.parse(temp_file_path)
        except ValueError as e:
            # 文档解析失败
            Path(temp_file_path).unlink(missing_ok=True)
            raise APIError(
                code=2000,
                message="Document parse error",
                details=str(e)
            )
        except Exception as e:
            # 其他解析错误
            Path(temp_file_path).unlink(missing_ok=True)
            raise APIError(
                code=2000,
                message="Document parse error",
                details=f"Unexpected parse error: {str(e)}"
            )
            
        # 5. 执行规则引擎分析
        try:
            rule_engine = RuleEngine()
            report: RuleReport = rule_engine.analyze(parsed_doc)
        except Exception as e:
            # 规则引擎执行失败
            Path(temp_file_path).unlink(missing_ok=True)
            raise APIError(
                code=5000,
                message="Analysis engine error",
                details=f"Rule engine failed: {str(e)}"
            )
            
        # 6. 清理临时文件
        Path(temp_file_path).unlink(missing_ok=True)
        
        # 7. 构建响应
        issues_data = []
        for issue in report.issues:
            issue_dict = {
                "rule_id": issue.rule_id,
                "category": issue.category,
                "severity": issue.severity,
                "message": issue.message,
                "suggestion": issue.suggestion,
                "evidence": issue.evidence
            }
            if hasattr(issue, 'line_no') and issue.line_no:
                issue_dict["line_no"] = issue.line_no
                
            issues_data.append(issue_dict)
            
        return JSONResponse(
            content={
                "code": 200,
                "message": "success",
                "data": {
                    "source_path": file.filename,
                    "issues": issues_data
                }
            }
        )
        
    except APIError:
        # 重新抛出API错误
        raise
    except Exception as e:
        # 捕获其他未预期的错误
        raise APIError(
            code=5000,
            message="Internal server error",
            details=f"Unexpected error during analysis: {str(e)}"
        )

# 开发服务器启动入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "prds_agent.api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )