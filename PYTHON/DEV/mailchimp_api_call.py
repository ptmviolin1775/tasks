import requests
import mailchimp_marketing as mm
from mailchimp_marketing.api_client import ApiClientError
from datetime import datetime as dt, timedelta as td
import pandas as pd

start_time = dt.now()

# Replace this with your actual API key
API_KEY = '<API KEY>'

# Extract your data center from the key (the part after the dash)
DATA_CENTER = API_KEY.split('-')[-1]

# GET PREVIOUS MONDAY TO SUNDAY DATES
today = dt.today().replace(hour=0, minute=0, second=0, microsecond=0)
previous_monday = (today - td(days=today.weekday() + 7)).isoformat() ##7
previous_sunday = (today - td(days=today.weekday() + 1)).isoformat() ##1

# SET UP MAILCHIMP CLIENT
client = mm.Client()
client.set_config({
    "api_key": API_KEY,
    "server": DATA_CENTER
  })

## VARIABLES
campaign_id_li = []
campaign_li = {}

offset_ctr = 0
len_campaign_id_li = 1
len_campaign_id_li_old = 0

while len_campaign_id_li_old != len_campaign_id_li:
    response = client.campaigns.list(count=1000, offset = offset_ctr,before_send_time = previous_sunday, since_send_time= previous_monday,status="save,paused,schedule,sending,sent")
    response2 = client.campaigns.list(count=1000, offset = offset_ctr,before_create_time = previous_sunday, since_create_time= previous_monday,status="save,paused,schedule,sending,sent")
    response = response.get('campaigns') + response2.get('campaigns')
    print(response)
    input()
    # temp_response = response.get('campaigns')
    # campaign_li.extend(temp_response)
    for vv in response:
        opened_response = client.reports.get_campaign_open_details(vv.get('id'))
        temp_d = {}
        temp_d['audience'] = vv.get('recipients').get('list_name')
        temp_d['title'] = vv.get('settings').get('title')
        temp_d['created'] = vv.get('create_time')
        temp_d['sent'] = vv.get('send_time')
        temp_d['rpt_summary'] = vv.get('report_summary')
        # temp_d['links'] = vv.get('_links')
        try:
            sent_to_offsetctr = 0
            len_sent_to_li = 1
            len_sent_to_old = 0
            temp_sent_to_li = []
            while len_sent_to_old != len_sent_to_li:
                recipient_response = client.reports.get_campaign_recipients(campaign_id = vv.get('id'),count = 1000, offset = sent_to_offsetctr)
                temp_sent_to_li.extend([i.get('merge_fields').get('ID_NUMBER').zfill(10) for i in recipient_response.get('sent_to') if i.get('merge_fields') and i['merge_fields'].get('ID_NUMBER')])
                len_sent_to_old = len_sent_to_li
                len_sent_to_li = len(temp_sent_to_li)
                sent_to_offsetctr += 1000
            temp_d['sent_to'] = list(set(temp_sent_to_li))
            temp_d['len_sent_to'] = len(list(set(temp_sent_to_li)))
        except Exception as e:
            print(f'ERROR IN RESPONSE: \n{recipient_response}')
            temp_d['sent_to'] = []
        try:
            unsub_offsetctr = 0
            len_unsub_li = 1
            len_unsub_old = 0
            temp_unsub_li = []
            while len_unsub_old != len_unsub_li:
                unsubscribed_response = client.reports.get_unsubscribed_list_for_campaign(campaign_id = vv.get('id'),count = 1000, offset = unsub_offsetctr)
                temp_unsub_li.extend([i.get('merge_fields').get('ID_NUMBER').zfill(10) for i in unsubscribed_response.get('unsubscribes') if i.get('merge_fields') and i['merge_fields'].get('ID_NUMBER')])
                len_unsub_old = len_unsub_li
                len_unsub_li = len(temp_unsub_li)
                unsub_offsetctr += 1000
            temp_d['unsubscribed'] = list(set(temp_unsub_li))
            temp_d['len_unsubscribed'] = len(list(set(temp_unsub_li)))
        except Exception as e:
            print(f'ERROR IN RESPONSE: \n{unsubscribed_response}')
            temp_d['unsubscribed'] = []
        try:
            op_offsetctr = 0
            len_op_li = 1
            len_op_old = 0
            temp_op_li = []
            while len_op_old != len_op_li:
                opened_response = client.reports.get_campaign_open_details(campaign_id = vv.get('id'),count = 1000, offset = op_offsetctr)
                temp_op_li.extend([i.get('merge_fields').get('ID_NUMBER').zfill(10) for i in opened_response.get('members') if i.get('merge_fields') and i['merge_fields'].get('ID_NUMBER')])
                len_op_old = len_op_li
                len_op_li = len(temp_op_li)
                op_offsetctr += 1000
            temp_d['opened'] = list(set(temp_op_li))
            temp_d['len_opened'] = len(list(set(temp_op_li)))
        except Exception as e:
            print(f'ERROR IN RESPONSE: \n{opened_response}')
            temp_d['opened'] = []
        try:
            clicks = {}
            # link_urls_ids = list(set([(i.get('url'),i.get('id')) for i in client.reports.get_campaign_click_details(campaign_id = vv.get('id')).get('urls_clicked')]))
            link_urls_ids = [(i.get('url'),i.get('id')) for i in client.reports.get_campaign_click_details(campaign_id = vv.get('id')).get('urls_clicked')]
            for (url,link_id) in link_urls_ids:
                cl_offset_ctr = 0
                len_cl_li = 1
                len_cl_li_old = 0
                temp_cl = []
                while len_cl_li_old != len_cl_li:
                    temp_li = [i.get('merge_fields').get('ID_NUMBER').zfill(10) for i in client.reports.get_subscribers_info(campaign_id = vv.get('id'),link_id = link_id,count = 1000,offset = cl_offset_ctr).get('members')]
                    temp_cl.extend(temp_li)
                    len_cl_li_old = len_cl_li
                    len_cl_li = len(temp_cl)
                    cl_offset_ctr += 1000
                if clicks.get(url) == None:
                    clicks[url] = list(set(temp_cl))
                else:
                    clicks[url].extend(list(set(temp_cl)))
            temp_d['link_clicks'] = {k:list(set(v)) for (k,v) in clicks.items()}
        except Exception as e:
            print(f"ERROR IN RESPONSE:\nID:{vv.get('id')}\n{link_urls_ids}")
            temp_d['link_clicks'] = []
        campaign_li[vv.get('id')] = temp_d
        # print(campaign_li)
        # input()
    len_campaign_id_li_old = len_campaign_id_li
    len_campaign_id_li = len(campaign_li)
    offset_ctr += 1000
    # print(len(campaign_id_li))


df = pd.DataFrame.from_dict(campaign_li,orient = 'index')
print(df)
df.to_excel('test.xlsx')

end_time = dt.now()

print(f'SCRIPT RUN TIME: {(end_time-start_time).total_seconds()/60} MINUTES ...')