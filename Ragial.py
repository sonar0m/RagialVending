import sys, os
import traceback
import time #for sleep
from SimplePyScrape.Scrape import Scrape, Item, eprint
import urllib
import datetime
try:
    from urllib2 import URLError, HTTPError
except:
    from urllib.error import URLError, HTTPError
try:
    from urllib import urlencode
except:
    import urllib.parse

    urlencode = urllib.parse.urlencode

try:
    import configparser as ConfigParser
except:
    import ConfigParser

lan = False
Seperator = "|"
'''
## get the history of an item IE who sold when##
## returns the rows of info of the scrapped output of the row count
'''
def getItemHistory(url, rowCount):
    #eprint(url)
    # configurations
######row data
    urlflag = [1, "href=", "\""]
    urlflags = {"tyfe": "string", "name": "url", "cfg": {}, "flags": urlflag}
    nameflag = [1, "/>", "<"]
    nameflags = {"type": "string", "name": "name", "cfg": {}, "flags": nameflag}
    dateflag = [1, "\"date\"", ">", "</td>"]
    dateflags = {"type": "string", "name": "date", "cfg": {},
                 "flags": dateflag}  #, "filter":"[a-zA-Z]{3}-\d{1,2}-\d{2}"
    priceflag = [1, "price nm\">", ">", "</a>"]
    priceflags = {"type": "string", "name": "price", "cfg": {}, "flags": priceflag
                  ,"filter": "(-invert)[0-9]"
                  }
    itemsflag = [-1, "<tr", "</tr>"]
    itemsflags = {"type": "string",
                  "name": "row",
                  #"cfg": {"Urls":{"type": "string", "name": "url", "cfg": {}, "flags": [1,"", ""]}} ,
                  "cfg": { "Name": nameflags, "Date": dateflags, "Price":priceflags},#"Urls":urlflags, 
                  "flags": itemsflag}
    ######end row tat
    ######start item and sat data
    
    cfg = [1, "</tfoot>", "</div>"]
    cfgs = {"type": "string",
            "name": "set",
            #"cfg": {"Urls":{"type": "string", "name": "url", "cfg": {}, "flags": [1,"", ""]}} ,
            "cfg": { "Set":itemsflags }, 
            #"filter":'<span class="__cf_email__".+</script>',#anti email crap 
            "flags": cfg}

    codeFlag = [1, "http://ragi.al/item/", "/", "\""]
    codes = {"type": "string", "name": "code", "cfg": {}, "flags": codeFlag}
    itemName = [1, "<title>", "-", "-"]
    itemNames = {"type": "string", "name": "Item Name", "cfg": {}, "flags": itemName}

    allHtml = [1, "", ""]
    alls = {"type": "string", "name": "All",
            #"cfg": {"code":{"type":"string", "name":"debug", "cfg":{},"flags":allHtml}},#debug
            "cfg": {"Data": cfgs, "Name": itemNames, "code": codes},#
            "flags": allHtml}
    ######end of set and items data

    #################################
    #########start of scrape#########
    src = Scrape(url=url)
    try:
        if lan and os.path.exists("History"):  #if you local test values
            urlR = "http://ragi.al/item/iRO-Renewal/"
            code, page = url[len(urlR):].split("/")
            f = open("History" + os.sep + "{}.{}.htm".format(code, page), "r")
            src.source = f.read()
            f.close()
        else:
            src.getSource()
    except HTTPError as e:
        print("HTTP Error")
        print(e)
        raise NameError("Get Source Error")
        return None
    except URLError as e:
        print("URL error")
        print(e)
        return None
    except NameError as e:
        print("Name Error")
        print(e)
        return None
    src.setConfig(alls)#cfgs)#
    src.doConfig()
    #################################
    #####end of scrape running#######
    
    ##debug##
    #print("debug(getItemHistory):")
    #print(src.output["All0|Data"]["set0|Set"]["row0|Name"].keys())
    #eprint(src.output["All0|Data"]["set0|Set"].keys())
    #eprint(len(src.output["All0|Data"]["set0|Set"].keys()))
    #eprint(len(src.output["All0|Data"]["set0|Set"].keys())/4)
    #return src.output
    
    #OVER RIDE rowcount for the less then max count
    rowCount = int(len(src.output["All0|Data"]["set0|Set"].keys())/4) #name,price,date,src
    
    
    #populate Items
    item = Item(Seperator, "name", "name" + Seperator + "date" + Seperator + "price" + Seperator + "active")
    data = src.output["All0|Data"]
    iname = ""
    iname = src.output["All0|Name"]
    if type(iname)==type({}):
        iname = str(iname["Item Name0"])
    if type(iname)==type(""):
        iname = iname.strip()
    item.itemDetails["name"] = iname
    
    #broke testing
    item.itemDetails["code"] = str(src.output["All0|code"]["code0"])
    #spacer = lambda d: "".join(["_" for a in range(d)])
    #print(spacer(67))
    
    config = getConfig()
    seperator = config.get("CSV", "seperator")
    for r in range(rowCount):
        if data["set0|Set"]["row"+str(r)] == None:
            break
        name = data["set0|Set"]["row" + str(r) + "|Name"]["name0"]
        if name != None:
            name = name.replace(seperator, "")
        else:
            name = "errored name"
            #eprint("Row" + str(r))
            try:
                None
                #eprint(data["set0|Set"]["row"+ str(r)])
            except:
                print()
        price = str(data["set0|Set"]["row" + str(r) + "|Price"]["price0"])
        date = data["set0|Set"]["row" + str(r) + "|Date"]["date0"]
        active = False
        if date == "Now":
            date = str(datetime.datetime.now().strftime("%b-%d-%y"))
            active = True
        if type(name)==type(""):
            name = name.strip()
        if type(date) ==type(""):
            date = date.strip();
        if type(price) ==type(""):
            price = price.strip();
        item.append(name=name, date=date, price=price, active=active)
    #print "{0:25}|{1:20}|{2:>20}".format(str(name), str(price), str(date))
    return item


