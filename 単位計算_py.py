#!/usr/bin/env python
# coding: utf-8

# In[5]:


import re
import pandas as pd
from pandas import MultiIndex
from bs4 import BeautifulSoup

html = input()
print("{0}{1}{0}".format('\n'*5, '~'*70))
output_df_format = {'必要単位詳細': {('1. 総合教育科目', 20, 'Ⅰ系'): 6.0,
                                                                  ('1. 総合教育科目', 20, 'Ⅱ系'): 10.0,
                                                                  ('1. 総合教育科目', 20, 'Ⅲ系'): '',
                                                                  ('2. 基礎教育科目', 8, '必修'): 8.0,
                                                                  ('2. 基礎教育科目', 8, '選択'): '',
                                                                  ('3. 外国語科目', 14, '必修'): 8.0,
                                                                  ('3. 外国語科目', 14, '選択必修'): 6.0,
                                                                  ('3. 外国語科目', 14, '選択'): '',
                                                                  ('4. 専門教育科目', 68, '基礎'): 16.0,
                                                                  ('4. 専門教育科目', 68, '基本'): 12.0,
                                                                  ('4. 専門教育科目', 68, '特殊及び関連'): '',
                                                                  ('5. 自主選択科目', ' ', '選択'): '',
                                                                  ('6. 合計', 126, ' '): ''},
                                     '自分': {('1. 総合教育科目', 20, 'Ⅰ系'): '',
                                                  ('1. 総合教育科目', 20, 'Ⅱ系'): '',
                                                  ('1. 総合教育科目', 20, 'Ⅲ系'): '',
                                                  ('2. 基礎教育科目', 8, '必修'): '',
                                                  ('2. 基礎教育科目', 8, '選択'): '',
                                                  ('3. 外国語科目', 14, '必修'): '',
                                                  ('3. 外国語科目', 14, '選択必修'): '',
                                                  ('3. 外国語科目', 14, '選択'): '',
                                                  ('4. 専門教育科目', 68, '基礎'): '',
                                                  ('4. 専門教育科目', 68, '基本'): '',
                                                  ('4. 専門教育科目', 68, '特殊及び関連'): '',
                                                  ('5. 自主選択科目', ' ', '選択'): '',
                                                  ('6. 合計', 126, ' '): 0.0}}

output_df_multiIndex = MultiIndex(levels=[['1. 総合教育科目', '2. 基礎教育科目', '3. 外国語科目', '4. 専門教育科目', '5. 自主選択科目', '6. 合計'], [8, 14, 20, 68, 126, ' '], [' ', 'Ⅰ系', 'Ⅱ系', 'Ⅲ系', '基本', '基礎', '必修', '特殊及び関連', '選択', '選択必修']],
           codes=[[0, 0, 0, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5], [2, 2, 2, 0, 0, 1, 1, 1, 3, 3, 3, 5, 4], [1, 2, 3, 6, 8, 6, 9, 8, 5, 4, 7, 8, 0]],
           names=['科目', '卒業必要単位', '詳細科目'])

output_df = pd.DataFrame(output_df_format).reindex(output_df_multiIndex)

soup = BeautifulSoup(html)
main_table = soup.find('form').find('table', class_ = 'main').find('tbody')

all_data = []
for tr in main_table.find_all('tr'):
    type_ = tr['class'][0]
    if type_ == 'field':
        current_key = re.findall('\d{2}-\d{2}-\d{2}', tr.text)[0]
        
    elif type_ == 'subject':
        temp_info = tr.find_all('td')
        
        class_name = temp_info[0].text
        prof_name = temp_info[1].text
        evaluation = temp_info[2].text
        n_credits = int(float(temp_info[3].text))
        year = temp_info[5].text
        semester =temp_info[6].text
        grade = temp_info[7].text
        
        all_data.append({'分野': current_key,
                                     '授業名': class_name,
                                     '教授名': prof_name,
                                     '評価': evaluation,
                                     '単位数':n_credits,
                                     '取得年': year,
                                     '学期':semester,
                                     '取得学年': grade})

