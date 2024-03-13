from thefuzz import fuzz
from thefuzz import process

# 待搜索的列表
fruits = ['apple', 'banana', 'cherry', 'date', 'bb', 'baban', 'elderberry', 'M 103|NGC 581|OCl 326', 'M 110|NGC 205|UGC 426|PGC 2429|MCG+07-02-014']

# 要搜索的字符串
search_term = 'M1'


# 找到最相似的字符串
# best_match = process.extractOne(search_term, fruits)
best_match = process.extractBests(search_term, fruits)
print(f"The best match is {best_match}")
print(f"The best match is {len(best_match)}")
print(f"The best match is {best_match[0]}")
