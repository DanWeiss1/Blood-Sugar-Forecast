import lib
def api_post(code,refresh):
    import http.client
    clientID = lib.get_conf('client_id')
    clientSecret = lib.get_conf('client_secret')
    redirect_URL ='http://127.0.0.1:5000/'
    conn = http.client.HTTPSConnection("api.dexcom.com")
    
    if refresh:
        payload = "client_secret=" + clientSecret + "&client_id=" +clientID \
        + "&refresh_token=" + code + "&grant_type=refresh_token&redirect_uri=" + redirect_URL
    
    else:
        payload = "client_secret=" + clientSecret + "&client_id=" +clientID \
        + "&code=" + code + "&grant_type=authorization_code&redirect_uri=" + redirect_URL
    
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
        }
    
    conn.request("POST", "/v2/oauth2/token", payload, headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return data
def refresh_token(code):
    
    import http.client
    
    conn = http.client.HTTPSConnection("api.dexcom.com")
    
    payload = "client_secret={your_client_secret}&client_id={your_client_id}&refresh_token={your_refresh_token}&grant_type=refresh_token&redirect_uri={your_redirect_uri}"
    
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
        }
    
    conn.request("POST", "/v2/oauth2/token", payload, headers)
    
    res = conn.getresponse()
    data = res.read()
    
    print(data.decode("utf-8"))
def get_data(auth_code,start_date,end_date):
    import http.client
    
    conn = http.client.HTTPSConnection("api.dexcom.com")
    
    headers = {
        'authorization': "Bearer " + auth_code
        }
    
    conn.request("GET", "/v2/users/self/egvs?startDate="+ start_date + "&endDate=" 
                + end_date, headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    
    return data

