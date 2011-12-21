#!/usr/bin/env python

"""
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2011-12-19 $"
"""

import sys
import urllib2
import urllib
from BeautifulSoup import BeautifulSoup
import threading
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
            print("Error: Date should in the format dd/mm/yyyy")
            self.__del__()
            raise
        
        self.params = dict()
        self.sections = dict()
        
        #if not self.isAvailable():
        #    self.__del__()
        #    raise
        
        self.params.update({'txtdate':self.date.strftime("%m/%d/%Y")})
        try:
            self.run(True)
        except e:
            print e.reason
        else:                       
            self.getPages()

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
                self.page=urllib2.urlopen(url + '?queryed=1&eddate=' + self.params['txtdate'],None,10)
            else:
                self.page = urllib2.urlopen(url,params,10)
        except urllib2.URLError,e:
            print 'Error: Failed to open %s\nReason: %s' % (url,e.reason)
        else:
            self.dom = BeautifulSoup(self.page)
            inputTags = self.dom.findAll('input')

            for i in inputTags:
                if i.has_key('name'):
                    if i.has_key('value'):
                        self.params[i['name']] = i['value']
                    else:
                        self.params[i['name']] = ''

    
    def getPage(self,semaphore,page=1,edition=MAIN):
        semaphore.acquire()
        try:
            #log('page=%s,txtpageno= %s' % (page,self.params['txtpageno']) )
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

            sectionList =  list(sorted(set(sectionList)))
            self.sections.update({page:sectionList})
        finally:
            semaphore.release()

    def isAvailable(self):
        flag=True
        try:
            urllib2.urlopen(self.getPageUrl(),'',5)
        except urllib2.URLError,e:
            flag=False
        return flag
        

        
    def hasVellimani(self):
        return self.date.strftime("%w") == "5" # 5 - Friday
    
    def hasKondattam(self):
        return self.date.strftime("%w") == "0" # 0 - Sunday
    
    def getPages(self,edition=MAIN):
        maxRange = 5

        if self.params['txtedition'] == str(Dinamani.MAIN):
            maxRange = 15
        #log('maxRange = %d' % maxRange)

        threads = []
        semaphore = threading.Semaphore(14)
        for i in range(1,maxRange):
            #self.sections.update({i:self.getPage(i,edition)})
            threads.append(threading.Thread(target=self.getPage,args=(semaphore,i,edition)))
            threads[-1].start()
                           
        #log('getPages Done.')

    def getEditionLabel(self):
          if len(self.sections) == 14:
              return "-cni-mn-"
          elif self.hasVellimani():
              return "-cni-vm-"
          elif self.hasKondattam():
              return "-cni-sk-"
          else:
              return "-cni-mn-"
            
    def getUrlFragment(self):
        return "%s%s/%s/%s%s" % (Dinamani.baseurl,'epaperimages',
                                ''.join(map( str, map(int,self.date.strftime("%d/%m/%Y").split('/')))),
                                self.date.strftime("%d%m%Y"),self.getEditionLabel())

    def getPageUrl(self,page=1,size=1):

        if not 1<=page<=len(self.sections): return list()
        
        if not 0<size<3: size=1
            
        if size == 1:
            return "%s%02ds.jpg" % (self.getUrlFragment(),page)
        else:
            return "%s%02dll.jpg" % (self.getUrlFragment(),page)
        
    def getAllLinks(self,pageDict=None):
          if pageDict == None:
              pageDict = self.sections
            
          imageUrls = list();  

          url = self.getUrlFragment()
                                
          for page in pageDict:
              imageUrls.append('%s%02ds.jpg' % (url,int(page)))  # Entire Page - Small
              imageUrls.append('%s%02dll.jpg' % (url,int(page))) # Entire Page - Large
              for section in pageDict[page]:
                  imageUrls.append('%s%02d/%s.jpg' % (url,int(page),section))

          return imageUrls
        
    def getLinks(self,page=1):
        if not 1<=page<=len(self.sections):
            return list()
        else:
            return self.getAllLinks({page:self.sections[page]})
        

def main():
    print ''
    
    
    
if __name__ == '__main__':
    main()

                                                            
