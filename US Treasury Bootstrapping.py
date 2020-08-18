import pandas as pd
import matplotlib.pyplot as plt

'''This script is build to collect the US treausry data from the treausry.gov
page and boot strap the yield curve returning the spot curve for those
time periods'''


#import treasury yield data
df = pd.read_html('https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/textview.aspx?data=yield')
yields = df[1].set_index('Date')


#select most recent dated treausry yields T=0,
#set to frame and set discount (should turn into function)
rates = yields.iloc[0]
rates = rates.to_frame()
rates = rates.reset_index().drop('index', axis = 1)
rates['power'] = pd.DataFrame([1/12,1/6,1/4,1/2,1,2,3,5,7,10,20,30])
rates.columns = ['r', 'power']


#plot yield curve
fig = plt.figure()
axes = fig.add_axes([0.1,0.1,0.8,0.8])
axes.plot(rates['r'])


#k_1 calculator function
def k1_calculator(C,M, i, count, cashflow_power, r, power, k1):
    '''RECURSIVE FUNCTION to calculate k1 power
       C = cashflow of bond
       M = maturity amount of bond
       i = selecting first row in discount power
       count = counter to determine which function to calculate
       r = series containing rates
       power = series containing discount powers
       k1 = input from k1 = ?
       RETURNS k1'''
    #this r = rate used in calculation
    r = r.iloc[i]
    if count == 0:
        k1 += (C+M)/((1+r/100) ** power.iloc[i])
        return k1
    else:
        k1 += (C)/((1+r/100) ** power.iloc[cashflow_power])
        count -= 1
        cashflow_power += 1
        return k1_calculator(C,M, i,count, cashflow_power, rates['r'], power, k1)


def k2_calculator(C, i, r, power, k2, spots):
    '''Function to calculate k2
        C = cashflow of bond
        M = maturity of bond
        i = indicator value to select appropriate row
        k2 = input from k2 = ?
        spots = dictionary containing spot values to be used in calculaion
        RETURNS k2'''
    if i == 0:
        k2 = 0
    else:
        for j in range(i):
            k2 += C/((spots['s' + str(j)]) + 1) ** power.iloc[j]
    return k2

def spot_calculator(C, M, k1, k2, power, i):
    '''FUNCTION to calculate and assign the variables to the spot dictionary
        C = cashflow of bond
        M = marutiy of bond
        k1 = varialbe calculated from k1_calculator
        k2 = variable calculated from k2_calculator
        power = pandas.series of discount powers
        i = point in time of the bootstrap to be used to select row
        RETURNS s'''
    s = (((C+M)/(k1 - k2))**(1/power.iloc[i])) - 1
    return s


def spot_curve_calculator(C, M, rates):
    '''FUNCTION to calculate the bootstrapped spotrate curve
        C = cashflow of bond
        M = marutiy of bond
        rates = dataframe that contains the the discount power and the
        prevailing rates'''
    spots = {}
    power = rates['power']
    r = rates['r']
    for i in range(len(rates)):
        k1 = 0
        count = i
        cashflow_power = 0
        k1 = k1_calculator(C, M, i, count, cashflow_power, r, power, k1)

        k2 = 0
        k2 = k2_calculator(C, i, r, power, k2, spots)

        s = spot_calculator(C, M , k1, k2, power, i)

        spots['s' + str(i)] = s
    return spots

#running the function and assigning and plotting the bootstrapped curve
spot_curve =spot_curve_calculator(50, 1000, rates)
df_spot_curve = pd.Series(spot_curve)
df_spot_curve.plot()
