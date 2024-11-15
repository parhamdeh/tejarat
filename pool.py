from telethon import TelegramClient, events
from pymongo import MongoClient
from telethon.tl.custom import Button
from telethon.events import StopPropagation, NewMessage
import requests
import datetime
import time
import config

client = TelegramClient('t', config.api_id, config.api_hash)
client.start(bot_token=config.bot_token)
mongo_client=MongoClient()
@client.on(events.NewMessage())
async def calc(event):
    B=[
        [
            Button.inline("خرید","k"),
            Button.inline("فروش","f"),
        ],
    ]
    if event.message.message== '/start':
        balance = mongo_client.tejarat.bazargan.find({'id':event.sender_id})
        total = 0
        hesab = 0
        alan=0
#mg meghdare arz ha hast ke ta alan ok hast
        mg = 0
        pro = 0
        for i in balance:
            arz_delkhah = i.get('arz')
            meghdar = i.get('value')
            a = i.get('gheimat_dolar')
            url = "https://rest.coinapi.io/v1/exchangerate/"+arz_delkhah+"/USD"
            payload = {}
            headers = {
            'X-CoinAPI-Key': config.coin_api_key
            }

            response_alan = requests.request("GET", url ,headers=headers, data=payload)
            dolare_alan=response_alan.json().get('rate')
            url = 'https://api.navasan.tech/latest?api_key=' + config.navasan_key + '&item=usd' 
            response_alan2 = requests.request('GET', url)

#alan mishe gheimat alane dolar 
            qq = response_alan2.json().get('usd').get('value')
            
            alan1 = float(qq)*float(dolare_alan)*float(meghdar)
            print('alan : ',alan1)
# ta inja ok
            mg = mg+float(meghdar)
            hesab=hesab+float(a)
            print('hesab:  ',hesab)
            alan=alan+alan1

#ok
            total = hesab
            print('total : ',total)
            sood_ziyan = alan-hesab
            print('soodz: ',sood_ziyan)
            pro = sood_ziyan
            print(pro)
        if pro>0:     
            sood_koli='سلام به ربات محاسبه ترید ما خوش اومدی انتخاب کن ارز رو خریدی یا فروختی! 🤓\nblance:\n'+str(mg)+arz_delkhah+': '+str(hesab)+' t\n\ntotal:'+str(total)+'\n\nprofit:'+str(pro)
            print(sood_koli)
            await event.reply(sood_koli,
                          buttons=B)
        elif pro<0:
            sood_koli='سلام به ربات محاسبه ترید ما خوش اومدی انتخاب کن ارز رو خریدی یا فروختی! 🤓\nblance:\n'+str(mg)+arz_delkhah+': '+str(hesab)+' t\n\ntotal:'+str(total)+'\n\nloss:'+str(pro)
            await event.reply(sood_koli,
                          buttons=B)
        elif event.sender_id not in balance:
             await event.reply('سلام به ربات محاسبه ترید ما خوش اومدی انتخاب کن ارز رو خریدی یا فروختی! 🤓',
                          buttons=B)


@client.on(events.CallbackQuery(pattern="k"))
async def call_handler(event):
    async with client.conversation(event.sender_id) as conv:
            await conv.send_message('چه ارزی خریدی؟ (لطفا نماد انگلیسی ارز رو وارد کن مثل BTC)')
            arz = await conv.get_response()
            await conv.send_message('چندتا از ارز مورد توجه خریدی؟')
            arz_meghadr = await conv.get_response()
            await conv.send_message('چه تاریخی ارز رو خریدی لطفا میلادی و مثل : 3-2-2020 وارد کن')
            arz_time = await conv.get_response()
#ta inja gheimat arz ok mishe
            url = "https://rest.coinapi.io/v1/exchangerate/"+arz.message+"/USD?time="+arz_time.message
            payload = {}
            headers = {
            'X-CoinAPI-Key': config.coin_api_key
            }

            response = requests.request("GET", url ,headers=headers, data=payload)
            dolar = (response.json().get('rate'))
# inja bayad time ro okay konam
            a = arz_time.message.split('-')
            rooz_asli = a[2]
            mah_asli = a[1]
            sal_asli = a[0]
            date_time_start = datetime.date(int(sal_asli), int(mah_asli), int(rooz_asli))
            unix_time_start = time.mktime(date_time_start.timetuple())
            rooz_fari = int(rooz_asli)+1
            date_time_end = datetime.date(int(sal_asli), int(mah_asli), rooz_fari)
            unix_time_end = time.mktime(date_time_end.timetuple())

            url = "http://api.navasan.tech/ohlcSearch/?api_key="+config.navasan_key+"&item=usd&start="+str(unix_time_start)+'&end='+str(unix_time_end)
            response2 = requests.request('GET', url)
            gheimat = response2.json()[0].get('close')
# inja sood mishe gheimat arz be tooman
            sood = float(dolar)*float(gheimat)*float(arz_meghadr.message)
            


# hala bayad to monog db sabt she
#gheimat dolar 2 tooye kharid farghi ba gh dolor 1 nadare
            mongo_client.tejarat.bazargan.insert_one({'id':event.sender_id,'type':'buy','arz':arz.message,'value':arz_meghadr.message,'price_d':gheimat ,'price':dolar,'gheimat_dolar':sood,'time':arz_time.message})
            balance = mongo_client.tejarat.bazargan.find({'id':event.sender_id})
#total majmooeh kol toomane kharj shodas
            total = 0
            hesab=0
