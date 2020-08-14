import requests
import threading
from threading import Thread
import json
import time as tm

from datetime import datetime
from datetime import timedelta
import speech 

class Stock:
		
	def __init__(self):
		self.apiKey = ''
		self.peerList = []
		self.headlines = []
		self.goodCount = 0
		self.badCount = 0
		self.peerChgs= []
		self.performance = None
		self.bear = None
		self.bull = None
		
	
	
	#gets description, name
	def company(self, symbol='fun'):
		try:
			symbol = symbol.upper()
			r = requests.get(f'https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={self.apiKey}')
			companyInfo = r.json()
	
			name = companyInfo['name']	
			industry = companyInfo['finnhubIndustry']
			
			return name, industry
			
		except Exception:
			pass
	
			
	#retrieves historical/current price data		
	def price(self, symbol='fun'):
		try:
				
			openPrice = None
			currentPrice = None
						
			symbol = symbol.upper()
			r = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.apiKey}')
				
			r = r.json()
		
			prevClose = r['pc']
			currentPrice = r['c']	
		
			change = self.percentChange(prevClose,currentPrice)
			return change	
			
		except Exception:
			pass
			
					
	#calculate percent change 
	def percentChange(self, original, final):
		try:
				original = float(original)
				final = float(final)
				change = final - original
				change = change / original * 100
				change = float('{:.2f}'.format(change))
				
				return change
		
		except Exception:
		 	pass
		
		
	#compares to nasdaq, sp500, etc
	def marketCompare(self, symbol ='fun'):
		try:
			pass
				
		except Exception:
			pass
	
	
	#calculate changes in peers
	def peerChange(self, symbol='fun'):
		try:
			
			symbol = symbol.upper()
			
			r = requests.get(f'https://finnhub.io/api/v1/stock/peers?symbol={symbol}&token={self.apiKey}')
	
			peers = r.json()
			#peers.remove(symbol)
			if peers:
				print('\n\nPeers:\n')
				for peer in peers:
					name, industry = self.company(peer)
					
					self.peerList.append(name)
					
					change = self.price(peer)				
					if change == None:
						change = 0
					#grabs symbol current performance
					if symbol == peer.upper():
						self.performance = change
						
					
				
					print(f'{peer} - {name} | Change: {change}%\n')
					if not (peer.upper() == symbol):
						self.peerChgs.append(change)
		
					tm.sleep(.2)
					
		except Exception:
			pass
				
									
	#retrieve and analyze company news
	def companyNews(self, symbol='fun'):
		try:
						
			goodWords = ['win','buy','increase','bid', 'promote', 'record','high','surpass','outperform','good','gain','jumps', 'raise','purchase', 'acquire']
			badWords = ['lose','avoid','decrease','sell','decline','falls','low','misses','underperform','bad','crash','drop','lost', 'lower','lawsuit','sold']
			
			today = datetime.today()
			fewDays = today - timedelta(days=3)
			
			today= today.strftime('%Y-%m-%d')
			fewDays = fewDays.strftime('%Y-%m-%d')
			
			r = requests.get(f'https://finnhub.io/api/v1/company-news?symbol={symbol}&from={fewDays}&to={today}&token={self.apiKey}')
			
			site = r.json()
			name, industry = self.company(symbol)
		
			name = list(name.split(' '))
			shortName = name[0]
			
			print('\n\nCompany News:\n')
			for page in site:
				if shortName.upper() in page['headline'].upper():
					self.headlines.append(page['headline'])
					for x in goodWords:
						if x.upper() in page['headline'].upper():
							self.goodCount +=1
					for x in badWords:
						if x.upper() in page['headline'].upper():
							self.badCount +=1
			
			if self.headlines:	
				self.headlines = list(dict.fromkeys(self.headlines))	
				for headline in self.headlines:		
					print('\n* ', headline)
				print(f'\nGood: {self.goodCount} Bad: {self.badCount}\n\n')
			
		except Exception:
			pass
	
			
	#provides earning history/next call
	def earnings(self, symbol = 'fun'):
		try:
			symbol = symbol.upper()
			r = requests.get(f'https://finnhub.io/api/v1/stock/earnings?symbol={symbol}&token={self.apiKey}')
	
		except Exception:
			pass
		
	
	def financials(self, symbol='fun'):
		try:
			symbol = symbol.upper()
			r = requests.get(f'https://finnhub.io/api/v1/stock/financials?symbol={symbol}&statement=bs&freq=quarterly&token={self.apiKey}')
						
		except Exception:
			pass
	
					
	def news(self, symbol= 'fun'):
		try:
			
			symbol = symbol.upper()
			r = requests.get(f'https://finnhub.io/api/v1/news-sentiment?symbol={symbol}&token={self.apiKey}')
			r = r.json()
			rating = r['sentiment']
			print('\n\nAnalyst Rating:\n')
			for rate, score in rating.items():		
					score = float('{:.1f}'.format(score * 100))
					if rate == 'bearishPercent':
						rate = 'Bear'
						self.bear = score
						
					elif rate == 'bullishPercent':
						rate = 'Bull'
						self.bull = score
						
					
					print(rate,': ', score)
					
		except Exception:
			pass
			
			
	def report(self):
		try:
			analystReport =''
			peerReport = ''
			newsReport = ''
			peerChgAvg = sum(self.peerChgs)/len(self.peerChgs)
		
			
			if self.bear < self.bull:
				analystReport = 'Analysts are {:.0f}% bullish on this stock\'s near term opportunities.'.format(self.bull)
			
			elif self.bear == self.bull:
				analystReport = 'Analysts are split on what this stock is going to do.'
			elif self.bear > self.bull:
				analystReport = 'Analysts are {:.0f}% bearish on this stock\'s potential for growth.'.format(self.bear)
			else:
				analystReport= 'No analyst information was found for this company.'
			
					
			if self.badCount == 0 and self.goodCount == 0:
				newsReport = 'There was no relevant news found; might want to do some extra searching.'
			elif self.badCount  >  self.goodCount:
				newsReport = ' I did a quick look through the news headlines and found more bad keywords than good. If this trails its peers this could be more put option or a hold position.'
			elif self.badCount  <  self.goodCount:
				newsReport = ' I looked through the news headlines and found more good info than bad. A healthy peer lead could make this more option buy.'
			elif self.badCount  == self.goodCount:
				newsReport = ' I saw a fair amount of good and bad news, but you may want to read and judge yourself to make sure I missed nothing important.'
			
			if self.performance == 0:
				peerReport = ' Either the stock is stock\'s performance hasn\'t changed or there may be an issue comparing peer performance.'
			elif self.performance < peerChgAvg:
				peerReport =' Today, this company is performing worse than the average of its peers.'
			
			elif self.performance == peerChgAvg:
				peerReport =' Today, this company is performing the same as its peers.'
			
			elif self.performance > peerChgAvg:
				peerReport =' Today, this company is performing better than the average of its peers.'
				
			else:
				peerReport = ' Either this company is unique and has no peers, or there was a problem pulling peer data.'
			
			report = ''
			
			if analystReport:
				report += analystReport
			
			if newsReport:
				report += newsReport
				
			if peerReport:
				report += peerReport
				
												
			if report:	
				speech.say(report)
		
			
		except Exception:
			speech.say('I have nothing to report.')
		

	#runs all functions		
	def search(self,symbol):
		if __name__ == '__main__':
			try:
				
				s = Stock			
				Thread(target = s.peerChange(self,symbol)).start()
				Thread(target = s.companyNews(self,symbol)).start()
				Thread(target = s.news(self,symbol)).start()
				Thread(target = s.report(self)).start()
				
			except TypeError:
				pass		

try:
	
	ticker = input('Enter symbol: ')
	name, industry = Stock().company(ticker)
	speech.say(name,'en_AU')
	#finish_speaking()
	print(f'\n\nCompany: {name}')

	print(f'\nIndustry: {industry}')
	Stock().search(ticker)

except Exception:
	print('\nTicker not found/foreign companies not accepted')
