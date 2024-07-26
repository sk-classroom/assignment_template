Plese feel free to post your code here. Again, this is not grading item.

## How to use to_student_version.sh

The `to_student_version.sh` script is used to convert a teacher's notebook into a student's notebook by removing specific cells and encrypting the original notebook.

Run the script with the following command:
```
./to_student_version.sh <teacher_notebook.ipynb> <student_notebook.ipynb> <encryption_password>
```
- Input arguments:
  - `<teacher_notebook.ipynb>`: The path to the teacher's notebook file.
  - `<student_notebook.ipynb>`: The path where the student's notebook file will be saved.
  - `<encryption_password>`: The password used to encrypt the teacher's notebook.
- Output files:
  - `<student_notebook.ipynb>`: The student's notebook file with cells that are tagged with "answer" removed.
  - `<teacher_notebook.ipynb>.enc`: The encrypted teacher's notebook file that can be added to the repository while hiding the original teacher's notebook.

  Example:
  ```bash
  bash to_student_version.sh assignment_teacher.ipynb ../assignment/assignment.ipynb mypassword 
  ```
