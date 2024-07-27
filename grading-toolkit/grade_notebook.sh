test_python_script=$1
assignment_notebook=$2

ungraded_notebook="tmp_ungraded.ipynb"
ungraded_py="tmp_ungraded.py"

# Get the cells with tag "gradable"
jq '.cells |= map(select(.metadata.tags and (.metadata.tags | index("gradable"))))' $assignment_notebook > $ungraded_notebook
#jupyter nbconvert --to notebook --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_cell_tags='["non-grading-item"]' --output $ungraded_notebook $ungraded_notebook

jupytext $ungraded_notebook --to py

cat $ungraded_py $test_python_script | python

rm $ungraded_notebook $ungraded_py