#!/usr/bin/python3
# -*- coding: utf-8 -*-

from keras import backend as K
from keras.models import load_model, model_from_json
from keras.layers import Dense, LSTM, InputLayer, Bidirectional, TimeDistributed, Embedding, Activation
from keras.optimizers import Adam

#読み込むモデルを指定
model = model_from_json(open('model/model.json').read())
model.load_weights('model/model.h5')

import numpy as np
tagged_sents = []
sentences = []
surfs = []

f = open('cw.txt', 'r')
lines = f.readlines() #ファイルの各行を読み込んでリストにする
f.close()

for line in lines:
    ln = line.strip() # \nを削除
    l = ln.split('\t') # タブの箇所で区切ってリストにする
    surf = l[1]
    surfs.append(surf)
    tlist = l[1].split() # GIS 所見 みたいなのを['GIS','所見']にする
    t_sentence = tuple(tlist)
    sentences.append(np.array(t_sentence))
test_sentences = sentences

# 単語，タグのID化
tag2index = {'GA': 1, 'PP': 2, 'EV': 3, 'Q_EN': 4, 'T_EN': 5, 'M_EN': 6, 'CL': 7, 'NUM': 8, 'TE': 9, 'NEG': 10, 'NI': 11, 'WO': 12, 'S_EV': 13, 'PA': 14, 'CLP': 15, 'JTE': 16, 'EN': 17, 'E_EN': 18, '-PAD-': 0}
word2index = {'湿疹': 2, '穿孔': 3, '目標': 4, '松葉杖': 5, '強': 6, '入園': 7, '一': 8, '閉塞': 9, '胃': 10, '誤': 11, '2025': 12, '網膜': 13, 'ドミノ': 14, '防御': 15, '鼠径': 16, '肝炎': 17, '2004': 18, 'acnu': 19, '瘤': 20, '物質': 21, 'c': 22, '出産': 23, '再開': 24, '38': 25, '新鮮': 26, '出現': 27, '類': 28, '膨満': 29, '赤沈': 30, '神経': 31, '1990': 32, '訪問': 33, '標本': 34, '数': 35, 'aw': 36, '減少': 37, 'トレーニング': 38, '戸籍': 39, '眼': 40, '予定': 41, '業': 42, '26': 43, '接合': 44, '病棟': 45, '形態': 46, '謳吐': 47, '高校': 48, '保護': 49, '化': 50, '持続': 51, 'ビラン': 52, '位置': 53, '12': 54, '視力': 55, '這い': 56, '帝京大学': 57, '用': 58, '上部': 59, 'ノイロトロピン': 60, '罹患': 61, '乳癌': 62, '不整': 63, '抜去': 64, '培養': 65, '対処': 66, '下大': 67, 'フルニトラゼパム': 68, '左肩': 69, '斜': 70, '聴覚': 71, '重要': 72, 'rfs': 73, '左': 74, '印': 75, '排除': 76, '栄養': 77, '対': 78, '貯留': 79, '温': 80, '管状': 81, '来院': 82, '大腸': 83, '褐色': 84, '頻度': 85, '33': 86, '報告': 87, '安定': 88, 'ip': 89, '属': 90, '胸痛': 91, '終了': 92, '脊髄': 93, '小児科': 94, '大動脈': 95, '咳嗽': 96, '蛋白': 97, '併用': 98, '蕁麻疹': 99, '永久': 100, '初期': 101, '運転': 102, '検査': 103, '2009': 104, '腰部': 105, '頸部': 106, 'う': 107, '入浴': 108, 'アプローチ': 109, '倫理': 110, '粘膜': 111, 'はさみ': 112, '腰': 113, '仮性': 114, '水性': 115, '塞栓': 116, 'コリン': 117, 'リポ': 118, '水疱': 119, '36': 120, 'ニボルマブ': 121, '内容': 122, '症': 123, 'psp': 124, 'vcm': 125, '膿瘍': 126, '言語': 127, '血清': 128, '増大': 129, '回避': 130, '入学': 131, '細胞': 132, '不': 133, '漏': 134, '行': 135, '銅': 136, '若年': 137, '重症': 138, '難治': 139, '結石': 140, '黒色': 141, '腸閉塞': 142, '球': 143, '腹水': 144, '安全': 145, '帰宅': 146, 'フェンタニル': 147, 'リンパ': 148, '補助': 149, '統合': 150, '比較': 151, '月': 152, 'シロアリ': 153, '仕事': 154, '門': 155, '急性': 156, '強化': 157, '筋力': 158, 'ct': 159, '提供': 160, 'cddp': 161, '円型': 162, 'ブドウ': 163, '2006': 164, '左右': 165, '換気': 166, 'リコンストラクションプレート': 167, '豆腐': 168, '近': 169, 'pgi': 170, '頚部': 171, '羅': 172, '胆嚢': 173, '疽': 174, '年': 175, '皮下': 176, '圧痛': 177, '腹膜': 178, 'fu': 179, '虚': 180, '貼付': 181, 'カリウム': 182, 'バル': 183, '心肺': 184, '睡眠': 185, 'dic': 186, '血': 187, '陰部': 188, '悪化': 189, '例': 190, '摂取': 191, '臨床': 192, '軽': 193, '亜': 194, '消': 195, '弱化': 196, '中毒': 197, '説明': 198, '3': 199, '椎間板': 200, '値': 201, 'ぶどう': 202, '前立腺': 203, 'イレウス': 204, 'コルチコステロイド': 205, '腎': 206, '年間': 207, '後': 208, '沈着': 209, '瘢痕': 210, 'か月': 211, '25': 212, '両': 213, '病状': 214, '攣縮': 215, '発症': 216, '裂孔': 217, 'カ月': 218, '生存': 219, '入院': 220, '汎': 221, '多': 222, 'll': 223, 'カルバマゼピン': 224, '音波': 225, '精神': 226, '角膜': 227, '栓': 228, '費': 229, '乳頭': 230, 'adl': 231, '医': 232, '糜爛': 233, '2011': 234, '選択': 235, '体調': 236, '飲酒': 237, '心室': 238, '浸出': 239, '傾向': 240, '慢性': 241, '前日': 242, '路上': 243, '腹壁': 244, '前頭葉': 245, '防除': 246, '委員': 247, '修復': 248, '化膿': 249, '敷地': 250, '分泌': 251, 'アレルギー性': 252, '骨髄': 253, 'ストレス': 254, '20': 255, '・': 256, '耳鼻': 257, '滞': 258, 'hs': 259, '起床': 260, '肺': 261, '冠動脈': 262, '病': 263, 'wf': 264, 'mrsa': 265, '照射': 266, '症候': 267, '定型': 268, 'o': 269, '的': 270, '大腿': 271, '17': 272, '食欲': 273, '鏡': 274, 'つかまり': 275, '浸潤': 276, 'バギー': 277, '変換': 278, '間': 279, 'mri': 280, '傾': 281, '増加': 282, '細': 283, '横隔膜': 284, '留置': 285, '者': 286, '周': 287, '39': 288, 'めまい': 289, '置換': 290, '主': 291, '亢進': 292, '隔': 293, '広尾': 294, '特異': 295, '外傷': 296, '60': 297, '都立': 298, '指導': 299, '扁平': 300, '肉眼': 301, '夕食': 302, '動作': 303, '他': 304, 'ラクチトール': 305, 'borrmann': 306, '筋': 307, '子宮': 308, '制限': 309, 'ヨード': 310, 'マイシン': 311, '嚢腫': 312, '法': 313, '嚢胞': 314, '代償': 315, '思不振': 316, '利尿': 317, 'qol': 318, '増量': 319, '剥離': 320, '系': 321, '補正': 322, '小学校': 323, '13': 324, '上': 325, '気管': 326, '29': 327, '2008': 328, '摘出': 329, '15': 330, '断': 331, '朝': 332, '背景': 333, '女性': 334, '原因': 335, '接触': 336, '抗生': 337, '装着': 338, '紅': 339, '乾燥': 340, 'かかりつけ': 341, 'サイトカイン': 342, '塞栓性': 343, 'ステロイド': 344, '腹部': 345, 'nst': 346, '硬': 347, '安静': 348, '臍帯': 349, '疾患': 350, '処方': 351, '狭心症': 352, '鎮痛': 353, '腫瘍': 354, '前': 355, '破裂': 356, '横行': 357, 'a': 358, 'lvfx': 359, '/': 360, '血小板': 361, '検': 362, 'fp': 363, '触': 364, '免疫': 365, '14': 366, 'アミラーゼ': 367, '融合': 368, 'ivc': 369, '立': 370, '調節': 371, '平滑': 372, '通院': 373, '電動': 374, '開': 375, '靴': 376, '炎': 377, 'ano': 378, '歯': 379, '科': 380, '静脈': 381, 'レーン': 382, 'アトピー': 383, '完成': 384, '採血': 385, '搬送': 386, '扼性': 387, '調整': 388, '中心': 389, '季': 390, '麻疹': 391, 'レベル': 392, '作成': 393, '拡散': 394, 'アセタゾラミド': 395, '深部': 396, '膝': 397, '芽': 398, '薬剤': 399, 'エコー': 400, 'イレウスチューブ': 401, '漸減': 402, '脳性': 403, '吸引': 404, '器': 405, '1987': 406, 'モンテルカスト': 407, '1989': 408, '刺激': 409, '使用': 410, 'mct': 411, 'sjogren': 412, '浮腫': 413, '原': 414, '裂': 415, '課題': 416, '合流': 417, '解決': 418, 'セルフ': 419, '認知': 420, 'カテーテル': 421, '組織': 422, '食': 423, '脂': 424, '先天': 425, '副腎': 426, '屈曲': 427, '緑': 428, 'ics': 429, 'st': 430, '記入': 431, '足': 432, '一時': 433, 'コバルト': 434, '阻害': 435, 'nppv': 436, '診断': 437, '救急': 438, '血栓': 439, '椎': 440, 'センチネルリンパ': 441, '患': 442, '拘': 443, '縦': 444, 'チューブ': 445, '播種': 446, '介入': 447, '病巣': 448, '経過': 449, '伸': 450, '前方': 451, 'ケ月': 452, 'er': 453, 'erbd': 454, '状況': 455, 'igm': 456, '繊維': 457, '層': 458, '暗紅': 459, '8': 460, '黄': 461, '2014': 462, '排便': 463, '腺': 464, '末梢': 465, '期': 466, '低下': 467, '病院': 468, '回復': 469, 'candida': 470, '介助': 471, '害虫': 472, '室内': 473, '頭頂': 474, 'v': 475, '乱用': 476, 'リハビリ': 477, '心電図': 478, '最高': 479, 'cmv': 480, '無': 481, '乳': 482, 'アブレーション': 483, '物': 484, '16': 485, 'vel': 486, '1964': 487, '肛門': 488, 'リンパ腫': 489, '注入': 490, '22': 491, '度': 492, '週': 493, '舌根': 494, 'oros': 495, 'l': 496, 'サルコイド': 497, '尿道': 498, '野球': 499, '完遂': 500, '豆乳': 501, '2015': 502, '蜂': 503, '生': 504, '血腫': 505, '服薬': 506, 'evar': 507, '副作用': 508, '2007': 509, '型': 510, '心不全': 511, '訓練': 512, '内服薬': 513, '槌': 514, '喪失': 515, '動': 516, '依頼': 517, '膠': 518, '発表': 519, '119': 520, 'ヘパリン': 521, '出生': 522, '胆道': 523, '尿': 524, '日': 525, '集中': 526, '類似': 527, '棘': 528, 'ヒト': 529, '跛行': 530, '音': 531, '膣': 532, '停止': 533, '合併症': 534, '室': 535, 'ガイドライン': 536, '静': 537, '膿疱': 538, '評価': 539, '光線': 540, '収縮': 541, 'sl': 542, '4': 543, 'mph': 544, '抵抗': 545, 'saba': 546, '脊椎': 547, 'consult': 548, '真': 549, '損傷': 550, '酸素': 551, 'グロブリン': 552, 'コンサルト': 553, '付着': 554, '方法': 555, '精査': 556, '塞栓術': 557, '病変': 558, '過敏': 559, '殺': 560, '乳がん': 561, '人員': 562, 'pppd': 563, '老人': 564, 'シグナル': 565, '当': 566, '骨盤': 567, '普及': 568, '節': 569, '流': 570, 'ハムストリングス': 571, '期間': 572, '色': 573, '自転車': 574, '体': 575, '側': 576, '再燃': 577, '階段': 578, '僧': 579, 'ドパミン': 580, '維持': 581, '筋炎': 582, 'ヒス': 583, '脾機能': 584, '縮': 585, '長与': 586, '卒業': 587, '痙直型': 588, '乾性': 589, '変動': 590, '膵胆管': 591, '翌日': 592, '肝': 593, '直腸': 594, '好': 595, '切開': 596, '傾斜': 597, '過程': 598, '中': 599, '陥没': 600, '門部': 601, '面': 602, '相': 603, '口内': 604, 'リハビリテーション': 605, '促進': 606, '内': 607, '増': 608, '在': 609, '抗菌': 610, '根治': 611, '摂': 612, '頓': 613, 'spo': 614, '有': 615, '1988': 616, '趣味': 617, '施設': 618, 'カリ': 619, 'アスピリン': 620, '単': 621, '嚥': 622, '野': 623, '局面': 624, 'バザン': 625, '軟膏': 626, '新生': 627, '巣': 628, '縦断': 629, '減量': 630, 'ソーシャルサポート': 631, '両側': 632, '転移': 633, '実測': 634, '変異': 635, '高速': 636, '強度': 637, '所見': 638, '反応': 639, '心房': 640, '伸展': 641, 'リドカイン': 642, '意識': 643, '訴': 644, '乾癬': 645, '赤色': 646, 'maze': 647, '産婦人科': 648, '観戦': 649, '一過': 650, '小児': 651, '肢': 652, '墜落': 653, '軽快': 654, '継続': 655, 'シャント': 656, '37': 657, '口腔': 658, '腹腔': 659, '撮影': 660, '距離': 661, '微生物': 662, '退院': 663, '負担': 664, 'フォロー': 665, '情報': 666, '痛': 667, 'パゾパニブ': 668, '姿勢': 669, '固定': 670, 'がん': 671, '肋': 672, '50': 673, 'インスリン': 674, '乾酪': 675, '当初': 676, '結': 677, '気': 678, '頻': 679, 'グルタミン': 680, '移植': 681, '抗癌剤': 682, '高度': 683, '発作': 684, 'クロマトグラフィー': 685, '胆': 686, '車椅子': 687, '内臓': 688, '脾臓': 689, '眼窩': 690, 'ra': 691, '質': 692, '尋常': 693, 'γ': 694, '叢': 695, '下腹部': 696, '抜歯': 697, '高': 698, '盲腸': 699, 'ige': 700, '不足': 701, '丘': 702, 'hfnc': 703, '能': 704, '高位': 705, '庖瘡': 706, '関節': 707, '発生': 708, '前後': 709, 'ercp': 710, '胆石': 711, '合併': 712, '吸入': 713, '不随': 714, '血沈': 715, '管': 716, '振幅': 717, '発疹': 718, '鋳型': 719, 'ヘルシンキ': 720, '限局': 721, '舌': 722, '下肢': 723, '粒': 724, '1996': 725, '一般': 726, '現在': 727, 'ハイ': 728, '肝硬変': 729, 'プログラム': 730, '心筋': 731, '胸腔': 732, '片': 733, '臥床': 734, 'ミノ': 735, '23': 736, '開腹': 737, '形成': 738, '防止': 739, '十二指腸': 740, '濃度': 741, 'mds': 742, '情動': 743, '分間': 744, '痒疹': 745, '腫': 746, '肥厚': 747, '径': 748, '梗塞': 749, '59': 750, '放射線': 751, '致死': 752, 'pt': 753, '紅色': 754, 'フィルター': 755, 'キャンディン': 756, '右側': 757, 'カリフラワー': 758, '皮膜': 759, '赤血球': 760, '虹彩': 761, 'low': 762, '白': 763, '未': 764, '99': 765, '乾': 766, '反': 767, '腹膜炎': 768, 'bil': 769, '皮': 770, '死亡': 771, '酵素': 772, '6': 773, '予防': 774, '解熱': 775, '2001': 776, '多発': 777, '同日': 778, '経': 779, '褪': 780, '帰': 781, 'タンパク': 782, '果物': 783, '水痘': 784, '化学': 785, '中止': 786, 'ショック': 787, '寛解': 788, '新規': 789, '四肢': 790, '承認': 791, '房内': 792, '狭窄': 793, '直前': 794, '満月': 795, '傍': 796, '漸増': 797, '体位': 798, 'ガンシクロビル': 799, '入部': 800, '基底': 801, '後腹': 802, '状': 803, '構造': 804, '思考': 805, 'アレルギー': 806, '心臓': 807, '多様': 808, '卵巣': 809, '支持': 810, '塞': 811, '不振': 812, '主要': 813, '破壊': 814, '拡張': 815, 'sof': 816, '結節': 817, '虫': 818, '歩行': 819, '前腕': 820, '表皮': 821, '開始': 822, '頸部痛': 823, '右': 824, '顕': 825, '線': 826, 'ド': 827, 'チェックポイント': 828, '9': 829, '心筋梗塞': 830, '脳卒中': 831, '耳鼻咽喉科': 832, '改善': 833, '2012': 834, '細菌': 835, '妊娠': 836, '便': 837, '特発': 838, '練習': 839, '作業': 840, '住宅': 841, '実施': 842, '表': 843, 'っ': 844, '掻痒': 845, '保持': 846, '判明': 847, '看護': 848, '網': 849, '発現': 850, 'nitroglycerin': 851, '胸部': 852, '眼瞼': 853, '蓋': 854, '受診': 855, '胃潰瘍': 856, '率': 857, '職員': 858, '糖尿': 859, '萎縮': 860, '嚥下': 861, '2010': 862, '典型': 863, '褥': 864, '増悪': 865, '虫垂': 866, '発': 867, '追加': 868, '路': 869, '短絡': 870, '1998': 871, '1982': 872, '薬': 873, '車': 874, '業務': 875, '肺炎': 876, '結膜炎': 877, '師': 878, '1986': 879, '硬化': 880, '48': 881, '禁忌': 882, 'アルコール': 883, '鼻炎': 884, '立ち': 885, '誘発': 886, '28': 887, '部': 888, '斑': 889, '二': 890, '心理': 891, '血管': 892, '髄': 893, '拍': 894, '円筒': 895, '抗': 896, '下痢': 897, 'brto': 898, 'ヘルニア': 899, '解離': 900, '胃腸': 901, '軽減': 902, 'パーキンソン': 903, '腎臓': 904, '潰瘍': 905, '5': 906, '腫脹': 907, '大殿': 908, 'bevacizumab': 909, '治癒': 910, 'メタリソクステント': 911, '義歯': 912, '固形': 913, '寒冷': 914, '体重': 915, 'ards': 916, '再現': 917, '出': 918, '消化': 919, '会': 920, '端座': 921, 'インタビュー': 922, '加療': 923, '目': 924, '虫垂炎': 925, '緊張': 926, 'ウイルス': 927, '代謝': 928, '昏睡': 929, '車いす': 930, '抑制': 931, '18': 932, '復帰': 933, '筋肉': 934, '退': 935, '感': 936, '同時': 937, '31': 938, '脳': 939, '洞': 940, '基本': 941, '液': 942, '悪性': 943, '症候群': 944, '麻痺': 945, '効果': 946, '確認': 947, '注': 948, '動脈': 949, '量': 950, 'ヵ月': 951, '滲出': 952, '半': 953, '症例': 954, '屈筋': 955, '紫': 956, '癒着': 957, '仙': 958, '葦': 959, '癖': 960, '半年': 961, '43': 962, '沈下': 963, 'リハ': 964, '早期': 965, '脾腎': 966, '増殖': 967, '時': 968, '眼科': 969, 'dds': 970, '装具': 971, '行動': 972, '伝染': 973, '整形': 974, '液体': 975, 'mcfg': 976, 'アシドーシス': 977, '湯葉': 978, '運動': 979, '頭': 980, '分': 981, '性': 982, '徒手': 983, '有害': 984, 'チガソン': 985, '11': 986, '窩織炎': 987, '児': 988, '症状': 989, '不整脈': 990, '含有': 991, 'inh': 992, '甲': 993, '心': 994, '103': 995, '以上': 996, 'インフルエンザ': 997, '葉': 998, 'ici': 999, 'ヒラメ': 1000, '液状': 1001, '顔貌': 1002, '本': 1003, '気管支': 1004, '乳白色': 1005, 'uva': 1006, '術後': 1007, '抗体': 1008, '角': 1009, '隆起': 1010, 'acp': 1011, 'kogoj': 1012, '併設': 1013, '挿入': 1014, '上殿': 1015, '作用': 1016, '日間': 1017, '形': 1018, '療養': 1019, 'b': 1020, '転院': 1021, '試験': 1022, '光': 1023, '身体': 1024, 'vp': 1025, '通所': 1026, '250': 1027, '血圧': 1028, '休': 1029, '潜': 1030, '喘息': 1031, '状態': 1032, 'プロメタジン': 1033, 'ポート': 1034, '縮小': 1035, '義足': 1036, '検索': 1037, '電気': 1038, '胃癌': 1039, '膵炎': 1040, '喉頭': 1041, '確保': 1042, '外用': 1043, '全': 1044, '違和感': 1045, '冠': 1046, '混合': 1047, '士': 1048, '顔面': 1049, '1999': 1050, '遺伝子': 1051, 'icu': 1052, '温熱': 1053, '先': 1054, '皮膚': 1055, '腸管': 1056, '時点': 1057, '調': 1058, 'vater': 1059, 'ファクター': 1060, 'psa': 1061, '測定': 1062, '様': 1063, '人工': 1064, 'dose': 1065, '獲得': 1066, '像': 1067, '股関節': 1068, '食道': 1069, '30': 1070, 'コントロール': 1071, 'pph': 1072, '以降': 1073, '転': 1074, '補': 1075, '2013': 1076, 'ホーム': 1077, '延長': 1078, '製剤': 1079, 'サルコイドーシス': 1080, '関連': 1081, 'インターベンション': 1082, '内科': 1083, '骨': 1084, '棟': 1085, '体温': 1086, '落屑性': 1087, '分化': 1088, '自覚': 1089, 'sle': 1090, '癬': 1091, '機能': 1092, '切断': 1093, '聴取': 1094, '外来': 1095, '乳房': 1096, '採石': 1097, '69': 1098, '塩酸': 1099, '投与': 1100, 'プレガバリン': 1101, '物理': 1102, '小脳': 1103, '菌': 1104, '線維': 1105, '発熱': 1106, 'サラゾビリン': 1107, '血球': 1108, '方形': 1109, '脾腫': 1110, '再建': 1111, '硬直': 1112, '膿': 1113, 'カタル': 1114, '切除': 1115, '張力': 1116, '術中': 1117, '治療': 1118, '呼吸': 1119, '健康': 1120, '昇降': 1121, '酸': 1122, '範囲': 1123, '設定': 1124, '気道': 1125, '変更': 1126, '知識': 1127, '源': 1128, '食事': 1129, '眼球': 1130, 'pd': 1131, '米': 1132, '院': 1133, '10': 1134, '淡紅': 1135, '先天的': 1136, '帽': 1137, '膜': 1138, '攣縮性': 1139, '正常': 1140, '反復': 1141, '画像': 1142, '上昇': 1143, '壊死': 1144, 'bph': 1145, '進行': 1146, '腹': 1147, 'モチベーション': 1148, '設計': 1149, 'ecmo': 1150, '総': 1151, '肥大': 1152, '除去': 1153, 'cabg': 1154, '加': 1155, '尖': 1156, '拡大': 1157, '事象': 1158, 'デュルバルマブ': 1159, '上皮': 1160, '観察': 1161, '49': 1162, 'ステント': 1163, '交通': 1164, 'ms': 1165, '消失': 1166, '位': 1167, '53': 1168, 'アドレナリン': 1169, '喘鳴': 1170, '活動': 1171, '疹': 1172, '手術': 1173, 'バイタル': 1174, '脂質': 1175, '腸': 1176, '小腸': 1177, '検討': 1178, '壁': 1179, '苔': 1180, '絞': 1181, '円錐': 1182, '環境': 1183, '気管支炎': 1184, 'びまん': 1185, '転位': 1186, '再発': 1187, '学園': 1188, '内服': 1189, '走行': 1190, '共有': 1191, '直後': 1192, '緊満性': 1193, '靱帯': 1194, '胆汁': 1195, '腰痛': 1196, 'nivolumab': 1197, '市原': 1198, '幽門': 1199, 'リスク': 1200, 'bd': 1201, '服用': 1202, '環': 1203, '瘙痒性': 1204, '黄疸': 1205, '降下': 1206, '体液': 1207, '瘡': 1208, '前額': 1209, '筋腫': 1210, 'アリ': 1211, '排泄': 1212, '咽喉': 1213, '施行': 1214, '異': 1215, 'ドレナージ': 1216, 'アドヒアランス': 1217, '96': 1218, '1': 1219, '壊疽': 1220, '2': 1221, '不全': 1222, '黄色': 1223, '天': 1224, '膵頭後': 1225, '浮動': 1226, '座': 1227, '家族': 1228, '泌尿器': 1229, '入所': 1230, '胸腺': 1231, '有意': 1232, '対象': 1233, '向上': 1234, '凍瘡': 1235, '頬': 1236, '軸': 1237, '弁': 1238, '非': 1239, '赤褐色': 1240, '有機': 1241, 'cfs': 1242, 'rom': 1243, 'プレドニン': 1244, '結腸': 1245, '下腿': 1246, '鼻': 1247, '負荷': 1248, '-': 1249, 'xeloda': 1250, '導入': 1251, '出血': 1252, '疼痛': 1253, '変形': 1254, '下部': 1255, '2005': 1256, '異常': 1257, '時間': 1258, '増強': 1259, '造影': 1260, '21': 1261, '理学': 1262, '肝臓': 1263, '水泡': 1264, '洗浄': 1265, '監視': 1266, 'cf': 1267, '創': 1268, '泡沫': 1269, '結膜': 1270, '薬物': 1271, '胸膜': 1272, '捻転': 1273, 'radiation': 1274, '乳腺': 1275, 'svr': 1276, '原発': 1277, '背部': 1278, '血液': 1279, '全身': 1280, '中葉': 1281, '1991': 1282, '独歩': 1283, '毛細血管': 1284, '7': 1285, '核': 1286, '摘術': 1287, '知': 1288, 'tur': 1289, '紹介': 1290, '大': 1291, '年齢': 1292, 'braf': 1293, '24': 1294, '柔軟': 1295, '外科': 1296, '塞栓症': 1297, '肝不全': 1298, 's': 1299, '巨大': 1300, '腋窩': 1301, '剤': 1302, '痙性四': 1303, '開張': 1304, '1993': 1305, '脳症': 1306, '身性': 1307, '患者': 1308, '下': 1309, '駆除': 1310, '脱落': 1311, '操作': 1312, '拘束': 1313, '白血球': 1314, '内圧': 1315, '週間': 1316, '下腹': 1317, '感染': 1318, 'チタン': 1319, 'bwstt': 1320, '連続': 1321, '唾液': 1322, '自己': 1323, '判定': 1324, '術': 1325, '血糖': 1326, '肺癌': 1327, '鱗屑': 1328, '変化': 1329, '療法': 1330, '宣言': 1331, '跳痛': 1332, 'ラ': 1333, '炎症': 1334, '力': 1335, '失調': 1336, '肺門': 1337, 'ローション': 1338, '四つ': 1339, '27': 1340, '感受性': 1341, '窓': 1342, '肉芽': 1343, 'ヶ月': 1344, '凝固': 1345, 'gp': 1346, '膀胱': 1347, 'リン': 1348, 'ポリオ': 1349, '変性': 1350, '塞栓療': 1351, '両足': 1352, 'プロ': 1353, 'pet': 1354, '坐': 1355, '1994': 1356, '受傷': 1357, '癌': 1358, '低': 1359, '超': 1360, '環状': 1361, '上肢': 1362, '障害': 1363, '医師': 1364, '散在': 1365, '外': 1366, 'bt': 1367, '乗車': 1368, '離脱': 1369, '教育': 1370, '疱瘡': 1371, '海綿': 1372, 'ミナルフェン': 1373, '破局': 1374, 'ヘルペス': 1375, '脈': 1376, '循環': 1377, '欠損': 1378, 'psl': 1379, '胸骨': 1380, '色素': 1381, '小': 1382, '憩': 1383, '滅': 1384, '分娩': 1385, '-PAD-': 0, '-OOV-': 1}


