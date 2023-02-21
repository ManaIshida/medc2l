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

#読み込んだCFG規則に基づいて予測した複合語タグをパーズする
def merge_pp(pre_surf, pre_tag): #PPタグを先に結合
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
            if index == 1 and subtree.label() == "EV_2": #等位接続のタグをいい感じにする！EV EV の複合語
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
            #if "EN" in tag and (subtree.label() == "EV" or subtree.label() == "S_EV")and len(tree) == 2:
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

    ev_en = [['追加', '薬剤'],['作用', '時期']]
    men_en = [['MRI', '検査'],['下肢', '装具'],['一般', '病棟'],['早期', '胃癌']]
    pa_en = [['咽頭', '癌'],['腎', '不全'],['脊髄', '腫瘍'],['鼠径', 'ヘルニア']]
    pp_en = [['整形', '外科'],['尿', '中'],['尿', '量'],['尿道', 'カテーテル']]
    wo_ev = [['PSL', '漸増'],['薬剤', '服用'],['動作', '改善']]
    men_wo_ev = [['基本', '動作', '改善'],['基本', '動作', '練習'],['入院', 'リハビリ', '開始']]
    pp_men_en = [['関節', 'リウマチ', '患者'],['足', '底', '装具']]
    pp_pp_pp_en = [['抗', 'PD', '1', '抗体'],['第', '一', '選択', '薬']]
    pp_men_pp_en = [['真', '菌', '感染', '症']]
    pp_pp_men_en = [['肝', '細胞', '性', '黄疸'],['肝', '胆道', '系', '酵素']]
    men_pp_men_en = [['三宅', '甲', '型', '肝硬変']]
    men_pa_pp_pp_en = [['右', '膝', '屈曲', '拘', '縮'],['左', '膝', '屈曲', '拘', '縮']]
    men_pp_ni_wo_ev = [['右', '尿', '管', 'ステント', '挿入'],['左', '尿', '管', 'ステント', '挿入']]
    men_pp_pa_pp_en = [['カンジダ', '尿', '路', '感染', '症'],['クラミジア', '尿', '路', '感染', '症']]
    men_pp_pp_pa_en = [['右', '腸', '腰', '筋', '膿瘍'],['左', '腸', '腰', '筋', '膿瘍']]

    if pre_surf in ev_en:
        pre_tag = ['EV', 'EN']
    elif pre_surf in men_en:
        pre_tag = ['M_EN', 'EN']
    elif pre_surf in pa_en:
        pre_tag = ['PA', 'EN']
    elif pre_surf in pp_en:
        pre_tag = ['PP', 'EN']
    elif pre_surf in wo_ev:
        pre_tag = ['WO', 'EV']
    elif pre_surf in men_wo_ev:
        pre_tag = ['M_EN', 'WO', 'EV']
    elif pre_surf in pp_men_en:
        pre_tag = ['PP', 'M_EN', 'EN']
    elif pre_surf in pp_pp_pp_en:
        pre_tag = ['PP', 'PP', 'PP', 'EN']
    elif pre_surf in pp_men_pp_en:
        pre_tag = ['PP', 'M_EN', 'PP', 'EN']
    elif pre_surf in pp_pp_men_en:
        pre_tag = ['PP', 'PP', 'M_EN', 'EN']
    elif pre_surf in men_pp_men_en:
        pre_tag = ['M_EN', 'PP', 'M_EN', 'EN']
    elif pre_surf in men_pa_pp_pp_en:
        pre_tag = ['M_EN', 'PA', 'PP', 'PP', 'EN']
    elif pre_surf in men_pp_pa_pp_en:
        pre_tag = ['M_EN', 'PP', 'PA', 'PP', 'EN']
    elif pre_surf in men_pp_pp_pa_en:
        pre_tag = ['M_EN', 'PP', 'PP', 'PA', 'EN']
    elif pre_surf in men_pp_ni_wo_ev:
        pre_tag = ['M_EN', 'PP', 'NI', 'WO', 'EV']
    elif pre_surf == ['歩行', '未', '獲得']:
        pre_tag = ['EV', 'NEG', 'S_EV']
    elif pre_surf == ['左側', '股関節', '伸展']:
        pre_tag = ['M_EN', 'GA', 'EV']
    elif pre_surf == ['精査', '加療']:
        pre_tag = ['EV', 'EV']
    elif pre_surf == ['右', '腎', '膿瘍']:
        pre_tag = ['M_EN', 'PA', 'EN']
    elif pre_surf == ['左', '膝', '屈曲', '拘', '縮', '除去', '術']:
        pre_tag = ['M_EN', 'PA', 'PP', 'PP', 'WO', 'EV', 'EN']
    elif pre_surf == ['真性', '動脈', '瘤']:
        pre_tag = ['M_EN', 'PP', 'EN']
    elif pre_surf == ['粘膜', '類', '天', '疱瘡']:
        pre_tag = ['M_EN', 'PP', 'PP', 'EN']
    elif pre_surf == ['定型', '抗', '酸', '菌', '症']:
        pre_tag = ['M_EN', 'PP', 'PP', 'PP', 'EN']
    elif pre_surf == ['非', '定型', '抗', '酸', '菌', '症']:
        pre_tag = ['NEG', 'M_EN', 'PP', 'PP', 'PP', 'EN']
    elif pre_surf == ['非', '持続', '性', '心室', '頻', '拍']:
        pre_tag = ['NEG', 'PP', 'M_EN', 'PP', 'PP', 'EN']
    elif pre_surf == ['肝', '機能', '改善', '効果']: #前後の文によって変わるので，一概にこれがいいとは限らない
        pre_tag = ['PA', 'GA', 'EV', 'E_EN']
    elif pre_surf == ['肝', '機能', '改善', '傾向']:
        pre_tag = ['PA', 'GA', 'EV', 'T_EN']
    elif pre_surf == ['直腸', '癌', '左', '副腎', '転移']:
        pre_tag = ['PA', 'GA', 'M_EN', 'NI', 'EV']
    elif pre_surf == ['腎', '細胞', '癌']:
        pre_tag = ['PA', 'M_EN', 'EN']
    elif pre_surf == ['炎症', '反応', '改善', '傾向']:
        pre_tag = ['PP', 'GA', 'EV', 'T_EN']
    elif pre_surf == ['当', '院', '搬送']:
        pre_tag = ['PP', 'NI', 'EV']
    elif pre_surf == ['腸', '骨', '筋', '弛緩']:
        pre_tag = ['PP', 'PP', 'GA', 'EV']
    elif pre_surf == ['自己', '免疫', '性', '肝炎', '類似', '像']:
        pre_tag = ['PP', 'PP', 'M_EN', 'NI', 'EV', 'EN']
    elif pre_surf == ['腸', '腰', '筋', '膿瘍']:
        pre_tag = ['PP', 'PP', 'PA', 'EN']
    elif pre_surf == ['短', '母', '指', '外', '転', '筋']:
        pre_tag = ['PP', 'PP', 'PA', 'PP', 'PP', 'EN']
    elif pre_surf == ['S', '-', '1', '+', 'CDDP', '療法']:
        pre_tag = ['PP', 'PP', 'PP', 'PP', 'PP', 'EN']
    elif pre_surf == ['S', '-', '1', '休', '薬', '期間']:
        pre_tag = ['PP', 'PP', 'WO', 'PP', 'EV', 'Q_EN']
    elif pre_surf == ['当', '科', '退院']:
        pre_tag = ['PP', 'WO', 'EV']
    elif pre_surf == ['免疫', '調整', '薬']: #PA PP EV
        pre_tag = ['WO', 'EV', 'EN']
    elif pre_surf == ['Nivolumab', '休', '薬']: #PA PP EV
        pre_tag = ['WO', 'PP', 'EV']
    elif pre_surf == ['慢性', '期', '皮膚', '筋炎', '患者']:
        pre_tag = ['PP', 'M_EN', 'PA', 'M_EN', 'EN']

    print(pre_surf, pre_tag)

    surf, tags = merge_pp(pre_surf, pre_tag)

    print(surf)
    print(tags)

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
        #PTBファイルに出力
        with open("cw_new.ptb", "w") as f:
            f.write(str(tree))

if __name__ == '__main__':
    main()
