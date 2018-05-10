import math

def import_db(station_count):
    global data
    global fp_db

    #db = open("dummy_db.csv", "r")
    db = open("rss_db_427.csv", "r")
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

    STATION_COUNT = 2
    K = 2
    flag = 0

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
    fp_loc = [0, 0, 0]
    dr_loc = [0, 0, 0]
    print ("------ INITIAL LOCATION ------")
    print("FP LOC: %.2f, %.2f, %.2f" % (fp_loc[0], fp_loc[1], fp_loc[2]))
    print("DR LOC: %.2f, %.2f, %.2f\n" % (dr_loc[0], dr_loc[1], dr_loc[2]))

    while 1:
        dr_loc[0] = dr_loc[0] + 0.5
        dr_loc[1] = dr_loc[1] + 0.5
        dr_loc[2] = dr_loc[2] + 0.5

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

        for i in range(0, len(data) - 1):
            if D[i] == 0:
                flag = 1
                fp_loc[0] = float(fp_db['X'][i])
                fp_loc[1] = float(fp_db['Y'][i])
                fp_loc[2] = float(fp_db['Z'][i])
                print("Flag is one")

        if flag == 0:

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

            fp_loc = [x, y, z]


        print('\n')
        print("FP LOC: %.2f, %.2f, %.2f" % (fp_loc[0], fp_loc[1], fp_loc[2]))
        print("DR LOC: %.2f, %.2f, %.2f" % (dr_loc[0], dr_loc[1], dr_loc[2]))

        measured_rss.clear()
        index_knn.clear()
        flag = 0
