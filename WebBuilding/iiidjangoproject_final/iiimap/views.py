#-*- coding: UTF-8 -*- 
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from iiimap.models import Attraction,Area,Article,Art_To_Att,Tag_To_Att,Tag,apriori,weather,Text_Cloud_Att
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
import math
from datetime import datetime
from datetime import timedelta
import json
import simplejson, urllib
import googlemaps
import requests
import time
import datetime

import re
#選標籤頁面-----------------------------------------------------------------------
def viewTag(request):#輸出頁面(1)
	taga = Tag.objects.all()
	return render_to_response("testDailog.html",locals())
#-----------------------------------------------------------------------
#以下是處理兩地之間的距離
def rad(d):
    return d*math.pi/180.0
def distance(lat1,lng1,lat2,lng2):
    radlat1=rad(lat1)
    radlat2=rad(lat2)
    a=radlat1-radlat2
    b=rad(lng1)-rad(lng2)
    s=2*math.asin(math.sqrt(math.pow(math.sin(a/2),2)+math.cos(radlat1)*math.cos(radlat2)*math.pow(math.sin(b/2),2)))
    earth_radius=6378.137 
    d=s*earth_radius
    if d<0:
        return -d
    else:
        return d
#----------------------------------------------------------------------------
#處理兩地的行駛時間
def signal_distance(lat1,lng1,lat2,lng2):
     
    orig_coord =lat1,lng1 
    dest_coord = lat2,lng2
    gmaps = googlemaps.Client(key='AIzaSyA5B_iud28ef_FCx0_rh53aM_kxAovxbUw')
    my_distance = gmaps.distance_matrix((orig_coord),(dest_coord),mode="transit")
    transit_distance = my_distance['rows'][0]['elements'][0]['distance']['value']
    transit_time = my_distance['rows'][0]['elements'][0]['duration']['value']
    return transit_time/60,transit_distance/float(1000)
	
def car_distance(lat1,lng1,lat2,lng2):
	orig_coord =lat1,lng1 
	dest_coord = lat2,lng2
	gmaps = googlemaps.Client(key='AIzaSyA5B_iud28ef_FCx0_rh53aM_kxAovxbUw')
	my_distance = gmaps.distance_matrix((orig_coord),(dest_coord),mode="transit")
	transit_distance = my_distance['rows'][0]['elements'][0]['distance']['value']
	a = transit_distance/float(1000)
	return a
#-----------------------------------------------------------------------------
#判斷超過60分鐘自動會變成小時
def min_to_hour(hour,minute):
    count  = minute / 60
    if minute >= 60:
        hour = hour + count
        minute = minute - (60*count)
    return hour,minute
#------------------------------------------------------------------------------	
#判斷這個景點是否通過以下條件:
"""
(1).到達時，這個景點已經開了
(2).要離開時，這個景點還沒關門
"""
def judgmentTime(now_time_hour,now_time_minute,oh,om,eh,em,playtime):
    afterplay_time_min = now_time_minute + playtime
    afterplay_time = min_to_hour(now_time_hour,afterplay_time_min)
    afterplay_time_hour = afterplay_time[0]
    afterplay_time_minute = afterplay_time[1]
    if now_time_hour == oh:
        if now_time_minute >= om:
            if  afterplay_time_hour == eh:
                if  afterplay_time_minute <= em:
                    return True
                else:
                    return False
            elif afterplay_time_hour < eh:
                return True
            else:
                return False
        else:
            return False
    elif now_time_hour > oh:
        if afterplay_time_hour == eh:
            if  afterplay_time_minute <= em:
                return True
            else:
                return False
        elif afterplay_time_hour < eh:
            return True
        else:
            return False        
    else:
        return False
#------------------------------------------------------------------------------
#判斷這個景點是不是最後一個景點	
def last_attr(Arrival_time_hour,Arrival_time_minute,u_end_hour,u_end_minute):
    
    if Arrival_time_hour +1 == u_end_hour:
        if Arrival_time_minute >= u_end_minute:
            return True
        else:
            return False    
    elif Arrival_time_hour+1 > u_end_hour:
        return True
    else:
        return False
