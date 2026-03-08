import subprocess

bundle_filename = "verification_artifacts_bundle.txt"

files_to_include = [
    "verification_report.md",
    "bootstrap/task_ledger.csv",
    "bootstrap/artifact_registry.csv",
    "bootstrap/evidence_register.csv",
    "bootstrap/reports/daily_state_snapshot.md",
    "docs/specs/identity_cid_uuidv7.md",
    "docs/specs/ledger_api_and_ordering.md",
    "docs/specs/issuerproof_v1.md",
    "docs/specs/evaluator_boundary_v1.md",
    "schemas/release_manifest.schema.json",
    "schemas/runtime_load_manifest.schema.json",
    "fixtures/release_manifest_fixture.json",
    "fixtures/runtime_load_manifest_fixture.json",
    "src/cid.py",
    "src/ledger.py",
    "src/issuer_proof.py",
    "src/evaluator.py",
    "src/loader.py",
    "tools/packager.py",
    "tests/test_cid.py",
    "tests/test_ledger.py",
    "tests/test_issuer_proof.py",
    "tests/test_evaluator.py",
    "tests/test_packager.py",
    "tests/test_loader.py",
    "dist/SupportOntologyRelease-v0.1.0/release_manifest.json",
    "dist/SCR_TBox_Release-v0.1.0/release_manifest.json",
]

commands_to_include = [
    "sha256sum dist/SupportOntologyRelease-v0.1.0/*",
    "sha256sum dist/SCR_TBox_Release-v0.1.0/*",
    "python3 -m unittest tests/test_cid.py",
    "python3 -m unittest tests/test_ledger.py",
    "python3 -m unittest tests/test_issuer_proof.py",
    "python3 -m unittest tests/test_evaluator.py",
    "python3 -m unittest tests/test_packager.py",
    "python3 -m unittest tests/test_loader.py",
]

with open(bundle_filename, "w", encoding="utf-8") as bundle_file:
    for file_path in files_to_include:
        bundle_file.write(f"===== BEGIN FILE: {file_path} =====\n")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                bundle_file.write(f.read())
        except FileNotFoundError:
            bundle_file.write("FILE NOT FOUND\n")
        except Exception as e:
            bundle_file.write(f"FILE READ ERROR: {e}\n")
        bundle_file.write("\n")
        bundle_file.write(f"===== END FILE: {file_path} =====\n\n")

    for command in commands_to_include:
        bundle_file.write(f"===== BEGIN COMMAND: {command} =====\n")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout:
                bundle_file.write(result.stdout)
            if result.stderr:
                bundle_file.write(result.stderr)
            if result.returncode != 0:
                bundle_file.write(f"COMMAND FAILED WITH EXIT CODE: {result.returncode}\n")
        except Exception as e:
            bundle_file.write(f"COMMAND EXECUTION ERROR: {e}\n")
        bundle_file.write("\n")
        bundle_file.write(f"===== END COMMAND: {command} =====\n\n")

print(f"DONE: {bundle_filename}")