'''checks if a url's history is empty on a page
returns true if it's empty falst if it is not =
'''
def checkHistoryEmpty(url):
    allHtml = [1, "<tr class=\"odd\">", ""]
    alls = {"type": "regex", "name": "is Empty",
                "flags": allHtml, "cfg":{}}
    src = Scrape(url=url)
    try:
        src.getSource()
    except HTTPError as e:
        print("HTTP Error")
        print(e)
        raise NameError("Get Source Error")
        return None
    except URLError as e:
        print("URL error")
        print(e)
        return None
    except NameError as e:
        print(e)
        return None
    src.setConfig(alls)
    src.doConfig()
    data = src.output
    #print("debug(is empty):"+str(-1==data["is Empty0"]))
    return -1 != data["is Empty0"]
'''
returns a name icon and code of a given item
'''
def findItem(name, page=0, rowCount=16):
    #gets the configs
    config = getConfig()
    Seperator = config.get("CSV", "seperator")
    urlbase = "http://ragi.al/search/iRO-Renewal/{}/{}"
    url = urlbase.format(name, page + 1)
    
    codeflag = [1, "href=\"", "iRO-Renewal/", "\""]
    codeflags = {"type": "string", "name": "code", "cfg": {}, "flags": codeflag}
    nameflag = [1, "<img", ">", "<"]
    nameflags = {"type": "string", "name": "name", "cfg": {}, "flags": nameflag}
    iconflag = [1, "<img src=\"", "\""]
    iconflags = {"type": "string", "name": "icon", "cfg": {}, "flags": iconflag}
    cfg = [rowCount, "<td class=\"name\">", "/tr>"]
    cfgs = {"type": "string",
            "name": "Search",
            "cfg": {"Code": codeflags, "Name": nameflags, "Icon": iconflags},
            "flags": cfg,
            "filter": "[a-zA-Z0-9]+"}
    src = Scrape(url=url)
    try:
        if lan:
            urlR = "http://ragi.al/search/iRO-Renewal/"
            code, page = url[len(urlR):].split("/")
            f = open("search.{}.{}.htm".format(code, page), "r")
            src.source = f.read()
            f.close()
        else:
            src.getSource()
    except HTTPError as e:
        print(e.code)
    except URLError as e:
        print("URL error")
        print(e.reason)
        return None
    src.setConfig(cfgs)
    src.doConfig()
    item = Item(Seperator, "", "name" + Seperator + "code" + Seperator + "icon")
    data = src.output
    for r in range(rowCount):
        name = data["Search" + str(r) + "|Name"]["name0"]
        url = str(data["Search" + str(r) + "|code"]["code0"])
        if url != None:
            url= url.replace(",", "")
        else:
            eprint("Row" + str(r)+ str(data["set0|Set"]["Search" + str(r) + ""]))
        icon = data["Search" + str(r) + "|Icon"]["icon0"]
        item.append(name=name.strip(), url=url.strip(), icon=icon.strip())
    # print "{0:25}|{1:20}|{2:>20}".format(str(name), str(price), str(date))
    return item

