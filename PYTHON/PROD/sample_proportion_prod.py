## WORKING WITH SAMPLE DISTRIBUTIONS OF SAMPLE PROPORTION

##  ASSUME A POPULATION WITH P(SUCCESS) = .16.  THIS PROGRAM SHOWS THAT IN ORDER FOR A SOMEWHAT NORMAL DISTRIBUTION
##  FOR THE SAMPLE DISTRIBUTION OF THE SAMPLE PROPORTIONS, THE FOLLOWING CONDITIONS NEED TO BE TRUE:
##  1) N*P >= 10
##  2) N * (1-P) >= 10
##  WHERE:
##  N = SAMPLE SIZE AND P = PROBABILITY OF SUCCESS


import random as r
import matplotlib.pyplot as plt
import seaborn as sns


### FUNCTIONS
def process_sample_sizes(num_trials:int,sample_sizes:list,p_success:float):
    population:list = ['S']*int(100*p_success)+['F']*int(100-(100*p_success))
    success_lis:list = []
    for sam_sz in sample_sizes:
        success_li:list = []
        for y in range(num_trials):
            temp_li:list = []
            for xx in range(sam_sz):
                temp_li.append(population[r.randint(0,len(population)-1)])
            success_li.append(len([i for i in temp_li if i=='S'])/len(temp_li))
        plot_distribution(success_li,sam_sz)
    
def plot_distribution(sample_proportion_li:list,sample_sz):
    sns.kdeplot(sample_proportion_li,fill=True)
    plt.title(f'KDE (SAMPLE SIZE {sample_sz})')
    plt.show()
    plt.hist(sample_proportion_li,bins = 100)
    plt.title(f'HISTOGRAM (SAMPLE SIZE {sample_sz})')
    plt.show()
        
### SCRIPT

process_sample_sizes(50000,[5,10,15,25,50,75,100,200,300,500],.16)





