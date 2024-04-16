# pyuniprot
`pyuniprot` parses a UniProt text file given a Uniprot ID into a python object. All information is made programmatically accessible when programming in python, the most used programming language in bioinformatics.

The text file format of the UniProt different API formats was chosen because we could download the whole dataset as text and run local queries without worrying about internet connection or UniProt API limits.

Through the python object, mostly a dictionary of different categories and each category is wrapped as a `dataclass` so that inside attributes are easy to access through dot notations. Convenient functions will be provided for some common usage.

Contributions are highly welcomed!

## Install

```bash
pip install pyuniprotkb
```

## Quick Start

### 1. Read a local file or download from UniprotKB and save to the current directory

```python
from pyuniprot import Uniprot
uniprot_id = "P01116"
uniprot = Uniprot(
    uniprot_id, local_download_dir='./', save_txt=True)
)  # If './P01116.txt' exists, pyuniprot reads it directly; if not pyuniprot downloads it from UniprotKB first and (optionally) saves it to './'
print(uniprot.category_lines)  # It prints out all the information for a Uniprot ID that UniprotKB has for it.
```

### 2. Access category information
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

### 3. Get database cross references information through dataclasses for `DR`.
```python
from pyuniprot import Uniprot
uniprot_id = "P04637"
uniprot = Uniprot(uniprot_id, save_txt=True, local_download_dir='./')
dr = uniprot.category_lines["DR"].database_references
# 1. Get PDB records for the protein
pdbs = dr['PDB']
print(len(pdbs))    # total number of PDB records for P04637, which is 268
print(pdbs[0])      # first PDB record: PDB(pdb_id='1A1U', experiment_method='NMR', resolution='-', resolution_unit='', chain_ids=['A', 'C'], uniprot_res_range=[SeqRange(seq_begin=324, seq_end=358)])
print(pdbs[0].pdb_id)   # access the pdb_id attribute in the PDB dataclass; here the result is 1A1U

# 2. Get EMBL records
embls = dr['EMBL']
print(len(embls))   # 85
print(embls[0])     # EMBL(nucleotide_sequence_id='X02469', protein_sequence_id='CAA26306.1', molecule_type='-', status='mRNA')
print(embls[0].nucleotide_sequence_id)      # X02469

# 3. Get CCDS records
ccds = dr['CCDS']
print(len(ccds))   # 9
print(ccds[0])     # CCDS(ccds_id='CCDS11118.1', isoform='P04637-1')
print(ccds[0].ccds_id)      # CCDS11118.1

# 4. Get PIR record
pir = dr['PIR']
print(len(pir))   # 1 (should be only one)
print(pir[0])     # PIR(uid='A25224', entry='DNHU53')
print(pir[0].uid)      # A25224

# 5. Get RefSeq records
refseqs = dr['RefSeq']
print(len(refseqs))   # 15
print(refseqs[0])     # RefSeq(protein_sequence_id='NP_000537.3', nucleotide_sequence_id='NM_000546.5.', isoform='P04637-1')
print(refseqs[0].protein_sequence_id)      # NP_000537.3

# 6. Get Reactome records
reactomes = dr['Reactome']
print(len(reactomes))   # 44
print(reactomes[0])     # Reactome(id='R-HSA-111448', pathway='Activation of NOXA and translocation to mitochondria')
print(reactomes[0].id)  # R-HSA-111448

# 7. Get GO records
gos = dr['GO']
print(len(gos))   # 176
print(gos[0])     # GO(accession_number='0005813', aspect='Cellular Component', term='centrosome', inferred_from='Direct Assay', source='UniProtKB')
print(gos[0].accession_number)  # 0005813
```
More to come! Make an issue if you need a specific one DR type.

### 4. Get the [UniRef](https://www.uniprot.org/help/uniref) data with certain sequence identity threshold. This data from UniProt provids reference clustered sets of sequences.
```python
from pyuniprot import UniRef
uniprot_id = "P36952"
uniref = UniRef(uniprot_id, local_download_dir='./') # default sequence identity threshold is 100
print(uniref.members)  # We get the following result
# [{"memberIdType": "UniParc", "memberId": "UPI0003EAE5A1","organismName": "Homo sapiens", "organismTaxId": 9606, "sequenceLength": 204,"proteinName": "serpin B5 isoform X1", "uniref90Id": "UniRef90_P36952"}]

# If we change the `thresh` keyword argument in the UniRef class to 90 or 50, we can get the data for clusters with 90 or 50 sequence identity.
uniref_90 = UniRef(uniprot_id, thresh=90, local_download_dir='./')
uniref_50 = UniRef(uniprot_id, thresh=50, local_download_dir='./')
print(len(uniref_50.members)) # now we get the following number of members in the cluster
# 218
```

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
