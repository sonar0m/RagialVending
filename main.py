#source
#https://stackoverflow.com/questions/18812614/embedding-a-python-library-in-my-own-package
import os
import sys

# Add vendor directory to module search path
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'RagialVending')

sys.path.append(parent_dir)
#start of program
import Ragial
import time #for sleep
from os import listdir
from os.path import isfile, join
try:
    import configparser as ConfigParser
except:
    import ConfigParser

def getInputs():
    ret = {}
    #configuration
    config= Ragial.getConfig()
    roDir = config.get("search","Ragnarok")
    tabName=config.get("search","ChatTabName")
    #file work
    if roDir[-1]!="\\":
        roDir = roDir+"\\"
    file=""

    stream=None
    tabfiles = [f for f in listdir(join(roDir, "Chat")) if isfile(join(join(roDir, "Chat"), f)) and "_"+tabName in f]
    tabfiles.sort()
    #open files
    try:
            #Ragial.eprint(join(join(roDir, "Chat"), tabfiles[-1]) )
            stream = open(join(join(roDir, "Chat"), tabfiles[-1]) )#open the newest file and join it to the chat location in the config
            file = stream.read()
    except:
        Ragial.eprint("get RO file error")
    finally:
        if stream != None:
            stream.close()
    ####
    ##parse file
    ####
    #Ragial.eprint(file)
    for line in file.split("\n"):
        if len(line)>0:
            if line[:8]=="You got ":
                #Ragial.eprint(line[::-1])
                #revirse look for the first ( incase it's double or tripple digitiet
                lastindex = (line[::-1].index("( ")+2)*-1#remember it's revirsed
                ret[line[8:lastindex]] = 0 #8="You Got "
    Ragial.eprint(ret.keys())
    return ret.keys()

def getCodes(names):
    ret = {}
    for name in names:
        ret[name] = Ragial.searchName(name)
        time.sleep(1)#flood control #SECONDS
    return ret

def getHistory(codes):
    ret = []
    config = Ragial.getConfig()
    rowCount = config.getint("CSV", "rowsPerPage")
    pages = config.getint("CSV", "pages")
    ret = Ragial.RunHistory(codes.values(), rowCount, pages)
    return ret
############################
#starting calculation get's#
############################
#calculat all median
def getMedian(items):
    ret={}
    for item in items:
        i= [ v['price'] for v in item]
        i.sort()
        if len(i) ==0:
            ret[item.itemDetails["name"]] = -1
        ret[item.itemDetails["name"]] = int(i[int(len(i)/2)])
    return ret
#calculat ACTIVE median
def getActiveMedian(items):
    ret={}
    for item in items:
        i = [ v['price'] for v in item if v["active"]] # inline for loop can also do {}
        i.sort()
        if len(i)>0:
            ret[item.itemDetails["name"]] = int(i[int(len(i)/2)])
        else:
            ret[item.itemDetails["name"]] = -1
    return ret
#calculate active minum
def getActiveMinum(items):
    ret={}
    for item in items:
        i = [ v['price'] for v in item if v["active"]]
        i.sort()
        if len(i)>0:
            ret[item.itemDetails['name']] = int(i[0])
        else:
            ret[item.itemDetails["name"]] = -1
    return ret
#get the active count
def getActiveCount(items):
    ret = {}
    for item in items:
        i = [ v['price'] for v in item if v["active"]]
        i.sort()
        ret[item.itemDetails['name']] = len(i)
    return ret


def run_RagialCart():
    #Inputs
    names = getInputs()#gets /savechat from configs
    codes = getCodes(names) # get's the codes from item names

    #get info
    #Ragial.eprint("codes"+codes)
    history = getHistory(codes) #get the history info

    #output calculate
    #insert check for 0 count and no returns
    median = getMedian(history)
    aMedian = getActiveMedian(history)
    aMin = getActiveMinum(history)
    aCount = getActiveCount(history)

    ####output####
    formatting = "{:>50}|"+"{:^12}|"*4
    header = (formatting).format(*["item", "med", "A Med", "aMin", "aCount"])
    formatting = "{:>50}|"+"{:^12,}|"*4
    print("".join(["-" for l in header]))
    print(header)
    print("".join(["=" for l in header]))
    for z in zip(names, median.values(), aMedian.values(), aMin.values(), aCount.values()):
        line= (formatting).format(*z)
        print(line)
        print("".join(["-" for l in line]))

#checks if the file needs to be run
def needsToRun():
    #check  if file was moved/ created
    config = Ragial.getConfig()
    roDir = config.get("search", "Ragnarok")
    tabName = config.get("search", "ChatTabName")
    if roDir[-1] != "\\":
        roDir = roDir + "\\"
    file = ""
    stream = None
    print(roDir)
    tabfiles = [f for f in listdir(join(roDir, "Chat")) if isfile(join(join(roDir, "Chat"), f)) and "_" + tabName in f]
    tabfiles.sort()
    print(tabfiles)
    last= tabfiles[-1]
    print("waiting for new file...")
    while not(isChanged(last)):
        continue
    print("running now")
    #check if ran after last time
    run_RagialCart()
    #move or remove file?

#check's if the directory has a new file
def isChanged(last):
    config= Ragial.getConfig()
    roDir = config.get("search","Ragnarok")
    tabName=config.get("search","ChatTabName")
    if roDir[-1]!="\\":
        roDir = roDir+"\\"
    file=""
    stream=None
    tabfiles = [f for f in listdir(join(roDir, "Chat")) if isfile(join(join(roDir, "Chat"), f)) and "_"+tabName in f]
    tabfiles.sort()
    if tabfiles[-1]!=last:
        return True
    else:
        return False



if __name__ == "__main__":
    needsToRun()# get's /savechants from configured locations then out put's in CSV

    '''
    row_format ="{:>15}" * (len(median.keys()) + 1)
    print row_format.format("", *median.keys())
    for team, row in zip(median.keys(), [median, aMedian, aMin]):
        print row_format.format(team, *row)
    #print("name  \tmedian\taMedian\tamin")
    #for k in median.keys():
    '''
#       i = int(len(k)/5)
#       if i == 0:
#           i = 1
#       print(k+""+("\t|"*(8-i))+ "\t".join([str(median[k]), str(aMedian[k]),str(aMin[k]) ]) )
    #todo: do math on adv, medien, and min and active of each
    #todo: output
