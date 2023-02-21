#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  Copyright 2020 Hitomi Yanaka
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os, os.path, sys
import glob
from xml.etree import ElementTree
from depccg.parser import JapaneseCCGParser
from depccg.tokens import Token, japanese_annotator, annotate_XX
from depccg.download import load_model_directory, SEMANTIC_TEMPLATES
from depccg.printer import print_
from depccg.semantics.ccg2lambda import parse as ccg2lambda
from depccg.tree import Tree
from lxml import etree
from prove import *
from semantic_tools import prove_doc
from visualization_tools import convert_root_to_mathml

class ConvertToJiggXML(object):
    def __init__(self, sid: int, use_symbol: bool):
        self.sid = sid
        self._spid = -1
        self.processed = 0
        self.use_symbol = use_symbol

    @property
    def spid(self) -> int:
        self._spid += 1
        return self._spid

    def process(self, tree: Tree, score: float = None):
        counter = 0
        def traverse(node: Tree):
            nonlocal counter
            id = f's{self.sid}_sp{self.spid}'
            xml_node = etree.SubElement(res, 'span')
            xml_node.set('category', str(node.cat.multi_valued))
            xml_node.set('id', id)
            if node.is_leaf:
                start_of_span = counter
                counter += 1
                xml_node.set('terminal', f's{self.sid}_{start_of_span}')
            else:
                childid, start_of_span = traverse(node.left_child)
                if not node.is_unary:
                    tmp, _ = traverse(node.right_child)
                    childid += ' ' + tmp
                xml_node.set('child', childid)
                xml_node.set('rule', node.op_symbol if self.use_symbol else node.op_string)
            xml_node.set('begin', str(start_of_span))
            xml_node.set('end', str(start_of_span+len(node)))
            return id, start_of_span

        res = etree.Element('ccg')
        res.set('id', f's{self.sid}_ccg{self.processed}')
        id, _ = traverse(tree)
        res.set('root', str(id))
        res[0].set('root', 'true')
        if score is not None:
            res.set('score', str(score))
        self.processed += 1
        return res

def to_jigg_xml(trees, tagged_doc, use_symbol=False):
    root_node = etree.Element('root')
    document_node = etree.SubElement(root_node, 'document')
    sentences_node = etree.SubElement(document_node, 'sentences')
    for i, (parsed, tagged) in enumerate(zip(trees, tagged_doc)):
        sentence_node = etree.SubElement(sentences_node, 'sentence')
        tokens_node = etree.SubElement(sentence_node, 'tokens')
        cats = [leaf.cat for leaf in parsed[0][0].leaves]
        assert len(cats) == len(tagged)
        for j, (token, cat) in enumerate(zip(tagged, cats)):
            token_node = etree.SubElement(tokens_node, 'token')
            token_node.set('start', str(j))
            token_node.set('cat', str(cat))
            token_node.set('id', f's{i}_{j}')
            if 'word' in token:
                token['surf'] = token.pop('word')
            if 'lemma' in token:
                token['base'] = token.pop('lemma')
            for k, v in token.items():
                token_node.set(k, v)
        converter = ConvertToJiggXML(i, use_symbol)
        for tree, score in parsed:
            sentence_node.append(converter.process(tree, score))
    return root_node

def annotate_using_janome(sentences, tokenize=False):
    from janome.tokenizer import Tokenizer
    tokenizer = Tokenizer()
    res = []
    raw_sentences = []
    for sentence in sentences:
        sentence = ''.join(sentence)
        tokenized = tokenizer.tokenize(sentence)
        tokens = []
        for token in tokenized:
            pos, pos1, pos2, pos3 = token.part_of_speech.split(',')
            token = Token(word=token.surface,
                          surf=token.surface,
                          pos=pos,
                          pos1=pos1,
                          pos2=pos2,
                          pos3=pos3,
                          inflectionForm=token.infl_form,
                          inflectionType=token.infl_type,
                          reading=token.reading,
                          base=token.base_form)
            tokens.append(token)
        raw_sentence = [token.surface for token in tokenized]
        res.append(tokens)
        raw_sentences.append(raw_sentence)
    return res, raw_sentences

