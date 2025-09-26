# from dotenv import load_dotenv
# from google.analytics.data_v1beta import BetaAnalyticsDataClient
# from google.analytics.data_v1beta.types import RunReportRequest
#
# # Path to your JSON key file
# client = BetaAnalyticsDataClient.from_service_account_file("service_account.json")
# import os
# load_dotenv()
# GA4_PROPERTY_ID= os.getenv("GA4_PROPERTY_ID")
# # Replace with your GA4 property ID
# property_id = GA4_PROPERTY_ID
#
# request = RunReportRequest(
#     property=f"properties/{property_id}",
#     dimensions=[{"name": "city"}],
#     metrics=[{"name": "activeUsers"}],
#     date_ranges=[{"start_date": "2023-09-01", "end_date": "2023-09-23"}],
# )
#
# response = client.run_report(request)
# for row in response.rows:
#     print(row.dimension_values[0].value, row.metric_values[0].value)
