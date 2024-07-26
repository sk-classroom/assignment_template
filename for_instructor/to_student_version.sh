if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <teacher_notebook.ipynb> <student_notebook.ipynb> <encryption_password>"
    exit 1
fi

teacher_notebook=$1
student_notebook=$2
encryption_password=$3

teacher_notebook_enc=${teacher_notebook%.ipynb}.ipynb.enc
teacher_notebook_py=${teacher_notebook%.ipynb}.py
teacher_notebook_py_tagged=${teacher_notebook%.ipynb}_tagged.py
teacher_notebook_ipynb_tagged=${teacher_notebook_py_tagged%.py}.ipynb

openssl enc -aes256 -in $teacher_notebook -out $teacher_notebook_enc -pass pass:$encryption_password

jupytext $teacher_notebook --to py

sed -e 's/^# \+$/# + tags=["non-grading-item"]/' $teacher_notebook_py > $teacher_notebook_py_tagged

jupytext $teacher_notebook_py_tagged --to ipynb
echo $teacher_notebook_py_tagged
jupyter nbconvert --to notebook --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_cell_tags='["answer"]' $teacher_notebook_ipynb_tagged  --output $student_notebook

rm $teacher_notebook_py $teacher_notebook_py_tagged $teacher_notebook_ipynb_tagged

