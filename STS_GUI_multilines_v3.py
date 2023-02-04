import os
import sys
import tkinter
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt;
import matplotlib as mpl
import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
#from ipywidgets import interact


def STSminimum_full(colX, transY, setN=8, N_lines=15):
    """
    Averaging of multiple STS curves in line scan

    Input: X data set, Y data set, int number of points in line scan,
    int number of STS curves at one point
    
    Output: set of averaged Y, set of smoothed Y, set of X, Y for minimum
    position
    """

    setOfMeanY = []
    setOfSmoothY = []
    setMinX = []
    setMinY = []
    
    for currentSet in range(setN):
        
        #to set range for a current set
        startLine = currentSet*(N_lines+1)
        endLine = currentSet*(N_lines+1) + N_lines
        
        
        #1 - make average for currentSet
        meanY = []
        
        for i in range(len(colX)):
            summ = 0
            
            for j in range(startLine, endLine):
                
                summ = summ + transY[j][i] #transY - global variable - our good colY set        
            meanY.append(summ/(N_lines))  #Why it was /(N_lines+1)??
        
        setOfMeanY.append(meanY)

        
        #2 - to smooth averaged colY in currentSet
        smoothY = savgol_filter(meanY, 17 ,2) #data, window, polynome degree
        
        setOfSmoothY.append(smoothY)
        
        #3 - to find the minimum
        index = np.argmin(smoothY)
        minY = smoothY[index]
        #minX = colX[(int(index[0]))] # corresponding position of X in the X-list
        minX = colX[index]
        
        setMinX.append(minX)
        setMinY.append(minY)
    return setOfMeanY, setOfSmoothY, setMinX, setMinY


def mainSTS(file):

    filename, file_extension = os.path.splitext(file)

    fileIn = filename + file_extension
    fileOut = filename + '_res' + file_extension
    fileOut1 = filename + '_smooth' + file_extension
    fileOut2 = filename + '_av' + file_extension

    # read all file to rows_list
    with open(fileIn, 'r') as ff:
        rows_list = [];
        for line in ff:
            try:
                rows_list.append(line.strip().split('  \t'))
            except:
                print('err')

    # find number of curves to average and number of points in line
    coordX = []
    for el in rows_list[19]:
        try:
            el = float(el)
            coordX.append(el)
        except:
            continue

    for i in range(len(coordX)):
        
        try:
            #print(i)
            #print(coordX[i], coordX[i+1])
            #print(coordX[i] == coordX[i+1])
            
            if coordX[i] == coordX[i+1]:
                # number of equal lines = i + 1(next is still the same) + 1 (because of start from zero)
                # it is doubled N of spectra, that we set in the software for one point
                nLines = i + 2
                #print('nLines', nLines)
            else:
                break
        except:
            break
    #nLines  - already dubbled STS number
    pointsN = int((len(coordX))/(nLines))

    print('\nnLines (doubled, up + down sweep):',nLines)
    print('N of points in line scan:',pointsN)


    colX = [];
    colY = [];
    iii = 0
    for row in rows_list[21:]:
        iii+=1
        try:
            #print(iii,': ', 'X= ', row[0])
            colX.append(float(row[0]))
        except:
            print('errX: ', row[0])
        try:
            #print(iii,': ', 'Y= ', row[1:])
            colY.append([float(val) for val in row[1:]])

        except:
            print('errY')

    colY.pop(-1)

    transY = []

    for i in range(len(colY[0])):
        col = []
        
        for el in colY:
            col.append(el[i])
            
        transY.append(col)

    for i in range(len(transY)):
        plt.plot(colX,transY[i])
    plt.show()

    setOfMeanY, setOfSmoothY, setMinX, setMinY = STSminimum_full(colX, transY, pointsN, nLines-1)

    plt.plot(list(range(len(setMinX))), setMinX, marker="o", markersize=5, markerfacecolor="green")

    plt.figure(figsize=(14,10))
    plt.xlim([-0.4, 0.4])
    plt.ylim([0, 0.1e-9])
    [plt.plot(colX, smY) for smY in setOfSmoothY]
    plt.plot(setMinX, setMinY, marker="o", markersize=5, markerfacecolor="green")
    plt.show()

    sts_res = pd.DataFrame(setMinY, setMinX)
   

    t_setOfSmoothY = []

    for i in range(len(setOfSmoothY[0])):
        col = []
        
        for el in setOfSmoothY:
            col.append(el[i])
            
        t_setOfSmoothY.append(col)

    sts_smooth = pd.DataFrame(t_setOfSmoothY, colX)


    t_setOfMeanY = []

    for i in range(len(setOfMeanY[0])):
        col = []
        
        for el in setOfMeanY:
            col.append(el[i])
            
        t_setOfMeanY.append(col)

    sts_av = pd.DataFrame(t_setOfMeanY, colX)


    with open (fileOut, 'w') as ff:
            #tst_t = sts_res.T
            sts_res.to_csv(ff)
    with open (fileOut1, 'w') as ff1:
            #tst_t = sts_res.T
            sts_smooth.to_csv(ff1)
    with open (fileOut2, 'w') as ff2:
            #tst_t = sts_res.T
            sts_av.to_csv(ff2)

def show_res(text):
    tkinter.messagebox.showinfo("Results", text)



def clicked():
    t = tkinter.filedialog.askopenfilename()
    mainSTS(t)

app = tkinter.Tk()
app.geometry('300x200')
app.title('Multi-STS analysis')

header = tkinter.Label(app, text="Please select ASCII multi-STS file:") # , fg="blue", font=("Arial Bold", 16))
header.pack(side="top", ipady=10)

open_files = tkinter.Button(app, text ="Choose file...", command=clicked)
open_files.pack(fill='x')
app.mainloop()















