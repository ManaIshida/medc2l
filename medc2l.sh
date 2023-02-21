#!/bin/bash
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

# Script to Recognize Textual Entailment of problems in Japanese, using
# multiple CCG parsers (Jigg and depccg at the moment).
# This script receives a file with several sentences (one per line), where all
# sentences are premises except the last one, which is a conclusion. It returns
# 'yes' (the premises entail the conclusion), 'no' (there is a contradiction) or
# 'unknown' (none of the former).
# You can use it as:
#
# ./medc2l.sh <sentences.txt> <semantic_templates.yaml> <nbest>
#

USAGE="Usage: ./medc2l.sh <sentences.txt> <semantic_templates.yaml> <transform.tsgn>"

# Set the number of nbest parses (Default: 1)
#nbest=${4:-1}

# Create a file named "tregex_location.txt" at the "scripts" directory
# $ cat tregex_location.txt
# /path/to/stanford-tregex-20XX-XX-XX
tregex_dir=`cat tense/tregex_location.txt`
export CLASSPATH=$tregex_dir/stanford-tregex.jar:$CLASSPATH

# This variable contains the filename where the tsurgeon template are.
tsurgeon_templates=$3
if [ ! -f $tsurgeon_templates ]; then
  echo "Error: File with tsurgeon templates does not exist."
  echo $USAGE
  exit 1
fi

# This variable contains the filename where the category templates are.
category_templates=$2
if [ ! -f $category_templates ]; then
  echo "Error: File with semantic templates does not exist."
  echo $USAGE
  exit 1
fi

