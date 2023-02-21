# 確実にccg2lambdaと互換性のあるCoq ver.8.4を入れる方法

1. If you do not have write access to /tmp, you should set the environment variable TMPDIR to the name of some other temporary directory.
```
 cd $HOME
 mkdir tmp
 export TMPDIR="/home/pascual/tmp" <- or add to ~/.bashrc
```

2. (optional) GNU make is needed to build ocamlbuild. If your system's default
  make is not GNU make, you need to define the GNUMAKE environment
  variable to the name of GNU make, typically with this command:
```
 export GNUMAKE=gmake
```

3. Make install directory.
```
 cd $HOME
 mkdir local
 export PATH="/home/pascual/local:/home/pascual/local/bin:$PATH"   <- or add to ~/.bashrc
```

4. Download ocaml-4.02.3, camlp5-rel614, coq-8.4pl6
```
 wget http://caml.inria.fr/pub/distrib/ocaml-4.02/ocaml-4.02.3.tar.gz
 wget https://github.com/camlp5/camlp5/archive/rel614.tar.gz
 wget https://coq.inria.fr/distrib/V8.4pl6/files/coq-8.4pl6.tar.gz
```

5. Install ocaml first
```
 tar xzf ocaml-4.02.3.tar.gz
 cd ocaml-4.02.3/
 ./configure -prefix $HOME/local
 make world.opt -j24
 umask 022
 make install
 clean up
 make clean
```

6. Install camlp second
```
 tar xzf rel614.tar.gz
 cd camlp5-rel614/
 ./configure -prefix $HOME/local
 make world.opt -j24
 make install
```

7. Install coq8.4
```
 tar xzf coq-8.4pl6.tar.gz
 cd coq-8.4pl6/
 ./configure -prefix $HOME/local
 make world -j24
 umask 022
 make install
 clean up
 make clean
```

8. if installation is fine, there will be $HOME/local/{bin,etc,lib,man,share}.
