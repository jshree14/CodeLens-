"""
API routes for CodeLens AI
Handles code analysis and report endpoints
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, validator

from analyzers.static_analyzer import StaticAnalyzer
from analyzers.ai_analyzer import AIAnalyzer
from utils.language_detector import detect_language
from database import get_database, DatabaseManager
from models import CodeAnalysisResult, AnalysisSummary, AnalysisMetrics, AnalysisIssue
from executors.code_executor import code_executor
from cache import analysis_cache
from rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api", tags=["analysis"])

# Initialize analyzers
static_analyzer = StaticAnalyzer()
ai_analyzer = AIAnalyzer()


# Request/Response models
class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "auto"  # auto-detect by default
    execute: bool = True  # Execute code by default
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    @validator('code')
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Code cannot be empty')
        if len(v) > 50000:
            raise ValueError('Code too long (maximum 50,000 characters)')
        return v
    
    @validator('language')
    def validate_language(cls, v):
        allowed = ['auto', 'python', 'javascript', 'typescript', 'java', 'cpp', 'c']
        if v not in allowed:
            raise ValueError(f'Language must be one of: {", ".join(allowed)}')
        return v


class ImprovementSuggestion(BaseModel):
    title: str
    description: str
    priority: str
    suggestion: str

class SecurityConcern(BaseModel):
    title: str
    description: str
    severity: str
    mitigation: str

class PerformanceNote(BaseModel):
    title: str
    description: str
    suggestion: str

class ExecutionResult(BaseModel):
    output: str
    error: str
    execution_time: float
    success: bool

class CodeAnalysisResponse(BaseModel):
    id: Optional[str] = None  # Database ID if saved
    summary: AnalysisSummary
    issues: List[AnalysisIssue]
    improvements: List[ImprovementSuggestion] = []
    security_concerns: List[SecurityConcern] = []
    performance_notes: List[PerformanceNote] = []
    metrics: AnalysisMetrics
    execution: Optional[ExecutionResult] = None  # Code execution output
    language: str
    created_at: Optional[str] = None


class ReportResponse(BaseModel):
    total_analyses: int
    languages_used: List[str]
    average_score: float
    recent_analyses: List[CodeAnalysisResponse]
    language_stats: Dict[str, int]


@router.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(
    analysis_request: CodeAnalysisRequest,
    request: Request,
    db: DatabaseManager = Depends(get_database)
):
    """
    Analyze code using both static analysis and AI
    Returns comprehensive analysis results
    """
    # Rate limiting
    client_ip = request.client.host
    is_allowed, remaining = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again in a minute.",
            headers={"X-RateLimit-Remaining": "0"}
        )
    
    try:
        logger.info(f"Starting analysis for {len(analysis_request.code)} characters of code (IP: {client_ip}, remaining: {remaining})")
        
        # Detect language if auto-detect is requested
        detected_language = detect_language(
            analysis_request.code, 
            analysis_request.language if analysis_request.language != "auto" else None
        )
        
        logger.info(f"Detected language: {detected_language}")
        
        # Check cache first (skip if execution is requested for fresh results)
        if not analysis_request.execute:
            cached_result = analysis_cache.get(analysis_request.code, detected_language)
            if cached_result:
                logger.info("Returning cached analysis result")
                return CodeAnalysisResponse(**cached_result)
        
        # Execute code if requested
        execution_result = None
        if analysis_request.execute:
            logger.info("Executing code...")
            exec_data = await code_executor.execute(analysis_request.code, detected_language)
            execution_result = ExecutionResult(**exec_data)
            logger.info(f"Code execution completed: {execution_result.success}")
        
        # Run static and AI analysis in parallel for better performance
        import asyncio
        static_task = static_analyzer.analyze(analysis_request.code, detected_language)
        ai_task = ai_analyzer.analyze(analysis_request.code, detected_language)
        
        static_results, ai_results = await asyncio.gather(static_task, ai_task)
        logger.info("Static and AI analysis completed")
        
        # Calculate overall score
        overall_score = calculate_overall_score(static_results, ai_results)
        
        # Create analysis summary with enhanced AI results
        summary = AnalysisSummary(
            purpose=ai_results.get("purpose", "Code analysis completed"),
            overview=ai_results.get("overview", "Analysis overview not available"),
            score=overall_score
        )
        
        # Combine issues from both analyzers
        combined_issues = combine_issues(
            static_results.get("issues", []), 
            ai_results.get("issues", [])
        )
        
        # Extract improvements, security concerns, and performance notes from AI results
        improvements = [
            ImprovementSuggestion(**imp) 
            for imp in ai_results.get("improvements", [])
        ]
        
        security_concerns = [
            SecurityConcern(**sec) 
            for sec in ai_results.get("security_concerns", [])
        ]
        
        performance_notes = [
            PerformanceNote(**perf) 
            for perf in ai_results.get("performance_notes", [])
        ]
        
        # Create metrics object from static analysis
        metrics_data = static_results.get("metrics", {})
        metrics = AnalysisMetrics(
            lines=metrics_data.get("total_lines", metrics_data.get("lines", 0)),
            functions=metrics_data.get("functions", 0),
            classes=metrics_data.get("classes", 0),
            loops=metrics_data.get("loops", 0),
            conditions=metrics_data.get("conditions", 0),
            complexity=static_results.get("complexity_analysis", {}).get("cyclomatic_complexity", metrics_data.get("complexity", 1))
        )
        
        # Create analysis result for database
        analysis_result = CodeAnalysisResult(
            code_snippet=analysis_request.code[:1000],  # Store first 1000 chars
            language=detected_language,
            summary=summary,
            issues=combined_issues,
            metrics=metrics,
            user_id=analysis_request.user_id,
            session_id=analysis_request.session_id
        )
        
        # Save to database (if connected)
        saved_id = await db.save_analysis(analysis_result)
        
        # Create response with all analysis data including execution
        response = CodeAnalysisResponse(
            id=saved_id,
            summary=summary,
            issues=combined_issues,
            improvements=improvements,
            security_concerns=security_concerns,
            performance_notes=performance_notes,
            metrics=metrics,
            execution=execution_result,
            language=detected_language,
            created_at=analysis_result.created_at.isoformat() if analysis_result.created_at else None
        )
        
        # Cache the result (without execution data for consistency)
        if not analysis_request.execute:
            cache_data = response.dict()
            cache_data.pop('execution', None)  # Don't cache execution results
            analysis_cache.set(analysis_request.code, detected_language, cache_data)
        
        logger.info(f"Analysis completed successfully with score: {overall_score}")
        return response
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/report", response_model=ReportResponse)
async def get_analysis_report(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    days: int = Query(30, description="Number of days to include in report"),
    db: DatabaseManager = Depends(get_database)
):
    """
    Get analysis report with history and statistics
    """
    try:
        logger.info(f"Generating report for user_id: {user_id}, days: {days}")
        
        # Get analysis history
        history = await db.get_analysis_history(user_id=user_id, days=days)
        
        # Get language statistics
        language_stats = await db.get_language_statistics()
        
        # Convert recent analyses to response format
        recent_analyses = []
        for analysis in history.recent_analyses:
            recent_analyses.append(CodeAnalysisResponse(
                id=str(analysis.id),
                summary=analysis.summary,
                issues=analysis.issues,
                metrics=analysis.metrics,
                language=analysis.language,
                created_at=analysis.created_at.isoformat()
            ))
        
        response = ReportResponse(
            total_analyses=history.total_analyses,
            languages_used=history.languages_used,
            average_score=history.average_score,
            recent_analyses=recent_analyses,
            language_stats=language_stats
        )
        
        logger.info(f"Report generated: {history.total_analyses} analyses found")
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/analysis/{analysis_id}")
async def get_analysis_by_id(
    analysis_id: str,
    db: DatabaseManager = Depends(get_database)
):
    """
    Get specific analysis result by ID
    """
    try:
        analysis = await db.get_analysis_by_id(analysis_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return CodeAnalysisResponse(
            id=str(analysis.id),
            summary=analysis.summary,
            issues=analysis.issues,
            metrics=analysis.metrics,
            language=analysis.language,
            created_at=analysis.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis")


@router.get("/languages")
async def get_supported_languages():
    """
    Get list of supported programming languages
    """
    return {
        "supported_languages": [
            "python", "javascript", "typescript", "java", 
            "cpp", "go", "rust", "php", "ruby", "swift"
        ],
        "auto_detect": True
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    cache_stats = analysis_cache.stats()
    return {
        "status": "healthy",
        "message": "CodeLens AI API is running",
        "version": "1.0.0",
        "cache": cache_stats
    }

@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics
    """
    return analysis_cache.stats()

