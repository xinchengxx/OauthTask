import requests
r=requests.get('http://localhost:5000/client/login')
print (r.text)
print ('==========')
print (r.url)
print  ("==========")
url_login=r.url.split('?')[0]+'?user=magigo&pw=123456'
print(url_login)
r2=requests.get(url_login)
print (r2.text)

print(r2.history)
print("===========")
r=requests.get('http://localhost:5000/test1',params={'token':r2.text})
print(r.text)