#------------------------------------------------------------------------------
#天氣

def udc_time(time):
    x = datetime.datetime.fromtimestamp(time).strftime('%m-%d ')
    month = int(x.split('-')[0])
    day = int(x.split('-')[1])
    return str(month)+'-'+str(day)

def weather(date):
    url = "http://api.openweathermap.org/data/2.5/forecast/daily?q=taipei\
            &mode=json&units=metric&cnt=7&appid=44db6a862fba0b067b1930da0d769e98"
    res = requests.get(url)
    data = json.loads(res.text)
    x = data['list']
    for i in x:
        if date == udc_time(i['dt']):
            mintemp = i['temp']['min']
            maxtemp = i['temp']['max']
            morning = i['temp']['morn']
            eve = i['temp']['eve']
            night = i['temp']['night']
            day = i['temp']['day']
            return mintemp,maxtemp,morning,eve,night,day, str(i['weather'][0]['icon'])
#------------------------------------------------------------------------------
#右方文字						
def directions(lat1,lng1,lat2,lng2,divid):
    f = ""
    divid="dir"+str(divid)
    orig_coord =lat1,lng1 #起點
    dest_coord = lat2,lng2 #終點
    orig_coord_str = ' ,'.join(map(str, orig_coord)) 
    dest_coord_str = ' ,'.join(map(str, dest_coord))   
    #API request
    gmaps = googlemaps.Client(key='AIzaSyAdpCJO7Xt8oNHC7m4GVNnYR5Otaj715Kc')

    
    directions_result = gmaps.directions(orig_coord_str,
                                         dest_coord_str,
                                         language='zh-TW',
                                         mode="transit") #參數設
    j = directions_result[0]   
    transit_time = j['legs'][0]['duration']['value']/60
    transit_distance = round(j['legs'][0]['distance']['value']/float(1000),2)
    i = 1
    for leg in j['legs']:
        startAddress = leg['start_address']
        f += "<div style="'color:Maroon'">起點:"+startAddress.encode('utf-8') + "</div>"
        endAddress = leg['end_address']
        f += "<div style="'color:Maroon'">終點:" + endAddress.encode('utf-8') + "</div>"
        f += "<div style="'color:Maroon'">行駛里數:"+str(transit_distance)+"公里-行駛時間:"+str(transit_time)+"分鐘"+"</div>"
        f += '<table class="' +divid + '">' 
        for step in j['legs'][0]['steps']:
            html_instructions = step['html_instructions']
            transit_plan = "step:{}{}".decode('utf-8').format(i ,html_instructions)
            i = i+1
            f += '<tr style="font:17px 微軟正黑體;color:#222;text-shadow:3px 3px 3px #888;border-bottom: 1px solid silver;">'
            f += "<td>" + transit_plan.encode('utf-8') + "</td>"
        f += '</table>' 
    return f        
#------------------------------------------------------------------------------
#主要程式

