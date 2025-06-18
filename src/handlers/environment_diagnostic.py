"""Check what's available in the current Lambda environment."""
import json
import logging
import subprocess
import sys
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Check Lambda environment capabilities."""
    results = {}
    
    try:
        # Check 1: Python environment
        results["python_version"] = sys.version
        results["python_path"] = sys.path
        
        # Check 2: Available system binaries
        binaries_to_check = ['ffmpeg', 'yt-dlp', 'youtube-dl']
        results["system_binaries"] = {}
        
        for binary in binaries_to_check:
            try:
                result = subprocess.run([binary, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                results["system_binaries"][binary] = {
                    "available": result.returncode == 0,
                    "version": result.stdout.split('\n')[0] if result.returncode == 0 else "N/A",
                    "error": result.stderr if result.returncode != 0 else None
                }
            except Exception as e:
                results["system_binaries"][binary] = {
                    "available": False,
                    "error": str(e)
                }
        
        # Check 3: Directory contents and permissions
        results["current_directory"] = os.getcwd()
        results["directory_contents"] = os.listdir('/tmp') if os.path.exists('/tmp') else []
        results["tmp_writable"] = os.access('/tmp', os.W_OK)
        
        # Check 4: Environment variables
        results["environment_vars"] = {
            "PATH": os.environ.get('PATH', 'Not set'),
            "LD_LIBRARY_PATH": os.environ.get('LD_LIBRARY_PATH', 'Not set'),
            "TRANSCRIPTION_BUCKET": os.environ.get('TRANSCRIPTION_BUCKET', 'Not set')
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'environment_check_complete',
                'results': results
            }, indent=2)
        }
        
    except Exception as e:
        logger.error(f"Environment check failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'environment_check_error',
                'error': str(e)
            })
        }
