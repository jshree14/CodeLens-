"""
Code Executor - Safely executes code and captures output
Supports Python, JavaScript, and other languages
"""

import subprocess
import tempfile
import os
import sys
import logging
from typing import Dict, Any, Optional
import asyncio
from io import StringIO
import contextlib

logger = logging.getLogger(__name__)


class CodeExecutor:
    """Safely executes code and captures output"""
    
    def __init__(self):
        self.timeout = 5  # 5 seconds timeout
        self.max_output_length = 10000  # Max 10KB output
    
    def _run_python_subprocess(self, python_exe: str, script_path: str) -> Dict[str, Any]:
        """Run Python subprocess synchronously (for Windows compatibility)"""
        try:
            result = subprocess.run(
                [python_exe, script_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8',
                errors='ignore'
            )
            return {
                'output': result.stdout[:self.max_output_length],
                'error': result.stderr[:self.max_output_length],
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'output': '',
                'error': f'Execution timeout ({self.timeout}s exceeded)',
                'returncode': 1
            }
        except Exception as e:
            return {
                'output': '',
                'error': f'Execution error: {str(e)}',
                'returncode': 1
            }
    
    def _run_node_subprocess(self, script_path: str) -> Dict[str, Any]:
        """Run Node.js subprocess synchronously (for Windows compatibility)"""
        try:
            result = subprocess.run(
                ['node', script_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8',
                errors='ignore'
            )
            return {
                'output': result.stdout[:self.max_output_length],
                'error': result.stderr[:self.max_output_length],
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'output': '',
                'error': f'Execution timeout ({self.timeout}s exceeded)',
                'returncode': 1
            }
        except FileNotFoundError:
            return {
                'output': '',
                'error': 'Node.js not found. Please install Node.js.',
                'returncode': 1
            }
        except Exception as e:
            return {
                'output': '',
                'error': f'Execution error: {str(e)}',
                'returncode': 1
            }
    
    def _run_java_subprocess(self, java_file: str, class_name: str, temp_dir: str) -> Dict[str, Any]:
        """Run Java compilation and execution synchronously (for Windows compatibility)"""
        try:
            # Compile
            compile_result = subprocess.run(
                ['javac', java_file],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8',
                errors='ignore',
                cwd=temp_dir
            )
            
            if compile_result.returncode != 0:
                return {
                    'output': '',
                    'error': f'Compilation error:\n{compile_result.stderr}',
                    'returncode': 1
                }
            
            # Execute
            run_result = subprocess.run(
                ['java', class_name],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8',
                errors='ignore',
                cwd=temp_dir
            )
            
            return {
                'output': run_result.stdout[:self.max_output_length],
                'error': run_result.stderr[:self.max_output_length],
                'returncode': run_result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'output': '',
                'error': f'Execution timeout ({self.timeout}s exceeded)',
                'returncode': 1
            }
        except FileNotFoundError:
            return {
                'output': '',
                'error': 'Java compiler not found. Please install JDK.',
                'returncode': 1
            }
        except Exception as e:
            return {
                'output': '',
                'error': f'Execution error: {str(e)}',
                'returncode': 1
            }
    
    def _run_cpp_subprocess(self, source_file: str, exe_file: str) -> Dict[str, Any]:
        """Run C++ compilation and execution synchronously (for Windows compatibility)"""
        try:
            # Compile
            compile_result = subprocess.run(
                ['g++', source_file, '-o', exe_file],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8',
                errors='ignore'
            )
            
            if compile_result.returncode != 0:
                return {
                    'output': '',
                    'error': f'Compilation error:\n{compile_result.stderr}',
                    'returncode': 1
                }
            
            # Execute
            run_result = subprocess.run(
                [exe_file],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding='utf-8',
                errors='ignore'
            )
            
            return {
                'output': run_result.stdout[:self.max_output_length],
                'error': run_result.stderr[:self.max_output_length],
                'returncode': run_result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'output': '',
                'error': f'Execution timeout ({self.timeout}s exceeded)',
                'returncode': 1
            }
        except FileNotFoundError:
            return {
                'output': '',
                'error': 'C++ compiler not found. Please install g++.',
                'returncode': 1
            }
        except Exception as e:
            return {
                'output': '',
                'error': f'Execution error: {str(e)}',
                'returncode': 1
            }
    
    async def execute(self, code: str, language: str) -> Dict[str, Any]:
        """
        Execute code and return output
        Returns: {
            "output": str,
            "error": str,
            "execution_time": float,
            "success": bool
        }
        """
        try:
            if language == 'python':
                return await self._execute_python(code)
            elif language in ['javascript', 'typescript']:
                return await self._execute_javascript(code)
            elif language == 'java':
                return await self._execute_java(code)
            elif language in ['cpp', 'c']:
                return await self._execute_cpp(code)
            else:
                return {
                    "output": "",
                    "error": f"Code execution not supported for {language}",
                    "execution_time": 0,
                    "success": False
                }
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "output": "",
                "error": str(e),
                "execution_time": 0,
                "success": False
            }
    
    async def _execute_python(self, code: str) -> Dict[str, Any]:
        """Execute Python code safely"""
        import time
        import platform
        
        start_time = time.time()
        temp_file = None
        
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            logger.info(f"Executing Python code from: {temp_file}")
            logger.info(f"Using Python executable: {sys.executable}")
            
            # On Windows, use ProactorEventLoop for subprocess support
            if platform.system() == 'Windows':
                # Use subprocess.run in thread pool for Windows compatibility
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._run_python_subprocess,
                    sys.executable,
                    temp_file
                )
                
                execution_time = time.time() - start_time
                
                # Clean up
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
                
                return {
                    "output": result['output'].strip() if result['output'] else "",
                    "error": result['error'].strip() if result['error'] else "",
                    "execution_time": round(execution_time, 3),
                    "success": result['returncode'] == 0 and not result['error']
                }
            
            # Unix/Linux: use asyncio subprocess
            process = await asyncio.create_subprocess_exec(
                sys.executable, temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
                
                execution_time = time.time() - start_time
                
                output = stdout.decode('utf-8', errors='ignore')[:self.max_output_length]
                error = stderr.decode('utf-8', errors='ignore')[:self.max_output_length]
                
                logger.info(f"Python execution completed: returncode={process.returncode}, output_len={len(output)}, error_len={len(error)}")
                
                # Clean up
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
                
                return {
                    "output": output.strip() if output else "",
                    "error": error.strip() if error else "",
                    "execution_time": round(execution_time, 3),
                    "success": process.returncode == 0 and not error
                }
                
            except asyncio.TimeoutError:
                logger.warning(f"Python execution timeout after {self.timeout}s")
                process.kill()
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
                return {
                    "output": "",
                    "error": f"Execution timeout ({self.timeout}s exceeded)",
                    "execution_time": self.timeout,
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"Python execution error: {e}", exc_info=True)
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
            return {
                "output": "",
                "error": f"Execution error: {str(e)}",
                "execution_time": time.time() - start_time,
                "success": False
            }
    
    async def _execute_javascript(self, code: str) -> Dict[str, Any]:
        """Execute JavaScript code using Node.js"""
        import time
        import platform
        
        start_time = time.time()
        temp_file = None
        
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            logger.info(f"Executing JavaScript code from: {temp_file}")
            
            # On Windows, use thread pool for subprocess
            if platform.system() == 'Windows':
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._run_node_subprocess,
                    temp_file
                )
                
                execution_time = time.time() - start_time
                
                # Clean up
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
                
                return {
                    "output": result['output'].strip() if result['output'] else "",
                    "error": result['error'].strip() if result['error'] else "",
                    "execution_time": round(execution_time, 3),
                    "success": result['returncode'] == 0 and not result['error']
                }
            
            # Unix/Linux: use asyncio subprocess
            process = await asyncio.create_subprocess_exec(
                'node', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
                
                execution_time = time.time() - start_time
                
                output = stdout.decode('utf-8', errors='ignore')[:self.max_output_length]
                error = stderr.decode('utf-8', errors='ignore')[:self.max_output_length]
                
                # Clean up
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
                
                return {
                    "output": output.strip() if output else "",
                    "error": error.strip() if error else "",
                    "execution_time": round(execution_time, 3),
                    "success": process.returncode == 0 and not error
                }
                
            except asyncio.TimeoutError:
                process.kill()
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
                return {
                    "output": "",
                    "error": f"Execution timeout ({self.timeout}s exceeded)",
                    "execution_time": self.timeout,
                    "success": False
                }
                
        except FileNotFoundError:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            return {
                "output": "",
                "error": "Node.js not found. Please install Node.js to execute JavaScript code.",
                "execution_time": 0,
                "success": False
            }
        except Exception as e:
            logger.error(f"JavaScript execution error: {e}", exc_info=True)
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
            return {
                "output": "",
                "error": f"Execution error: {str(e)}",
                "execution_time": time.time() - start_time,
                "success": False
            }
    
    async def _execute_java_online(self, code: str) -> Dict[str, Any]:
        """Execute Java code using Piston API (free, no auth required)"""
        import time
        import httpx
        
        start_time = time.time()
        
        try:
            # Use Piston API - free and no auth required
            async with httpx.AsyncClient(timeout=15.0) as client:
                payload = {
                    "language": "java",
                    "version": "15.0.2",
                    "files": [{
                        "content": code
                    }]
                }
                
                response = await client.post(
                    "https://emkc.org/api/v2/piston/execute",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    execution_time = time.time() - start_time
                    
                    run_data = result.get("run", {})
                    output = run_data.get("output", "").strip()
                    stderr = run_data.get("stderr", "").strip()
                    
                    return {
                        "output": output if output else "",
                        "error": stderr if stderr else "",
                        "execution_time": round(execution_time, 3),
                        "success": run_data.get("code", 1) == 0
                    }
                else:
                    return {
                        "output": "",
                        "error": "Online Java compiler unavailable. Please try again.",
                        "execution_time": time.time() - start_time,
                        "success": False
                    }
        except Exception as e:
            logger.error(f"Online Java execution failed: {e}")
            return {
                "output": "",
                "error": f"Java execution unavailable: {str(e)}",
                "execution_time": time.time() - start_time,
                "success": False
            }
    
    async def _execute_java(self, code: str) -> Dict[str, Any]:
        """Execute Java code"""
        import time
        import platform
        
        start_time = time.time()
        
        try:
            # Extract class name from code
            import re
            class_match = re.search(r'public\s+class\s+(\w+)', code)
            if not class_match:
                return {
                    "output": "",
                    "error": "No public class found in Java code",
                    "execution_time": 0,
                    "success": False
                }
            
            class_name = class_match.group(1)
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            try:
                java_file = os.path.join(temp_dir, f"{class_name}.java")
                
                # Write code to file
                with open(java_file, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                logger.info(f"Executing Java code: {class_name}")
                
                # On Windows, use thread pool
                if platform.system() == 'Windows':
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        self._run_java_subprocess,
                        java_file,
                        class_name,
                        temp_dir
                    )
                    
                    execution_time = time.time() - start_time
                    
                    return {
                        "output": result['output'].strip() if result['output'] else "",
                        "error": result['error'].strip() if result['error'] else "",
                        "execution_time": round(execution_time, 3),
                        "success": result['returncode'] == 0 and not result['error']
                    }
                
                # Unix/Linux: use asyncio subprocess
                # Compile
                compile_process = await asyncio.create_subprocess_exec(
                    'javac', java_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=temp_dir
                )
                
                compile_stdout, compile_stderr = await compile_process.communicate()
                
                if compile_process.returncode != 0:
                    return {
                        "output": "",
                        "error": f"Compilation error:\n{compile_stderr.decode('utf-8', errors='ignore')}",
                        "execution_time": time.time() - start_time,
                        "success": False
                    }
                
                # Execute
                run_process = await asyncio.create_subprocess_exec(
                    'java', class_name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=temp_dir
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        run_process.communicate(),
                        timeout=self.timeout
                    )
                    
                    execution_time = time.time() - start_time
                    
                    return {
                        "output": stdout.decode('utf-8', errors='ignore')[:self.max_output_length].strip(),
                        "error": stderr.decode('utf-8', errors='ignore')[:self.max_output_length].strip(),
                        "execution_time": round(execution_time, 3),
                        "success": run_process.returncode == 0 and not stderr
                    }
                    
                except asyncio.TimeoutError:
                    run_process.kill()
                    return {
                        "output": "",
                        "error": f"Execution timeout ({self.timeout}s exceeded)",
                        "execution_time": self.timeout,
                        "success": False
                    }
            finally:
                # Clean up temp directory
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except:
                    pass
                    
        except FileNotFoundError:
            # Fallback to online compiler
            logger.info("Java not found locally, using online compiler")
            return await self._execute_java_online(code)
        except Exception as e:
            logger.error(f"Java execution error: {e}", exc_info=True)
            return {
                "output": "",
                "error": f"Execution error: {str(e)}",
                "execution_time": time.time() - start_time,
                "success": False
            }
    
    async def _execute_cpp(self, code: str) -> Dict[str, Any]:
        """Execute C/C++ code"""
        import time
        import platform
        
        start_time = time.time()
        source_file = None
        exe_file = None
        
        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False, encoding='utf-8') as f:
                f.write(code)
                source_file = f.name
            
            exe_file = source_file.replace('.cpp', '.exe')
            
            logger.info(f"Executing C++ code from: {source_file}")
            
            # On Windows, use thread pool
            if platform.system() == 'Windows':
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._run_cpp_subprocess,
                    source_file,
                    exe_file
                )
                
                execution_time = time.time() - start_time
                
                # Clean up
                if source_file and os.path.exists(source_file):
                    os.unlink(source_file)
                if exe_file and os.path.exists(exe_file):
                    os.unlink(exe_file)
                
                return {
                    "output": result['output'].strip() if result['output'] else "",
                    "error": result['error'].strip() if result['error'] else "",
                    "execution_time": round(execution_time, 3),
                    "success": result['returncode'] == 0 and not result['error']
                }
            
            # Unix/Linux: use asyncio subprocess
            # Compile
            compile_process = await asyncio.create_subprocess_exec(
                'g++', source_file, '-o', exe_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            compile_stdout, compile_stderr = await compile_process.communicate()
            
            if compile_process.returncode != 0:
                if source_file and os.path.exists(source_file):
                    os.unlink(source_file)
                return {
                    "output": "",
                    "error": f"Compilation error:\n{compile_stderr.decode('utf-8', errors='ignore')}",
                    "execution_time": time.time() - start_time,
                    "success": False
                }
            
            # Execute
            run_process = await asyncio.create_subprocess_exec(
                exe_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    run_process.communicate(),
                    timeout=self.timeout
                )
                
                execution_time = time.time() - start_time
                
                # Clean up
                if source_file and os.path.exists(source_file):
                    os.unlink(source_file)
                if exe_file and os.path.exists(exe_file):
                    os.unlink(exe_file)
                
                return {
                    "output": stdout.decode('utf-8', errors='ignore')[:self.max_output_length].strip(),
                    "error": stderr.decode('utf-8', errors='ignore')[:self.max_output_length].strip(),
                    "execution_time": round(execution_time, 3),
                    "success": run_process.returncode == 0 and not stderr
                }
                
            except asyncio.TimeoutError:
                run_process.kill()
                if source_file and os.path.exists(source_file):
                    os.unlink(source_file)
                if exe_file and os.path.exists(exe_file):
                    os.unlink(exe_file)
                return {
                    "output": "",
                    "error": f"Execution timeout ({self.timeout}s exceeded)",
                    "execution_time": self.timeout,
                    "success": False
                }
                
        except FileNotFoundError:
            if source_file and os.path.exists(source_file):
                os.unlink(source_file)
            if exe_file and os.path.exists(exe_file):
                os.unlink(exe_file)
            return {
                "output": "",
                "error": "C++ compiler not found. Please install g++ to execute C++ code.",
                "execution_time": 0,
                "success": False
            }
        except Exception as e:
            logger.error(f"C++ execution error: {e}", exc_info=True)
            if source_file and os.path.exists(source_file):
                try:
                    os.unlink(source_file)
                except:
                    pass
            if exe_file and os.path.exists(exe_file):
                try:
                    os.unlink(exe_file)
                except:
                    pass
            return {
                "output": "",
                "error": f"Execution error: {str(e)}",
                "execution_time": time.time() - start_time,
                "success": False
            }


# Global executor instance
code_executor = CodeExecutor()