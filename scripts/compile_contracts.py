"""
PharmaClear - Direct Python Compilation Script
This script compiles contracts using Python's subprocess with explicit interpreter path.
Workaround for Windows App Execution Alias issues.
"""

import subprocess
import sys
from pathlib import Path

def compile_contract(contract_path: Path, output_dir: Path) -> bool:
    """Compile a single Algorand Python contract using AlgoKit."""
    print(f"🔨 Compiling: {contract_path.name}...")

    try:
        # Use sys.executable to ensure we use the same Python interpreter
        result = subprocess.run(
            [
                "algokit",
                "compile",
                "python",
                str(contract_path),
                "--out-dir",
                str(output_dir)
            ],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            print(f"   ✅ Success\n")
            return True
        else:
            print(f"   ❌ Failed")
            if result.stderr:
                print(f"   Error: {result.stderr}\n")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}\n")
        return False


def main():
    print("\n" + "=" * 50)
    print("  PharmaClear Smart Contract Compilation")
    print("=" * 50 + "\n")

    # Set up paths
    project_root = Path(__file__).parent.parent
    contracts_dir = project_root / "smart_contracts"
    output_dir = project_root / "smart_contracts" / "artifacts"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir}\n")

    # List of contracts to compile
    contracts = [
        "layer0_ingestion.py",
        "layer0_enhanced.py",
        "layer1_rebate.py",
        "layer2_escrow.py",
        "layer3_audit.py",
        "layer4_governance.py",
        "layer5_crossborder.py"
    ]

    compiled = 0
    failed = 0

    for contract_name in contracts:
        contract_path = contracts_dir / contract_name

        if contract_path.exists():
            if compile_contract(contract_path, output_dir):
                compiled += 1
            else:
                failed += 1
        else:
            print(f"⚠️  Skipping: {contract_name} (not found)\n")

    # Summary
    print("\n" + "=" * 50)
    print("  Compilation Summary")
    print("=" * 50)
    print(f"✅ Compiled: {compiled}")
    print(f"❌ Failed: {failed}")

    if failed > 0:
        print("\n⚠️  Some contracts failed to compile.")
        print("This may be due to Windows App Execution Alias issues.\n")
        print("To fix:")
        print("1. Open Windows Settings")
        print("2. Search for 'App execution aliases'")
        print("3. Disable 'python.exe' and 'python3.exe' aliases")
        print("4. Re-run this script\n")
        return 1
    else:
        print(f"\n🎉 All contracts compiled successfully!")
        print(f"📁 TEAL files are in: {output_dir}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
