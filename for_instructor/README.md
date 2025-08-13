# For instructor

## Workflow

- [ ] Write test scripts
  - Write test scripts (e.g., `test_01.py`) and place them in the `tests` folder
- [ ] Create the teacher notebook with answers in "grading/assignment.py"
- [ ] Test run the teacher notebook by running
  - `uv run tests/test_01.py`  (more tests if needed)
  - `./grading/run_quiz_test.sh --config ./grading/config.toml --quiz-file ./assignment/quiz.toml --api-key ${{ secrets.CHAT_API }} --output ./assignment/quiz_results.json`
  - If the results are not as expected, fix the code in "grading/assignment.py" and repeat the process
- [ ] Generate the student version and the encrypted teacher's notebook
  - Copy "./grading/assignment.py" to "./assignment/assignment.py"
  - Remove the code to test in the student version
  - Set an environment variable for the encryption key (e.g., `GITHUB_CLASSROOM_ASSIGNMENT_KEY`)
  - Encrypt using OpenSSL with PBKDF2 and iterations (recommended):
    ```bash
    openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 \
      -in grading/assignment.py \
      -out grading/assignment.py.enc \
      -pass env:GITHUB_CLASSROOM_ASSIGNMENT_KEY
    ```
    - Alternatively (less preferred), if you must pass the value explicitly, always quote it to avoid issues with special characters:
      ```bash
      openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 \
        -in grading/assignment.py \
        -out grading/assignment.py.enc \
        -pass pass:"$GITHUB_CLASSROOM_ASSIGNMENT_KEY"
      ```
- [ ] Add the encrypted teacher's notebook to the repository
  - Remove all commit history if needed by following these steps:
    1. Create a fresh orphan branch: `git checkout --orphan latest_branch`
    2. Add all files: `git add -A`
    3. Commit: `git commit -am "Initial commit"`
    4. Delete the old branch: `git branch -D main` (or your current branch name)
    5. Rename the new branch: `git branch -m main`
    6. Force push to overwrite history: `git push -f origin main`
    7. One line command: `git checkout --orphan latest_branch && git add -A && git commit -am "Initial commit" && git branch -D main && git branch -m main && git push -f origin main`
- [ ] Distribute the assignment to students

## Check list

- [ ] Upload
  - [ ] The `assignment/assignment.py` is uploaded to the repository
  - [ ] The `grading/assignment.py` is **NOT** uploaded to the repository
  - [ ] The `grading/assignment.py.enc` is uploaded to the repository
- [ ] Autograding
  - [ ] All tests run successfully
- [ ] Keep the password secret

## How to decrypt the teacher's notebook

1) Ensure the encryption key is available as an environment variable (recommended name):

- macOS/Linux (bash or zsh):
  ```bash
  export GITHUB_CLASSROOM_ASSIGNMENT_KEY='your-very-strong-secret'
  ```
- Windows PowerShell:
  ```powershell
  $Env:GITHUB_CLASSROOM_ASSIGNMENT_KEY = 'your-very-strong-secret'
  ```

Tip: Avoid printing the secret in CI logs. Locally, you can verify it’s set (don’t do this in CI):
```bash
echo "${GITHUB_CLASSROOM_ASSIGNMENT_KEY:+set}"
```

2) Decrypt using OpenSSL with PBKDF2 and iterations (recommended):
```bash
openssl enc -d -aes-256-cbc -salt -pbkdf2 -iter 100000 \
  -in ./grading/assignment.py.enc \
  -out ./grading/assignment.py \
  -pass env:GITHUB_CLASSROOM_ASSIGNMENT_KEY
```

3) Alternative (less preferred): pass the value explicitly, but always quote it:
```bash
openssl enc -d -aes-256-cbc -salt -pbkdf2 -iter 100000 \
  -in ./grading/assignment.py.enc \
  -out ./grading/assignment.py \
  -pass pass:"$GITHUB_CLASSROOM_ASSIGNMENT_KEY"
```

4) Safety/cleanup:
- Do not commit `grading/assignment.py`. Ensure it’s in `.gitignore`.
- Remove the decrypted file when done grading:
  ```bash
  rm ./grading/assignment.py
  ```

## How to use `update-repo.sh` (Propagate Template Updates to Student Repos)

The `update-repo.sh` script is designed to automate the process of propagating changes from the template repository to all student repositories in a GitHub Classroom setup. It merges updates from the template into each student fork, handling merge conflicts by creating pull requests for manual resolution.

### Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) must be installed and authenticated with sufficient permissions to access the organization and student repos.
- You must have push access to the template repo and the ability to create PRs on student repos.

### Usage

1. **Check and Update Script Arguments**

   The `update-repo.sh` script requires four command-line arguments:
   ```
   bash update-repo.sh CLASSROOM_ORG REPO_A REPO_B BRANCH
   ```
   - `CLASSROOM_ORG`: GitHub Classroom organization name (e.g., `sk-classroom`)
   - `REPO_A`: Source repo (e.g., `sk-classroom/starter`)
   - `REPO_B`: Template repo (e.g., `sk-classroom/advnetsci-starter-starter`)
   - `BRANCH`: Branch to propagate (usually `main`)

   Review the top of the script for usage instructions and update the arguments as needed.

2. **Run the Script**

   From the `for_instructor` directory, run the script with the required arguments. For example:
   ```bash
   bash update-repo.sh sk-classroom sk-classroom/starter sk-classroom/advnetsci-starter-starter main
   ```

   The script will:
   - Merge changes from the source repo (`REPO_A`) into the template repo (`REPO_B`).
   - For each student fork of the template repo:
     - Attempt to merge the template updates into the student's specified branch.
     - If the merge succeeds, push directly.
     - If there are conflicts, create a new branch and open a pull request for manual resolution.

3. **Monitor Output**

   - The script prints progress and any errors to the console.
   - For repos with conflicts, a pull request will be created and a message will be printed with the PR details.

### Notes

- The script creates and cleans up temporary directories for each operation.
- If you want to test the script, try it on a small set of test repos first.
- Make sure you have the necessary permissions to push and create PRs on all target repositories.
- To change the branch name (if not `main`), supply the desired branch as the fourth argument when running the script.

### Troubleshooting

- If you see authentication errors, ensure you have run `gh auth login` and have the correct permissions.
- If a merge fails due to conflicts, the script will automatically create a pull request for the student repo with the conflict markers for manual resolution.

For further customization, edit the script as needed to fit your organization's workflow.
