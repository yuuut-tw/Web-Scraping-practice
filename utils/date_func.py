
from datetime import datetime, timedelta



def dateTD():
    DD=(datetime.today()).date()
    MMday=(datetime.today()).date().strftime("%Y-%m")
    
    return DD.strftime("%Y-%m-%d"), DD.strftime("%Y%m%d"), DD.strftime("%m%d"), MMday


def datecoll(startday,endday):
    x=list()
    count=0
    while datetime.strptime(endday,'%Y-%m-%d')>=(datetime.strptime(startday,'%Y-%m-%d')+timedelta(days=count)):
        DD=(datetime.strptime(startday,'%Y-%m-%d')+timedelta(days=count)).date()
        if (DD.strftime("%A")!='Sunday' and DD.strftime("%A")!='Saturday'):
            x.append([DD.strftime("%Y-%m-%d"), DD.strftime("%Y%m%d"), DD.strftime("%m%d"), DD.strftime("%Y-%m"),
                      DD])
        count=count+1
    return x