# データのID化
test_sentences_X = []

for s in test_sentences:
    s_int = []
    for w in s:
        try:
            s_int.append(word2index[w.lower()])
        except KeyError:
            s_int.append(word2index['-OOV-'])

    test_sentences_X.append(s_int)

MAX_LENGTH = 20
# pad_sequencesで配列のサイズを一致させる
from keras.preprocessing.sequence import pad_sequences
test_sentences_X = pad_sequences(test_sentences_X, maxlen=MAX_LENGTH, padding='post')


#sequenceをone-hotベクトルにする
def to_categorical(sequences, categories):
    cat_sequences = []
    for s in sequences:
        cats = []
        for item in s:
            cats.append(np.zeros(categories))
            cats[-1][item] = 1.0
        cat_sequences.append(cats)
    return np.array(cat_sequences)

test_samples_X = []
for line in lines:
    ln = line.strip() # \nを削除
    l = ln.split('\t') # タブの箇所で区切ってリストにする
    tlist = l[1].split() # 「GIS 所見」を['GIS','所見']にする
    s_int = []
    for sen in tlist:
        try:
            s_int.append(word2index[sen.lower()])
        except KeyError:
            s_int.append(word2index['-OOV-'])
    test_samples_X.append(s_int)

test_samples_X = pad_sequences(test_samples_X, maxlen=MAX_LENGTH, padding='post')
predictions = model.predict(test_samples_X)

def logits_to_tokens(sequences, index):
    token_sequences = []
    for categorical_sequence in sequences:
        token_sequence = []
        for categorical in categorical_sequence:
            token_sequence.append(index[np.argmax(categorical)])
        token_sequences.append(token_sequence)
    return token_sequences

tags = logits_to_tokens(predictions, {i: t for t, i in tag2index.items()})

f = open('cw_tag.txt', 'w')
pair = []
for (s, out) in zip(surfs, tags):
    tag = [t for t in out if t != '-PAD-']
    tag = " ".join(tag)
    f.write(s + "," + tag + "\n")
    print(s + "," + tag)

f.close()
