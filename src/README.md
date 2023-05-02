# Instructions to run 

1. Run the catalog service in the "src/catalog/" folder:

To run with default settings of host = "0.0.0.0" and port = 6000:

```shell
python3 catalogService.py
```

To run with specific host and port settings by setting environment variables: 

```shell
CATALOG_HOST="0.0.0.0" CATALOG_PORT=6000 python3 catalogService.py
```

2. Run the order service in the src/order/ folder:

```shell
CATALOG_HOST=<catalog_host> CATALOG_PORT=<catalog_port> ORDER_ID=<order_ids> ORDER_PORT=<order_ports> ORDER_HOST=<order_hosts> python3 orderService.py <order_service_id> <order_service_file_path> <order_port> <order_host>
```

Example:

Run first replica on port 6001:

```shell
CATALOG_HOST="0.0.0.0" CATALOG_PORT=6000 ORDER_ID="5,6,7" ORDER_PORTS="6001,6002,6003" ORDER_HOSTS="0.0.0.0,0.0.0.0,0.0.0.0" python3 orderService.py 5 ../data/ 6001 0.0.0.0
```

Run second replica on port 6002:

```shell
CATALOG_HOST="0.0.0.0" CATALOG_PORT=6000 ORDER_ID="5,6,7" ORDER_PORTS="6001,6002,6003" ORDER_HOSTS="0.0.0.0,0.0.0.0,0.0.0.0" python3 orderService.py 6 ../data/ 6002 0.0.0.0
```

Run third replica on port 6003:

```shell
CATALOG_HOST="0.0.0.0" CATALOG_PORT=6000 ORDER_ID="5,6,7" ORDER_PORTS="6001,6002,6003" ORDER_HOSTS="0.0.0.0,0.0.0.0,0.0.0.0" python3 orderService.py 8 ../data/ 6003 0.0.0.0
```

3. Run the front-end service in the src/front-end/frontendweb/ folder:

Set the environment variables "ORDER_ID", "ORDER_PORT", and "ORDER_HOST" for the host, port and file path of all the order replicas.

```shell
export ORDER_ID="<order_service_id1>,<order_service_id2>,<order_service_id3>"
```

```shell
export ORDER_PORTS="<order_port_1>,<order_port_2>,<order_port_3>"
```

```shell
export ORDER_HOSTS="<order_host_1>,<order_host_2>,<order_host_3>"
```

```shell
CATALOG_HOST=<catalog_host> CATALOG_PORT=<catalog_port> python3 manage.py runserver
```

Example:

```shell
export ORDER_ID="5,6,7"
```

```shell
export ORDER_PORT="6001,6002,6003"
```

```shell
export ORDER_HOST="0.0.0.0,0.0.0.0,0.0.0.0"
```

```shell
CATALOG_HOST="0.0.0.0" CATALOG_PORT=6000 python3 manage.py runserver
```

4. Run client in the src/client/ folder:

The client takes front-end host, port and probability percentage as command line arguments:

```shell
python3 client.py <host> <port> <p> 
```

To run client with front-end on localhost, port 8000, just pass the probability(p):

```shell
python3 client.py <p>
```

To run client with front-end on a specific host, port and with prob = [1, 0.8, 0.6, 0.4, 0.2, 0]

```shell
python3 client.py <host> <port>
```

Example:

Run client with front-end on localhost, port 8000, and a probability(p):

```shell
python3 client.py 0.3
```

In order to connect a client on the local machine to a remote host say "54.174.216.173", port 8000 and probability 0.5, run:

```shell
python3 client.py "54.174.216.173" 8000 0.5
```

To run client with front-end on a specific host, port and with prob = [1, 0.8, 0.6, 0.4, 0.2, 0]

```shell
python3 client.py "54.174.216.173" 8000
```


2. AWS Deployment:

Obtain Public IPAddress of the EC2 instance - This can be obtained by using aws ec2 describe-instances command from the "PublicIpAddress" field:

```shell
aws ec2 describe-instances --instance-id <instance-id>
```
Run client locally and sent request to front-end service hosted on EC2 instance with Public IPAddress "54.174.216.173":

```shell
python3 client.py "54.174.216.173" 8000 0.5
```



