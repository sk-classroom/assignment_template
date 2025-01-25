# For instructor

## Workflow

- [ ] Create the teacher notebook with answers
  - Add tag "answer" for the cells with the assignment answers
  - Add tag "gradable" for the cells that are gradable
- [ ] Write test scripts
  - Write test scripts (e.g., `test_01.py`) and place them in the `tests` folder
  - Make sure that the grading works locally by running `bash grading-toolkit/grade_notebook.sh tests/test_01.py for_instructor/assignment_teacher.ipynb answer`
- [ ] Generate the student version and the encrypted teacher's notebook
  - Run the `to_student_version.sh` script by
  - `bash grading-toolkit/to_student_version.sh for_instructor/assignment_teacher.ipynb assignment/assignment.ipynb mypassword`
  - Change the password to something more secure
- [ ] Add the encrypted teacher's notebook to the repository
  - `git rm -f for_instructor/assignment_teacher.ipynb`
  - `git add for_instructor/assignment_teacher.ipynb.enc & git commit -m "Update assignment" & git push`
- [ ] Test the auto-grader
  - [ ] Make sure that requirements.txt is updated
  - [ ] Change the branch to "test"
  - [ ] Edit `.github/workflows/classroom.yml` to add the test id to the `runners` list
  - [ ] Check the auto-grader by yourself by submitting the assignment
  - [ ] If the auto-grader passes, change the branch back to "main" and delete the test branch by
     - `git checkout main`
     - `git branch -d test`
     - `git push origin --delete test`
- [ ] Set up the auto-grader
  - Open an assignment in Github Classroom
- [ ] Make sure the auto-grader works
  - [ ] Play the student role by yourself by accepting the assignment
  - [ ] Check the auto-grader by yourself by submitting the assignment
- [ ] Distribute the assignment to students

## Check list

- [ ] Upload
  - [ ] The `assignment/assignment.ipynb` is uploaded to the repository
  - [ ] The `assignment_teacher.ipynb` is **NOT** uploaded to the repository
  - [ ] The `assignment_teacher.ipynb.enc` is uploaded to the repository
- [ ] Autograding
  - [ ] All tests run successfully
- [ ] Keep the password secret

## How to decrypt the teacher's notebook

```bash
openssl enc -d -aes256 -pass pass:mypassword -in assignment_teacher.ipynb.enc >assignment_teacher.ipynb
```
- Change the password used to encrypt the notebook

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
