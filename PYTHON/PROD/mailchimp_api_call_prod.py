import pandas as pd
from datetime import datetime as dt, timedelta as td
import mailchimp_marketing as mm
from mailchimp_marketing.api_client import ApiClientError
from typing import List, Dict, Any

API_KEY = 'API_KEY'
DATA_CENTER = API_KEY.split('-')[-1]

# ------------------------ Helper Functions ------------------------ #

def get_previous_week_dates() -> (str, str):
    """Return ISO format for previous Monday and Sunday."""
    today = dt.today().replace(hour=0, minute=0, second=0, microsecond=0)
    previous_monday = (today - td(days=today.weekday() + 7)).isoformat()
    previous_sunday = (today - td(days=today.weekday() + 1)).isoformat()
    return previous_monday, previous_sunday


def paginate_request(fetch_func, **kwargs) -> List[Dict[str, Any]]:
    """
    Generic paginator for Mailchimp API requests.
    fetch_func: callable returning dictionary with key containing list.
    kwargs: parameters for fetch_func.
    """
    offset = 0
    all_results = []
    while True:
        response = fetch_func(count=1000, offset=offset, **kwargs)
        results = []
        # Determine the key dynamically for campaigns or members
        if 'campaigns' in response:
            results = response['campaigns']
        elif 'members' in response:
            results = response['members']
        elif 'sent_to' in response:
            results = response['sent_to']
        elif 'unsubscribes' in response:
            results = response['unsubscribes']
        else:
            results = response
        if not results:
            break
        all_results.extend(results)
        offset += 1000
        if len(results) < 1000:
            break
    return all_results


def fetch_campaign_metrics(client: mm.Client, campaign_id: str) -> Dict[str, Any]:
    """Fetch recipients, unsubscribed, opened, and clicked info for a campaign."""
    data: Dict[str, Any] = {}
    
    # Recipients
    try:
        sent_to = paginate_request(client.reports.get_campaign_recipients, campaign_id=campaign_id)
        data['sent_to'] = list({i.get('merge_fields', {}).get('ID_NUMBER', '').zfill(10) for i in sent_to if i.get('merge_fields')})
        data['len_sent_to'] = len(data['sent_to'])
    except Exception as e:
        print(f"Error fetching recipients for {campaign_id}: {e}")
        data['sent_to'], data['len_sent_to'] = [], 0

    # Unsubscribed
    try:
        unsubscribed = paginate_request(client.reports.get_unsubscribed_list_for_campaign, campaign_id=campaign_id)
        data['unsubscribed'] = list({i.get('merge_fields', {}).get('ID_NUMBER', '').zfill(10) for i in unsubscribed if i.get('merge_fields')})
        data['len_unsubscribed'] = len(data['unsubscribed'])
    except Exception as e:
        print(f"Error fetching unsubscribes for {campaign_id}: {e}")
        data['unsubscribed'], data['len_unsubscribed'] = [], 0

    # Opened
    try:
        opened = paginate_request(client.reports.get_campaign_open_details, campaign_id=campaign_id)
        data['opened'] = list({i.get('merge_fields', {}).get('ID_NUMBER', '').zfill(10) for i in opened})
        data['len_opened'] = len(data['opened'])
    except Exception as e:
        print(f"Error fetching opens for {campaign_id}: {e}")
        data['opened'], data['len_opened'] = [], 0

    # Clicks
    try:
        clicks = {}
        urls = client.reports.get_campaign_click_details(campaign_id=campaign_id).get('urls_clicked', [])
        for url_info in urls:
            url, link_id = url_info.get('url'), url_info.get('id')
            clicked_members = paginate_request(client.reports.get_subscribers_info, campaign_id=campaign_id, link_id=link_id)
            ids = list({i.get('merge_fields', {}).get('ID_NUMBER', '').zfill(10) for i in clicked_members})
            clicks[url] = ids
        data['link_clicks'] = clicks
    except Exception as e:
        print(f"Error fetching clicks for {campaign_id}: {e}")
        data['link_clicks'] = {}

    return data


# ------------------------ Main Script ------------------------ #

def main():
    start_time = dt.now()

    previous_monday, previous_sunday = get_previous_week_dates()

    # Setup Mailchimp client
    client = mm.Client()
    client.set_config({
        "api_key": API_KEY,
        "server": DATA_CENTER
    })

    campaigns_data = {}

    offset = 0
    while True:
        # Fetch campaigns by send_time and create_time
        campaigns_send = client.campaigns.list(count=1000, offset=offset,
                                               before_send_time=previous_sunday,
                                               since_send_time=previous_monday,
                                               status="save,paused,schedule,sending,sent").get('campaigns', [])
        campaigns_create = client.campaigns.list(count=1000, offset=offset,
                                                 before_create_time=previous_sunday,
                                                 since_create_time=previous_monday,
                                                 status="save,paused,schedule,sending,sent").get('campaigns', [])
        campaigns = campaigns_send + campaigns_create
        if not campaigns:
            break

        for campaign in campaigns:
            campaign_id = campaign.get('id')
            metrics = fetch_campaign_metrics(client, campaign_id)
            campaigns_data[campaign_id] = {
                "audience": campaign.get('recipients', {}).get('list_name'),
                "title": campaign.get('settings', {}).get('title'),
                "created": campaign.get('create_time'),
                "sent": campaign.get('send_time'),
                "rpt_summary": campaign.get('report_summary'),
                **metrics
            }

        offset += 1000

    df = pd.DataFrame.from_dict(campaigns_data, orient='index')
    df.to_excel('test1.xlsx', index=False)

    end_time = dt.now()
    print(f"Script runtime: {(end_time - start_time).total_seconds() / 60:.2f} minutes")


if __name__ == "__main__":
    main()
