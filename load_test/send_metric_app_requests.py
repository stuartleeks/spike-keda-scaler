import os
from locust import HttpUser, task, constant, events

flag_value = os.getenv("FLAG_VALUE")

#
# This is a locustfile for the metric-app
#
# It can be run with the following command:
#   locust -H http://localhost:8080/ -f load_test/send_metric_app_requests.py --autostart --users 2
#
# Additionally, locust allows you to use `w` and `s` to increase and decrease 
# the number of users during the test run
#


class MetricAppUser(HttpUser):
    """
    MetricAppUser makes calls to the metric-app
    """

    wait_time = constant(1)  # wait 1 second between requests

    @task
    def get_completion(self):
        query_string = f"?flag={flag_value}" if flag_value else ""
        url = f"{query_string}"
        self.client.get(url)