#mg meghdare arz ha hast ke ta alan ok hast
            mg = 0
            alan = 0
            pro = 0
            for i in balance:
                arz_delkhah = i.get('arz')
                meghdar = i.get('value')
                a = i.get('gheimat_dolar')
#gheimat ye arz be toman mishe c
                
                url = "https://rest.coinapi.io/v1/exchangerate/"+arz_delkhah+"/USD"
                payload = {}
                headers = {
                'X-CoinAPI-Key': config.coin_api_key
                }

                response_alan = requests.request("GET", url ,headers=headers, data=payload)
                dolare_alan=response_alan.json().get('rate')
                url = 'https://api.navasan.tech/latest?api_key='+config.navasan_key+'&item=usd' 
                response_alan2 = requests.request('GET', url)

#alan mishe gheimat alane dolar 
                qq = response_alan2.json().get('usd').get('value')
                alan1 = float(qq)*float(dolare_alan)*float(meghdar)
                alan=alan+alan1
                mg = mg+float(meghdar)
                hesab=hesab+float(a)
                total = hesab
                sood_ziyan = alan-hesab
                pro = sood_ziyan
#ta hesab okaye
            if pro>0:     
                sood_koli='blance:\n'+str(mg)+' '+arz_delkhah+': '+str(hesab)+' t\n\ntotal:'+str(total)+'\n\nprofit:'+str(pro)
                await conv.send_message(sood_koli)
            elif pro<0:
                sood_koli='blance:\n'+str(mg)+' '+arz_delkhah+': '+str(hesab)+' t\n\ntotal:'+str(total)+'\n\nloss:'+str(pro)
            await conv.send_message(sood_koli)
            raise StopPropagation
            


@client.on(events.CallbackQuery(pattern="f"))
async def call_handler_1(event):
    async with client.conversation(event.sender_id) as conv:
            await conv.send_message('چه ارزی فروختی؟ (لطفا نماد انگلیسی ارز رو وارد کن مثل BTC)')
            arz=await conv.get_response()
            await conv.send_message('چندتا از ارز مورد توجه فروختی؟')
            arz_meghdar = await conv.get_response()
            await conv.send_message('چه تاریخی ارز رو فروختی لطفا میلادی و مثل : 3-2-2020 وارد کن')
            arz_time=await conv.get_response()
            url = "https://rest.coinapi.io/v1/exchangerate/"+arz.message+"/USD?time="+arz_time.message
            payload = {}
            headers = {
            'X-CoinAPI-Key': config.coin_api_key
            }

            response = requests.request("GET", url ,headers=headers, data=payload)
            dolar=(response.json().get('rate'))
# inja bayad time ro okay konam
            a = arz_time.message.split('-')
            rooz_asli=a[2]
            mah_asli=a[1]
            sal_asli=a[0]
            date_time_start =datetime.date(int(sal_asli), int(mah_asli), int(rooz_asli))
            unix_time_start = time.mktime(date_time_start.timetuple())
            rooz_fari=int(rooz_asli)+1
            date_time_end =datetime.date(int(sal_asli), int(mah_asli), rooz_fari)
            unix_time_end = time.mktime(date_time_end.timetuple())

            url="http://api.navasan.tech/ohlcSearch/?api_key="+config.navasan_key+"&item=usd&start="+str(unix_time_start)+'&end='+str(unix_time_end)
            response2 = requests.request('GET', url)
            gheimat=response2.json()[0].get('close')
            sood=float(dolar)*float(gheimat)*float(arz_meghdar.message)
            az=-float(arz_meghdar.message)
            


# hala bayad to monog db sabt she
            
            mongo_client.tejarat.bazargan.insert_one({'id':event.sender_id,'type':'sell','arz':arz.message,'value':az, 'price':dolar,'gheimat_dolar':sood,'time':arz_time.message,'price_d':gheimat})
            balance=mongo_client.tejarat.bazargan.find({'id':event.sender_id})
            total=0
            hesab=0
            pro=0
            alan = 0
            mg=0
            for i in balance:
                arz_delkhah=i.get('arz')
                print(arz_delkhah)
                meghdar=i.get('value')
                a=i.get('gheimat_dolar')
                url = "https://rest.coinapi.io/v1/exchangerate/"+arz_delkhah+"/USD"
                payload = {}
                headers = {
                'X-CoinAPI-Key': config.coin_api_key
                }

                response_alan = requests.request("GET", url ,headers=headers, data=payload)
                dolare_alan=response_alan.json().get('rate')
                url = 'https://api.navasan.tech/latest?api_key='+config.navasan_key+'&item=usd' 
                response_alan2 = requests.request('GET', url)
                qq=response_alan2.json().get('usd').get('value')
                alan1=float(qq)*float(dolare_alan)*float(meghdar)
                alan=alan+alan1
                mg=mg+float(meghdar)
                hesab=hesab+float(a)
                total=hesab
                sood_ziyan=alan-hesab
                pro=sood_ziyan
            if pro>0:     
                sood_koli='blance:\n'+str(mg)+' '+arz_delkhah+': '+str(hesab)+' rial\ntotal:'+str(total)+'\nprofit:'+str(pro)
                await conv.send_message(sood_koli)
            elif pro<0:
                sood_koli='blance:\n'+str(mg)+' '+arz_delkhah+': '+str(hesab)+' rial\ntotal:'+str(total)+'\n\nloss:'+str(pro)
            await conv.send_message(sood_koli)
            

            

            
            raise StopPropagation
            

    

client.run_until_disconnected()