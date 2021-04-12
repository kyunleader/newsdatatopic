# 뉴스데이터 토픽 모델링 해보기

import pandas as pd

data = pd.read_excel('data.xlsx', index_col = False)

# 필요없는 칼럼 제거
del data['Unnamed: 0']
del data['words']; del data['length_word']  # 필요하나 복습을 위해 제거

# 본문 전처리
data = data.drop_duplicates()  # 중복제거
data = data[data['text'] != 0]  # 0인 값 제거

# 본문 형태소 분석
from tqdm import tqdm
from konlpy.tag import Okt
okt = Okt()


# 형태소 분석
list_text = data['text']

words = [okt.nouns(i) for i in tqdm(list(list_text))]  # 행별로 형태소 분석

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
    plt.subplot(6, 1, i+1)  # 그래프 나눠 그리기 준비
    #  Counter 함수로 단어 빈도수 세기
    label = dict(Counter(result).most_common(20)).keys()
    values = dict(Counter(result).most_common(20)).values()
    # Basic Bar Chart
    plt.bar(label, values, color='green', width= 0.5)
    plt.xticks(fontsize=7)
    plt.yticks(fontsize=5)
    plt.ylabel("{}월".format(i+3))




