# HomeHub
A Home Automation hub and API.
<hr>
## *HTTPS/SSL* <br>
In the HomeHUB.json add ["https" : "True"] <br>
Then to create the SSL certs run: openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /full/path/to/SSL/hub.key -out /full/path/to/SSL/hub.crt <br>
To tell HomeHub about the keys add the following to HomeHUB.json <br>
["sslcrt" : "/full/path/to/hub.crt"] and ["sslkey" : "/full/path/to/hub.key"]<br>

## *Username & Password* <br>
In the HomeHUB.json add ["use_secure" : "True"] <br>
Then to create a password database run: python store_pass.py \<filename\> <br>
Add ["passwd_file" : "/full/path/to/passwdfile"] <br>

## *API Key* <br>
In the HomeHUB.json add ["apikey" : "\<Your API KEY\>" <br>


## *Logging* <br>
In the HomeHUB.json add ["logfile" : "/full/path/to/logfile"] <br>

## *Testing* <br>
You can test your API with curl.

```{r, engine='bash', count_lines}
curl -k -X POST 'https://localhost:5000/homehub/<API KEY HERE>/lights/' \                                  
     -H 'Content-Type: application/json' \                                                                                   
     -d \
'{                                                                                                                             
  "user": "sam",
  "passwd": "pass",
  "action": "all"
}'  
```