df = pd.DataFrame(all_data, columns = ['分野','授業名','教授名','評価','単位数','取得年','学期','取得学年'])

def credits_sum(df):
    return df.query("評価 in ['Ｓ', 'Ｂ', 'Ａ', 'Ｃ']").sum().単位数

def show_overall(df):
    print('{概要}')
    #通算単位取得数、3学期前期取得数   
    credits_so_far = credits_sum(df)
    spring_semester = credits_sum(df.query('取得学年 == "3年"', engine='python'))
    print('\t通算単位取得数: {}'.format(credits_so_far))
    print('\t\t3年前期取得単位数: {}'.format(spring_semester))
    print('\t' + '='*70)
    
    #3年終了時取得単位予定数
    fall_semester = df.query('取得学年 == "3年"', engine='python').query('学期 == "秋"').sum().単位数 
    print('\t3年終了時取得単位予定数: {}'.format(credits_so_far + fall_semester))
    print('\t\t3年後期単位取得予定数:{}'.format(fall_semester))

def pass_check(df):
    print('{進級条件チェック}')
    #1-1. 基礎教育科目8単位
    basics_credits = credits_sum(df.query('分野.str.match("20-.*")', engine='python').query("評価 in ['Ｓ', 'Ｂ', 'Ａ', 'Ｃ']"))
    print('\t1-1. 基礎教育科目8単位: ', end='')
    print('○') if basics_credits >= 8 else print('×')
    
    #1-2. 専門教育科目の基本科目16単位
    specialized_credits = credits_sum(df.query('分野.str.match("40-1.*|40-20.*|40-21.*")', engine='python'))
    print('\t1-2. 専門教育科目の基礎科目16単位: ', end='')
    print('○') if specialized_credits >= 16 else print('×')
        
    #2-1. 第三学年において、履修上限の範囲内で履修した科目のうち28単位の取得
    third_grade_credits = credits_sum(df.query('取得学年 == "3年"', engine='python'))
    print('\t2-1. 第三学年において、履修上限の範囲内で履修した科目のうち28単位の取得:', end='')
    if third_grade_credits >= 28:
        print('○')
    else:
        print('×')
        print('\t\t{}単位足りていません'.format(28-third_grade_credits))  