def viewtag_attr(request):
	final_attr = []#存最後要輸出的景點編號
	final_attr_count = 0#總共有幾個景點
	date = request.POST.get("date")
	ptime = request.POST.get("time")#post 遊玩時間(時)
	u_start_hour = int(request.POST.get("start_hour"))#post 開始時間(時)
	u_start_minute = int(request.POST.get("start_minute"))#post 開始時間(分)
	u_end_hour = int(request.POST.get("end_hour"))#post 結束時間(時)
	u_end_minute = int(request.POST.get("end_minute"))#post 結束時間(分)
	now_time_hour = 0 #判斷時間用(時)
	now_time_minute = 0 #判斷時間用(分)
	rel_time_hour = 0 #流程目前時間(時)
	rel_time_minute = 0 #流程目前時間(分)
	lastAttr = False
	summary = ""
	p1 = "起點站：台北車站"
	car_dis = 0#行程距離
	tran_dis = 0
	x1 = 121.517292#台北車站的經緯度
	y1 = 25.048164
	attr_hot = int(request.POST.get('hot'))
	month = int(date.split('-')[1])
	day = int(date.split('-')[2])
	#處理天氣
	weathertemp = weather(str(month)+'-'+str(day))
	mintemp = weathertemp[0]
	maxtemp = weathertemp[1]
	morning = weathertemp[2]
	eve = weathertemp[3]
	night = weathertemp[4]
	day = weathertemp[5]
	icon = weathertemp[6]
	summary += '<div style="font:bold 20px 微軟正黑體">起始時間：'+ str(u_start_hour) +":"+ str(u_start_minute) +"分</div>"
	tags = request.POST.getlist('id',[])# post 點選的標籤，已照順序	
	while True:
		for tagid in tags:	#跑標籤
			apri_attr_data = []
			random_attr_data = []
			#依照每次跑的標籤 下query
			attr_list=[]#把標籤內的景點歸零
			if final_attr_count == 0:#如果是第一個隨機景點，則無須用關聯規則
				tagg = Tag_To_Att.objects.filter(tag_id = tagid)#把目前這個標籤的所有tag_to_att都撈出來
				for j in tagg:#跑這個標籤內的景點
					if j.Attr.Attr_hot == attr_hot:
						if distance(y1,x1,j.Attr.Attr_latitude,j.Attr.Attr_longitude) <8:#如果距離大於八時，就不要(怕行車時間過久)
							attr_dic = {}#把每個景點的資料存到dic{}裡
							attr_dic["id"] = j.Attr.Attr_id
							attr_dic["name"] = j.Attr.Attr_name
							attr_dic["longitude"] = j.Attr.Attr_longitude
							attr_dic["latitude"] = j.Attr.Attr_latitude
							attr_dic["dis"] = distance(y1,x1,attr_dic["latitude"],attr_dic["longitude"])
							open_time = j.Attr.Attr_opentime
							close_time = j.Attr.Attr_endtime
							attr_dic["oh"] = int(open_time.split(':')[0])
							attr_dic["om"] = int(open_time.split(':')[1])			
							attr_dic["eh"] = int(close_time.split(':')[0])
							attr_dic["em"] = int(close_time.split(':')[1])
							if ptime == 1:
								attr_dic["playtime"] = int(j.Attr.Attr_stay1)
							elif ptime == 2:
								attr_dic["playtime"] = int(j.Attr.Attr_stay2)
							else:
								attr_dic["playtime"] = int(j.Attr.Attr_stay3)
							attr_list.append(attr_dic)
				attr_list.sort(key=lambda a:a["dis"])#案距離排序
				
			else:#如果不是第一個景點了話，一開始都要以關聯規則下去判斷，如果關聯規則都沒有的話 才要跑一般的隨機型程
				for randomcount in range(1,3):#randomcount為1時，就是要處理apriori的資料，如果為2時，就是要處理一般的隨機型程
					tagg = []
					if randomcount ==1:#處理apriori
						apriori_attr = apriori.objects.filter(Attr_id = final_attr[final_attr_count-1])#把上個景點拿去跑查詢apriori
						apri_id=[]#用來裝apriori的id
						for a in apriori_attr:
							apri_id.append(a.ap_id)
						k = apriori.objects.filter(ap_id__in=apri_id)
						apAttr_id = set()#用來裝這些景點id去查詢下來的所有關聯景點
						for aid in k:
							apAttr_id.add(aid.Attr_id)
						attr = Tag_To_Att.objects.filter(Attr_id__in = apAttr_id)
						for at in attr:
							if at.tag.id == tagid:
								tagg.append(at)
					else:#處理隨機
						tagg = Tag_To_Att.objects.filter(tag_id = tagid)
						
					for j in tagg:#跑這個標籤內的景點
						if j.Attr.Attr_hot == attr_hot:#這個景點的熱門度有沒有等於使用者的
							if distance(y1,x1,j.Attr.Attr_latitude,j.Attr.Attr_longitude) <8:
								attr_dic = {}#把每個景點的資料存到dic{}裡
								attr_dic["id"] = j.Attr.Attr_id
								attr_dic["name"] = j.Attr.Attr_name
								attr_dic["longitude"] = j.Attr.Attr_longitude
								attr_dic["latitude"] = j.Attr.Attr_latitude
								attr_dic["dis"] = distance(y1,x1,attr_dic["latitude"],attr_dic["longitude"])
								open_time = j.Attr.Attr_opentime
								close_time = j.Attr.Attr_endtime
								attr_dic["oh"] = int(open_time.split(':')[0])
								attr_dic["om"] = int(open_time.split(':')[1])			
								attr_dic["eh"] = int(close_time.split(':')[0])
								attr_dic["em"] = int(close_time.split(':')[1])
								if ptime == 1:
									attr_dic["playtime"] = int(j.Attr.Attr_stay1)
								elif ptime == 2:
									attr_dic["playtime"] = int(j.Attr.Attr_stay2)
								else:
									attr_dic["playtime"] = int(j.Attr.Attr_stay3)
								if randomcount ==1:#如果是關聯規則，就把關連規則的景點資料加在apri_attr_data裡
									apri_attr_data.append(attr_dic)#加到標籤list裡
								else:#如果是隨機的話，就加在random_attr_data裡
									random_attr_data.append(attr_dic)
					if randomcount == 1:
						apri_attr_data.sort(key=lambda a:a["dis"])
					else:
						random_attr_data.sort(key=lambda a:a["dis"])
				attr_list = apri_attr_data+random_attr_data
				
			
			for attr_data in attr_list:#跑上面加入一個標籤裡面的景點資料
				if final_attr_count == 0:#如果是第一個景點的話，就把開始時間設為判斷時間
					now_time_hour = u_start_hour
					try:
						drive_time = signal_distance(y1,x1,attr_data["latitude"],attr_data["longitude"])[0]#從google抓兩地之間的距離時間
					except:
						continue
					now_time_minute = u_start_minute + drive_time
				else:#如果是第二景點後的
					now_time_hour = rel_time_hour#就拿流程時間當判斷時間
					try:
						drive_time = signal_distance(y1,x1,attr_data["latitude"],attr_data["longitude"])[0]
					except:
						continue
					now_time_minute = rel_time_minute + drive_time
				
				now_time = min_to_hour(now_time_hour,now_time_minute)
				now_time_hour = now_time[0]
				now_time_minute = now_time[1]
				
				playtime = attr_data["playtime"]
				

				oh = attr_data["oh"]
				om = attr_data["om"]
				eh = attr_data["eh"]
				em = attr_data["em"]
				# 判斷是否可以進去
				
				if judgmentTime(now_time_hour,now_time_minute,oh,om,eh,em,playtime):
					if attr_data["id"] not in final_attr:#這個景點是否已經出現過了
						final_attr.append(attr_data["id"])
						final_attr_count += 1
						tran_dis = tran_dis + signal_distance(y1,x1,attr_data["latitude"],attr_data["longitude"])[1]
						car_dis = car_dis + car_distance(y1,x1,attr_data["latitude"],attr_data["longitude"])
						
						p2 = attr_data["name"].encode('utf-8')
						rel_time_hour = now_time_hour 
						rel_time_minute = now_time_minute + playtime
						rel_time = min_to_hour(rel_time_hour,rel_time_minute)
						rel_time_hour = rel_time[0]
						rel_time_minute = rel_time[1]
						
						summary += "<div style="'margin-top:15px;'"><font color='blue' size='5'>" + p1 +"→"+ p2 + "</font></div>"
						summary += directions(y1,x1,attr_data["latitude"],attr_data["longitude"],attr_data["id"])
						summary += '<div style="font:bold 20px 微軟正黑體">到達時間：'+ str(now_time_hour) +":"+ str(now_time_minute) +"分</div><div style='font:bold 20px 微軟正黑體'>遊玩景點：" + p2 + "(時間:"+ str(playtime) +"分鐘)</div><div style='font:bold 20px 微軟正黑體'> 離開時間： " +str(rel_time_hour)+":"+ str(rel_time_minute) +"分</div>"						
						p1 = p2
						x1 = attr_data["longitude"]
						y1 = attr_data["latitude"]
						
						break
				
			Taipei_longitude = 121.517878
			Taipei_latitude =25.046309
			try:
				back_time = signal_distance(y1,x1,Taipei_latitude,Taipei_longitude)[0]
			except:
				back_time = 30
				pass
			back_time_minute = rel_time_minute + back_time 
			back_time_judgment = min_to_hour(rel_time_hour,back_time_minute)
			Arrival_time_hour = back_time_judgment[0]
			Arrival_time_minute = back_time_judgment[1]
			
			if last_attr(Arrival_time_hour,Arrival_time_minute,u_end_hour,u_end_minute):
				lastAttr = True
				break
		if lastAttr == True:
			break
	final_attr_datas = set()
	
	tran_dis = tran_dis + signal_distance(y1,x1,Taipei_latitude,Taipei_longitude)[1]
	car_dis = car_dis + car_distance(y1,x1,attr_data["latitude"],attr_data["longitude"])
	car_dis_co2 = car_dis * 0.2
	tran_dis_co2 = tran_dis * 0.05
	car_distance_co2 = round(car_dis_co2 - tran_dis_co2,2)
	co2tree = round(car_distance_co2 / 18.3,2)
	summary += "<div style="'margin-top:15px;'"><font color='blue' size='5'>" + p1 +"→終點站：台北車站</font></div>"
	summary += directions(y1,x1,Taipei_latitude,Taipei_longitude,"_final")
	summary += "<div style='font:bold 20px 微軟正黑體'>結束時間： " +str(Arrival_time_hour)+":"+ str(Arrival_time_minute) +"分</div>"
	for final in final_attr:
		final_attr_data = Attraction.objects.filter(Attr_id = final)
		for aaa in final_attr_data:
			final_attr_datas.add(aaa)
	
	return render_to_response("testmap.html",locals())

	
