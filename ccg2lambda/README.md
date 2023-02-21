# ccg2lambda in python

## Preparation
- Python version >= 3.6
- [Coq 8.4](https://github.com/verypluming/flask_sts/tree/master/ccg2lambda/install_coq.md)
```
pyenv activate flask
```

### Install modules and models
```
pip install cython numpy depccg nltk=3.0.5 janome
depccg_ja download
```

### Factcheck with ccg2lambda
```
coqc coqlib.v
cd ccg2lambda
python fact_check.py
```

#### Programmatic Usage
```
import sys
sys.path.append('./ccg2lambda')
from fact_check import check_fact
target = "これは文です。"
source = ["これはテストの文です。", "これはテストです。", "これは仮のテストです。"]
ret = check_fact(target, source)
print(ret)
```


## Contact
Hitomi Yanaka hitomi.yanaka@riken.jp

## License
Apache License