def graduation_check(df, output_df):
    print('{卒業条件チェック}')
    #---------------------------総合教育科目------------------------------------------------------------------------------------#
    general_1 = credits_sum(df.query('分野.str.match("10-21.*")', engine='python'))
    general_2 =  credits_sum(df.query('分野.str.match("10-22.*")', engine='python'))
    general_3 = credits_sum(df.query('分野.str.match("10-23.*")', engine='python'))
    general_sum = general_1 + general_2 + general_3
    
    print('\t<総合教育科目>')
    if general_1 < 6: print('\t\t総合教育科目Ⅰ系が{}単位足りていません'.format(6 - general_1))
    if general_2 < 10: print('\t\t総合教育科目Ⅱ系が{}単位足りていません'.format(10 - general_2))
    if general_sum < 20: print('\t\t総合教育科目全体が{}単位足りていません'.format(20 - general_sum))

    #---------------------------基礎教育科目------------------------------------------------------------------------------------#    
    stat_1 = credits_sum(df.query('分野 == "20-10-01"'))
    stat_2 = credits_sum(df.query('分野 == "20-10-02"'))
    basic_must_each = credits_sum(df.query('分野.str.match("20-1.*")', engine='python').query('分野 != "20-10-01"').query('分野 != "20-10-02"'))
    basic_opt = credits_sum(df.query('分野.str.match("20-3.*")', engine='python'))
    basic_sum = sum([stat_1,stat_2, basic_must_each, basic_opt])

    print('\t<基礎教育科目>')
    if stat_1 < 2: print('\t\t統計学Ⅰが足りていません')
    if stat_2 < 2: print('\t\t統計学Ⅱが足りていません')
    if basic_must_each < 4: print('\t\tタイプ別の必修科目(微分積分、線形代数、日本経済概論、歴史的経済分析の視点)のいずれかが{}単位足りていません'.format(4 - basic_must_each))
    if basic_sum < 8: print('\t\t基礎教育科目が{}単位足りていません'.format(8 - basic_sum))
        
        
    #---------------------------外国語科目------------------------------------------------------------------------------------#
    foreign_lang_must_1 = credits_sum(df.query('分野 == "30-10-01"'))
    foreign_lang_must_2 = credits_sum(df.query('分野.str.match("30-10-0.*")', engine='python').query('分野 != "30-10-01"'))
        
    foreign_lang_opt_must_1 =  credits_sum(df.query('分野 == "30-20-01"'))
    foreign_lang_opt_must_2 = credits_sum(df.query('分野.str.match("30-2.*")', engine='python').query('分野 != "30-20-01"'))
    foreign_lang_opt_sum = sum([foreign_lang_opt_must_1, foreign_lang_opt_must_2]) 
    
    foreign_lang_opt = credits_sum(df.query('分野.str.match("30-30.*")', engine='python'))    
    foreign_lang_sum = sum([foreign_lang_must_1,foreign_lang_must_2,foreign_lang_opt_sum, foreign_lang_opt])
    
    
    print('\t<外国語科目>')
    if foreign_lang_must_1< 2: print('\t\tStudy Skillsの単位が足りていません')
    if foreign_lang_must_2 < 6:print('\t\t第二外国語科目の必修単位が{}足りていません'.format(6 - foreign_lang_opt_must_2))
        
    if foreign_lang_opt_must_1 < 2: print('\t\t英語セミナーもしくは英語リーディングの単位が足りていません')
    if foreign_lang_opt_must_2 < 2: print('\t\t第二外国語科目の選択必修単位が足りていません')
    if foreign_lang_opt_sum < 6: print('\t\t外国語科目の選択必修が{}単位足りていません'.format(6 - foreign_lang_opt_sum)) 
        
    if foreign_lang_sum < 14: print('\t\t外国語科目が{}単位足りていません'.format(14 - foreign_lang_sum))
    
    #---------------------------専門教育科目------------------------------------------------------------------------------------# 
                #----------------------------------------基礎科目_代入---------------------------------------------------------------------------------# 
    macro_1 = credits_sum(df.query('分野 == "40-11-03"'))
    macro_2 = credits_sum(df.query('分野 == "40-11-04"'))
    micro_1 = credits_sum(df.query('分野 == "40-12-01" or 分野 =="40-13-1"'))
    micro_2 = credits_sum(df.query('分野 == "40-12-02" or 分野 == "40-13-02"'))
    zaishi = credits_sum(df.query('分野 == "40-12-03" or 分野 == "40-12-04" or 分野 == "40-13-03" or 分野 == "40-13-04"'))
    specialized_opt_must = credits_sum(df.query('分野 == "40-20-01" or 分野 == "40-21-01"'))
    
    specialized_basic_SUM = sum([macro_1,macro_2, micro_1,micro_2, zaishi, specialized_opt_must])
        
                #----------------------------------------基本科目_代入---------------------------------------------------------------------------------# 
    kihon_df = df.query('分野.str.match("40-22.*")', engine='python').query("評価 in ['Ｓ', 'Ｂ', 'Ａ', 'Ｃ']").loc[:,['分野', '単位数']]
    kihon_df = kihon_df.set_index('分野')
    kihon_bools = [True if n >= 4 else False for n in kihon_df.groupby('分野').sum().単位数.values]
    
                #---------------------------特殊科目及び関連科目_代入-------------------------------------------------------------------------------------#
    specialized_and_related = credits_sum(df.query('分野.str.match("40-3.*")', engine='python'))
                #---------------------------総合_代入-------------------------------------------------------------------------------------#
    specialized_SUM = sum([specialized_basic_SUM, kihon_df.sum().単位数, specialized_and_related])
    
    
    #----------------------------------------専門教育科目_出力---------------------------------------------------------------------------------# 
    print('\t<専門教育科目>')
    if specialized_SUM < 68:
        print('\t\t[専門教育科目が{}単位足りていません]'.format(68 - specialized_SUM))
    
    if macro_1 < 2: print('\t\t\tマクロ経済学初級Ⅰの単位が足りていません')
    if macro_2 < 2: print('\t\t\tマクロ経済学初級Ⅱの単位が足りていません')
    if micro_1 < 2: print('\t\t\tミクロ経済学初級Ⅰの単位が足りていません')
    if micro_2 < 2: print('\t\t\tミクロ経済学初級Ⅱの単位が足りていません')
    if zaishi < 4:print('\t\t\t経済史が{}単位足りていません'.format(4 - zaishi))
        
    if kihon_bools.count(True) < 3:
        print('\t\t\t専門教育科目の基本科目における1分野4単位以上×3分野が{}分野足りていません'.format(3 - kihon_bools.count(True)))

    #---------------------------自主選択科目------------------------------------------------------------------------------------# 
    self_1 = min(3,credits_sum(df.query('分野 == "50-30-01" or 分野 == "50-31-01"')))
    self_2 = min(2,credits_sum(df.query('分野 == "50-32-01" or 分野 == "50-32-02"')))
    self_3 = credits_sum(df.query('分野 == "50-50-01"'))
    
    #----------------------------全体------------------------------------------------------------------------------------------------------------------#
    print('\t<全体>')
    credits_so_far = credits_sum(df)
    fall_semester = df.query('取得学年 == "3年"', engine='python').query('学期 == "秋"').sum().単位数
    sum_ = credits_so_far + fall_semester
    if sum_  >= 126:
        print('\t\t卒業必要単位数を取得しています')
    else:
        print('\t\tこの履修予定だと卒業まで{}単位足りていません'.format(126 - sum_))

        
        
    #------------------------------データフレームの作成-----------------------------------------------------------------------------------------------------------------#
    output_df.loc[('1. 総合教育科目',20, 'Ⅰ系'), ['自分']] = general_1
    output_df.loc[('1. 総合教育科目',20, 'Ⅱ系'), ['自分']] = general_2
    output_df.loc[('1. 総合教育科目',20, 'Ⅲ系'), ['自分']] = general_3
    
    output_df.loc[('2. 基礎教育科目',8, '必修'), ['自分']] = sum([stat_1, stat_2, basic_must_each])
    output_df.loc[('2. 基礎教育科目',8, '選択'), ['自分']] = basic_opt
    
    output_df.loc[('3. 外国語科目',14, '必修'), ['自分']] = sum([foreign_lang_must_1, foreign_lang_must_2])
    output_df.loc[('3. 外国語科目',14, '選択必修'), ['自分']] = foreign_lang_opt_sum
    output_df.loc[('3. 外国語科目',14, '選択'), ['自分']] = foreign_lang_opt
    
    output_df.loc[('4. 専門教育科目',68, '基礎'), ['自分']] = specialized_basic_SUM
    output_df.loc[('4. 専門教育科目',68, '基本'), ['自分']] = kihon_df.sum().単位数
    output_df.loc[('4. 専門教育科目',68, '特殊及び関連'), ['自分']] = specialized_and_related
    output_df.loc[('5. 自主選択科目'," ", '選択'), ['自分']]  = min(sum([self_1,self_2,self_3]),4)
    
    output_df.loc[('6. 合計',126, ' '), ['自分']] = output_df.自分.sum()
    
    display(output_df)    
    print('\n\t*通算取得単位から出力してるため、3年後期の単位は未計上')

show_overall(df)
pass_check(df)
graduation_check(df, output_df)


# In[ ]:




