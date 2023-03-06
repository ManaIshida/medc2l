# medc2l

## 事前準備
- Python version >= 3.6
- [Coq 8.4](https://github.com/verypluming/flask_sts/tree/master/ccg2lambda/install_coq.md)
- depccg == 1.1.0

pyenv, virtualenv のインストール (follow https://qiita.com/Kodaira_/items/feadfef9add468e3a85b)
```
pyenv install 3.6.1
pyenv virtualenv 3.6.1 medc2l
```

medc2l をアクティブにする:
```
pyenv activate mec2l
```

### パッケージのインストール
```
pip install cython numpy depccg=1.1.0 nltk==3.0.5 janome
depccg_ja download
```
```
git clone https://github.com/ManaIshida/medc2l.git
```

### depccgのテスト
```
pyenv activate flask
python test.py --input "平成15年12月 に 出産2週間後 より 発熱 、 発疹 が 出現 し た 。" > test.html
```

You can also check the semantic representation with `--sem` option.
```
pyenv activate flask
python test.py --input "平成15年12月 に 出産2週間後 より 発熱 、 発疹 が 出現 し た 。" --sem > test.html
```

## データセット
このリポジトリの data/ フォルダには、以下のデータセットが含まれています。

### 複合語意味関係データセット
- ann_data/*.tok.ann


### 推論データセット
- rte_dataset.tsv

このデータセットには、前提文、仮説文、正解ラベル（2値分類）が含まれています。


## 参考文献
- 石田 真捺，谷中 瞳，馬目 華奈，戸次 大介．
「論理推論による症例検索に向けた日本語症例テキストの複合語解析の試案」
第35回人工知能学会全国大会論文集,2021．

- 石田 真捺，谷中 瞳，戸次 大介．
「日本語症例テキストの複合語解析と論理推論」
第36回人工知能学会全国大会論文集，2022．

- Mana Ishida, Hitomi Yanaka, and Daisuke Bekki.
"Compositional Semantics for Compound Words in Medical Case Retrieval."
In Proceedings of the 18th International Workshop on Logic and Engineering of Natural Language Semantics (LENLS18), pp.231-239, 2021.
