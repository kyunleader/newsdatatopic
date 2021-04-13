# 뉴스데이터 토픽 모델링 해보기

import pandas as pd

data = pd.read_excel('data.xlsx', index_col=False)

# 필요없는 칼럼 제거
del data['Unnamed: 0']

# 본문 전처리
data = data.drop_duplicates()  # 중복제거
data = data[data['text'] != 0]  # 0인 값 제거
data['words'] = [i.replace("'", "").replace('[', '').replace(']', '').replace(' ', '').split(',') for i in
                 data['words']]  # words 가 텍스트 형식으로 되어 있을 경우

# 본문 형태소 분석
from tqdm import tqdm
from konlpy.tag import Okt

okt = Okt()

# 형태소 분석
list_text = data['text']

words = [okt.nouns(i) for i in tqdm(list(list_text))]  # 행별로 형태소 분석 약 1시간 소요

# 불용어 사전 만들기
Prohibit_words = ['기자', '연합뉴스', '뉴시스', '시사저널', '신문', '뉴스', '사진', '헤럴드경제', '노컷뉴스', '파이낸셜뉴스', '특파원',
                  '라며', '대해', '지난', '위해', '오전', '오후', '무단', '배포', '이데일리', '머니투데이', '앵커']

# 불용어 제외
j = 0
for i in tqdm(words):
    for k in Prohibit_words:
        while k in i:
            i.remove(k)
    words[j] = i
    j += 1

# 한글자 단어 제외
for k in range(len(words)):
    words[k] = [i for i in words[k] if len(i) > 1]

# 데이터 셋에 형태소 분석한 단어 추가
data['words'] = words

# 단어 갯수 칼럼 추가
data['length_word'] = [len(i) for i in tqdm(data['words'])]

## 형태소 분석 결과 살펴보기

# 월별로 구분해보기
data['month'] = [i.month for i in data['date']]

from collections import Counter
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import matplotlib

font_name = font_manager.FontProperties(fname='C:/Windows/Fonts/H2HDRM.TTF').get_name()
rc('font', family=font_name)
matplotlib.rcParams['axes.unicode_minus'] = False  # matplotlib 에 한국어 폰트 적용

plt.figure(figsize=(9, 9))
for i in range(6):
    result = []
    # 월별로 단어 모으기
    for j in data[data['month'] == i + 3]['words']:
        result.extend(j)
    plt.subplot(6, 1, i + 1)  # 그래프 나눠 그리기 준비
    #  Counter 함수로 단어 빈도수 세기
    label = dict(Counter(result).most_common(20)).keys()
    values = dict(Counter(result).most_common(20)).values()
    # Basic Bar Chart
    plt.bar(label, values, color='green', width=0.5)
    plt.xticks(fontsize=7)
    plt.yticks(fontsize=5)
    plt.ylabel("{}월".format(i + 3))

# 토픽모델링 해보기
import gensim
import gensim.corpora as corpora
from gensim.models import CoherenceModel

# 3월달만 해보기

def topic(word):
    id2word = corpora.Dictionary(word)
    texts = word
    corpus = [id2word.doc2bow(text) for text in texts]  # 단어 corpus 만들기

    # 토픽모델링 함수
    def compute_coherence_values(dictionary, corpus, texts, limit, start=2, step=3):
        coherence_values = []
        model_list = []
        for num_topics in tqdm(range(start, limit, step)):
            model = gensim.models.ldamodel.LdaModel(corpus=corpus,  # LDA 모델 활용한 토픽모델
                                                    id2word=id2word,
                                                    num_topics=num_topics,
                                                    random_state=100,
                                                    update_every=1,
                                                    chunksize=100,
                                                    passes=10,
                                                    alpha='auto',
                                                    per_word_topics=True)
            model_list.append(model)
            coherencemodel = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
            coherence_values.append(coherencemodel.get_coherence())
        return model_list, coherence_values  # 토픽모델링의 주제의 갯수에 따라 정확도 측정

    model_list, coherence_values = compute_coherence_values(dictionary=id2word, corpus=corpus, texts=texts, start=2,
                                                            limit=20, step=1)

    # Show graph 주제 갯수에 따른 정확도 그래프화
    limit = 20;
    start = 2;
    step = 1;
    x = range(start, limit, step)
    plt.plot(x, coherence_values)
    plt.xlabel("Num Topics")
    plt.ylabel("Coherence score")
    plt.legend(("coherence_values"), loc='best')
    plt.show()
    print(coherence_values.index(max(coherence_values)) + 2, '개의 주제가 이상적')

    # 가장 적합한 주제 갯수로 dataframe화 하기
    coherence_values.index(max(coherence_values))
    optimal_model = model_list[coherence_values.index(max(coherence_values))]
    topic_dic = {}
    for i in range(coherence_values.index(max(coherence_values)) + 2):
        words2 = optimal_model.show_topic(i, topn=20)
        topic_dic['topic ' + '{:02d}'.format(i + 1)] = [i[0] for i in words2]
    da = pd.DataFrame(topic_dic)
    return da

topic_result_month3 = topic(data[data['month'] == 3]['words'])
