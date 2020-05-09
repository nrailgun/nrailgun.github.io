
Check [this post](https://stackoverflow.com/questions/38822764/how-to-send-a-https-request-with-a-certificate-golang) and [this post](https://www.ibm.com/support/knowledgecenter/en/SSWHYP_4.0.0/com.ibm.apimgmt.cmc.doc/task_apionprem_gernerate_self_signed_openSSL.html) for details.

## Certificates

1. Generate CA.
```bash
openssl genrsa -out ca.key 4096
openssl req -x509 -new -key ca.key -days 3650 -out ca.crt
```

2. Generate certificate.
```bash
openssl genrsa -out wjy.key 2048
openssl req -new -key wjy.key -out wjy.csr
openssl x509 -req -in wjy.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 365 -out wjy.crt
```

## Https server

```go
func serve() {
	http.HandleFunc(config.Pattern, handler)
	http.ListenAndServeTLS(config.Addr, "wjy.crt", "wjy.key", nil)
}

func handler(w http.ResponseWriter, r *http.Request) {
}
```

## Https client

```go
func client() {
    cert, _ := ioutil.ReadFile("ca.crt")
    certPool := x509.NewCertPool()
    certPool.AppendCertsFromPEM(cert)
    
    c := &http.Client{
    	Transport: &http.Transport{
    		TLSClientConfig: &tls.Config{
    			RootCAs: certPool,
    			InsecureSkipVerify: true, // it's self-signed.
    		},
    	},
    }
}
```

You see? All better.
