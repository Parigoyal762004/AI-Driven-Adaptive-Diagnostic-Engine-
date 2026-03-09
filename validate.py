#!/usr/bin/env python3
"""
Comprehensive validation script for Adaptive Testing Engine
Tests all components before final packaging
"""
import os
import sys
import json
import ast

def test_structure():
    """Test project structure"""
    print("=" * 60)
    print("TEST 1: Project Structure")
    print("=" * 60)
    
    required = {
        'dirs': ['app', 'app/models', 'app/services', 'app/repositories', 
                 'app/routes', 'app/utils', 'tests', 'tests/unit', 'scripts'],
        'files': ['requirements.txt', 'README.md', '.env.example', 'Dockerfile',
                  'run.sh', 'run.bat', 'setup.bat', 'app/main.py']
    }
    
    errors = []
    for d in required['dirs']:
        if not os.path.isdir(d):
            errors.append(f"Missing directory: {d}")
    
    for f in required['files']:
        if not os.path.isfile(f):
            errors.append(f"Missing file: {f}")
    
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        return False
    
    print(f"  ✓ All {len(required['dirs'])} directories present")
    print(f"  ✓ All {len(required['files'])} required files present")
    return True

def test_python_syntax():
    """Test Python file syntax"""
    print("\n" + "=" * 60)
    print("TEST 2: Python Syntax")
    print("=" * 60)
    
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip venv and cache
        dirs[:] = [d for d in dirs if d not in ['venv', 'test_venv', '__pycache__', '.pytest_cache']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    errors = []
    for filepath in python_files:
        try:
            with open(filepath) as f:
                ast.parse(f.read())
        except SyntaxError as e:
            errors.append(f"{filepath}: {e}")
    
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        return False
    
    print(f"  ✓ All {len(python_files)} Python files have valid syntax")
    return True

def test_json_files():
    """Test JSON file validity"""
    print("\n" + "=" * 60)
    print("TEST 3: JSON Files")
    print("=" * 60)
    
    # Test questions JSON
    try:
        with open('scripts/gre_questions.json') as f:
            questions = json.load(f)
        
        if not isinstance(questions, list):
            print("  ✗ Questions file is not a list")
            return False
        
        if len(questions) < 20:
            print(f"  ✗ Only {len(questions)} questions (expected 20)")
            return False
        
        # Validate question structure
        required_fields = ['question_text', 'options', 'correct_answer', 
                          'difficulty', 'discrimination', 'topic']
        
        for i, q in enumerate(questions):
            for field in required_fields:
                if field not in q:
                    print(f"  ✗ Question {i}: missing {field}")
                    return False
            
            # Validate ranges
            if not (-3 <= q['difficulty'] <= 3):
                print(f"  ✗ Question {i}: difficulty {q['difficulty']} out of range")
                return False
            
            if not (0.5 <= q['discrimination'] <= 2.5):
                print(f"  ✗ Question {i}: discrimination {q['discrimination']} out of range")
                return False
            
            if q['correct_answer'] not in q['options']:
                print(f"  ✗ Question {i}: correct_answer not in options")
                return False
        
        print(f"  ✓ Loaded {len(questions)} valid questions")
        
        # Show distribution
        topics = {}
        difficulties = {'easy': 0, 'medium': 0, 'hard': 0}
        
        for q in questions:
            topics[q['topic']] = topics.get(q['topic'], 0) + 1
            if q['difficulty'] < 0.4:
                difficulties['easy'] += 1
            elif q['difficulty'] < 0.7:
                difficulties['medium'] += 1
            else:
                difficulties['hard'] += 1
        
        print(f"  ✓ Topics: {', '.join(sorted(topics.keys()))}")
        print(f"  ✓ Difficulty: {difficulties['easy']} easy, "
              f"{difficulties['medium']} medium, {difficulties['hard']} hard")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error validating questions: {e}")
        return False

def test_requirements():
    """Test requirements.txt"""
    print("\n" + "=" * 60)
    print("TEST 4: Dependencies")
    print("=" * 60)
    
    try:
        with open('requirements.txt') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        required = ['fastapi', 'uvicorn', 'motor', 'pydantic', 'python-dotenv']
        missing = []
        
        for pkg in required:
            if not any(pkg in line.lower() for line in packages):
                missing.append(pkg)
        
        if missing:
            print(f"  ✗ Missing packages: {missing}")
            return False
        
        print(f"  ✓ Found {len(packages)} dependencies")
        print(f"  ✓ All critical packages present")
        return True
        
    except Exception as e:
        print(f"  ✗ Error reading requirements.txt: {e}")
        return False

def test_documentation():
    """Test documentation files"""
    print("\n" + "=" * 60)
    print("TEST 5: Documentation")
    print("=" * 60)
    
    docs = {
        'README.md': 100,  # min lines
        'QUICKSTART.md': 50,
        'API_EXAMPLES.md': 100,
        'WINDOWS_README.md': 50,
        'PROJECT_SUMMARY.md': 50,
    }
    
    errors = []
    for doc, min_lines in docs.items():
        if not os.path.isfile(doc):
            errors.append(f"Missing: {doc}")
            continue
        
        with open(doc) as f:
            lines = len([l for l in f if l.strip()])
        
        if lines < min_lines:
            errors.append(f"{doc}: only {lines} lines (expected {min_lines}+)")
        else:
            print(f"  ✓ {doc}: {lines} lines")
    
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        return False
    
    return True

def test_scripts():
    """Test startup scripts"""
    print("\n" + "=" * 60)
    print("TEST 6: Startup Scripts")
    print("=" * 60)
    
    scripts = {
        'run.sh': 'Linux/Mac startup script',
        'run.bat': 'Windows startup script',
        'setup.bat': 'Windows setup script',
        'seed.bat': 'Windows seed script',
    }
    
    errors = []
    for script, desc in scripts.items():
        if not os.path.isfile(script):
            errors.append(f"Missing: {script} ({desc})")
        else:
            size = os.path.getsize(script)
            print(f"  ✓ {script}: {size} bytes")
            
            # Check Windows files have CRLF
            if script.endswith('.bat'):
                with open(script, 'rb') as f:
                    content = f.read()
                if b'\r\n' not in content:
                    errors.append(f"{script}: missing Windows line endings (CRLF)")
    
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ADAPTIVE TESTING ENGINE - VALIDATION SUITE")
    print("=" * 60 + "\n")
    
    tests = [
        test_structure,
        test_python_syntax,
        test_json_files,
        test_requirements,
        test_documentation,
        test_scripts,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED - Ready for packaging!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Fix issues before packaging")
        return 1

if __name__ == '__main__':
    sys.exit(main())
