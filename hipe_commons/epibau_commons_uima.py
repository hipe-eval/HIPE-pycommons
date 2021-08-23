"""UIMA stuff."""

__author__ = "Matteo Romanello"
__email__ = "matteo.romanello@epfl.ch"
__organisation__ = "DH Lab, EPFL"
__status__ = "development"

import os
import json
# import ipdb
from tqdm import tqdm
import surf
import pandas as pd
import pyCTS
from .index import clean_scope
from pyCTS import CTS_URN
from cassis import Cas, load_cas_from_xmi, load_typesystem
from knowledge_base import KnowledgeBase


ccType = "webanno.custom.CitationComponents"
reType = "webanno.custom.Re"
neType = "de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity"
posType = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'
sentType = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'


def write_cas(document, typesystem, output_dir):
    """
    Needs:
        - path to typesystem
        - text
        - line breaks
        - entities
        - relations
        - disambiguations
    """

    # types of UIMA annotations
    sentType = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'
    tokenType = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token'
    posType = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'
    ccType = "webanno.custom.CitationComponents"
    reType = "webanno.custom.Re"

    tsf = TypeSystemFactory()
    tsf = tsf.readTypeSystem(typesystem)
    cas = CAS(tsf)
    cas.documentText = document["text"]
    cas.sofaMimeType = 'text'

    # create sentence-level annotations
    start_offset = 0
    for break_offset, next_offset in document["linebreaks"]:
        start = start_offset
        end = break_offset
        start_offset = next_offset
        sntc = cas.createAnnotation(sentType, {'begin': start, 'end': end})
        cas.addToIndex(sntc)

    # create token annotations
    for token in document["tokens"]:
        token_ann = cas.createAnnotation(
            tokenType,
            {
                'begin': token["start_offset"],
                'end': token["end_offset"]
            }
        )
        cas.addToIndex(token_ann)

    # create PosTag annotations
    for token in document["tokens"]:
        pos_ann = cas.createAnnotation(
            posType,
            {
                'begin': token["start_offset"],
                'end': token["end_offset"],
                'PosValue': token["pos_tag"]
            }
        )
        cas.addToIndex(pos_ann)

    # create entity annotations
    entity_mappings = {}
    for entity_id in document["entities"]:
        entity = document["entities"][entity_id]
        tmp = {
            'value': entity["entity_type"],
            'begin': int(entity["start_offset"]),
            'end': int(entity["end_offset"])
        }

        fields = ['norm_scope', 'author_uri', 'work_uri']
        for field in fields:
            if field in entity:
                if entity[field] is not None:
                    tmp[field] = entity[field]
                else:
                    tmp[field] = ""

        entity_ann = cas.createAnnotation(ccType, tmp)
        entity_mappings[int(entity_id)] = entity_ann
        cas.addToIndex(entity_ann)

    if document["relations"] is not None:

        # create relation annotations
        for relation_id in document["relations"]:
            relation = document["relations"][relation_id]
            arg1 = entity_mappings[relation[0]]
            arg2 = entity_mappings[relation[1]]

            relation_ann = cas.createAnnotation(
                reType,
                {
                    'value': 'scope',
                    'begin': arg2.begin,
                    'end': arg2.end,
                    'Governor': [arg1],
                    'Dependent': [arg2],
                }
            )
            cas.addToIndex(relation_ann)

    writer = XmiWriter()
    outfile_path = os.path.join(
        output_dir,
        '{}.xmi'.format(document['doc_name'])
    )
    writer.write(cas, outfile_path)


def xmi2iob(document, input_dir, output_dir):
    """Serialize the output of `read_cas()` as an IOB file."""
    iob_data = []
    start_pos = 0

    # read the document sentence by sentence (using sentence offsets)
    for lb, next_pos in document["line_breaks"]:

        sentence_data = []

        # retain only the tokens belonging to the current sentence
        tokens = [
            token
            for token in document["tokens"]
            if token['start_offset'] >= lb and
            token['end_offset'] <= next_pos
        ]

        for token in tokens:
            start = token['start_offset']
            end = token['end_offset']
            nes = [
                e
                for e in document["entities"].values()
                if start >= e['start_offset'] and end <= e['end_offset']
            ]
            if len(nes) > 0:
                e = nes[0]
                prefix = "I" if start > e['start_offset'] else "B"
                ne_tag = "{}-{}".format(prefix, e["entity_type"])
            else:
                ne_tag = 'O'
            sentence_data.append(
                (token["surface"], token["pos_tag"], ne_tag)
            )

        # append the sentece to the output
        iob_data.append(sentence_data)
        start_pos = next_pos
    iob_as_string = "\n\n".join([
        "\n".join([
            "\t".join(token)
            for token in sent
        ])
        for sent in iob_data
    ])

    iob_file_name = f"{document['doc_name']}.iob"
    iob_file_path = os.path.join(output_dir, iob_file_name)

    with open(iob_file_path, 'w') as outfile:
        outfile.write(iob_as_string)

    return iob_data


