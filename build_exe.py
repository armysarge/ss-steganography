"""
build_exe.py - Build script for SS Steganography

This script builds the SS Steganography application into an executable file using
PyInstaller
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

def get_script_dir():
    """Get the directory of the current script."""
    return Path(__file__).parent.absolute()

def clean_build_dirs():
    """Clean up previous build directories."""
    dirs_to_clean = ['dist', 'build', '__pycache__']

    for dir_name in dirs_to_clean:
        dir_path = get_script_dir() / dir_name
        if dir_path.exists():
            print(f"Cleaning {dir_path}...")
            shutil.rmtree(dir_path)

def copy_python_files(script_path, output_dir):
    """Simple copy of Python files"""
    print("\n=== Preparing Python files ===")

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)

    try:
        script_name = Path(script_path).name
        output_file = Path(output_dir) / script_name
        script_dir = Path(script_path).parent

        # Copy main script
        shutil.copy(script_path, output_file)
        print(f"Copied main script to {output_file}")

        # Copy dependencies - steganography.py if it exists
        steg_module = script_dir / "steganography.py"
        if steg_module.exists():
            steg_output = Path(output_dir) / "steganography.py"
            shutil.copy(steg_module, steg_output)
            print(f"Copied dependency: steganography.py")

        # Add any other dependencies here if needed

        return True
    except Exception as e:
        print(f"Error copying Python files: {e}")
        return False

def run_pyinstaller(script_path, icon_path=None, one_file=True):
    """Run PyInstaller to create the executable."""
    print("\n=== Building executable with PyInstaller ===")

    cmd = ["pyinstaller"]

    # Add icon if provided
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])

    # Create a single file or directory
    if one_file:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    # Add other PyInstaller options
    cmd.extend([
        "--clean",            # Clean PyInstaller cache
        "--noconfirm",        # Replace output directory without confirmation
        "--name", "SS-Steganography",  # Name of the executable
        "--windowed",         # Windows application (no console)
        script_path           # Script to build
    ])

    try:
        subprocess.run(cmd, check=True)
        print("PyInstaller build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller build failed: {e}")
        return False

def copy_additional_files():
    """Copy any additional files needed for the application."""
    # Check for icon.ico file
    icon_path = get_script_dir() / "icon.ico"
    if icon_path.exists():
        dist_dir = get_script_dir() / "dist"
        shutil.copy(icon_path, dist_dir)
        print(f"Copied {icon_path} to {dist_dir}")

    # Add other files that need to be copied to dist

def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description='Build SS Steganography executable')
    parser.add_argument('--clean-only', action='store_true', help='Only clean build directories')
    parser.add_argument('--no-onefile', action='store_true', help='Create a directory instead of a single executable')
    args = parser.parse_args()

    script_dir = get_script_dir()
    script_path = script_dir / "ss_steganography.py"
    icon_path = script_dir / "icon.ico"

    if not icon_path.exists():
        icon_path = None
        print("Warning: icon.ico not found. The executable will use the default icon.")
    print(f"Building from: {script_path}")

    # Create build directory
    build_dir = script_dir / "build"

    # Clean previous build artifacts
    clean_build_dirs()

    if args.clean_only:
        print("Clean-only requested. Exiting.")
        return

    # Check if the script exists
    if not script_path.exists():
        print(f"Error: Script not found at {script_path}")
        return    # Step 1: Copy Python files to the build directory
    if not copy_python_files(str(script_path), str(build_dir)):
        return

    # Define the path to the copied script
    build_script = build_dir / Path(script_path).name

    # Step 2: Create the executable with PyInstaller
    if not run_pyinstaller(str(build_script), icon_path, not args.no_onefile):
        return

    # Step 3: Copy any additional files needed
    copy_additional_files()

    print("\n=== Build Completed Successfully! ===")
    dist_dir = script_dir / "dist"
    print(f"Executable can be found in: {dist_dir}")

if __name__ == "__main__":
    main()
