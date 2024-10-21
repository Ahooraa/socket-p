import pandas as pd
import numpy as np

def load_data_from_csv(csv_file):
    records = pd.read_csv(csv_file)
    return records


def main():
    csv_file = './RandomData.csv'

    # Load data into a pandas DataFrame
    # data = load_data_from_csv(csv_file)
    # mydata= data[:15]
    # mydata.loc[:,"client"]=0
    # # Generate an array of random indices
    # random_indices = np.random.randint(0, len(mydata), size=7)
    # mydata.iloc[random_indices, mydata.columns.get_loc('client')] = 1
    # print(random_indices)
    # print(mydata)
    message= input()
    indexes= message.split(',')
    for i,index in enumerate(indexes):
        indexes[i]= int(index)
    print(indexes)
    print(type(indexes[0]))




if __name__ == "__main__":
    main()