'''
finds code for the URLlink given a name.
'''
def searchName(name):
    # setup configs
    config = getConfig()
    urlbase = "http://ragi.al/search/iRO-Renewal/{link}/{page}"#swap to format 2  inputs
    enc = urlencode({"": name})[1:]
    url = urlbase.format(link=enc,page="{page}")
    nameFlags = [1, "</a>", "\">", "</a>"]
    names = {"type": "string", "name": "", "cfg": {}, "flags": nameFlags, "filter": "(^[ \t]+)|([ \t]+$)"}
    linkFlags = [1, "iRO-", "/", "\""]
    links = {"type": "string", "name": "", "cfg": {"Name": names}, "flags": linkFlags}
    listNameFlags = [-1, "class=\"name\"", "</tr>"]# add check for count on page less then config.getint("search", "itemsPerPage")
    listNames = {"type": "string", "name": "Search", "cfg": {"Name": names, "Link": links}, "flags": listNameFlags}
    #scrape name
    toLoop=True
    for i in range(config.getint("search", "maxpage")):
        url = url.format(page=i)
        src = Scrape(url=url)
        try:
            src.getSource()
            #print(src.source)
        except HTTPError as e:
            print("HTTP Error")
            print(e)
            raise NameError("Get Source Error")
            return None
        except URLError as e:
            print("URL error")
            print(e)
            return None
        except NameError as e:
            print(e)
            return None
        src.setConfig(listNames)
        src.doConfig()
        retvalues = []
        for i in range(config.getint("search", "itemsPerPage")):
            #if "Search" + str(i) + "|Name" in src.output:
                #eprint("|"+src.output["Search" + str(i) + "|Name"]["0"]+"|")
            if "Search" + str(i) + "|Name" in src.output and src.output["Search" + str(i) + "|Name"]["0"] == name:
            #if name in src.output["Search" + str(i) + "|Name"]["0"]:
                linkName = src.output["Search" + str(i) + "|Name"]["0"]
                link = src.output["Search" + str(i) + "|Link"]["0"]
                retvalues.append({"name": linkName, "link": link})
                #eprint("name: "+ linkName+" link: "+link)
                break
        for value in retvalues:
            if value["name"] == name:  #test nextpage/page count
                #print("debug (searchName)name:" + value["name"] + " value:" + value["link"])
                return value["link"]
            else:
                print("not found")
            #for a, b in src.output.items():
                #f  eprint(b)
    #do while for checking for match or max pagging
    #return url
    return ""


