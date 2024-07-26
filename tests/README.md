## Test for assignment

A student's assignment is evaluated in the following steps:
1. cells with `grading` tag are removed from the student's notebook, and then converted to .py script
2. The .py script is prepended to the test script (e.g., `test_01.py`)
3. Run the test script

The whole process is automated by `grade_notebook.sh`. For instance, to grade `assignment/assignment.ipynb` with `test_01.py`, run:

```bash
bash tests/grade_notebook.sh tests/test_01.py assignment/assignment.ipynb
```
