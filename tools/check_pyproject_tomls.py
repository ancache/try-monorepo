import sys
import tomllib
from pathlib import Path
from typing import Dict, Any

EXCLUDED_DIRS = {"venv", ".venv", "env", ".env", "virtualenv", ".virtualenv"}

# Load the root pyproject.toml as the template, including dev dependencies
def load_root_config():
    root_path = Path("pyproject.toml")
    if not root_path.is_file():
        print("Root pyproject.toml not found.")
        sys.exit(1)
    
    with open(root_path, "rb") as f:
        root_config = tomllib.load(f)
    
    # Filter out path dependencies from the root config
    def filter_external_deps(deps: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in deps.items() if not (isinstance(v, dict) and "path" in v)}
    
    root_dependencies = filter_external_deps(root_config.get("tool", {}).get("poetry", {}).get("dependencies", {}))
    root_dev_dependencies = filter_external_deps(
        root_config.get("tool", {}).get("poetry", {}).get("group", {}).get("dev", {}).get("dependencies", {})
    )
    
    return root_config, root_dependencies, root_dev_dependencies

# Recursively find all pyproject.toml files in the repo, excluding virtual environments
def find_all_pyproject_files():
    repo_path = Path(".")
    
    pyproject_files = []
    for p in repo_path.rglob("pyproject.toml"):
        if any(excluded in p.parts for excluded in EXCLUDED_DIRS):
            continue
        if p != repo_path / "pyproject.toml":
            pyproject_files.append(p)
    
    return pyproject_files

# Compare dependencies between root and a given pyproject.toml
def compare_dependencies(root_dependencies: Dict[str, Any], current_dependencies: Dict[str, Any], filepath: Path, dep_type: str) -> bool:
    has_difference = False

    # Filter out path dependencies in the current file
    current_deps = {k: v for k, v in current_dependencies.items() if not (isinstance(v, dict) and "path" in v)}
    # Check for any missing or differing dependencies
    for dep, version in root_dependencies.items():
        if dep not in current_deps:
            print(f"{filepath}: Missing {dep_type} dependency '{dep}' required by root pyproject.toml.")
            has_difference = True
        elif current_deps[dep] != version:
            print(f"{filepath}: {dep_type} dependency '{dep}' version mismatch. Found '{current_deps[dep]}', expected '{version}'.")
            has_difference = True

    return has_difference

# Compare black configuration between root and a given pyproject.toml
def compare_black_config(root_config: Dict[str, Any], current_config: Dict[str, Any], filepath: Path) -> bool:
    has_difference = False
    for key, value in root_config.items():
        if current_config.get(key) != value:
            print(f"{filepath}: Black configuration mismatch for '{key}'. Found '{current_config.get(key)}', expected '{value}'.")
            has_difference = True
    return has_difference

# Validate each pyproject.toml against the root template
def validate_pyproject_files():
    root_config, root_dependencies, root_dev_dependencies = load_root_config()
    root_black_config = root_config.get("tool", {}).get("black", {})

    all_files_valid = True
    for filepath in find_all_pyproject_files():
        with open(filepath, "rb") as f:
            current_config = tomllib.load(f)
        
        current_dependencies = current_config.get("tool", {}).get("poetry", {}).get("dependencies", {})
        current_dev_dependencies = current_config.get("tool", {}).get("poetry", {}).get("group", {}).get("dev", {}).get("dependencies", {})
        current_black_config = current_config.get("tool", {}).get("black", {})

        # Compare dependencies, dev-dependencies, and black config
        deps_valid = not compare_dependencies(root_dependencies, current_dependencies, filepath, "main")
        dev_deps_valid = not compare_dependencies(root_dev_dependencies, current_dev_dependencies, filepath, "dev")
        black_valid = not compare_black_config(root_black_config, current_black_config, filepath)
        
        if not (deps_valid and dev_deps_valid and black_valid):
            all_files_valid = False

    return all_files_valid

# Run validation and exit with appropriate code
if __name__ == "__main__":
    if not validate_pyproject_files():
        print("Some pyproject.toml files did not match the root configuration.")
        sys.exit(1)
    else:
        print("All pyproject.toml files match the root configuration.")
        sys.exit(0)