# TODO: a better name would be read_xmi
def read_cas(xmi_file, xml_file):
    """Read CAS document."""

    ccType = "webanno.custom.CitationComponents"
    reType = "webanno.custom.Re"
    neType = "de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity"
    posType = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'
    sentType = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'

    entities, relations, annotations = {}, {}, {}
    line_breaks = []
    tokens = []

    with open(xml_file, "rb") as f:
        typesystem = load_typesystem(f)

    with open(xmi_file, "rb") as f:
        cas = load_cas_from_xmi(f, typesystem=typesystem)

    # derive line breaks from sentence boundaries
    for sentence in cas.select(sentType):
        line_breaks.append((sentence.begin, sentence.end))

    # read in POS tags
    for token in cas.select(posType):
        tokens.append({
            "surface": token.get_covered_text(),
            "pos_tag": token.PosValue,
            "end_offset": token.end,
            "start_offset": token.begin
        })

    # read in the entities (CitationComponents)
    for ann in cas.select(ccType):

        entity = {
            "id": ann.xmiID,
            "ann_layer": ann.type,
            "entity_type": ann.value,
            "start_offset": ann.begin,
            "end_offset": ann.end,
            "surface": ann.get_covered_text()
        }

        try:
            entity['author_uri'] = ann.author_uri
        except AttributeError:
            pass

        try:
            entity['work_uri'] = ann.work_uri
        except AttributeError:
            pass

        try:
            entity['norm_scope'] = ann.norm_scope
        except AttributeError:
            pass

        entities[ann.xmiID] = entity

    # read in the relations between citation components
    for rel in cas.select(reType):
        rel_id = "R{}".format(rel.xmiID)
        relation = {
            "id": rel_id,
            "relation_type": rel.value,
            "arguments": (rel.Governor.xmiID, rel.Dependent.xmiID)
        }
        relations[rel_id] = relation

    filename = os.path.basename(xmi_file)

    return {
        "doc_id": filename,
        "doc_name": filename.split(".")[0],
        "text": cas.sofa_string,
        "entities": entities,
        "relations": relations,
        "tokens": tokens,
        "linebreaks": line_breaks
    }


def update_cas(xmi_path, json_path, typesystem_path, output_path):
    """Transfer relations and entity disambiguations from JSON to XMI file."""

    ccType = "webanno.custom.CitationComponents"
    reType = "webanno.custom.Re"
    neType = "de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity"
    posType = 'de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS'
    sentType = 'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'

    caf = CasFactory()
    xmi_doc = caf.buildCAS(xmi_path, typesystem_path)

    with open(json_path, 'r') as jsonfile:
        json_doc = json.load(jsonfile)

    entity_mappings = {ann.FSid: ann for ann in xmi_doc.getAnnotation(ccType)}

    for relation_id in json_doc['relations']:
        arg1_id, arg2_id = json_doc['relations'][relation_id]
        arg1 = entity_mappings[arg1_id]
        arg2 = entity_mappings[arg2_id]
        arg1_json = json_doc['entities'][str(arg1_id)]
        arg2_json = json_doc['entities'][str(arg2_id)]

        if 'work_uri' in arg1_json:
            arg1.work_uri = arg1_json['work_uri']

        if 'norm_scope' in arg2_json:
            arg2.norm_scope = arg2_json['norm_scope']

        relation_ann = xmi_doc.createAnnotation(
            reType,
            {
                'value': 'scope',
                'begin': arg2.begin,
                'end': arg2.end,
                'Governor': [arg1],
                'Dependent': [arg2],
            }
        )
        xmi_doc.addToIndex(relation_ann)

    writer = XmiWriter()
    writer.write(xmi_doc, output_path)
    return xmi_doc


def find_sentence(xmi_document, annotation):
    """Returns the sentence containing the annotation.

    NB: in some cases it can be a partial containment (e.g. when
        the annotation spans two different sentences/lines.
    """

    previous_sentence = None
    for sentence in xmi_document.getAnnotation(sentType):
        if sentence.begin:
            if sentence.end >= annotation.end:
                return previous_sentence, sentence
        previous_sentence = sentence
    return None