# This variable contains the name of the dataset (fracas or jsem).
sentences_fname=$1
sentences_basename=${sentences_fname##*/}
if [ ! -f $sentences_fname ]; then
  echo "Error: File with plain sentences does not exist."
  echo $USAGE
  exit 1
fi

# These variables contain the names of the directories where intermediate
# results will be written.
#plain_dir="ja_plain" # tokenized sentences.
#parsed_dir="ja_parsed" # parsed sentences into XML or other formats.
#results_dir="ja_results" # HTML semantic outputs, proving results, etc.

#tre_* は、coqlib.vが tense/coqlib_my_nlp2023.v
#tre_*_test は、coqlib.vが tense/coqlib_my_nlp2023_test.v (nltac_initを、昔のルールに寄せてみた)

plain_dir="rte_plain" # tokenized sentences.
parsed_dir="rte_parsed" # parsed sentences into XML or other formats.
results_dir="rte_results"
tags_dir="rte_tags"

mkdir -p $plain_dir $parsed_dir $results_dir $tags_dir

# Copy the input text to plain_dir
if [ ! -f ${plain_dir}/${sentences_basename} ]; then
  cp $sentences_fname ${plain_dir}/${sentences_basename}
fi

function timeout() { perl -e 'alarm shift; exec @ARGV' "$@"; }

function parse_depccg() {
  # Parse using depccg.
  base_fname=$1
  cat ${plain_dir}/${base_fname} | \
  depccg_ja \
      --input-format raw \
      --annotator janome \
      --format jigg_xml \
  > ${parsed_dir}/${base_fname}.jigg.xml \
  2> ${parsed_dir}/${base_fname}.log
}

function tsurgeon() {
  sentences_basename=$1
  tsurgeon=$2
  java -mx100m edu.stanford.nlp.trees.tregex.tsurgeon.Tsurgeon -s \
    -treeFile ${parsed_dir}/${sentences_basename}.mod.ptb $tsurgeon
}

function semantic_parsing() {
  sentences_basename=$1
  python ccg2lambda/semparse.py \
    $parsed_dir/${sentences_basename}.jigg.mod.xml \
    $category_templates \
    $parsed_dir/${sentences_basename}.sem.xml \
    --arbi-types \
    2> $parsed_dir/${sentences_basename}.sem.err
}

function proving() {
  sentences_basename=$1
  start_time=`python -c 'import time; print(time.time())'`
    timeout 200 python ccg2lambda/prove.py \
      ${parsed_dir}/${sentences_basename}.sem.xml \
      --graph_out ${results_dir}/${sentences_basename}.html \
      > ${results_dir}/${sentences_basename}.answer \
      2> ${results_dir}/${sentences_basename}.err
  rte_answer=`cat ${results_dir}/${sentences_basename}.answer`
  echo "judging entailment for ${parsed_dir}/${sentences_basename}.sem.xml $rte_answer"
  proof_end_time=`python -c 'import time; print(time.time())'`
  proving_time=`echo "${proof_end_time} - ${start_time}" | bc -l | \
       awk '{printf("%.2f\n",$1)}'`
  echo $proving_time > ${results_dir}/${sentences_basename}.time
}


# Set the current answer
current_answer="unknown"

# CCG parsing, semantic parsing and theorem proving
echo "parsing ${plain_dir}/${sentences_basename}"
parse_depccg $sentences_basename

# original tree (ptb file)
python ccg2lambda/brackets.py ${parsed_dir}/${sentences_basename}.jigg.xml \
    > ${parsed_dir}/${sentences_basename}.ptb

# TODO: detect cw and output cw_origin_x.ptb and cw.txt
rm cw.txt
python extract_cw.py ${parsed_dir}/${sentences_basename}.jigg.xml

# TODO: predict cw tags with cw.txt
echo "predict tags"
python predict_tags.py > ${tags_dir}/${sentences_basename}

rm cw_new.ptb
IFS_BACKUP=$IFS
count=0
while IFS=, read su ta
do
  s=`echo $su`
  t=`echo $ta`
  surf=`echo "${s}"`
  tags=`echo "${t}"`

  #CFG木を構築
  python parse_cw.py --surf="${surf}" --tags="${tags}"

  cat cw_new.ptb
  # pattern match and modify tree
  # input: ${parsed_dir}/${sentences_basename}.ptb, cw_origin_x.ptb, cw_new.ptb
  # output: ${parsed_dir}/${sentences_basename}.mod.ptb
  origin_ptb="cw_origin_${count}.ptb"

  if [ $count -eq 0 ]; then
    total=$(cat ${parsed_dir}/${sentences_basename}.ptb)
  fi
  ori_cw=$(echo | awk '{print $1}' $origin_ptb | sed -e 's#\\#\\\\#g' | sed -e 's#(##g')
  echo $ori_cw
  ori_tmp=$(cat $origin_ptb)
  new_tmp=$(cat cw_new.ptb)
  ori=$(echo $ori_tmp | sed -e 's#\\#\\\\#g' | sed -e 's#\/#\\\/#g'  | sed -e 's#\[#\\\[#g' | sed -e 's#\]#\\\]#g')

  #統語範疇のかっこは<>にしないとエラーになる
  new=$(echo $new_tmp | sed -e "s#CW#$ori_cw#g" | sed -e 's#NEG1#<NP[case=X1,mod=neg,fin=en]/NP[case=X1,mod=X2,fin=en]>/<NP[case=X1,mod=m_en,fin=en]/NP[case=X1,mod=X2,fin=en]>#g' | sed -e 's#NEG2#S[mod=neg,form=X2,fin=ev]/S[mod=ev,form=X2,fin=ev]#g' | sed -e 's#NEG3#NP[case=X1,mod=neg,fin=en]/NP[case=X1,mod=X2,fin=en]#g' | sed -e 's#M_QEN#NP[case=X1,mod=m_en,fin=en]/NP[case=X1,mod=X2,fin=q_en]#g' | sed -e 's#M_TEN#NP[case=X1,mod=m_en,fin=en]/NP[case=X1,mod=X2,fin=t_en]#g' | sed -e 's#M_EEN#NP[case=X1,mod=m_en,fin=en]/NP[case=X1,mod=X2,fin=e_en]#g' | sed -e 's#M_EN2#NP[case=X1,mod=m_en,fin=en]/NP[case=X1,mod=X2,fin=en]#g' | sed -e 's#M_EN#NP[case=X1,mod=m_en,fin=en]/NP[case=X1,mod=X2,fin=en]#g' | sed -e 's#PA2#NP[case=X1,mod=pa,fin=en]/NP[case=X1,mod=X2,fin=en]#g' | sed -e 's#PA#NP[case=X1,mod=pa,fin=en]/NP[case=X1,mod=X2,fin=en]#g' | sed -e 's#WO_2#S[mod=wo,form=X2,fin=ev]/S[mod=X1,form=X2,fin=ev]#g' | sed -e 's#WO#S[mod=wo,form=X2,fin=ev]/S[mod=X1,form=X2,fin=ev]#g' | sed -e 's#NI#S[mod=ni,form=X2,fin=ev]/S[mod=X1,form=X2,fin=ev]#g' | sed -e 's#GA#S[mod=ga,form=X2,fin=ev]/S[mod=X1,form=X2,fin=ev]#g' | sed -e 's#S_EV#S[mod=ev,form=X2,fin=ev]#g' | sed -e 's#EV_2#S[mod=ev,form=X2,fin=ev]/S[mod=ev,form=X2,fin=ev]#g' | sed -e 's#EV_wo#S[mod=ev,form=X2,fin=ev]#g' | sed -e 's#EV#S[mod=ev,form=X2,fin=ev]#g' | sed -e 's#Q_EN#NP[case=X1,mod=X2,fin=q_en]#g' | sed -e 's#T_EN#NP[case=X1,mod=X2,fin=t_en]#g' | sed -e 's#E_EN#NP[case=X1,mod=X2,fin=e_en]#g' | sed -e 's#EN#NP[case=X1,mod=X2,fin=en]#g' | sed -e 's#\\#\\\\#g' | sed -e 's#\/#\\\/#g' | sed -e 's#\[#\\\[#g' | sed -e 's#\]#\\\]#g' )

  ####################
  ####################


  echo $new

  echo "$total" | sed -e "s/$ori/$new/" > ${parsed_dir}/${sentences_basename}.mod.ptb
  total=$(cat ${parsed_dir}/${sentences_basename}.mod.ptb)
  let ++count
done < cw_tag.txt
IFS=$IFS_BACKUP

#意味合成について失敗したとき、１つずつデバッグしたい場合は、ccg2lambda/semantic_index.py のprint（L73,L85~88）を復活させてください

echo "Execute tsurgeon"
tsurgeon $sentences_basename $tsurgeon_templates \
  > ${parsed_dir}/${sentences_basename}.tsgn.ptb

# modify jigg.xml with modified tree (ptb file: ${parsed_dir}/${sentences_basename}.mod.ptb)
cat ${parsed_dir}/${sentences_basename}.tsgn.ptb \
  | sed 's#<#(#g' | sed 's#>#)#g' \
  | sed 's#{#[#g' | sed 's#}#]#g' \
  > ${parsed_dir}/${sentences_basename}.tsgn.tmp.ptb
python -m depccg.tools.ja.tagger --format jigg_xml ${parsed_dir}/${sentences_basename}.tsgn.tmp.ptb \
  > ${parsed_dir}/${sentences_basename}.jigg.tmp.xml
  2> ${results_dir}/${sentences_basename}.tmp.err

python ccg2lambda/map_tokens.py ${parsed_dir}/${sentences_basename}.jigg.xml \
  ${parsed_dir}/${sentences_basename}.jigg.tmp.xml \
  > ${parsed_dir}/${sentences_basename}.jigg.mod.xml

# semantic parsing and visualize
echo "semantic parsing $parsed_dir/${sentences_basename}.sem.xml"
semantic_parsing $sentences_basename

proving $sentences_basename

if [ ! -e ${results_dir}/${sentences_basename}.answer ]; then
  python ccg2lambda/visualize.py ${parsed_dir}/${sentences_basename}.sem.xml \
  > ${results_dir}/${sentences_basename}.html
fi

#rm ${parsed_dir}/${sentences_basename}.mod.tmp.ptb
#rm   ${parsed_dir}/${sentences_basename}.jigg.tmp.xml
