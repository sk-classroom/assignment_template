if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <teacher_notebook.ipynb> <student_notebook.ipynb> <encryption_password>"
    exit 1
fi

teacher_notebook=$1
student_notebook=$2
encryption_password=$3

teacher_notebook_enc=${teacher_notebook%.ipynb}.ipynb.enc

openssl enc -aes256 -in $teacher_notebook -out $teacher_notebook_enc -pass pass:$encryption_password

jupyter nbconvert --to notebook --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_cell_tags='["answer"]' $teacher_notebook --inplace

cp $teacher_notebook $student_notebook

