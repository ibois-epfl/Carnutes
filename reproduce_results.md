# Reproduction of the paper's results

To reproduce the results of the publication, please reproduce the following steps:

## environment activation
To run the evaluation, you will need to activate the conda environment defined by the environment.yml provided in the repository:
```bash
# from Carnute's repository root directory:
conda env create -f environment
conda activate Carnutes
```
You should see "(Carnutes)" in your terminal.

then go to the tests directory and run the evaluation script:
```bash
cd tests
python3 evaluate_unoptimized_tree_selection.py <parameters>
```

the different parameters are:
```bash
# evaluate single simple truss
python3 evaluate_unoptimized_tree_selection.py -d 0.3 -t "simple_frame" -n 1

# evaluate the 19 simple frames
python3 evaluate_unoptimized_tree_selection.py -d 0.3 -t "simple_frame" -n 19

# evaluate single scissor frame
python3 evaluate_unoptimized_tree_selection.py -d 0.3 -t "scissor_truss" -n 1

# evaluate 11 scissor frames
python3 evaluate_unoptimized_tree_selection.py -d 0.3 -t "scissor_truss" -n 11

# evaluate single symmetrical portal
python3 evaluate_unoptimized_tree_selection.py -d 0.3 -t "symmetrical_portal" -n 1

# evaluate 10 symmetrical portals
python3 evaluate_unoptimized_tree_selection.py -d 0.3 -t "symmetrical_portal" -n 10

# evaluate single asymmetrical portal
python3 evaluate_unoptimized_tree_selection.py -d 0.3 -t "asymmetrical_portal" -n 1

# evaluate single asymmetrical portal
python3 evaluate_unoptimized_tree_selection.py -d 0.3 -t "asymmetrical_portal" -n 15

# evaluate single tower
python3 evaluate_unoptimized_tree_selection.py -d 0.3 -t "tower" -n 1

# evaluate 3 towers
python3 evaluate_unoptimized_tree_selection.py -d 0.3 -t "tower" -n 3
