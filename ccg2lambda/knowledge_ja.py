# -*- coding: utf-8 -*-
#
#  Copyright 2015 Pascual Martinez-Gomez
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

from collections import defaultdict
import itertools
from normalization import denormalize_token, normalize_token
import numpy as np
from numpy import dot
from numpy.linalg import norm
import os
#from ModelKB import Model
#from pyknp import KNP
import sys
import re
import subprocess
import spacy
#import gensim

path = os.getcwd()
#w2v_model = gensim.models.KeyedVectors.load_word2vec_format(path+"/w2v_model/w2v.repname.256.100K.blog_4M.bin", binary=True, encoding='utf8', unicode_errors='ignore')
#dcs_model = Model(path+"/dcs_model/entity.vocab", path+"/dcs_model/relation.vocab", path+"/dcs_model/")
#knp = KNP(jumanpp=True)

# get the head word from a given bnst (general method)
def get_head_word_from_bnst(bnst):
    m = re.search("<主辞’代表表記:([^>]+)", bnst.fstring)
    if m:
        return m.group(1);
    else:
        m = re.search("<主辞代表表記:([^>]+)", bnst.fstring)
        if m:
            return m.group(1);
        else:
            return None

# get the head word from a given governor
def get_head_word_from_governor(bnst):
    # get the last tag from bnst to extract (標準)用言代表表記
    tag = bnst.tag_list()[-1]
    if "<用言:" in tag.fstring:
        m = re.search("<標準用言代表表記:([^>]+)", tag.fstring)
        if m:
            return m.group(1);
        else:
            m = re.search("<用言代表表記:([^>]+)", tag.fstring)
            if m:
                return m.group(1);
    return get_head_word_from_bnst(bnst)

# get the dependency type from a given bnst
def get_dpnd_type(bnst):
    m = re.search("<係:([^>]+)", bnst.fstring)
    if m:
        return m.group(1)
    else:
        return None

# get the dependency type for 複合辞
def get_dpnd_type_for_compound_case(bnst):
    # get the last tag from bnst to extract 解析格
    tag = bnst.tag_list()[-1]
    # a normalized form of 複合辞 is stored in 解析格 (needs case analysis)
    m = re.search("<解析格:([^>]+)", tag.fstring)
    if m:
        return m.group(1)
    else:
        return "複合辞連用"

def extract_triple(word):
    modifier_str, dpnd_type, governor_str = "","",""
    result = knp.parse(word)
    for bnst in result.bnst_list():
        # skip 複合辞 as a modifier
        if "複合辞" in bnst.fstring:
            continue
        modifier_str = get_head_word_from_bnst(bnst)
        if not modifier_str:
            continue
        parent = bnst.parent
        if parent:
            if "複合辞" in parent.fstring:
                dpnd_type = get_dpnd_type_for_compound_case(bnst)
                # grandparent is the predicate for 複合辞
                parent = parent.parent
                if not parent:
                    return modifier_str, dpnd_type, governor_str
                    continue
            else:
                dpnd_type = get_dpnd_type(bnst)
                # NONE is exceptional
                if dpnd_type == "NONE":
                    return modifier_str, dpnd_type, governor_str
                    continue
            governor_str = get_head_word_from_governor(parent)
            if not governor_str:
                return modifier_str, dpnd_type, governor_str
                continue
        return modifier_str, dpnd_type, governor_str
    return triples


def knp_phrase_expr_to_vec(expr):
    # split "味/あじ?味/み" into ["味/あじ", "味/み"] then average each word vector
    return dcs_model.get_average_word_vector(expr.split("?"))


def get_tokens_from_xml_node(node):
    tokens = node.xpath(
        ".//token[not(@base='*')]/@base | //token[@base='*']/@surf")
    return tokens


