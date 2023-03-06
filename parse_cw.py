#!/usr/bin/python3
# -*- coding: utf-8 -*-
import nltk
from lxml import etree
from xml.etree import ElementTree as ET
import re
import argparse

#CFG規則の読み込み
grammar1 = nltk.CFG.fromstring("""
  CW -> EN | T_EN | Q_EN | E_EN | EV | EV_2 | S_EV
  NEG1 -> "NEG"
  NEG2 -> "NEG"
  NEG3 -> "NEG"
  M_EN -> "M_EN" | M_EN2 M_EN | PA2 M_EN | NEG1 M_EN
  M_EN2 -> "M_EN" | PA2 M_EN2 | NEG1 M_EN2
  PA -> "PA" | PA2 PA2 | M_EN PA
  PA2 -> "PA"
  WO -> "WO" | M_EN WO_2 | PA WO_2 | EV_wo WO_2
  WO_2 -> "WO" | M_EN WO_2 | PA WO_2
  NI -> "NI" | M_EN NI | PA NI
  GA -> "GA" | M_EN GA | PA GA
  EV -> "EV" | GA EV | WO EV | NI EV | EV_2 EV_2 | NEG2 EV
  EV_2 -> "EV"
  EV_wo -> WO_2 EV_2 | NI EV_2 | GA EV_2
  S_EV -> "S_EV" | EV S_EV | NEG2 S_EV
  EN -> "EN" | S_EV EN | EV EN | M_EN EN | PA EN | GA EN | NEG3 EN
  Q_EN -> "Q_EN" | EV Q_EN
  T_EN -> "T_EN" | EV T_EN
  E_EN -> "E_EN" | S_EV E_EN | EV E_EN
  """)

#CFG規則適用前にPPタグを先に結合
def merge_pp(pre_surf, pre_tag):
    new_cw, new_surf = [], []
    surf_pp = ""
    pp = 0
    for surf, tags in zip(pre_surf, pre_tag):
        if tags == "PP":
            pp = 1
            surf_pp = surf_pp + surf
        elif pp == 1:
            surf_pp = surf_pp + surf
            new_surf.append(surf_pp)
            new_cw.append(tags)
            pp = 0
            surf_pp = ""
        else:
            new_surf.append(surf)
            new_cw.append(tags)
    return new_surf, new_cw


#読み込んだCFG規則に基づいて予測した複合語タグをパーズする
finidx = 0
def translate(tree, tags, surf):
    global finidx
    for index, subtree in enumerate(tree):
        idx = []
        if type(subtree) == nltk.tree.Tree:
            translate(subtree, tags, surf)
        elif type(subtree) == str:
            idx = [i for i, x in enumerate(tags) if x == subtree and i >= finidx]
            subtree = surf[idx[0]]
            finidx += 1
            tree[index] = subtree

flag = 0
def to_en(tree):
    global finidx, flag
    for index, subtree in enumerate(tree):
        tree_label = tree.label()
        if "_1" in tree_label or "_2" in tree_label or "_3" in tree_label:
            tag = tree_label[0:-2]
        else:
            tag = tree_label
        idx = []
        if type(subtree) == nltk.tree.Tree:
            if index == 1 and subtree.label() == "EV_2": #等位接続に関するルール
                subtree.set_label("EV")
                to_en(subtree)
            elif tag == "S_EV" and subtree.label() == "EV":
                finidx += 1
                new_subtree = subtree.copy()
                new_tree = nltk.tree.Tree("WO", [new_subtree])
                tree[0] = new_tree
            elif ((tag == "NI" or tag == "GA" or tag == "WO") and ("M_EN" in subtree.label() or "PA" in subtree.label())) or ("M_EN2" in subtree.label()) or (tag == "M_EN" and "M_EN" in subtree.label() and "NEG" not in tree[0].label()) or (tag == "WO" and ("EV_wo" in subtree.label())):
                finidx += 1
                new_tree = tree.copy()
                if len(new_tree[1]) == 2:
                    flag = 1
                new_tree.set_label("EN")
                if "EV_wo" in subtree.label():
                    to_en(new_tree[0])
                else:
                    to_en(new_tree[1])
                new_tree[1].set_label("EN")
                if flag == 1 and len(new_tree[1]) != 2:
                    tree = new_tree
                    flag = 0
                else:
                    tree[0] = new_tree
                    tree = nltk.tree.Tree.remove(tree,tree[1])
            else:
                to_en(subtree)
        elif type(subtree) == str:
            finidx += 1
            tree[index] = subtree

