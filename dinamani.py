import sys
import urllib2
import urllib
from BeautifulSoup import BeautifulSoup
from datetime import datetime, date
import time

def log(str):
    print "%s >>> %s" % (time.strftime("%x - %X", time.localtime()), str)

class Dinamani:
    baseurl = 'http://epaper.dinamani.com/'
    MAIN, VELLIMANI, KONDATTAM = (1,3,6)
    
    def __init__(self,date=datetime.today().strftime("%d/%m/%Y")):
        
        try:
            self.date = datetime.strptime(date, "%d/%m/%Y")
        except ValueError,e:
            sys.exit("Error: Date should in the format dd/mm/yyyy")
        self.params = dict()
        self.sections = dict()
        self.params.update({'txtdate':self.date.strftime("%m/%d/%Y")})
        self.run(True)

    def setDate(self,date):
        try:
            self.date = datetime.strptime(date, "%d/%m/%Y")
            self.params.update({'txtdate':self.date.strftime("%m/%d/%Y")})
            self.run(True)
        except ValueError,e:
            sys.exit("Error: Date should in the format dd/mm/yyyy")
            
    def run(self,init=False):
        params = urllib.urlencode(self.params)
        #print params
        if (self.date-datetime.today()).days == -1:
            url = Dinamani.baseurl + 'epapermain.aspx'
        else:
            url = Dinamani.baseurl + 'epapermainarchives.aspx'
            
        try:
            if init: # for First Iteration 
                self.page=urllib2.urlopen(url + '?queryed=1&eddate=' + self.params['txtdate'])
            else:
                self.page = urllib2.urlopen(url,params)
        except urllib2.URLError,e:
            print 'URL %s failed: %s' % (url,e.reason)
        
        self.dom = BeautifulSoup(self.page)
        inputTags = self.dom.findAll('input')
        for i in inputTags:
            if i.has_key('name'):
                if i.has_key('value'):
                    self.params[i['name']] = i['value']
                else:
                    self.params[i['name']] = ''

    
    def getPage(self,page=1,edition=MAIN):
        
        sectionList = []

        # Vellimani
        if edition == Dinamani.VELLIMANI and not self.hasVellimani(): return sectionList

        # Kondattam
        if edition == Dinamani.KONDATTAM and not self.hasKondattam(): return sectionList
        
        # Update Viewstate if edition changes
        if not self.params['txtedition'] == edition:
            self.params.update({'txtpageno':1, 'txtedition':edition})
            self.run()

        self.params.update({'txtpageno':page, 'txtedition':edition})
        self.run()
        
        areaTags = self.dom.findAll('area')

        for a in areaTags:
            if a.has_key('onclick'):
                sectionList.append(a['onclick'].split("\'")[3])

        return list(sorted(set(sectionList)))
        
    def hasVellimani(self):
        return self.date.strftime("%w") == "5" # 5 - Friday
    
    def hasKondattam(self):
        return self.date.strftime("%w") == "0" # 0 - Sunday
    
    def getPages(self,edition=MAIN):
        maxRange = 5

        if self.params['txtedition'] == str(Dinamani.MAIN):
            maxRange = 15
        log('maxRange = %d' % maxRange)
        for i in range(1,maxRange):
            self.sections.update({i:self.getPage(i,edition)})
        log('getPages Done.') 
        return self.sections
        

def main():
    dm = Dinamani("16/12/2011")
    #print dm.getPage(4,Dinamani.VELLIMANI)
    #print dm.getPage(3,Dinamani.MAIN)
    print dm.getPages()
    
    
    
    
if __name__ == '__main__':
    main()

                                                            