def aprioritest(request):#測試用
	playtime = int(request.POST.get("time"))#post 遊玩時間(時)
	date = request.POST.get("date")#post 遊玩時間(時)
	month = int(date.split('-')[1])
	day = int(date.split('-')[2])
	weath = weather.objects.filter(W_month = month).filter(W_day = day)
	hot = int(request.POST.get("hot"))#post 遊玩時間(時)
	u_start_hour = int(request.POST.get("start_hour"))#post 開始時間(時)
	u_start_minute = int(request.POST.get("start_minute"))#post 開始時間(分)
	u_end_hour = int(request.POST.get("end_hour"))#post 結束時間(時)
	u_end_minute = int(request.POST.get("end_minute"))#post 結束時間(分)
	post_test = request.POST.getlist('id')
	
	attr_test = []
	x1 = 121.517292
	y1 = 25.048164
	drive_time = []
	for i in post_test:
		attr = Tag_To_Att.objects.filter(tag_id = i)
		for j in attr:
			attr_test.append(j)
			x2 = j.Attr.Attr_longitude
			y2 = j.Attr.Attr_latitude
			j.time = signal_distance(y1,x1,y2,x2)[0]
			drive_time.append(signal_distance(y1,x1,y2,x2)[0])
			x1 = x2
			y1 = y2
	x2 = 121.517292
	y2 = 25.048164
	drive_time.append(signal_distance(y1,x1,y2,x2)[0])
	return render_to_response("apriori.html",locals())
	
def textcloud(request):#景點資訊欄
	textc = Text_Cloud_Att.objects.filter(Attr_id = request.GET['Attr_id'])
	attr = Attraction.objects.get(Attr_id = request.GET['Attr_id'])
	t_t = Tag_To_Att.objects.filter(Attr_id = request.GET['Attr_id'])
	return render_to_response("textcloud.html",locals())
	
def test(request):#測試用
	
	return render_to_response("testmap.html",locals())