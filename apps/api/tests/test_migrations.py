import os
import sqlite3
import subprocess
import sys


def test_fresh_sqlite_migration_creates_schema(tmp_path) -> None:
    database = tmp_path / "migration.db"
    environment = os.environ.copy()
    environment["DATABASE_URL"] = f"sqlite:///{database.as_posix()}"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    with sqlite3.connect(database) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        experiment_columns = {row[1] for row in connection.execute("PRAGMA table_info(experiments)")}
    assert {"alembic_version", "projects", "traces", "spans", "events", "experiments", "evaluations"} <= tables
    assert "input_json" in experiment_columns


def test_upgrade_from_initial_schema_adds_experiment_input(tmp_path) -> None:
    database = tmp_path / "upgrade.db"
    environment = os.environ.copy()
    environment["DATABASE_URL"] = f"sqlite:///{database.as_posix()}"
    root = os.path.dirname(os.path.dirname(__file__))
    initial = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "0001_initial"], cwd=root, env=environment, capture_output=True, text=True, check=False)
    assert initial.returncode == 0, initial.stderr
    upgraded = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=root, env=environment, capture_output=True, text=True, check=False)
    assert upgraded.returncode == 0, upgraded.stderr
    with sqlite3.connect(database) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(experiments)")}
    assert "input_json" in columns
