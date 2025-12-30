import csv
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.size': 16})
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False



with open('block_gas_usages_tosem_b.csv', 'r') as file:
    csv_reader = csv.DictReader(file)
    data = [row for row in csv_reader]


our_gas = [int(d['our_tool_gas_cost']) for d in data]
syrup_gas = [int(d['syrup_tool_gas_cost']) for d in data]
original_gas = [int(d['original_gas_cost']) for d in data]


#our improvement over baseline
temp = [(1-i/j)*100 for i, j in zip(our_gas, original_gas)]
imp1 = []
total_improvement = 0
for x in temp:
	if x>0:
		imp1.append(x)
		total_improvement+=x

print("Number of blocks for which we are better than unoptimized = "+str(len(imp1)))
print("Average improvement = "+str(total_improvement/len(imp1)))

values, bins, bars = plt.hist(imp1, bins=range(0, 101,5))
plt.bar_label(bars)
plt.xticks(range(0, 101, 5))
plt.show()
plt.clf()

#syrup's improvement over baseline
temp_syrup = [(1-i/j)*100 for i, j in zip(syrup_gas, original_gas)]
imp1_syrup = []
total_improvement_syrup = 0
for x in temp_syrup:
	if x>0:
		imp1_syrup.append(x)
		total_improvement_syrup+=x
	
print("Number of blocks for which syrup is better than unoptimized = "+str(len(imp1_syrup)))
print("Average improvement = "+str(total_improvement_syrup/len(imp1_syrup)))


#our improvement over syrup
temp = [(1-i/j)*100 for i, j in zip(our_gas, syrup_gas)]
imp1 = []
total_improvement = 0
for x in temp:
	if x>0:
		imp1.append(x)
		total_improvement+=x

print("Number of blocks for which we are better than syrup = "+str(len(imp1)))
print("Average improvement = "+str(total_improvement/len(imp1)))

values, bins, bars = plt.hist(imp1, bins=range(0, 101,5))
plt.bar_label(bars)
plt.xticks(range(0, 101, 5))
plt.show()
plt.clf()

#scatter plot
our_syrup = list(zip(our_gas, syrup_gas))
our_syrup.sort()
plt.scatter([i for (i, j) in our_syrup], [j for (i, j) in our_syrup])
#plt.show()
