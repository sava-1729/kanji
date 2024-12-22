import os
import csv
from jamdict import Jamdict
from collections import defaultdict
from random import sample, shuffle
import pykakasi
import networkx as nx
kks = pykakasi.kakasi()
jam = Jamdict()
seen = defaultdict(bool)
yomikata = defaultdict(str)
kanji_of_chapter = defaultdict(list)
kanji_chars_of_chapter = defaultdict(set)
radicals_of = defaultdict(set)
all_kanji = set()
radical_graph = nx.Graph()
extremely_similar_kanji = set()
very_similar_kanji = set()
kanji_with_common_radical = set()
yomikata2 = defaultdict(str)
# print(jam.krad["起"])
imp_radicals = set()
# imp_radicals = set(["辶"]) # also 起 and 建
# imp_radicals = set(["勿"])
# imp_radicals = set(["氵"])
# imp_radicals = set(["木"])
# imp_radicals = set(["也"])
# imp_radicals = set(["言"])
# print(jam.krad["課"])
# print(jam.krad["校"])
# print(jam.krad["思"])
# print(jam.krad["課"])
# 課 lhs, 校 rbhs, 新 lths, 村 rhs, 妹 lhs, 相 rhs, 時 rhs, 地 lhs/rhs, 思 bhs
kanjis_with_radical = defaultdict(set)


def import_kanji(filename="kanji.csv"):
    with open(filename, "r") as file:
        reader = csv.reader(file)
        chapter = 0
        for row in reader:
            if row[0].startswith("-"):
                chapter += 1
            else:
                kanji_of_chapter[chapter].append(row[0])
                yomikata[row[0]] = kks.convert(row[0])[0]["hira"]
                for k in row[0]:
                    if k in jam.krad and k not in all_kanji:
                        kanji_chars_of_chapter[chapter].add(k)
                        all_kanji.add(k)
                        if k not in radicals_of:
                            radicals_of[k] = set(jam.krad[k])
                        if k not in yomikata:
                            yomikata[k] = kks.convert(k)[0]["hira"]
                        for r in imp_radicals:
                            if r in jam.krad[k]:
                                kanjis_with_radical[r].add(k)


def import_n4kanji(filename="n4_kanji2.txt"):
    global yomikata2
    with open(filename, "r") as file:
        while file.readable():
            phrase = file.readline()
            if '：' not in phrase:
                break
            phrase, meaning = phrase.split('：')
            while "（" in meaning and "）" in meaning:
                l = meaning.index("（")
                r = meaning.index("）")
                meaning = meaning[:l] + meaning[r+1:]
            phrase = phrase.split('・')
            meaning = meaning.split('・')
            assert len(phrase) == len(meaning)
            for k, m in zip(phrase, meaning):
                yomikata2[k] = m

def yomikata_quiz2():
    global yomikata2
    ques = list(yomikata2.keys())
    shuffle(ques)
    for k in ques:
        print("-------------------------------------------")
        print("How do you read: %s?" % k)
        ans = input()
        print(yomikata2[k])

def yomikata_quiz(num_questions, chapters=[], input_mode="romaji"):
    kanjis = []
    if len(chapters) == 0:
        kanjis = yomikata.keys()
    else:
        for c in chapters:
            kanjis = kanjis + kanji_of_chapter[c]
    kanjis = sample(kanjis, min(num_questions, len(kanjis)))
    
    for k in kanjis:
        print("-------------------------------------------")
        print("How do you read: %s?" % k)
        hiragana = [converted["hira"] for converted in kks.convert(k)]
        hiragana = "".join(hiragana)
        ans = input()
        if input_mode == "hiragana":
            if ans == hiragana:
                print("Correct!")
            else:
                print("Maybe incorrect. Ans: %s" % hiragana)
        else:
            print(hiragana)


def print_radicals():
    with open("kanji.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            kan = row[0]
            for k in kan:
                if k in jam.krad and not seen[k]:
                    print(k, " = ",jam.krad[k])
                    seen[k] = True
                    if input():
                        continue

def make_graph():
    for k1 in all_kanji:
        for k2 in all_kanji:
            if k1 != k2 and not radical_graph.has_edge(k1, k2):
                common_rads = len(radicals_of[k1].intersection(radicals_of[k2]))
                if common_rads > 0:
                    radical_graph.add_edge(k1, k2, weight=common_rads)
    for k1, k2, w in radical_graph.edges.data('weight'):
        if w >= 3:
            extremely_similar_kanji.add((k1, k2))
        if w >= 2:
            very_similar_kanji.add((k1, k2))
        kanji_with_common_radical.add((k1, k2))
    
def visualize_radical_graph():
    import matplotlib.pyplot as plt
    sub = plt.subplot(111)
    nx.draw(radical_graph, with_labels=True, font_weight='bold')
    plt.show()

def same_radical_quiz():
    for r in imp_radicals:
        for k in kanjis_with_radical[r]:
            print(k)
            input()
            print(yomikata[k])
            print("------------------------------")

if __name__ == "__main__":
    import_kanji("kanji_pk2.csv")
    yomikata_quiz(100, chapters=[3])

    # import_n4kanji()
    # yomikata_quiz2()

    # print(len(yomikata2))
    # print_radicals()
    # import_kanji()
    # yomikata_quiz(100, chapters=list(range(20)))
    # same_radical_quiz()
    # make_graph()
    # visualize_radical_graph()
    # for x, y in extremely_similar_kanji:
    #     print(x, "vs", y)
    #     input()
    #     print(yomikata[x], "vs", yomikata[y])
    #     print("----------------------------------")