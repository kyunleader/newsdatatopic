# 뉴스데이터 토픽 모델링 해보기

import pandas as pd

data = pd.read_excel('data.xlsx', index_col = False)

#  필요없는 칼럼 제거
del data['Unnamed: 0']
del data['words']; del data['length_word'] # 필요하나 복습을 위해 제거