def calc_dcsvec(w1, w2):
    head1, rel1, tail1 = extract_triple(w1)
    phrase1_head = (
        knp_phrase_expr_to_vec(head1)
    )
    # phrase1_tail = (
    #     knp_phrase_expr_to_vec(word1)
    # )
    # path1 = [
    #     phrase1_head,
    #     phrase1_rel + ">",
    #     phrase1_tail,
    # ]
    head2, rel2, tail2 = extract_triple(w2)
    phrase2_head = (
        knp_phrase_expr_to_vec(head2)
    )
    # phrase2_tail = (
    #     knp_phrase_expr_to_vec(word2)
    # )
    # path2 = [
    #     phrase2_head,
    #     phrase2_rel + ">",
    #     phrase2_tail,
    # ]
    vec1 = phrase1_head
    vec2 = phrase2_head
    cos_sim = dot(vec1, vec2) / (norm(vec1) * norm(vec2))
    print(w1, w2, cos_sim)
    if cos_sim > 0.5:
        return 'dcsvec'
    else:
        return

def check_vec(words):
    newwords = []
    for word in words:
        if word in w2v_model.wv:
            newwords.append(word)
        else:
            continue
    return newwords

def calc_cos_w2v(w1, w2):
    head1, rel1, tail1 = extract_triple(w1)
    head2, rel2, tail2 = extract_triple(w2)
    p1, p2 = [], []
    tmp = re.split('[\+\?]', head1)
    p1.extend(tmp)
    tmp = re.split('[\+\?]', tail1)
    p1.extend(tmp)
    tmp = re.split('[\+\?]', head2)
    p2.extend(tmp)
    tmp = re.split('[\+\?]', tail2)
    p2.extend(tmp)
    np1 = check_vec(p1)
    np2 = check_vec(p2)
    if len(np1) > 0 and len(np2) > 0:
        sim = w2v_model.n_similarity(np1, np2)
        return sim
    else:
        return 0

def calc_w2v(w1, w2):
    cos_sim = calc_cos_w2v(w1, w2)
    if cos_sim > 0.5:
        return 'word2vec'
    else:
        return

def calc_ginza(w1, w2):
    nlp = spacy.load('ja_ginza')
    doc1 = nlp(w1)
    doc2 = nlp(w2)
    cos_sim = doc1.similarity(doc2)
    if cos_sim > 0.5:
        return 'ginza'
    else:
        return

def create_entail_axioms(relations_to_pairs, relation='dcsvec'):
    """
    For every linguistic relationship, check if 'relation' is present.
    If it is present, then create an entry named:
    Axiom ax_relation_token1_token2 : forall x, _token1 x -> _token2 x.
    """
    rel_pairs = relations_to_pairs[relation]
    axioms = []
    if not rel_pairs:
        return axioms
    for t1, t2 in rel_pairs:
        axiom = 'Axiom ax_{0}_{1}_{2} : forall x, _{1} x -> _{2} x.'\
                .format(relation, t1, t2)
        axioms.append(axiom)
    return axioms

def get_lexical_relations_from_preds(premise_preds, conclusion_pred, pred_args=None, model='dcs'):
    src_preds = [denormalize_token(p) for p in premise_preds]
    trg_pred = denormalize_token(conclusion_pred)
    relations_to_pairs = defaultdict(list)
    relations = []
    relation = ''
    for src_pred in src_preds:
        if src_pred == trg_pred or \
           src_pred in '_False' or \
           src_pred in '_True' or \
           trg_pred == 'True' or \
           trg_pred == 'False':
            continue
        print(src_pred, trg_pred)
        if model == 'dcs':
            relation = calc_dcsvec(src_pred, trg_pred)
        elif model == 'w2v':
            relation = calc_w2v(src_pred, trg_pred)
        elif model == 'ginza':
            relation = calc_ginza(src_pred, trg_pred)
        if relation:
            relations_to_pairs[relation].append((src_pred, trg_pred))
    dcsvec_axioms = create_entail_axioms(relations_to_pairs, 'dcsvec')
    word2vec_axioms = create_entail_axioms(relations_to_pairs, 'word2vec')
    ginza_axioms = create_entail_axioms(relations_to_pairs, 'ginza')
    axioms = dcsvec_axioms + word2vec_axioms + ginza_axioms
    print(axioms)
    return list(set(axioms))
