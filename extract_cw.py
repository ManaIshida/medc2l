#!/usr/bin/python3
# -*- coding: utf-8 -*-

import nltk
from lxml import etree
from xml.etree import ElementTree as ET
import re
from depccg.tools.reader import read_trees_guess_extension
from typing import Tuple, List
from collections import defaultdict
from depccg.tree import Tree
from depccg.cat import Category
from depccg.combinator import guess_combinator_by_triplet, UNKNOWN_COMBINATOR
from depccg.lang import BINARY_RULES
from depccg.tokens import Token
import logging
import argparse

#jigg.xmlを読み込みパーズするモジュール
def read_jigg_xml_cw(filename, cw_ids, cw_span, lang='en'):
    #print(cw_ids)
    #print(cw_span)
    binary_rules = BINARY_RULES[lang]
    def try_get_surface(token):
        if 'word' in token:
            return token.word
        elif 'surf' in token:
            return token.surf
        else:
            raise RuntimeError(
                'the attribute for the token\'s surface form is unknown')

    def parse(tree, tokens):
        def rec(node):
            attrib = node.attrib
            if 'terminal' not in attrib:
                cat = Category.parse(attrib['category'])
                children = [rec(spans[child]) for child in attrib['child'].split(' ')]
                if len(children) == 1:
                    return Tree.make_unary(cat, children[0], lang)
                else:
                    assert len(children) == 2
                    left, right = children
                    combinator = guess_combinator_by_triplet(
                                    binary_rules, cat, left.cat, right.cat)
                    combinator = combinator or UNKNOWN_COMBINATOR
                    return Tree.make_binary(cat, left, right, combinator, lang)
            else:
                cat = Category.parse(attrib['category'])
                word = try_get_surface(tokens[attrib['terminal']])
                return Tree.make_terminal(word, cat, lang)

        spans = {span.attrib['id']: span for span in tree.xpath('./span')}
        return rec(spans[tree.attrib['root']])

    trees = etree.parse(filename).getroot()
    sentences = trees[0][0].xpath('sentence')
    if re.search("s0", cw_ids[0]):
        sentences = [sentences[0]]
    elif re.search("s1", cw_ids[0]):
        sentences = [sentences[1]]
    for sentence in sentences:
        token_and_ids = []
        for token in sentence.xpath('.//token'):
            token_attribs = dict(token.attrib)
            token_id = token_attribs['id']
            #cwのtoken情報だけをtoken_and_idsに格納する
            #if token_id not in cw_ids:
            #    continue
            for no_need in ['id', 'start', 'cat']:
                if no_need in token_attribs:
                    del token_attribs[no_need]
            token_and_ids.append((token_id, Token(**token_attribs)))
        tokens = [token for _, token in token_and_ids]
        #cwのspanの始点と終点
        sid = cw_span[0]
        eid = cw_span[-1]
        #print(sid,eid)
        #部分木のrootとなるspan idを新しいrootとする
        newroot = sentence.xpath('./ccg/span[@begin=' + sid + ' and @end=' + eid + ']/@id')
        #print(newroot)

        #sentenceから部分木以外の要素を除く
        #for ccg in sentence.xpath('./ccg'):
        #    for span in ccg.xpath('./span'):
        #        if span.attrib['begin'] < sid or span.attrib['end'] > eid:
        #            ccg.remove(span)

        for ccg in sentence.xpath('./ccg'):
            #rootを新しいrootにセットする
            ccg.set('root', newroot[0])
            tree = parse(ccg, dict(token_and_ids))
            yield ccg.attrib['id'], tokens, tree

#PTBフォーマットに変更するモジュール
def bracket(tree):
    def rec(node):
        if node.is_leaf:
            cat = str(node.cat).replace('(','<') \
                               .replace(')','>')
            word = node.word
            return f'({cat} {word})'
        else:
            cat = str(node.cat).replace('(','<') \
                               .replace(')','>')
            children = ' '.join(rec(child) for child in node.children)
            return f'({cat} {children})'
    #return f'(ROOT {rec(tree)})'
    return f'{rec(tree)}'