@router.post("/cache/clear")
async def clear_cache():
    """
    Clear analysis cache
    """
    analysis_cache.clear()
    return {"message": "Cache cleared successfully"}


# Helper functions
def calculate_overall_score(static_results: Dict, ai_results: Dict) -> int:
    """Calculate comprehensive code quality score from 0-100"""
    base_score = 100
    
    # Deduct points for static analysis issues
    static_issues = static_results.get("issues", [])
    for issue in static_issues:
        severity = issue.get("severity", "info")
        if severity == "error":
            base_score -= 15
        elif severity == "warning":
            base_score -= 8
        else:
            base_score -= 3
    
    # Factor in complexity from static analysis
    complexity_analysis = static_results.get("complexity_analysis", {})
    cyclomatic_complexity = complexity_analysis.get("cyclomatic_complexity", 1)
    nesting_depth = complexity_analysis.get("nesting_depth", 0)
    
    if cyclomatic_complexity > 10:
        base_score -= min(20, (cyclomatic_complexity - 10) * 2)
    
    if nesting_depth > 5:
        base_score -= min(15, (nesting_depth - 5) * 3)
    
    # Factor in quality indicators
    quality_indicators = static_results.get("quality_indicators", {})
    if quality_indicators.get("has_error_handling", False):
        base_score += 5
    if quality_indicators.get("has_docstrings", False) or quality_indicators.get("documentation_ratio", 0) > 0.1:
        base_score += 5
    
    # Deduct points for AI-detected issues
    ai_issues = ai_results.get("issues", [])
    improvements = ai_results.get("improvements", [])
    security_concerns = ai_results.get("security_concerns", [])
    
    for issue in ai_issues:
        severity = issue.get("severity", "info")
        if severity == "error":
            base_score -= 12
        elif severity == "warning":
            base_score -= 6
        else:
            base_score -= 2
    
    # Deduct points for needed improvements
    for improvement in improvements:
        priority = improvement.get("priority", "low")
        if priority == "high":
            base_score -= 8
        elif priority == "medium":
            base_score -= 4
        else:
            base_score -= 2
    
    # Deduct points for security concerns
    for security in security_concerns:
        severity = security.get("severity", "medium")
        if severity == "critical":
            base_score -= 25
        elif severity == "high":
            base_score -= 15
        elif severity == "medium":
            base_score -= 8
        else:
            base_score -= 4
    
    # Factor in AI assessment (weighted)
    ai_score = ai_results.get("score", 80)
    final_score = int((base_score * 0.7) + (ai_score * 0.3))
    
    return max(0, min(100, final_score))


