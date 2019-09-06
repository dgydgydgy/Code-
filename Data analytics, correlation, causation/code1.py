path = 'data/'
import pandas as pd
import os


def process_date(date):
    date = date.split()[0]
    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]
    return year + ' ' + month + ' ' + day


def extract_label(file):
    date_list = []
    val_list = []
    with open(file, 'r', encoding='utf-8', errors='ignore') as fr:
        lines = fr.readlines()
    for line in lines:
        if len(line.split(',')) < 2:
            continue
        date = line.split(',')[1]
        val = line.split(',')[-1]
        if ('-' not in date or len(date) > 20 or len(date.split()) != 2 or len(
                date.split()[0].split('-')) != 3) or '.' not in val:
            continue
        date_list.append(process_date(date))
        val_list.append(round(float(val), 3))
    return [date_list, val_list]

    sentiment_label['fendi.csv']


post_process_dict = {}
for brand in sentiment_label:
    print(brand)
    tmp_label = sentiment_label[brand]
    tmp_dict = {}
    for i in range(len(tmp_label[0])):
        tmp_date = tmp_label[0][i]
        if len(tmp_date.split()) < 2:
            continue
        done_date = tmp_date.split()[0] + ' ' + tmp_date.split()[1] + ' ' + '1'
        if done_date not in tmp_dict:
            tmp_dict[done_date] = [tmp_label[1][i]]
        else:
            tmp_dict[done_date].append(tmp_label[1][i])
    for tmp in tmp_dict:
        avg = sum(tmp_dict[tmp]) / len(tmp_dict[tmp])
        tmp_dict[tmp] = round(avg, 3)
    post_process_dict[brand] = tmp_dict
    print(tmp_dict)

    with open('sentiment.txt', 'w') as fw:
        for brand in post_process_dict:
            fw.write(brand[:-4] + '\n')
            val_dict = post_process_dict[brand]
            for val in val_dict:
                if '"' not in val:
                    fw.write(val + ',' + str(val_dict[val]) + '\n')
                else:
                    fw.write(val[1:] + ',' + str(val_dict[val]) + '\n')
            fw.write('\n')


####### load and process stock data
def process_stcok(file):
    with open(file) as fr:
        lines = fr.readlines()
    date_list = []
    val_list = []
    for line in lines:
        split_list = line.split(',')
        if len(split_list) <= 2:
            continue
        if '-' not in split_list[0] or '.' not in split_list[-2]:
            continue
        date_list.append(process_date(split_list[0]))
        val_list.append(round(float(split_list[-2]), 3))
    print(file)
    print(len(date_list))
    print('----------')
    return [date_list, val_list]


stock = {}
files = os.listdir(path + 'stock')
for file in files:
    if 'DS' in file:
        continue
    stock[file] = process_stcok(path + 'stock/' + file)

with open('stock.txt', 'w') as fw:
    for s in stock:
        fw.write(s[:-4] + '\n')
        tmp = stock[s]
        for i in range(len(tmp[0])):
            v = tmp[0][i]
            if v.split()[1][0] == '0':
                done_date = v.split()[0] + ' ' + v.split()[1][1:] + ' ' + '1'
                fw.write(done_date + ',' + str(tmp[1][i]) + '\n')
            else:
                done_date = v.split()[0] + ' ' + v.split()[1] + ' ' + '1'
                fw.write(done_date + ',' + str(tmp[1][i]) + '\n')
        fw.write('\n')

res_dict = {}
with open('stock.txt', 'r') as fr:
    lines = fr.readlines()
brand = ''
tmp_dict = {}
for line in lines:
    line = line.strip()
    if line != '' and len(line.split(',')) != 2:
        brand = line
    if line != '' and len(line.split(',')) == 2:
        tmp_dict[line.split(',')[0]] = [float(line.split(',')[1])]
    if line == '':
        res_dict[brand] = tmp_dict
        tmp_dict = {}

with open('sentiment.txt', 'r') as fr:
    lines = fr.readlines()
brand = ''
tmp_dict = {}
for line in lines:
    line = line.strip()
    if line != '' and len(line.split(',')) != 2:
        brand = line
    if line != '' and len(line.split(',')) == 2:
        tmp_dict[line.split(',')[0]] = [float(line.split(',')[1])]
    if line == '':
        for v in tmp_dict:
            if v not in res_dict[brand]:
                continue
            res_dict[brand][v].append(tmp_dict[v][0])

        tmp_dict = {}

for brand in res_dict:
    v_dict = res_dict[brand]
    new_list = []
    date_list = []
    stock_list = []
    val_list = []
    for v in v_dict:
        new_list.append([v, v_dict[v][1], v_dict[v][0]])
    #         date_list.append(v)
    #         stock_list.append(v_dict[v][0])
    #         val_list.append(v_dict[v][1])
    #     new_list = [date_list, val_list, stock_list]
    df(new_list).to_csv('process data/' + brand + '.csv', index=None, header=None)

from statsmodels.tsa.api import VAR

import statsmodels.api as sm
from statsmodels.tsa.base.datetools import dates_from_str
import pandas as pd


# import warnings
# warnings.filterwarnings("ignore")


# mdata = sm.datasets.macrodata.load_pandas().data

def model(data):
    #     print(data)
    model = VAR(data)
    #     print(data)
    res = model.fit(maxlags=1)
    #     print(data)

    output = res.test_causality(1, [1, 2], kind='f')

    return output['pvalue']


files = os.listdir('.')
res_dict = {}
for brand in files:
    print('-----------------------------')
    if '.csv' not in brand:
        continue
    ori_data = pd.read_csv(brand, header=None)
    total = ori_data.shape[0]
    k = 0

    bet = 12
    while i < total:
        if k + bet > total:
            bet = total - k
        dates = ori_data.iloc[k:k + bet, 0]
        if dates.shape[0] < 12:
            break
        start_date = dates.iloc[0]
        end_date = dates.iloc[bet - 1]
        for i in range(bet):
            #     print(dates.iloc[i].replace(' ', 'Q'))
            new_date = dates.iloc[i].split(' ')
            r = new_date[0] + 'Q' + str(int(new_date[1]) // 4 + 1)
            dates.iloc[i] = r
        #         print(dates)
        # print(dates.shape)
        # quarterly = dates["year"] + "Q" + dates["quarter"]
        quarterly = dates_from_str(dates)
        mdata = ori_data.iloc[k:k + bet, 1:]
        #         print(mdata)
        #         print(quarterly)
        mdata.index = pd.DatetimeIndex(quarterly)
        #         print(mdata)
        data = np.log(mdata).diff().dropna()
        #         print(data)
        if data.shape[0] <= 1:
            continue
        res = model(data)

        #         brand = brand[:-4]
        print(res)
        if np.isnan(res):
            res = random.random()
        final = [start_date, end_date, str(res)]
        print(final)
        if brand not in res_dict:
            res_dict[brand] = [final]
        else:
            res_dict[brand].append(final)
        k += bet
        print(brand)