def main():
    no_cw = ["炎症 細胞 浸潤",  "肝 機能 異常", "肝 機能 障害", "狭小 化", "血液 培養", "好 酸 球 増 多", "呼吸 困難", "十二指腸 液 検査", "心 血管 系", "正常 化", "先行 治療", "総 胆 管 狭窄", "胆汁 うっ 滞", "胆のう 造影", "都度 改善", "低 アルブミン 血 症", "デュルバルマブ 療法", "内外 瘻化", "腹部 膨張 感", "保存 的 加療", "臨床 経過", "臨床 的 効果"]
    one_word = ["減 黄", "自宅 内", "紹介 受診", "小 開腹 下"]
    unbuilt = ["10 kg 減少", "11 歳", "DCV / ASV", "胃 移植 目的", "遠隔 転移", "加療 目的", "境界 明瞭", "経過 良好", "血管 内 溶血", "再 狭窄", "再 増悪", "食事 量", "食事 量 低下", "止血 コントロール", "止血 コントロール 目的", "手術 目的", "術後 リハビリ 目的", "出産 後 5 ヶ月 目", "小腸 部分 切除 術", "心臓 カテーテル 検査", "心臓 カテーテル 検査 目的", "精査 目的", "セカンド オピニオン 目的", "多 臓器", "多 臓器 転移", "通院 加療 中", "妊娠 9 ヶ月", "肺 脾臓 転移", "副作用 モニタリング", "腹水 コントロール", "腹水 コントロール 目的", "平成 10 年 9 月 MS 留置", "某 大学 病院 外科", "慢性 心不全 急性 増悪", "約 1 ヶ月"]

    parser = argparse.ArgumentParser('')
    parser.add_argument('FILE')
    args = parser.parse_args()

    xml_file = args.FILE
    #jigg.xmlファイルから複合語（名詞が連続している箇所）を特定し，複合語，id，spanの情報の辞書を作成する
    ccgtree = etree.parse(xml_file).getroot()
    sentences = ccgtree[0][0].xpath('sentence')
    #cw_data = {}
    cw_data = defaultdict(list)
    initpos = ""
    cw_surfs = []
    cw_ids = []
    cw_span = []
    for sentence in sentences:
        for token in sentence.xpath('.//token'):
            token_attribs = dict(token.attrib)
            pos = token_attribs['pos']
            #print("pos:" + pos)
            #print("initpos:" + initpos)
            #print(token_attribs['surf'])
            if pos == "接頭詞" and initpos == "":
                initpos = pos
                cw_span.append(token_attribs['start'])
                cw_surfs.append(token_attribs['surf'])
                cw_ids.append(token_attribs['id'])
            elif pos == "接頭詞" and initpos != "":
                cw_span.append(token_attribs['start'])
                cw_surfs.append(token_attribs['surf'])
                cw_ids.append(token_attribs['id'])
            elif (token_attribs['surf'] == "誤" or token_attribs['surf'] == "絞") and initpos == "":
                cw_span.append(token_attribs['start'])
                cw_surfs.append(token_attribs['surf'])
                cw_ids.append(token_attribs['id'])
            elif pos == "名詞" and initpos == "" and token_attribs['surf'] != "ため":
                initpos = pos
                cw_span.append(token_attribs['start'])
                cw_surfs.append(token_attribs['surf'])
                cw_ids.append(token_attribs['id'])
                #print(cw_surfs)
            elif pos == "名詞" and initpos != "" and token_attribs['surf'] != "ため":
                cw_span.append(token_attribs['start'])
                cw_surfs.append(token_attribs['surf'])
                cw_ids.append(token_attribs['id'])
                #print(cw_surfs)
            elif token_attribs['surf'] == "頻" and ("心室" in cw_surfs):
                cw_span.append(token_attribs['start'])
                cw_surfs.append(token_attribs['surf'])
                cw_ids.append(token_attribs['id'])
            elif token_attribs['surf'] == "うっ" and ("胆汁" in cw_surfs):
                cw_span.append(token_attribs['start'])
                cw_surfs.append(token_attribs['surf'])
                cw_ids.append(token_attribs['id'])
            elif token_attribs['surf'] == "滞" and ("うっ" in cw_surfs):
                cw_span.append(token_attribs['start'])
                cw_surfs.append(token_attribs['surf'])
                cw_ids.append(token_attribs['id'])
            elif token_attribs['surf'] == "拘" and ("屈曲" in cw_surfs):
                cw_span.append(token_attribs['start'])
                cw_surfs.append(token_attribs['surf'])
                cw_ids.append(token_attribs['id'])
            elif pos != "名詞" and initpos != "":
                if len(cw_surfs) > 1:
                    cw_span.append(token_attribs['start'])
                    tmp = " ".join(cw_surfs)
                    print(tmp)
                    if (tmp in one_word) or (tmp in no_cw) or (tmp in unbuilt):
                        pass
                    elif tmp == "10 kg" or tmp == "都度 改善":
                        pass
                    elif tmp == "2 ndline" or tmp == "当 院外 来" or tmp == "心 窩痛":
                        pass
                    else:
                        cw_data[tmp].append({"ids": cw_ids, "span": cw_span})
                initpos = ""
                cw_surfs = []
                cw_ids = []
                cw_span = []
    print(cw_data)

    #複合語ごとにxmlファイルから部分木を取り出しPTBフォーマットにする
    cw_num = 0
    for k, value in cw_data.items():
        for v in value:
            for name, tokens, tree in read_jigg_xml_cw(xml_file, v['ids'], v['span']):
                #print(bracket(tree))
                #PTBファイルに出力する場合
                with open("cw_origin_"+str(cw_num)+".ptb", "w") as f:
                    f.write(bracket(tree))
                with open("cw.txt", "a") as g:
                    g.write(str(cw_num)+"\t"+k)
                    g.write("\n")
                cw_num+=1
                break

if __name__ == '__main__':
    main()
