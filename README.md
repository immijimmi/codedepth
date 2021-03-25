# codedepth

###### Generates scores for how many layers of local imports/exports are in a file

## Dependencies

You will need the following packages:
- `pip install networkx`
- `pip intall matplotlib`
- `pip install graphviz`

You will also need Graphviz installed as an application - installation instructions can be found at https://graphviz.org/download/

## Quickstart

From the command line (this will use default parameters and output a ranked directional graph as a PDF):

```
C:\Repos\codedepth> python -m codedepth <path of the target directory>
```

In a python script:

```python
from codedepth import Scorer

scorer = Scorer(r"<path of the target directory>")  # Replace this path string with your own

# Calculates scores for all files in the target directory
scorer.parse_all()

"""
Generates a PDF saved in the working directory,
containing a ranked directional graph of the file dependencies for the target directory.
Once this is generated, it will be opened automatically.
Also generates and saves a file containing the DOT code required to create the graph
"""
scorer.plot_ranked()

# Generates and displays a circular directional graph of the file dependencies for the target directory in memory
scorer.plot_circular()
```
