# HIPE-pycommons

HIPE-pycommons is a python library for the management of NE-annotated data. It deals with the import and manipulation of annotations coming from INCEpTION and with the export and manipulation of HIPE-compliant `tsv` files.

The `helpers` package contains functions and objects to manipulate tsv files. It allows notably to : 

- parse `tsv`s to dedicated objects, such as `HipeDocument`, `TSVComment` and `TSVAnnotation`. 


- Export `tsv`s to: 
  - `pandas.DataFrame` using `tsv_to_dataframe`
  - Lists of samples/examples using `tsv_to_lists`
  - Pytorch `Datasets` using `tsv_to_torch_datasets`


