import csv
with open('block_gas_usages_tosem_b.csv', 'r') as file:
    csv_reader = csv.DictReader(file)
    data = [row for row in csv_reader]

print("Number of basic blocks = "+str(len(data)))

total_unoptimized=0
total_syrup=0
total_us=0
for d in data:
	total_unoptimized += int(d['original_gas_cost'])
	total_syrup += int(d['syrup_tool_gas_cost'])
	total_us += int(d['our_tool_gas_cost'])
	
print("The total gas usage of unoptimized contracts = "+str(total_unoptimized))
print("The total gas usage of syrup = "+str(total_syrup)+ "\tImprovement: "+str((1-total_syrup/total_unoptimized)*100))
print("The total gas usage of our approach = "+str(total_us)+"\tImprovement: "+str((1-total_us/total_unoptimized)*100)+ " \t over syrup:"+str((1-total_us/total_syrup)*100))


our_gas = [int(d['our_tool_gas_cost']) for d in data]
syrup_gas = [int(d['syrup_tool_gas_cost']) for d in data]
original_gas = [int(d['original_gas_cost']) for d in data]



