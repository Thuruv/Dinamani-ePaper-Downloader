import sys
import os
import urllib2
import urllib
from iniparse import INIConfig
from datetime import datetime
from datetime import date
from datetime import timedelta
from BeautifulSoup import BeautifulSoup

today = datetime.now()
ePaperSetting = INIConfig()

if len(sys.argv) != 2:
    print 'Getting today\'s ePaper...'
    inputDate = today
else:
	try:
		inputDate = datetime.strptime(sys.argv[1],'%d/%m/%y')
	except ValueError:
		sys.exit('\n\tUsage: ' + sys.argv[0] + ' dd/mm/yy')

ePaperDate = inputDate.strftime('%m/%d/%Y')       

dirName = inputDate.strftime('%d-%b-%Y')
#For Supplementary 
fileTag = ''

try:
	os.mkdir(dirName)
except OSError:
	#sys.exit('Error: Unable to create dir \'' + dirName + '\'\nExiting...')
	pass

#print 'ePaperDate = '+ ePaperDate

availableFromDate =  today - timedelta(days=525)

if inputDate < availableFromDate or inputDate > today:
	sys.exit('\n\tError: ePaper is available only between ' + availableFromDate.strftime('%d-%b-%Y') + ' and ' + today.strftime('%d-%b-%Y'))


def uniq(inlist):
    # order preserving
    uniques = []
    for item in inlist:
        if item not in uniques:
            uniques.append(item)
    return uniques



if inputDate == datetime.now():
	url = 'http://epaper.dinamani.com/epapermain.aspx?queryed=1&eddate='
	url += ePaperDate.replace('/','%2F')
	archiveUrl = 'http://epaper.dinamani.com/epapermain.aspx'
else:
	url = 'http://epaper.dinamani.com/epapermainarchives.aspx?queryed=1&eddate='
	url += ePaperDate.replace('/','%2F')
	archiveUrl = 'http://epaper.dinamani.com/epapermainarchives.aspx'
	
#print url 
#print archiveUrl

imageBaseUrl = 'http://epaper.dinamani.com/epaperimages/'
#18112011/18112011-cni-vm-01/23123375.JPG

page = urllib2.urlopen(url)
soup = BeautifulSoup(page)
#soup.originalEncoding
inputTags = soup.findAll('input')


#soup = soup.prettify()


postQueryDict = dict()

for i in inputTags:
    if i.has_key('name'):
        if i.has_key('value'):
            postQueryDict[i['name']] = i['value']
        else:
            postQueryDict[i['name']] = ''
            
editionTag = '-cni-mn-'


while (int(postQueryDict['txtpageno']) <= int(postQueryDict['txtmaxpageno']) + 1):
	
	

    postQueryDict['txtdate'] = ePaperDate
    pageNumber = int(postQueryDict['txtpageno'])
    editionDate = datetime.strptime(ePaperDate,'%m/%d/%Y')
    editionDateStr = editionDate.strftime('%d/%m/%Y')
    #postQueryDict['txtpageno'] = pageNumber
    postQueryString = urllib.urlencode(postQueryDict)
    #print 'postQueryString = ' + postQueryString
    #print postQueryDict
    
    responseData = urllib2.urlopen(archiveUrl, postQueryString)
    
    if postQueryDict['txtedition'] == 3 or postQueryDict['txtedition'] == 6:
		if postQueryDict['txtpageno'] == 1:
			soup = BeautifulSoup(responseData)
			inputTags = soup.findAll('input')
			postQueryDict = dict()

			for i in inputTags:
				if i.has_key('name'):
					if i.has_key('value'):
						postQueryDict[i['name']] = i['value']
					else:
						postQueryDict[i['name']] = ''

		
    postQueryDict['txtparentid'] = int(postQueryDict['txtparentid']) +  1
    postQueryDict['txtpageno'] = int(postQueryDict['txtpageno']) + 1
    responsePage = responseData.read()
    #print responsePage
   
    
    
    soup = BeautifulSoup(responsePage)
    areaTags = soup.findAll('area')

    imageIdList = []
    for a in areaTags:
        if a.has_key('onclick'):
            onclickText = a['onclick']
            imageIdList.append(onclickText.split('\'')[3])

    imageIdList = uniq(imageIdList)

    imagePageUrl = editionDate.strftime('%d%m%Y') + editionTag + '%02d' % (pageNumber)
    imageUrl  = imageBaseUrl + ''.join(map( str, map(int,editionDateStr.split('/')))) 
    imageUrl += '/' + imagePageUrl
    
    # Patch for First Page of Supplementary
    imageUrl = imageUrl.replace('vm-05','vm-01')
    imageUrl = imageUrl.replace('sk-05','sk-01')
    #End of Patch
    
    imagePageUrlSmall = imageUrl + 's.jpg'
    imagePageUrlLarge = imageUrl + 'll.jpg'

	

    #Page URL
    fileName = dirName + '\\' + '%02d' % (pageNumber)
    #print '\nPage :::' + fileName
    #print imagePageUrlSmall
    print '\nGetting Page ::' + fileName + '...'
    urllib.urlretrieve(imagePageUrlSmall, fileName + fileTag + '-small.jpg')
    #print imagePageUrlLarge
    urllib.urlretrieve(imagePageUrlLarge, fileName + fileTag + '-large.jpg')
    
    iLoop=0
    for imageId in imageIdList:
		iLoop = iLoop + 1
		imageFullUrl = imageUrl + '/' + imageId + '.jpg'
		print '\tGetting Section :::' + str(iLoop) + '...'
		#print imageFullUrl
		fileName += fileTag
		# Patch for 5th Loop of Supplementary reset to Page 01 of Sup.
		fileName = fileName.replace('05sup','01sup')
		# End of Patch
		urllib.urlretrieve(imageFullUrl, fileName + '-' + '%02d' % (iLoop) + '.jpg')
		
        
	
    if (postQueryDict['txtpageno'] == 15):
		fileTag = 'sup'
		if inputDate.strftime('%w') == '0':
			editionTag = '-cni-sk-'
			postQueryDict['txtedition'] = 6
			postQueryDict['txtpageno'] = 1
			postQueryDict['txtmaxpageno'] = 4
		elif inputDate.strftime('%w') == '5':
			editionTag = '-cni-vm-'
			postQueryDict['txtedition'] = 3
			postQueryDict['txtpageno'] = 1
			postQueryDict['txtmaxpageno'] = 4
		else:
			# Do Nothing
			print 'Done...'	
			
    if ( postQueryDict['txtpageno'] == 15 ):
		break
