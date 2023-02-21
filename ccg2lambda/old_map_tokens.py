from lxml import etree
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('TAGGED')
parser.add_argument('UNTAGGED')
args = parser.parse_args()

tagged = etree.parse(args.TAGGED)
untagged = etree.parse(args.UNTAGGED)
tagged_sentences = tagged.getroot().findall('*//sentence')
untagged_sentences = untagged.getroot().findall('*//sentence')
assert len(tagged_sentences) == len(untagged_sentences)

for untagged_sentence, tagged_sentence in zip(untagged_sentences, tagged_sentences):
    untagged_tokens = untagged_sentence.xpath('tokens[1]')[0]
    tagged_tokens = tagged_sentence.xpath('tokens[1]')[0]
    #print(len(untagged_tokens))
    t = 0
    for u in range(len(untagged_tokens)):
        untagged_token = untagged_tokens[u].attrib
        tagged_token = tagged_tokens[t].attrib
        if "s0_" in untagged_token['id']:
            id = "s0_" + str(u)
        elif "s1_" in untagged_token['id']:
            id = "s1_" + str(u)
        #print(untagged_token)
        #print(tagged_token)
        if untagged_token['surf'] == tagged_token['surf'] :
            tagged_tokens[t].set('start', str(u))
            tagged_tokens[t].set('id', id)
            untagged_tokens.replace(untagged_tokens[u],tagged_tokens[t])
            #untagged_tokens[u].extend(tagged_tokens[t].xpath('token'))
            #print("新")
            #print("ここ")
            #print(untagged_tokens[u].attrib)
            #print(tagged_tokens[t].attrib)
            #print("だよ")
            t = t-1
        else:
            tagged_tokens[t+1].set('start', str(u))
            tagged_tokens[t+1].set('surf', untagged_token['surf'])
            tagged_tokens[t+1].set('base', untagged_token['surf'])
            tagged_tokens[t+1].set('reading', "*")
            tagged_tokens[t+1].set('id', id)
            #print(untagged_tokens[u].attrib)
            #print(tagged_tokens[t+1].attrib)
            untagged_tokens.replace(untagged_tokens[u],tagged_tokens[t+1])
            #t = t+1
        t = t+1
        #untagged_tokens.remove(token)
    #untagged_tokens.extend(tagged_tokens.xpath('token'))

print(etree.tostring(untagged, encoding='utf-8', pretty_print=True).decode('utf-8'))
