import http.client

conn = http.client.HTTPSConnection("api.dexcom.com")

headers = {
    'authorization': "Bearer ZYOdwiVUkFg2p5lzmDTp0zyr2SN4"
    }

conn.request("GET", "/v2/users/self/egvs?startDate=2018-06-05T15:30:00&endDate=2018-06-07T15:45:00", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))