def combine_enhanced_issues(
    static_issues: List, 
    ai_issues: List, 
    improvements: List, 
    security_concerns: List, 
    performance_notes: List
) -> List[AnalysisIssue]:
    """Combine all types of analysis results into structured issues"""
    combined = []
    
    # Add static analysis issues
    for issue in static_issues:
        combined.append(AnalysisIssue(
            title=issue.get("title", "Static Analysis Issue"),
            description=issue.get("description", ""),
            severity=issue.get("severity", "info"),
            suggestion=issue.get("suggestion", ""),
            source="static"
        ))
    
    # Add AI-detected issues
    for issue in ai_issues:
        combined.append(AnalysisIssue(
            title=issue.get("title", "AI Detected Issue"),
            description=issue.get("description", ""),
            severity=issue.get("severity", "info"),
            suggestion=issue.get("suggestion", ""),
            source="ai"
        ))
    
    # Add improvement suggestions as info-level issues
    for improvement in improvements:
        priority_to_severity = {"high": "warning", "medium": "info", "low": "info"}
        combined.append(AnalysisIssue(
            title=f"Improvement: {improvement.get('title', 'Code Enhancement')}",
            description=improvement.get("description", ""),
            severity=priority_to_severity.get(improvement.get("priority", "low"), "info"),
            suggestion=improvement.get("suggestion", ""),
            source="ai_improvement"
        ))
    
    # Add security concerns as warning/error level issues
    for security in security_concerns:
        severity_map = {"critical": "error", "high": "error", "medium": "warning", "low": "warning"}
        combined.append(AnalysisIssue(
            title=f"Security: {security.get('title', 'Security Concern')}",
            description=security.get("description", ""),
            severity=severity_map.get(security.get("severity", "medium"), "warning"),
            suggestion=security.get("mitigation", security.get("suggestion", "")),
            source="ai_security"
        ))
    
    # Add performance notes as info-level issues
    for performance in performance_notes:
        combined.append(AnalysisIssue(
            title=f"Performance: {performance.get('title', 'Performance Note')}",
            description=performance.get("description", ""),
            severity="info",
            suggestion=performance.get("suggestion", ""),
            source="ai_performance"
        ))
    
    return combined

