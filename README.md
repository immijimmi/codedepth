# codedepth

###### Generates scores for how many layers of local imports are in a file

## Quickstart

Below is an example of scores being generated and then displayed in graph forms, for files in the provided directory.

```python
from codedepth import Scorer

scorer = Scorer(r"C:\Repos\managedstate\managedstate")

# Calculates scores for all files in the provided directory
scorer.generate_scores()

"""
Generates a PDF saved in the working directory,
containing a ranked directional graph of the file dependencies.
Once this is generated, it will be opened automatically
"""
scorer.plot_ranked()

# Generates and displays a circular directional graph of the file dependencies in memory
scorer.plot_circular()
```
