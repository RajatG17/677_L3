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
SERVICE_ID=<order_service_id> ORDER_HOST=<order_host> ORDER_PORT=<order_port> CATALOG_HOST=<catalog_host> CATALOG_PORT=<catalog_port> ORDER_ID=<order_ids> FILE_PATH=<order_service_file_path> ORDER_PORTS=<order_ports> ORDER_HOSTS=<order_hosts> python3 orderService.py
```

Example:

Run first replica on port 6001:

```shell
SERVICE_ID="5" ORDER_HOST="0.0.0.0" ORDER_PORT=6001 CATALOG_HOST="0.0.0.0" CATALOG_PORT=6000 ORDER_ID="5,6,8" FILE_PATH="../data/" ORDER_PORTS="6001,6002,6003" ORDER_HOSTS="0.0.0.0,0.0.0.0,0.0.0.0" python3 orderService.py
```

Run second replica on port 6002:

```shell
SERVICE_ID="6" ORDER_HOST="0.0.0.0" ORDER_PORT=6002 CATALOG_HOST="0.0.0.0" CATALOG_PORT=6000 ORDER_ID="5,6,8" FILE_PATH="../data/" ORDER_PORTS="6001,6002,6003" ORDER_HOSTS="0.0.0.0,0.0.0.0,0.0.0.0" python3 orderService.py
```

Run third replica on port 6003:

```shell
SERVICE_ID="8" ORDER_HOST="0.0.0.0" ORDER_PORT=6003 CATALOG_HOST="0.0.0.0" CATALOG_PORT=6000 ORDER_ID="5,6,8" FILE_PATH="../data/" ORDER_PORTS="6001,6002,6003" ORDER_HOSTS="0.0.0.0,0.0.0.0,0.0.0.0" python3 orderService.py
```

3. Run the front-end service in the src/front-end/frontendweb/ folder:

Set the environment variables "ORDER_ID", "ORDER_PORTS", and "ORDER_HOSTS" for the host, port and file path of all the order replicas.

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
CACHE_SIZE=<cache_size> FRONTEND_HOST=<frontend_host> FRONTEND_PORT=<frontend_port> CATALOG_HOST=<catalog_host> CATALOG_PORT=<catalog_port> ORDER_HOSTS=<order_hosts> ORDER_ID=<order_ids> ORDER_PORTS=<order_ports> python3 front-end-http-server.py
```

Example:

```shell
export ORDER_ID="5,6,8"
```

```shell
export ORDER_PORT="6001,6002,6003"
```

```shell
export ORDER_HOST="0.0.0.0,0.0.0.0,0.0.0.0"
```

```shell
CACHE_SIZE=5 FRONTEND_HOST="0.0.0.0" FRONTEND_PORT=8000 CATALOG_HOST="0.0.0.0" CATALOG_PORT=6000 ORDER_HOSTS="0.0.0.0,0.0.0.0,0.0.0.0" ORDER_ID="5,6,8" ORDER_PORTS="6001,6002,6003" python3 front-end-http-server.py
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



