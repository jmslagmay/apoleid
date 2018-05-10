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
    #K = 2
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
    old_fp_loc = [0, 0, 0]
    dr_loc = [0, 0, 0]
    actual_loc = [0, 0, 0]

    radius = 6 #radius of dynamic subarea

    print ("------ INITIAL LOCATION ------")
    print("FP LOC: %.2f, %.2f, %.2f" % (fp_loc[0], fp_loc[1], fp_loc[2]))
    print("DR LOC: %.2f, %.2f, %.2f\n" % (dr_loc[0], dr_loc[1], dr_loc[2]))
    print("ACTUAL LOC: %.2f, %.2f, %.2f\n" % (actual_loc[0], actual_loc[1], actual_loc[2]))


    while 1:
        #dr_loc[0] = dr_loc[0] + 0.5
        dr_loc[1] = dr_loc[1] + 0.5
        #dr_loc[2] = dr_loc[2] + 0.5

        old_fp_loc[0] = fp_loc[0]
        old_fp_loc[1] = fp_loc[1]
        old_fp_loc[2] = fp_loc[2]

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

        print (D)
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
            #for i in range(0, K):
            #    min_D = min(D)
            #    index = D.index(min_D)

            #    D[index] = 1000000
            #    index_knn.append(index)

            #getting the indices of the points with euclidean
            #distances less than radius
            for i in range (0, len(data) - 1):
                if D[i] < radius:
                    index_knn.append(i)

            print(index_knn)
            K = len(index_knn)
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

        delta_x = fp_loc[0] - actual_loc[0]
        delta_y = fp_loc[1] - actual_loc[1]
        delta_z = fp_loc[2] - actual_loc[2]
        d_fp = math.sqrt(pow(delta_x, 2) + pow(delta_y, 2) + pow(delta_z, 2))

        delta_x = dr_loc[0] - actual_loc[0]
        delta_y = dr_loc[1] - actual_loc[1]
        delta_z = dr_loc[2] - actual_loc[2]
        d_dr = math.sqrt(pow(delta_x, 2) + pow(delta_y, 2) + pow(delta_z, 2))

        print("d_fp: %f, d_dr: %f" % (d_fp, d_dr))
        print("FP LOC: %f, %f, %f" % (fp_loc[0], fp_loc[1], fp_loc[2]))
        print("DR LOC: %f, %f, %f" % (dr_loc[0], dr_loc[1], dr_loc[2]))

        if d_fp == 0:
            r = radius
        elif d_dr == 0:
            r = 0
        else:
            r = (1 / d_fp) / ((1 / d_fp) + (1 / d_dr))

        if (old_fp_loc[0] == fp_loc[0] and old_fp_loc[1] == fp_loc[1] and old_fp_loc[2] == fp_loc[2]):
            actual_loc[0] = dr_loc[0]
            actual_loc[1] = dr_loc[1]
            actual_loc[2] = dr_loc[2]

        else:
            actual_loc[0] = ((1 - r) * dr_loc[0]) + (r * fp_loc[0])
            actual_loc[1] = ((1 - r) * dr_loc[1]) + (r * fp_loc[1])
            actual_loc[2] = ((1 - r) * dr_loc[2]) + (r * fp_loc[2])

        #print("FP LOC: %.2f, %.2f, %.2f" % (fp_loc[0], fp_loc[1], fp_loc[2]))
        #print("DR LOC: %.2f, %.2f, %.2f" % (dr_loc[0], dr_loc[1], dr_loc[2]))
        #print("ACTUAL LOC: %.2f, %.2f, %.2f\n" % (actual_loc[0], actual_loc[1], actual_loc[2]))

        #print("FP LOC: %f, %f, %f" % (fp_loc[0], fp_loc[1], fp_loc[2]))
        #print("DR LOC: %f, %f, %f" % (dr_loc[0], dr_loc[1], dr_loc[2]))
        print("ACTUAL LOC: %f, %f, %f\n" % (actual_loc[0], actual_loc[1], actual_loc[2]))
        #print('\n')

        measured_rss.clear()
        index_knn.clear()
        flag = 0
