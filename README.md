# pyuniprot
`pyuniprot` parses a Uniprot txt file given a Uniprot ID into a python object. All information is made programmatically accessible when programming in python, the most used programming language in bioinformatics.

Through the python object, mostly a dictionary of different categories and each category is wrapped as a `dataclass` so that inside attributes are easy to access through dot notations. Convenient functions will be provided for some common usage.

Contributions are highly welcomed!

## Install

```bash
pip install pyuniprotkb
```

## Quick Start

1. Read a local file `./P01116.txt` or download from UniprotKB and save to the current directory

```python
from pyuniprot import Uniprot
uniprot_id = "P01116"
uniprot = Uniprot(
    uniprot_id, local_download_dir='./', save_txt=True)
)  # If './P01116.txt' exists, pyuniprot reads it directly; if not pyuniprot downloads it from UniprotKB first and (optionally) saves it to './'
print(uniprot.category_lines)  # It prints out all the information for a Uniprot ID that UniprotKB has for it.
```

2. Access category information
```python
print(uniprot.category_lines['AC'])
# result: AC(primary_accession='P01116;', secondary_accessions=['A8K8Z5', 'B0LPF9', 'P01118', 'Q96D10'])
```

Currently, most information can only be accessed from the `category_lines` python dictionary. In this dictionary, the keys are just the two-letter codes used by UniprotKB.

They are (in my understanding):

- `ID`: UniprotKB identifers
- `AC`: accession numbers (the example above)
- `DT`: entry brief history
- `DE`: protein names/descriptions
- `GN`: gene name (by HGNC?)
- `OS`,`OC`,`OX` (grouped as `OSCX` in pyuniprot): organism names
- `RN`,`RP`,`RC`,`RX`,`RA`,`RT`,`RL` (grouped as `RNPCXATL` in pyuniprot): references
- `CC`: activity comments
- `DR`: database cross references
- `PE`: protein evidence level
- `KW`: protein keywords
- `FT`: protein feature tables
- `SQ`: protein sequence

## Contributing
1. Fork this repository
2. Create a branch for your fix of an issue/feature/doc (`git checkout -b my-fix`)
3. Stage your changes, run `pre-commit`, and run `pytest` until every thing looks fine
4. Commit your changes (`git commit -am 'Added some feature/fix/doc'`)
5. Push to the branch (`git push origin my-fix`)
6. Create new Pull Request

For code quality control, we use `pre-commit` hooks for formatting and type hints.

Try your best to add test cases for bug fixes and new features. We use `pytest` for testing.

For documentation, we should try to follow the [Google Python docstrings style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).
