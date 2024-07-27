if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <test_python_script> <assignment_notebook> [cell_tag]"
  echo "cell_tag: The name of the tag used to extract the cells (default is 'assignment')"
  exit 1
fi

test_python_script=$1
assignment_notebook=$2
if [ -z "$3" ]; then
  cell_tag="gradable"
else
  cell_tag=$3
fi

ungraded_notebook="tmp_ungraded.ipynb"
ungraded_py="tmp_ungraded.py"

# Get the cells with tag "gradable"
jq '.cells |= map(select(.metadata.tags and (.metadata.tags | index("'$cell_tag'"))))' $assignment_notebook > $ungraded_notebook

#jupyter nbconvert --to notebook --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_cell_tags='["non-grading-item"]' --output $ungraded_notebook $ungraded_notebook

jupytext $ungraded_notebook --to py

cat $ungraded_py $test_python_script | python

rm $ungraded_notebook $ungraded_py