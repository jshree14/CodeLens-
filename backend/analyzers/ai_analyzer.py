import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
import json
import re
import httpx
from datetime import datetime
import google.generativeai as genai

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    AI-powered code analyzer using Google Gemini, OpenAI GPT, or Hugging Face models
    Provides intelligent code analysis including bug detection, improvements, and explanations
    """
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        self.use_gemini = bool(self.gemini_api_key)
        self.use_openai = bool(self.openai_api_key)
        self.use_huggingface = bool(self.huggingface_api_key)
        self.use_mock = not (self.use_gemini or self.use_openai or self.use_huggingface)
        
        # Initialize Gemini if API key is available
        if self.use_gemini:
            genai.configure(api_key=self.gemini_api_key)
            # Use gemini-2.0-flash-exp for fastest responses
            self.gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
        
        # API endpoints
        self.openai_base_url = "https://api.openai.com/v1"
        self.huggingface_base_url = "https://api-inference.huggingface.co/models"
        
        logger.info(f"AI Analyzer initialized - Gemini: {self.use_gemini}, OpenAI: {self.use_openai}, HuggingFace: {self.use_huggingface}, Mock: {self.use_mock}")
    
    async def analyze(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code using available AI services
        Priority: Gemini > OpenAI > HuggingFace > Mock
        Returns structured analysis with issues, suggestions, and explanations
        """
        try:
            if self.use_gemini:
                return await self._gemini_analysis(code, language)
            elif self.use_openai:
                return await self._openai_analysis(code, language)
            elif self.use_huggingface:
                return await self._huggingface_analysis(code, language)
            else:
                return await self._enhanced_mock_analysis(code, language)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fallback to mock analysis
            return await self._enhanced_mock_analysis(code, language)
    
    async def _gemini_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """
        Advanced Google Gemini analysis with comprehensive code review
        """
        try:
            logger.info(f"Starting Gemini analysis for {language} code")
            
            # Create comprehensive analysis prompt
            prompt = self._create_gemini_analysis_prompt(code, language)
            
            # Generate content with Gemini (optimized for speed)
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Lower for faster, more consistent results
                    max_output_tokens=800,  # Reduced for faster response
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response
            result = json.loads(response.text)
            
            # Add metadata
            result["confidence_score"] = 95
            result["analysis_method"] = "google_gemini"
            result["timestamp"] = datetime.utcnow().isoformat()
            
            logger.info(f"Gemini analysis completed successfully with score: {result.get('score', 'N/A')}")
            return self._validate_and_enhance_result(result, code, language)
            
        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON: {e}")
            return await self._enhanced_mock_analysis(code, language)
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            # Fallback to enhanced mock analysis
            return await self._enhanced_mock_analysis(code, language)
    
    def _create_gemini_analysis_prompt(self, code: str, language: str) -> str:
        """Create comprehensive analysis prompt specifically for Gemini"""
        return f"""
You are an expert code reviewer and software engineer. Analyze the following {language} code and provide a comprehensive code review.

Code to analyze:
```{language}
{code}
```

Provide your analysis in this exact JSON format (ensure valid JSON syntax):
{{
    "purpose": "Brief one-line description of what the code does",
    "overview": "Detailed explanation of code structure, design patterns, and overall quality (2-3 sentences)",
    "issues": [
        {{
            "title": "Issue title",
            "description": "Detailed description of the issue",
            "severity": "error|warning|info",
            "suggestion": "Specific actionable suggestion to fix the issue",
            "line_number": 1
        }}
    ],
    "improvements": [
        {{
            "title": "Improvement suggestion",
            "description": "Why this improvement would help",
            "priority": "high|medium|low",
            "suggestion": "How to implement the improvement"
        }}
    ],
    "security_concerns": [
        {{
            "title": "Security issue title",
            "description": "Description of security vulnerability",
            "severity": "critical|high|medium|low",
            "mitigation": "How to fix the security issue"
        }}
    ],
    "performance_notes": [
        {{
            "title": "Performance consideration",
            "description": "Performance impact or optimization opportunity",
            "suggestion": "How to optimize"
        }}
    ],
    "score": 85,
    "explanation": "Explanation of the score based on code quality factors"
}}

Focus on:
1. Logic errors and potential bugs
2. Code style and best practices for {language}
3. Security vulnerabilities
4. Performance optimizations
5. Maintainability and readability
6. Error handling
7. Documentation quality
8. Language-specific conventions

Ensure the response is valid JSON only, no additional text.
"""
    
    async def _enhanced_mock_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """
        Enhanced mock AI analysis with comprehensive code review simulation
        Provides realistic analysis results for development and testing
        """
        # Simulate realistic API delay
        await asyncio.sleep(0.5)
        
        # Analyze code characteristics
        lines = len(code.split('\n'))
        functions = len(re.findall(r'def\s+\w+|function\s+\w+|class\s+\w+', code))
        
        # Generate comprehensive analysis
        purpose = self._generate_mock_purpose(code, language)
        overview = self._generate_mock_overview(code, language, lines, functions)
        issues = self._generate_mock_issues(code, language)
        improvements = self._generate_mock_improvements(code, language)
        security_concerns = self._generate_mock_security_concerns(code, language)
        performance_notes = self._generate_mock_performance_notes(code, language)
        score = self._calculate_enhanced_mock_score(code, issues, improvements)
        
        return {
            "purpose": purpose,
            "overview": overview,
            "issues": issues,
            "improvements": improvements,
            "security_concerns": security_concerns,
            "performance_notes": performance_notes,
            "score": score,
            "explanation": self._generate_score_explanation(score, issues, improvements),
            "confidence_score": 85,
            "analysis_method": "enhanced_mock",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_mock_purpose(self, code: str, language: str) -> str:
        """Generate mock purpose based on code analysis"""
        if 'factorial' in code.lower():
            return "Calculates the factorial of a number using recursion"
        elif 'sort' in code.lower():
            return "Implements a sorting algorithm for data arrangement"
        elif 'class' in code.lower():
            return "Defines a class with methods for object-oriented programming"
        elif 'function' in code.lower() or 'def ' in code:
            return "Contains function definitions for modular code organization"
        else:
            return f"A {language} code snippet that performs computational tasks"
    
    def _generate_mock_overview(self, code: str, language: str, lines: int, functions: int) -> str:
        """Generate mock overview"""
        complexity = "simple" if lines < 20 else "moderate" if lines < 50 else "complex"
        
        overview = f"This {language} code consists of {lines} lines with {functions} function(s). "
        overview += f"The code structure appears {complexity} and "
        
        if 'try:' in code or 'catch' in code:
            overview += "includes error handling mechanisms. "
        else:
            overview += "lacks explicit error handling. "
        
        if '#' in code or '//' in code or '/*' in code:
            overview += "The code includes comments for documentation."
        else:
            overview += "The code would benefit from more comments and documentation."
        
        return overview
    
    def _generate_mock_issues(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Generate mock issues based on code patterns"""
        issues = []
        
        # Check for common issues
        if language == 'python':
            if 'print(' in code:
                issues.append({
                    "title": "Debug Print Statements",
                    "description": "Found print statements that should be removed in production",
                    "severity": "info",
                    "suggestion": "Use logging module instead of print statements"
                })
            
            if not re.search(r'""".*?"""', code, re.DOTALL) and 'def ' in code:
                issues.append({
                    "title": "Missing Docstrings",
                    "description": "Functions lack proper documentation",
                    "severity": "warning",
                    "suggestion": "Add docstrings to describe function purpose and parameters"
                })
        
        elif language == 'javascript':
            if 'var ' in code:
                issues.append({
                    "title": "Outdated Variable Declaration",
                    "description": "Using 'var' instead of modern 'let' or 'const'",
                    "severity": "warning",
                    "suggestion": "Replace 'var' with 'let' or 'const' for better scoping"
                })
        
        # Generic issues
        if len(code.split('\n')) > 50 and not re.search(r'class\s+\w+', code):
            issues.append({
                "title": "Large Function",
                "description": "Code appears to be a large single function",
                "severity": "warning",
                "suggestion": "Consider breaking down into smaller, more focused functions"
            })
        
        # If no issues found, add a positive note
        if not issues:
            issues.append({
                "title": "Code Quality Good",
                "description": "No major issues detected in the code structure",
                "severity": "info",
                "suggestion": "Consider adding unit tests to ensure code reliability"
            })
        
        return issues
    
    def _calculate_mock_score(self, code: str, issues: List[Dict]) -> int:
        """Calculate mock quality score"""
        base_score = 85
        
        # Deduct points for issues
        for issue in issues:
            if issue["severity"] == "error":
                base_score -= 20
            elif issue["severity"] == "warning":
                base_score -= 10
            else:
                base_score -= 2
        
        # Bonus for good practices
        if '#' in code or '//' in code:  # Has comments
            base_score += 5
        
        if 'try:' in code or 'catch' in code:  # Has error handling
            base_score += 5
        
        return max(60, min(100, base_score))
    
    async def _openai_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """
        Advanced OpenAI GPT analysis with comprehensive code review
        """
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.openai_api_key)
            
            # Enhanced prompt for better analysis
            prompt = self._create_analysis_prompt(code, language)
            
            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Use GPT-4 for better analysis
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer and software engineer. Provide detailed, actionable code analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.2,  # Lower temperature for more consistent results
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Add confidence score and metadata
            result["confidence_score"] = 95
            result["analysis_method"] = "openai_gpt4"
            result["timestamp"] = datetime.utcnow().isoformat()
            
            return self._validate_and_enhance_result(result, code, language)
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            # Fallback to enhanced mock analysis
            return await self._enhanced_mock_analysis(code, language)
    
    async def _huggingface_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """
        Hugging Face model analysis using CodeBERT or similar models
        """
        try:
            # Use CodeBERT for code understanding
            model_name = "microsoft/codebert-base"
            
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
                
                # Analyze code with CodeBERT
                payload = {
                    "inputs": f"Analyze this {language} code for bugs and improvements:\n{code}",
                    "parameters": {"max_length": 512, "temperature": 0.3}
                }
                
                response = await client.post(
                    f"{self.huggingface_base_url}/{model_name}",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    hf_result = response.json()
                    return await self._process_huggingface_result(hf_result, code, language)
                else:
                    logger.warning(f"Hugging Face API error: {response.status_code}")
                    return await self._enhanced_mock_analysis(code, language)
                    
        except Exception as e:
            logger.error(f"Hugging Face analysis failed: {e}")
            return await self._enhanced_mock_analysis(code, language)
    
    def _create_analysis_prompt(self, code: str, language: str) -> str:
        """Create comprehensive analysis prompt for AI models"""
        return f"""
Analyze the following {language} code and provide a comprehensive code review in JSON format:

```{language}
{code}
```

Provide analysis in this exact JSON structure:
{{
    "purpose": "Brief one-line description of what the code does",
    "overview": "Detailed explanation of code structure, design patterns, and overall quality",
    "issues": [
        {{
            "title": "Issue title",
            "description": "Detailed description of the issue",
            "severity": "error|warning|info",
            "suggestion": "Specific actionable suggestion to fix the issue",
            "line_number": "Line number if applicable (optional)"
        }}
    ],
    "improvements": [
        {{
            "title": "Improvement suggestion",
            "description": "Why this improvement would help",
            "priority": "high|medium|low",
            "suggestion": "How to implement the improvement"
        }}
    ],
    "security_concerns": [
        {{
            "title": "Security issue title",
            "description": "Description of security vulnerability",
            "severity": "critical|high|medium|low",
            "mitigation": "How to fix the security issue"
        }}
    ],
    "performance_notes": [
        {{
            "title": "Performance consideration",
            "description": "Performance impact or optimization opportunity",
            "suggestion": "How to optimize"
        }}
    ],
    "score": 85,
    "explanation": "Explanation of the score based on code quality factors"
}}

Focus on:
1. Logic errors and potential bugs
2. Code style and best practices
3. Security vulnerabilities
4. Performance optimizations
5. Maintainability and readability
6. Error handling
7. Documentation quality
"""
    
    async def _process_huggingface_result(self, hf_result: Any, code: str, language: str) -> Dict[str, Any]:
        """Process Hugging Face model output into structured format"""
        try:
            # Extract insights from HF model output
            generated_text = ""
            if isinstance(hf_result, list) and len(hf_result) > 0:
                generated_text = hf_result[0].get("generated_text", "")
            
            # Parse the generated analysis (this would need refinement based on actual model output)
            analysis = {
                "purpose": self._extract_purpose_from_text(generated_text, code, language),
                "overview": f"Analysis using Hugging Face CodeBERT model. {generated_text[:200]}...",
                "issues": self._extract_issues_from_hf_output(generated_text, code, language),
                "improvements": [],
                "security_concerns": [],
                "performance_notes": [],
                "score": self._calculate_hf_score(generated_text, code),
                "explanation": "Score based on Hugging Face model analysis",
                "confidence_score": 75,
                "analysis_method": "huggingface_codebert",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to process Hugging Face result: {e}")
            return await self._enhanced_mock_analysis(code, language)
    
    def _extract_purpose_from_text(self, text: str, code: str, language: str) -> str:
        """Extract code purpose from generated text or analyze code directly"""
        # Fallback to pattern-based analysis
        if 'class' in code.lower():
            return f"Defines a {language} class with methods and properties"
        elif 'function' in code.lower() or 'def ' in code:
            return f"Implements {language} functions for specific functionality"
        elif 'import' in code.lower():
            return f"A {language} module with imports and implementations"
        else:
            return f"A {language} code snippet performing computational tasks"
    
    def _extract_issues_from_hf_output(self, text: str, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract issues from Hugging Face output"""
        issues = []
        
        # Basic pattern-based issue detection as fallback
        if language == 'python':
            if 'print(' in code and 'def ' in code:
                issues.append({
                    "title": "Debug Print Statements",
                    "description": "Found print statements in function code",
                    "severity": "info",
                    "suggestion": "Consider using logging instead of print statements"
                })
        
        return issues
    
    def _calculate_hf_score(self, text: str, code: str) -> int:
        """Calculate quality score from Hugging Face analysis"""
        base_score = 80
        
        # Adjust based on code characteristics
        if len(code.split('\n')) > 50:
            base_score -= 5  # Longer code might be more complex
        
        if 'error' in text.lower() or 'bug' in text.lower():
            base_score -= 15
        
        if 'good' in text.lower() or 'clean' in text.lower():
            base_score += 10
        
        return max(60, min(100, base_score)) 
   
    def _generate_mock_improvements(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Generate mock improvement suggestions"""
        improvements = []
        
        # Check for common improvement opportunities
        if language == 'python':
            if 'for i in range(len(' in code:
                improvements.append({
                    "title": "Use Direct Iteration",
                    "description": "Iterate directly over collections instead of using range(len())",
                    "priority": "medium",
                    "suggestion": "Replace 'for i in range(len(items))' with 'for item in items' or 'for i, item in enumerate(items)'"
                })
            
            if not re.search(r'""".*?"""', code, re.DOTALL) and 'def ' in code:
                improvements.append({
                    "title": "Add Type Hints",
                    "description": "Adding type hints improves code readability and IDE support",
                    "priority": "medium",
                    "suggestion": "Add type hints to function parameters and return values"
                })
        
        elif language == 'javascript':
            if 'var ' in code:
                improvements.append({
                    "title": "Modern Variable Declarations",
                    "description": "Use const/let instead of var for better scoping",
                    "priority": "high",
                    "suggestion": "Replace 'var' with 'const' for constants or 'let' for variables"
                })
            
            if not re.search(r'async|await', code) and 'fetch(' in code:
                improvements.append({
                    "title": "Use Async/Await",
                    "description": "Modern async/await syntax is more readable than promises",
                    "priority": "medium",
                    "suggestion": "Consider using async/await instead of .then() chains"
                })
        
        # Generic improvements
        if len(code.split('\n')) > 30 and code.count('if ') > 5:
            improvements.append({
                "title": "Reduce Complexity",
                "description": "Consider breaking down complex logic into smaller functions",
                "priority": "high",
                "suggestion": "Extract complex conditional logic into separate, well-named functions"
            })
        
        return improvements
    
    def _generate_mock_security_concerns(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Generate mock security concern analysis"""
        security_concerns = []
        
        # Check for potential security issues
        if 'eval(' in code:
            security_concerns.append({
                "title": "Code Injection Risk",
                "description": "Use of eval() can lead to code injection vulnerabilities",
                "severity": "critical",
                "mitigation": "Avoid eval() and use safer alternatives like JSON.parse() or specific parsing functions"
            })
        
        if 'sql' in code.lower() and ('+' in code or 'format(' in code):
            security_concerns.append({
                "title": "Potential SQL Injection",
                "description": "String concatenation in SQL queries can lead to injection attacks",
                "severity": "high",
                "mitigation": "Use parameterized queries or prepared statements"
            })
        
        if language == 'python' and 'pickle.load' in code:
            security_concerns.append({
                "title": "Unsafe Deserialization",
                "description": "pickle.load() can execute arbitrary code from untrusted data",
                "severity": "high",
                "mitigation": "Use safer serialization formats like JSON or validate data sources"
            })
        
        if 'password' in code.lower() and ('=' in code or 'const' in code):
            security_concerns.append({
                "title": "Hardcoded Credentials",
                "description": "Hardcoded passwords or API keys in source code",
                "severity": "medium",
                "mitigation": "Use environment variables or secure configuration management"
            })
        
        return security_concerns
    
    def _generate_mock_performance_notes(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Generate mock performance optimization suggestions"""
        performance_notes = []
        
        # Check for performance opportunities
        if language == 'python':
            if 'for' in code and 'append(' in code:
                performance_notes.append({
                    "title": "List Comprehension Opportunity",
                    "description": "List comprehensions are often faster than append() in loops",
                    "suggestion": "Consider using list comprehension: [expression for item in iterable]"
                })
            
            if '+=' in code and 'str' in code.lower():
                performance_notes.append({
                    "title": "String Concatenation Optimization",
                    "description": "Repeated string concatenation can be inefficient",
                    "suggestion": "Use join() for multiple string concatenations: ''.join(strings)"
                })
        
        elif language == 'javascript':
            if 'document.getElementById' in code and code.count('document.getElementById') > 2:
                performance_notes.append({
                    "title": "DOM Query Optimization",
                    "description": "Multiple DOM queries for the same element",
                    "suggestion": "Cache DOM elements in variables to avoid repeated queries"
                })
        
        # Generic performance notes
        nested_loops = len(re.findall(r'for.*for|while.*while', code, re.DOTALL))
        if nested_loops > 0:
            performance_notes.append({
                "title": "Nested Loop Complexity",
                "description": f"Found {nested_loops} nested loop(s) which may impact performance",
                "suggestion": "Consider algorithm optimization or data structure improvements"
            })
        
        return performance_notes
    
    def _calculate_enhanced_mock_score(self, code: str, issues: List, improvements: List) -> int:
        """Calculate enhanced quality score based on multiple factors"""
        base_score = 90
        
        # Deduct points for issues
        for issue in issues:
            severity = issue.get("severity", "info")
            if severity == "error":
                base_score -= 20
            elif severity == "warning":
                base_score -= 10
            else:
                base_score -= 3
        
        # Deduct points for needed improvements
        for improvement in improvements:
            priority = improvement.get("priority", "low")
            if priority == "high":
                base_score -= 8
            elif priority == "medium":
                base_score -= 5
            else:
                base_score -= 2
        
        # Bonus for good practices
        if '#' in code or '//' in code or '"""' in code:  # Has comments
            base_score += 5
        
        if 'try:' in code or 'catch' in code or 'except' in code:  # Has error handling
            base_score += 5
        
        if len(code.split('\n')) < 50:  # Reasonable length
            base_score += 3
        
        return max(50, min(100, base_score))
    
    def _generate_score_explanation(self, score: int, issues: List, improvements: List) -> str:
        """Generate explanation for the quality score"""
        if score >= 90:
            return "Excellent code quality with minimal issues and good practices"
        elif score >= 80:
            return "Good code quality with minor improvements needed"
        elif score >= 70:
            return "Acceptable code quality but several areas for improvement"
        elif score >= 60:
            return "Below average code quality with multiple issues to address"
        else:
            return "Poor code quality requiring significant improvements"
    
    def _validate_and_enhance_result(self, result: Dict[str, Any], code: str, language: str) -> Dict[str, Any]:
        """Validate and enhance AI analysis result"""
        # Ensure required fields exist
        if "purpose" not in result:
            result["purpose"] = self._generate_mock_purpose(code, language)
        
        if "overview" not in result:
            result["overview"] = "AI analysis completed successfully"
        
        if "issues" not in result:
            result["issues"] = []
        
        if "score" not in result:
            result["score"] = 75
        
        # Add missing fields if not present
        if "improvements" not in result:
            result["improvements"] = []
        
        if "security_concerns" not in result:
            result["security_concerns"] = []
        
        if "performance_notes" not in result:
            result["performance_notes"] = []
        
        if "explanation" not in result:
            result["explanation"] = self._generate_score_explanation(
                result["score"], result["issues"], result.get("improvements", [])
            )
        
        return result