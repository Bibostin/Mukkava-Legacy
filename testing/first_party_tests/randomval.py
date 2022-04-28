import random
site1 = [145, 48, 14, 5, 5, 5, 0] #these are ordered lists equivilent to java or c arrays
site2 = [ 2,   0,  9, 3, 0, 0, 7]
site3 = []

for i in range(7):
    site3.append(random.randrange(site1[i], site2[i]) if site1[i] < site2[i] else random.randrange(site2[i], site1[i]))
    print(site3[i])