def combine_issues(static_issues: List, ai_issues: List) -> List[AnalysisIssue]:
    """Legacy method for backward compatibility"""
    return combine_enhanced_issues(static_issues, ai_issues, [], [], [])

@router.delete("/analysis/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    db: DatabaseManager = Depends(get_database)
):
    """
    Delete a specific analysis result
    """
    try:
        # In a real implementation, you'd want to check user permissions here
        success = await db.delete_analysis(analysis_id)
        
        if success:
            return {"message": "Analysis deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Analysis not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete analysis")


@router.post("/analyze/batch")
async def analyze_batch_code(
    files: List[Dict[str, str]],  # [{"filename": "test.py", "code": "...", "language": "python"}]
    db: DatabaseManager = Depends(get_database)
):
    """
    Analyze multiple code files in batch
    """
    try:
        results = []
        
        for file_data in files[:10]:  # Limit to 10 files
            filename = file_data.get("filename", "unknown")
            code = file_data.get("code", "")
            language = file_data.get("language", "auto")
            
            if not code.strip():
                continue
            
            logger.info(f"Analyzing file: {filename}")
            
            # Detect language if auto-detect is requested
            detected_language = detect_language(
                code, 
                language if language != "auto" else None
            )
            
            # Run analyses
            static_results = await static_analyzer.analyze(code, detected_language)
            ai_results = await ai_analyzer.analyze(code, detected_language)
            
            # Calculate score and create result
            overall_score = calculate_overall_score(static_results, ai_results)
            
            file_result = {
                "filename": filename,
                "language": detected_language,
                "score": overall_score,
                "issues_count": len(static_results.get("issues", [])) + len(ai_results.get("issues", [])),
                "metrics": static_results.get("metrics", {}),
                "analysis_summary": {
                    "purpose": ai_results.get("purpose", ""),
                    "complexity": static_results.get("complexity_analysis", {}).get("cyclomatic_complexity", 1)
                }
            }
            
            results.append(file_result)
        
        return {
            "batch_results": results,
            "total_files": len(results),
            "average_score": sum(r["score"] for r in results) / len(results) if results else 0
        }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/statistics")
