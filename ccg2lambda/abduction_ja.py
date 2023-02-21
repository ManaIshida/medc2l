#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#  Copyright 2017 Pascual Martinez-Gomez
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

from abduction_tools_ja import try_abductions_dcs, try_abductions_w2v, try_abductions_ginza

class AxiomsDCS(object):
    """
    Create axioms using relations in DCSVec.
    """
    def __init__(self):
        pass

    def attempt(self, coq_scripts, context=None):
        return try_abductions_dcs(coq_scripts)

class AxiomsW2V(object):
    """
    Create axioms using relations in Word2Vec.
    """
    def __init__(self):
        pass

    def attempt(self, coq_scripts, context=None):
        return try_abductions_w2v(coq_scripts)

class AxiomsGINZA(object):
    """
    Create axioms using relations in GINZA.
    """
    def __init__(self):
        pass

    def attempt(self, coq_scripts, context=None):
        return try_abductions_ginza(coq_scripts)