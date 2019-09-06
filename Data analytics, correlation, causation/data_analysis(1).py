import re
from datetime import date
import numpy as np
import matplotlib.pyplot as plt

filename="tods_label.csv"
with open(filename,"r",encoding="utf-8") as file_data:
    file_data.readline()
    lines=file_data.readlines()
    f=open("new_"+filename,"w",encoding="utf-8")
    for line in lines:
        if not line[0]==",":
            f.write(line[:-1])
        else:
            f.write(line)
f.close()
rematches=[r"(\d{4}-\d{1,2}-\d{1,2})",
            r"(\d{4}年\d{1,2}月\d{1,2}日)",
            r"(\d{4}/\d{1,2}/\d{1,2})"]
positiveCount=np.zeros((10*12))
negtiveCount=np.zeros((10*12))
neutralCount=np.zeros((10*12))
minyear=3000
with open("new_"+filename,"r",encoding="utf-8") as raw_file:
    lines=raw_file.readlines()
    countFoundDate=0
    for line in lines:
        line=line.split(",")
        foundDate=0
        year,month,day=0,0,0
        for rematch in rematches:
            rawDate=re.search(rematch,line[1])
            if not rawDate==None:
                newDate=rawDate[0]
                newDate=newDate.replace("年","-")
                newDate=newDate.replace("月","-")
                newDate=newDate.replace("日","-")
                newDate=newDate.replace(r"/","-")
                newDate=newDate.split("-")
                year,month,day=eval(newDate[0]),eval(newDate[1].lstrip("0")),eval(newDate[2].lstrip("0"))
                foundDate=1
                break
        if foundDate:
            if line[3] == "0":
                negtiveCount[(year - 2010) * 12 + month - 1] += 1
            if line[3] == "1":
                neutralCount[(year - 2010) * 12 + month - 1] += 1
            elif line[3] == "2":
                positiveCount[(year - 2010) * 12 + month - 1] += 1
        countFoundDate+=foundDate
    print("total entrys {},success found date {}".format(len(lines),countFoundDate))

    figsize = 11, 9
    figure, ax = plt.subplots(figsize=figsize)


    plt.title("Sentiment Classification Results for Tods", fontsize=18)
    plt.xlabel("Time",fontsize=11)
    plt.ylabel("Amount of Labels",fontsize=11)
    start=0
    for i in range(120):
        if negtiveCount[i]>0 and positiveCount[i]>0 and neutralCount[i]>0:
            start=i
            break
    xticks=[]
    for i in range(start,120):
        if i%10==0:
            xticks.append("{}-{}".format(2010+i//12,i%12))
    plt.xticks(range(0,120-start,3),xticks)
    plt.plot(negtiveCount[start:],  label = 'Negtive Count')
    plt.plot(positiveCount[start:], label = 'Positive Count')
    plt.plot(neutralCount[start:], label='Neutral Count')
    plt.legend(loc='upper right', fontsize=11)

    negtiveCount=negtiveCount/np.max(negtiveCount[start:])
    positiveCount=positiveCount/np.max(positiveCount[start:])
    neutralCount=neutralCount/np.max(neutralCount[start:])


    plt.show()

        


