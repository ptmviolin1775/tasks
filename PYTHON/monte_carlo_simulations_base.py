import matplotlib.pyplot as plt
import random
import sys


#####FUNCTIONS


def roll_dice():
    die_1=random.randint(1,6)
    die_2=random.randint(1,6)
    
    roll=die_1+die_2
    return roll


#####INPUTS
num_simulations=10000
label=''
bet=25



#####CREATE GRAPH
fig=plt.figure()
# plt.title("Monte Carlo Craps Game ["+ str(num_simulations)+" simulations]")
# plt.xlabel("Num Games")
# plt.ylabel("Balance $")
# plt.xlim([0,100])


for number_games in [24,49,74,99]:
    plt.clf()
    plt.xlabel("Num Games")
    plt.ylabel("Balance $")
    plt.xlim([0,number_games])
    plt.show()
    num_games_list=[]
    balance_list=[]
    wins_list=[]
    win_probability=[]
    end_balance=[]
    winning_sims=[]
    for i in range(num_simulations):
        balance=[1000]
        num_games=[0]
        num_wins=[0]
        while balance[-1]>0 and num_games[-1]<number_games:
            label=''
            while label not in ['win','lose']:
                
                point=0
                num_rolls=[0]
                rolls=[]
                roll=roll_dice()
                rolls.append(roll)
                num_rolls.append(num_rolls[-1]+1)
                
                if balance[-1] in range(0,10):
                    bet=balance[-1]
                
                if roll in [7,11]:
                    label='win'
                    balance.append(balance[-1]+(bet*2))
                    num_wins.append(num_wins[-1]+1)
                elif roll in [2,3,12]:
                    label='lose'
                    balance.append(balance[-1]-bet)
                else:
                    label='point'
                    point=roll
                    while roll !=7:
                        roll=roll_dice()
                        num_rolls.append(num_rolls[-1]+1)
                        rolls.append(roll)
                        if roll==point:
                            label='win'
                            balance.append(balance[-1]+(bet*2))
                            num_wins.append(num_wins[-1]+1)
                            break
                        elif roll==7:
                            label='lose'
                            balance.append(balance[-1]-bet)
                            break
                num_games.append(num_games[-1]+1)
        end_balance.append(balance[-1])
        balance_list.append(balance)
        wins_list.append(num_wins)
        num_games_list.append(num_games)
        plt.plot(num_games,balance)
    plt.title(f'Monte Carlo Craps Game: Player stays for {number_games+1} games [{str(num_simulations)} simulations]')
    plt.show()


    print(f'LOSSES: {len([i for i in end_balance if i<1000])}')
    print(f'WINS: {len([i for i in end_balance if i>=1000])}')
    # end_balance.sort()
    # print(end_balance)

