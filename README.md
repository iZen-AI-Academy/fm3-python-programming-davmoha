[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=23766247&assignment_repo_type=AssignmentRepo)
# FM3 - Python Programming

This repository is the GitHub Classroom template for the Foundations Python Programming assignment.

## Student workflow

1. Accept the GitHub Classroom assignment.
2. Open the repository in **GitHub Codespaces**.
3. Complete the required functions inside `python_programming_exercises.ipynb`.
4. Commit and push your changes to `main`.
5. Your push triggers GitHub Actions autograding.
6. The score is written to GitHub Classroom and then synced to Moodle.

## Functions to implement

Implement these ten functions in the notebook:

- `full`
- `get`
- `set`
- `equal`
- `copy`
- `transpose`
- `flatten`
- `reshape`
- `compute`
- `mean`

## Local testing in Codespaces

Open a terminal and run:

```bash
pip install -r requirements.txt
python scripts/extract_notebook.py
pytest tests/ -q
```

The extraction script creates `student_solution.py` from the code in the notebook so the tests can import it.

## Notes for instructors

- The workflow is designed so that **grading happens first**.
- Moodle sync happens after grading and is marked non-fatal so a Moodle issue does not hide the GitHub Classroom result.
- `MOODLE_URL` and `MOODLE_TOKEN` should be stored as **organization secrets**.
- The GitHub-to-Moodle student map is fetched from the shared config repo at runtime. If that download fails, the workflow falls back to the local `github_moodle_map.csv` file.
