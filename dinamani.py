import sys
import urllib2
import urllib
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from datetime import date

class Dinamani:
    baseurl = 'http://epaper.dinamani.com/'
    paper = { 'main':1, 'kondattam':3,'vellimani':6}
    
    def __init__(self,date=datetime.today().strftime("%d/%m/%Y")):
        
        try:
            self.date = datetime.strptime(date, "%d/%m/%Y")
        except ValueError,e:
            sys.exit("Error: Date should in the format dd/mm/yyyy")
        self.params = dict()
        self.sectionList = dict()
        self.page = ''
        self.dom=''
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

    
    def getSections(self,page=1,edition='main'):
        
        #if (Dinamani.paper[edition] - int(self.date.strftime("%w")))< 1:
        #    print edition + ' is not available for the specified date '
        #    return []
        #if Dinamani.paper[edition] - int(self.date.strftime("%w")) != 3:
        #    print edition + ' is not available for the specified date '
        #    return []


        self.params.update({'txtpageno':page})
        
        #self.params.update({'txtedition':Dinamani.paper[edition]})
        self.run()
        sectionList = []
        areaTags = self.dom.findAll('area')

        for a in areaTags:
            if a.has_key('onclick'):
                sectionList.append(a['onclick'].split("\'")[3])

        return list(sorted(set(sectionList)))
        
    def hasVellimani(self):
        return self.date.strftime("%w") == "5"
    
    def hasKondattam(self):
        return self.date.strftime("%w") == "0"
    
    def sectionListing(self,edition='main'):
         maxRange = 5
         if self.params['txtedition'] == 1:
             maxRange = 15
         for i in range(1,maxRange):
             self.sectionList.update({i:self.getSections(i,Dinamani.paper[edition])})
         
    
        

def main():
    dm = Dinamani("13/12/2011")
    #print dm.getSections(3)
    print dm.hasKondattam()
    #dm.sectionListing()
    #print dm.sectionList
    
    
    
if __name__ == '__main__':
    main()

                                                            