def getConfig():
    config = ConfigParser.ConfigParser()
    if "EXTERNAL_STORAGE" in os.environ:
        cfg = {"nt": "", "posix": os.environ["EXTERNAL_STORAGE"] + "/com.hipipal.qpyplus/projects/Ragial/", "other": ""}
    else:
        cfg = {"nt": "", "other": ""}
    cfgOS = "nt"
    if os.name in cfg:
        cfgOS = os.name
    config.read(cfg[cfgOS] + "settings.ini")
    return config


def newRagialItem():
    config = getConfig()
    seperator = config.get("CSV", "seperator")
    return Item(seperator, "name", "name" + seperator + "date" + seperator + "price" + seperator + "active")


def ragialItemPopulation(item, url, rowCount):
    i = getItemHistory(str(url), rowCount)
    #print("debug(ragialItemPopulation)"+str(i.itemDetails.keys()))
    if i == None:
        return None
    if i != None:
        #eprint(str(i.itemDetails["name"])+" "+str(i.itemDetails["code"]))
        item.itemDetails["name"] = i.itemDetails["name"]
        item.itemDetails["code"] = i.itemDetails["code"]
        item.append(i)
    else:
        print("no items")
        pass
    return item

def RunHistory(code, rowCount, pages):
    src = None
    itemsz = []
    for c in code:
        item = newRagialItem()
        for p in range(pages):
            urlbase = "http://ragi.al/item/iRO-Renewal/{}/{}"
            url = urlbase.format(c, p + 1)
            #eprint(url)
            if checkHistoryEmpty(url):
                try:
                    item = ragialItemPopulation(item, url, rowCount)
                except Exception as e:
                    print("ERROR(RunHistory): "+url)
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_name)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    traceback.print_exc()
            time.sleep(1)#flood control #SECONDS
        itemsz.append(item)
        # end for pages
        src = None
        time.sleep(2)#flood control #SECONDS
    # end for codes
    return itemsz


def csvOutput(item):
    itemz = item
    if type(item) == type(newRagialItem()):
        itemz = [item]
    for i in itemz:
        if "code" in i.itemDetails:
            if not os.path.exists("output"):
                os.makedirs("output")
            f = open("output" + os.sep + str(i.itemDetails["code"]) + ".csv", "w")
            try:
                f.write(str(i))
            finally:
                f.close()
            # end output


if __name__ == "__main__":
    print("main output")
    ''' old testing '''

    #print(checkHistoryEmpty("http://ragi.al/item/iRO-Renewal/ZhA/2"))#test agenst mya purple card
    #print(checkHistoryEmpty("http://ragi.al/item/iRO-Renewal/2QY/1"))
    item = {}
    # searchName("Chain Mail [1]")
    config = getConfig()
    code = config.get("CSV", "code").split(',')
    rowCount = config.getint("CSV", "rowsPerPage")
    pages = config.getint("CSV", "pages")
    iz = RunHistory(code, rowCount, pages)
    for i in iz:
        if i is None:
            break
        print(i.itemDetails["code"])
        print(len(i))
        csvOutput(i)
    
    #a = getItemHistory("http://ragi.al/item/iRO-Renewal/zAM/1", 3)
    #print("Debug(main):"+str(a))
    #for info in a:
    #    print("Debug(main):"+str(info))
    #print("Debug(main):"+str(a["All0|Data"]["set0|Set"]["row0|Name"]))
    #print("Debug(main):"+str(a["All0|Data"]["set0|Set"]["row0|Date"]))
    #print("Debug(main):"+str(a["All0|Data"]["set0|Set"]["row0|Urls"]))
    #print("Debug(main):"+str(a["All0|Data"]["set0|Set"]["row0|Price"]))
    #not req
    #print("Debug(main):"+str(a["All0|Data"]["set0|Set"]["Current Price1|Urls"]))
    #items = getItemHistory("http://ragi.al/item/iRO-Renewal/zAM/1", 16)
    #for i in items:
        #print("debug(main area):"+i)