async def get_analysis_statistics(
    db: DatabaseManager = Depends(get_database)
):
    """
    Get comprehensive analysis statistics
    """
    try:
        # Get language statistics
        language_stats = await db.get_language_statistics()
        
        # Get recent analysis history
        recent_analyses = await db.get_recent_analyses(limit=100)
        
        # Calculate statistics
        if recent_analyses:
            scores = [analysis.summary.score for analysis in recent_analyses]
            avg_score = sum(scores) / len(scores)
            
            # Score distribution
            score_distribution = {
                "excellent": len([s for s in scores if s >= 90]),
                "good": len([s for s in scores if 80 <= s < 90]),
                "fair": len([s for s in scores if 70 <= s < 80]),
                "poor": len([s for s in scores if s < 70])
            }
            
            # Complexity analysis
            complexities = []
            for analysis in recent_analyses:
                if hasattr(analysis.metrics, 'complexity'):
                    complexities.append(analysis.metrics.complexity)
            
            avg_complexity = sum(complexities) / len(complexities) if complexities else 0
            
        else:
            avg_score = 0
            score_distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
            avg_complexity = 0
        
        return {
            "total_analyses": len(recent_analyses),
            "average_score": round(avg_score, 1),
            "score_distribution": score_distribution,
            "language_statistics": language_stats,
            "average_complexity": round(avg_complexity, 1),
            "most_common_issues": await _get_common_issues(recent_analyses),
            "analysis_trends": await _get_analysis_trends(recent_analyses)
        }
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


async def _get_common_issues(analyses: List) -> List[Dict[str, Any]]:
    """Get most common issues from recent analyses"""
    issue_counts = {}
    
    for analysis in analyses:
        for issue in analysis.issues:
            title = issue.title
            if title in issue_counts:
                issue_counts[title] += 1
            else:
                issue_counts[title] = 1
    
    # Sort by frequency and return top 10
    sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {"issue": issue, "count": count} 
        for issue, count in sorted_issues[:10]
    ]


async def _get_analysis_trends(analyses: List) -> Dict[str, Any]:
    """Get analysis trends over time"""
    if not analyses:
        return {"trend": "stable", "score_change": 0}
    
    # Sort by date
    sorted_analyses = sorted(analyses, key=lambda x: x.created_at)
    
    if len(sorted_analyses) < 2:
        return {"trend": "insufficient_data", "score_change": 0}
    
    # Calculate trend (simple: compare first half vs second half)
    mid_point = len(sorted_analyses) // 2
    first_half_avg = sum(a.summary.score for a in sorted_analyses[:mid_point]) / mid_point
    second_half_avg = sum(a.summary.score for a in sorted_analyses[mid_point:]) / (len(sorted_analyses) - mid_point)
    
    score_change = second_half_avg - first_half_avg
    
    if score_change > 5:
        trend = "improving"
    elif score_change < -5:
        trend = "declining"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "score_change": round(score_change, 1),
        "first_half_average": round(first_half_avg, 1),
        "second_half_average": round(second_half_avg, 1)
    }


@router.get("/export/{format}")
async def export_analysis_data(
    format: str,  # json, csv
    user_id: Optional[str] = Query(None),
    days: int = Query(30),
    db: DatabaseManager = Depends(get_database)
):
    """
    Export analysis data in different formats
    """
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Supported formats: json, csv")
        
        # Get analysis history
        history = await db.get_analysis_history(user_id=user_id, days=days)
        
        if format == "json":
            return {
                "export_format": "json",
                "export_date": datetime.utcnow().isoformat(),
                "total_analyses": history.total_analyses,
                "average_score": history.average_score,
                "languages_used": history.languages_used,
                "analyses": [
                    {
                        "id": str(analysis.id),
                        "language": analysis.language,
                        "score": analysis.summary.score,
                        "purpose": analysis.summary.purpose,
                        "issues_count": len(analysis.issues),
                        "complexity": analysis.metrics.complexity,
                        "created_at": analysis.created_at.isoformat()
                    }
                    for analysis in history.recent_analyses
                ]
            }
        
        elif format == "csv":
            # For CSV, we'd return a structured response that the frontend can convert
            csv_data = []
            for analysis in history.recent_analyses:
                csv_data.append({
                    "ID": str(analysis.id),
                    "Language": analysis.language,
                    "Score": analysis.summary.score,
                    "Purpose": analysis.summary.purpose,
                    "Issues Count": len(analysis.issues),
                    "Complexity": analysis.metrics.complexity,
                    "Created At": analysis.created_at.isoformat()
                })
            
            return {
                "export_format": "csv",
                "headers": ["ID", "Language", "Score", "Purpose", "Issues Count", "Complexity", "Created At"],
                "data": csv_data
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Export failed")