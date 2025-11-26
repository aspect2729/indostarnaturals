"""Quick test summary script"""
import subprocess
import sys

test_files = [
    "tests/test_models.py",
    "tests/test_cart_service.py",
    "tests/test_user_service.py",
    "tests/test_product_service.py",
    "tests/test_order_service.py",
]

results = {}

for test_file in test_files:
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-v", "--tb=no", "-q"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Extract summary line
    lines = result.stdout.split('\n')
    for line in lines:
        if 'passed' in line or 'failed' in line:
            print(line)
            results[test_file] = line
            break

print(f"\n{'='*60}")
print("SUMMARY")
print('='*60)
for test_file, summary in results.items():
    print(f"{test_file}: {summary}")
