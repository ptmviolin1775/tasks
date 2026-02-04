## WORKING WITH SAMPLE DISTRIBUTIONS OF SAMPLE PROPORTION

##  ASSUME A POPULATION WITH P(SUCCESS) = .12.  THIS PROGRAM SHOWS THAT IN ORDER FOR A SOMEWHAT NORMAL DISTRIBUTION
##  FOR THE SAMPLE DISTRIBUTION OF THE SAMPLE PROPORTIONS, THE FOLLOWING CONDITIONS NEED TO BE TRUE:
##  1) N*P >= 10
##  2) N * (1-P) >= 10
##  WHERE:
##  N = SAMPLE SIZE AND P = PROBABILITY OF SUCCESS


import matplotlib.pyplot as plt
import random as r

x = ['S'] * 12 + ['F'] * 88

sample_size = [15,25,50,75,100,200,300,500]

for sam_sz in sample_size:
    trials = []
    for y in range(50000):
        temp_li=[]
        for xx in range(sam_sz):
            temp_li.append(x[r.randint(0,99)])
        trials.append(temp_li)

    success_li = []

    for num in range(50000):
        # print(f'TRIAL {x}:')
        # print(f'P(FAIL): {len([i for i in trials[x] if i=='F'])/len(trials[x])}')
        # print(f'P(SUCCESS): {len([i for i in trials[x] if i=='S'])/len(trials[x])}\n')
        success_li.append(len([i for i in trials[num] if i=='S'])/len(trials[num]))
        
    success_dict = {}

    for n in success_li:
        try:
            success_dict[n] += 1
        except:
            success_dict[n] = 1

    success_dict = dict(sorted(success_dict.items()))

    ###  PLOT
    xvals=success_dict.keys()
    yvals=success_dict.values()
    plt.plot(xvals,yvals,marker='o',label=sam_sz)

plt.legend()
plt.show()
