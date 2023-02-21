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