def get_sem_visualize(sentences, pretokenized=False):
    model, config = load_model_directory('ja')
    parser = JapaneseCCGParser.from_json(config, model)
    doc = [l.strip() for l in sentences]
    doc = [sentence for sentence in doc if len(sentence) > 0]
    if pretokenized is True:
        # tokenize
        annotate_fun = annotate_XX
        tagged_doc = annotate_fun([[word for word in sent.split(' ')] for sent in doc])
        # ccg parse
        res = parser.parse_doc(doc)
        jigg_xml = to_jigg_xml(res, tagged_doc)
        # semantic parse
        templates = SEMANTIC_TEMPLATES.get("ja")
        result_xml_str, _ = ccg2lambda.parse(jigg_xml, str(templates))
        root = etree.fromstring(result_xml_str)
        return convert_root_to_mathml(root)
    else:
        # tokenize
        annotate_fun = japanese_annotator["janome"]
        tagged_doc = annotate_fun([[word for word in sent.split(' ')] for sent in doc], tokenize="janome")
        tagged_doc, doc = tagged_doc
        # ccg parse
        res = parser.parse_doc(doc)
        jigg_xml = to_jigg_xml(res, tagged_doc)
        # semantic parse
        templates = SEMANTIC_TEMPLATES.get("ja")
        result_xml_str, _ = ccg2lambda.parse(jigg_xml, str(templates))
        root = etree.fromstring(result_xml_str)
        return convert_root_to_mathml(root)

def get_sem(sentences, pretokenized=False):
    model, config = load_model_directory('ja')
    parser = JapaneseCCGParser.from_json(config, model)
    doc = [l.strip() for l in sentences]
    doc = [sentence for sentence in doc if len(sentence) > 0]
    if pretokenized is True:
        # tokenize
        annotate_fun = annotate_XX
        tagged_doc = annotate_fun([[word for word in sent.split(' ')] for sent in doc])
        # ccg parse
        res = parser.parse_doc(doc)
        jigg_xml = to_jigg_xml(res, tagged_doc)
        # semantic parse
        templates = SEMANTIC_TEMPLATES.get("ja")
        result_xml_str, _ = ccg2lambda.parse(jigg_xml, str(templates))
        return result_xml_str.decode("utf-8")
    else:
        # tokenize
        annotate_fun = japanese_annotator["janome"]
        tagged_doc = annotate_fun([[word for word in sent.split(' ')] for sent in doc], tokenize="janome")
        tagged_doc, doc = tagged_doc
        # ccg parse
        res = parser.parse_doc(doc)
        jigg_xml = to_jigg_xml(res, tagged_doc)
        # semantic parse
        templates = SEMANTIC_TEMPLATES.get("ja")
        result_xml_str, _ = ccg2lambda.parse(jigg_xml, str(templates))
        return result_xml_str.decode("utf-8")

def get_ccg(sentences):
    model, config = load_model_directory('ja')
    parser = JapaneseCCGParser.from_json(config, model)
    doc = [l.strip() for l in sentences]
    doc = [sentence for sentence in doc if len(sentence) > 0]
    annotate_fun = annotate_XX
    tagged_doc = annotate_fun([[word for word in sent.split(' ')] for sent in doc])  
    # ccg parse
    res = parser.parse_doc(doc)
    print_(res, tagged_doc, format='html', file=sys.stdout)

def check_fact(target, source):
    corr_source = []
    for premise in source:
        pair = [premise, target]
        try:
            sems = get_sem(pair)
            root = etree.fromstring(sems.encode("utf-8"))
            DOCS = root.findall('.//document')
            theorem = prove_doc(DOCS[0], None, None)
            inference_result = theorem.result
        except:
            inference_result = "unknown"
        corr_source.append(inference_result)
        #if inference_result == "yes":
        #    corr_source.append(premise)
    return corr_source

# target = "これは文です。"
# source = ["これはテストの文です。", "これはテストです。", "これは仮のテストです。"]
# ret = check_fact(target, source)
# print(ret)

# 不要な処理
# def merge_xml(xml_files):
#     #xml_files = glob.glob(files +"/*.xml")
#     xml_element_tree = None
#     for xml_file in xml_files:
#         data = ElementTree.parse(xml_file).getroot()
#         # print ElementTree.tostring(data)
#         for result in data.iter('sentences'):
#             print(result)
#             if xml_element_tree is None:
#                 xml_element_tree = data 
#                 insertion_point = xml_element_tree.findall(".//sentences")[0]
#             else:
#                 insertion_point.extend(result) 
#     if xml_element_tree is not None:
#         return ElementTree.tostring(xml_element_tree, encoding="utf-8")
# folder = "xml"
# ret = merge_xml(sems)
# with open("merge.xml", "w") as f:
#     f.write(ret.decode("utf-8")) 

 

