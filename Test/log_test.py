
import traceback
import json
import time
url = "http://dl.russellcloud.com:80/api/v1/logs"

querystring = {"method":"kafka", "id":"3ed41e84be9c47c38c96b164282c0ed1"}

payload = ""
headers = {
    'content-type': "application/json",
    'authorization': "Basic cnVzc2VsbC12aXAtdGVzdDpydXNzZWxsLXZpcC10ZXN0",
    # 'cache-control': "no-cache",
    'postman-token': "fc712b09-f9c9-b70f-cd64-9a81bb69e6fa"
    }
s = time.time()
response = requests.request("GET", url, data=payload, headers=headers, params=querystring, stream=True)
print 'resposne duration', time.time() - s
i = 0
for line in response.iter_lines():
    if i== 0:
        print 'first line', time.time() - s
        i += 1
	print line
print 'all duration', time.time() - s

from kafka import KafkaConsumer
def container_log_generator(task_id):
    try:
        consumer = KafkaConsumer(task_id,
                             bootstrap_servers="47.92.31.158:9092",
                             auto_offset_reset='earliest',
                             enable_auto_commit=False,
                             request_timeout_ms=40000,
                             consumer_timeout_ms=10000)
    except Exception:
        print repr(traceback.format_exc())
        yield []
    else:
        try:
            for msg in consumer:
                str_line = json.loads(msg.value).get("log").strip("\n") + b'\r\n'
                yield bytes(str_line)
        except StopIteration as e:
            return
s_time = time.time()
i = 0
from itertools import chain

for line in chain(container_log_generator("3ed41e84be9c47c38c96b164282c0ed1"),['tail']):
    if i == 0:
        print 'first line', time.time() - s_time
        i+= 1
    print line
e_time = time.time()
print 'duration', e_time - s_time



# ########
s = time.time()
try:

    consumer = KafkaConsumer("3ed41e84be9c47c38c96b164282c0ed1",
                         bootstrap_servers="47.92.31.158:9092",
                         auto_offset_reset='earliest',
                         enable_auto_commit=False,
                         request_timeout_ms=40000,
                         consumer_timeout_ms=1000)
except Exception:
    print repr(traceback.format_exc())
    print 'exception######'
else:
    try:
        for msg in consumer:
            str_line = json.loads(msg.value).get("log").strip("\n") + b'\r\n'
            print 'bytes line',bytes(str_line)
    except StopIteration:
        print 'stoped#####'
print 'no iter duration', time.time() - s