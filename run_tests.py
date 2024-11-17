from pathlib import Path
import subprocess


def run_and_validate_outputs(yaml_dir: str, script_name: str = "aufgabe1.py", validator_name: str | None = None
                             # "test_output.py"
                             ) -> None:
    """
    Processes YAML files in a directory, organizes outputs, and validates results.

    Args:
        yaml_dir (str): Directory containing YAML problem files.
        script_name (str): Name of the Python script to solve the problems (default: "aufgabe1.py").
        validator_name (str): Name of the script to validate outputs (default: "test_output.py").
    """
    # Path to the directory containing YAML files
    tests_path = Path(yaml_dir)
    output_files = ["aufgabe1-1.yaml", "aufgabe1-2.yaml", "aufgabe1-3.yaml"]

    for yaml_file in tests_path.glob("*.yaml"):
        base_name = yaml_file.stem
        folder_path = tests_path / base_name

        # Ensure a folder exists for each YAML file
        folder_path.mkdir(exist_ok=True)

        # Run the problem-solving script
        try:
            subprocess.run(["python", script_name, str(yaml_file)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running {script_name} for {yaml_file}: {e}")
            continue

        # Move output files to the respective folder
        for output_file in output_files:
            output_path = Path(output_file)
            destination_path = folder_path / output_file
            if output_path.exists():
                if destination_path.exists():
                    destination_path.unlink()  # Remove existing file
                output_path.rename(destination_path)
            else:
                print(f"Warning: Expected output file {output_file} not found for {yaml_file}")

        # Validate each output file
        if validator_name is not None:
            for output_file in folder_path.glob("aufgabe1-*.yaml"):
                try:
                    subprocess.run(["python", validator_name, str(yaml_file), str(output_file)], check=True)
                    print(f"Validation passed for {output_file}")
                except subprocess.CalledProcessError as e:
                    print(f"Validation failed for {output_file}: {e}")

    print("Processing and validation completed.")


# Example usage
run_and_validate_outputs("tests")