def ev_to_men(tree):
    global finidx
    for index, subtree in enumerate(tree):
        tree_label = tree.label()
        if "_1" in tree_label or "_2" in tree_label or "_3" in tree_label:
            tag = tree_label[0:-2]
        else:
            tag = tree_label
        idx = []
        if type(subtree) == nltk.tree.Tree:
            if "EN" in tag and "EV" in subtree.label() and len(tree) == 2:
                finidx += 1
                new_tree = subtree.copy()
                new_tree2 = subtree.copy()
                if tag == "EN":
                    new_tree2.set_label("M_EN")
                elif tag == "T_EN":
                    new_tree2.set_label("M_TEN")
                elif tag == "Q_EN":
                    new_tree2.set_label("M_QEN")
                elif tag == "E_EN":
                    new_tree2.set_label("M_EEN")
                new_tree2[0] = new_tree
                if len(new_tree2) != 1:
                    nltk.tree.Tree.remove(new_tree2,new_tree2[1])
                tree[0] = new_tree2
                tree.set_label("EN")
            else:
                ev_to_men(subtree)
        elif type(subtree) == str:
            finidx += 1
            tree[index] = subtree

def main():
    global finidx
    parser = argparse.ArgumentParser('')
    parser.add_argument("--surf", nargs='?', type=str, help="cw surface")
    parser.add_argument("--tags", nargs='?', type=str, help="cw tags")
    args = parser.parse_args()

    pre_surf1 = args.surf
    pre_tags1 = args.tags
    pre_surf = pre_surf1.split()
    pre_tag = pre_tags1.split()

    print(pre_surf, pre_tag)

    surf, tags = merge_pp(pre_surf, pre_tag)

    print(surf)
    print(tags)

    #木の結合順が理想とするものではない場合、何番目の木を採用するか自分で指定する必要がある
    lst_finidx0 = [['リドカイン', '血中', '濃度'],['C型', '慢性', '肝炎'],['C型', '非', '代償性', '肝硬変'],['シャント型', '肝性', '脳症'],['原発性', '胆汁性', '胆管炎'],['症候性', '原発性', '胆汁性', '胆管炎'],['難治性', '肝性', '腹水'],['急性', 'アルコール性', '肝炎'],['糖尿病性', '壊死性', '筋膜炎'],['末梢性', '神経障害性', '疼痛'],['蜂窩織炎性', '急性', '虫垂炎']]
    lst_finidx1 = [['脳性', '麻痺', '患者'],['C型', '肝硬変', '患者'],['非', '昏睡型', '急性', '肺不全'],['2型', '糖尿病', '患者'],['慢性', '非', '化膿性', '破壊性', '胆管炎'],['長与', '甲型', '肝硬変'],['慢性期', '皮膚筋炎', '患者'],['非', '上皮性', '悪性', '腫瘍']]#別の結合を採用したい複合語はここに追加
    lst_finidx2 = [['痙性', '四肢', '麻痺', '患者']]
    lst_finidx5 = [['C型', '非', '代償性', '肝硬変', '患者']]
    #lst_finidx0 = [['急性', '出血性', '壊疽性', '胆嚢炎'],['C型', '慢性', '肝炎'],['糖尿病性', '壊死性', '筋膜炎'],['急性', 'アルコール性', '肝炎'],['難治性', '肝性', '腹水'],['C型', '非', '代償性', '肝硬変', '患者'],['原発性', '胆汁性', '胆管炎'],['症候性', '原発性', '胆汁性', '胆管炎'],['シャント型', '肝性', '脳症'],['非', '代償性', '肝硬変', '患者'],['C型', '非', '代償性', '肝硬変'],['左', '房内', '血栓']] #1つ目の結合を採用したい複合語はここに追加する

    rd_parser = nltk.RecursiveDescentParser(grammar1)
    for i, tree in enumerate(rd_parser.parse(tags)):
        print(i, tree)
        if (tags.count('M_EN')>1 or tags.count('PA')>1):
            if ((surf in lst_finidx1) and i==1) or ((surf in lst_finidx2) and i==2) or ((surf in lst_finidx5) and i==5):
                finidx = 0
            elif surf in lst_finidx1+lst_finidx2+lst_finidx5:
                continue
        translate(tree, tags, surf)
        finidx = 0
        to_en(tree)
        if "EV" in tags :
            finidx = 0
            ev_to_men(tree)
        print(tree)

        with open("cw_new.ptb", "w") as f:
            f.write(str(tree)) #PTBファイルに出力

if __name__ == '__main__':
    main()
