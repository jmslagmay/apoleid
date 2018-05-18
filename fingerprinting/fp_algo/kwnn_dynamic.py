import math

def import_db(station_count):
    global data
    global fp_db

    #db = open("dummy_db.csv", "r")
    #db = open("rss_db_427.csv", "r")
    db = open("rss_db_514_orig.csv", "r")
    db_content = db.read()
    db.close()

    data = db_content.split('\n')

    fp_db = {}
    fp_db['X'] = []
    fp_db['Y'] = []
    fp_db['Z'] = []

    for i in range (1, station_count + 1):
        key = "station" + str(i)
        fp_db[key] = []

    for i in range(0, len(data) - 1):
        split_data = data[i].split(',')

        fp_db['X'].append(split_data[0])
        fp_db['Y'].append(split_data[1])
        fp_db['Z'].append(split_data[2])

        for j in range(1, station_count + 1):
            key = "station" + str(j)
            fp_db[key].append(split_data[j+2])


if __name__ == "__main__":

    global data
    global fp_db

    STATION_COUNT = 3
    K = 2
    radius = 4

    import_db(STATION_COUNT)

    #print(len(data))

    #for i in range(0, len(data) - 1):
    #    print(data[i])

    #print(fp_db)
    #print('\n')
    #print(fp_db['X'])
    #print('\n')
    #print(fp_db['Y'])
    #print('\n')
    #print(fp_db['Z'])
    #print('\n')
    #print(fp_db['station1'])
    #print('\n')
    #print(fp_db['station2'])
    #print('\n')
    #print(fp_db['station3'])
    #print('\n')
    #print(fp_db['station4'])

    measured_rss = []
    index_knn = []

    for i in range(1, STATION_COUNT + 1):
        rss = input('Station %d: ' % i)
        measured_rss.append(rss)

    #print (measured_rss)

    D = []
    weight = []

    #computing euclidean distances and storing them to list D
    for i in range(0, len(data) - 1):
        num = 0
        for j in range(0, STATION_COUNT):
            key = "station" + str(j+1)
            num = num + pow((int(fp_db[key][i]) - int(measured_rss[j])), 2)

        D.append(math.sqrt(num))

    #print('\n')
    #print(D)

    #checking if there is a point wherein the
    #euclidean distance is 0
    for i in range(0, len(data) - 1):
        if D[i] == 0:
            #loc = [float(fp_db['X'][i]), float(fp_db['Y'][i]), float(fp_db['Z'][i])]
            #return loc
            x = float(fp_db['X'][i])
            y = float(fp_db['Y'][i])
            z = float(fp_db['Z'][i])
            done = 1


    if done == 0:
    #computing weights from euclidean distances
        for i in range(0, len(data) - 1):
            num = 1 / D[i]
            weight.append(num)

        #print('\n')
        #print(weight)

        #storing index of K nearest neighbors to list index_knn
        for i in range(0, K):
            min_D = min(D)
            index = D.index(min_D)

            D[index] = 1000000
            index_knn.append(index)

        #print('\n')
        #print(index_knn)

        #getting the location by using the formula for KWNN
        # K nearest neighbors
        denominator = 0
        for i in range (0, K):
            denominator = denominator + (weight[index_knn[i]])

        x = 0
        for i in range(0, K):
            x = x + (float(fp_db['X'][index_knn[i]]) * weight[index_knn[i]])

        x = x / denominator

        y = 0
        for i in range(0, K):
            y = y + (float(fp_db['Y'][index_knn[i]]) * weight[index_knn[i]])

        y = y / denominator

        z = 0
        for i in range(0, K):
            z = z + (float(fp_db['Z'][index_knn[i]]) * weight[index_knn[i]])

        z = z / denominator

    print('\n')
    print("%.2f, %.2f, %.2f" % (x, y, z))