def load_data(knowledge_base: KnowledgeBase, **kwargs) -> pd.DataFrame:
    """
    TODO:
    - use kwargs for parameters
    - if `input_dir` is given: process all its XMI files
    - if `input_file` is given: process only that files
    """

    if "input_dir" in kwargs:
        # find all xmi files in the directory
        # for each xmi file call `load_data(input_file)`
        # concatenate all dataframes together
        input_dir = kwargs['input_dir']
        input_files = [
            os.path.join(input_dir, file)
            for file in os.listdir(input_dir)
            if ".xmi" in file
        ]

        # load each chapter's XMI file into a DataFrame
        dfs = [
            load_data(knowledge_base, input_file=file)
            for file in input_files
        ]

        # then stich all dataframes together
        df = pd.concat(dfs, ignore_index=True)  # don't forget to reset the idx!
        return df
    elif "input_file" in kwargs:
        # determine path to typesystem file (assume same containing dir)
        # load the XMI file
        # DF columns: doc_id / surface / urn / sentence /

        # 1. iterate through relations
        # 2. iterate through entities if work_uri != ""
        input_file = kwargs['input_file']
        docid = os.path.basename(input_file)
        dirname = os.path.dirname(input_file)
        typesystem_path = os.path.join(dirname, "TypeSystem.xml")

        print(input_file)
        caf = CasFactory()
        cas = caf.buildCAS(input_file, typesystem_path)
        records = []

        # first we process scope relations that express citations
        for rel in tqdm(cas.getAnnotation(reType)):
            arg1 = rel.Governor[0]
            arg2 = rel.Dependent[0]
            surface = f'{arg1.getCoveredText()} {arg2.getCoveredText()}'

            arg1_features = [
                feature_name
                for feature in arg1.getFeatureValsAsDictList()
                for feature_name in feature.keys()
            ]
            arg2_features = [
                feature_name
                for feature in arg2.getFeatureValsAsDictList()
                for feature_name in feature.keys()
            ]

            if 'work_uri' in arg1_features:
                work_uri = arg1.work_uri
            elif 'work_uri' in arg2_features:
                work_uri = arg2.work_uri
            else:
                work_uri = None

            # TODO: replace em dash instead of hyphen '–'/'-' if present
            if 'norm_scope' in arg2_features:
                scope = arg2.norm_scope
            else:
                scope = None

            if scope is None or work_uri is None:
                continue

            # find sentence containing arg2 (our reference anchor)
            previous_sentence, sentence = find_sentence(cas, arg2)
            if len(sentence.getCoveredText().split()) < 3:
                context = previous_sentence.getCoveredText() + sentence.getCoveredText()
            else:
                context = sentence.getCoveredText()

            try:
                assert sentence is not None
            except AssertionError:
                raise

            # convert URI to URN
            Work = knowledge_base._session.get_class(
                surf.ns.EFRBROO['F1_Work']
            )
            work = knowledge_base._session.get_resource(work_uri, Work)
            work_urn = str(work.get_urn())
            try:
                scope = scope.replace(
                    "–", '-'
                ) if "–" in scope else scope
                passage_urn = CTS_URN(f'{work_urn}:{scope}')
            except pyCTS.BadCtsUrnSyntax:
                print(
                    f"Scope :{scope}, work_uri: {work_uri}",
                    f"Sentence: {sentence.getCoveredText()}"
                    f"You may want to check it"
                )
                continue

            # if the passage is a range, we need to pick the starting
            # URN for indexing purposes
            if passage_urn.is_range():
                base_urn = passage_urn.get_urn_without_passage()
                range_begin = clean_scope(passage_urn._range_begin)
                indexable_urn = f'{base_urn}:{range_begin}'
            else:
                base_urn = passage_urn.get_urn_without_passage()
                cleaned_scope = clean_scope(scope)
                indexable_urn = f'{base_urn}:{cleaned_scope}'

            try:
                author_urn = str(work.author.get_urn())
            except Exception:
                print(
                    f"Scope :{scope}, work_uri: {work_uri}",
                    f"Sentence: {sentence.getCoveredText()}"
                    f"You may want to check it"
                )
                continue

            records.append({
                'surface': surface,
                'docid': docid,
                'path': input_file,
                'scope': scope,
                'work_uri': work_uri,
                'urn': str(passage_urn),
                'indexable_urn': indexable_urn,
                'work_urn': work_urn,
                'author_urn': author_urn,
                'sentence': context,
                'ann_type': ''
            })


        for entity in cas.getAnnotation(ccType):

            try:
                # sometimes it happens that the type if not set
                entity_type = entity.value
            except Exception:
                pass

            if entity_type != "FRAGREF":
                continue

            surface = entity.getCoveredText()
            prev_sentence, sentence = find_sentence(cas, entity)

            records.append({
                'surface': surface,
                'docid': docid,
                'path': input_file,
                'scope': None,
                'work_uri': None,
                'urn': None,
                'indexable_urn': None,
                'work_urn': None,
                'author_urn': None,
                'sentence': sentence.getCoveredText(),
                'ann_type': entity_type
            })

        df = pd.DataFrame(records)
        return df
