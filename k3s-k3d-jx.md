# K3s, K3d and JenkinX

## What is Edge computing

### Definition

Edge computing is a distributed computing paradigm that brings computation and data storage closer to the location where it is needed, to improve response times and save bandwidth.

### Motive

In the age of microservices, it's not strange to see the need of more than one embedded system working together to do a huge amount of work that's not possible with one embedded system. From analytics to operational control of systems, there is a lot of different applications that can be run out at the network edge.

The increase of IoT devices at the edge of the network is producing a massive amount of data to be computed at data centers, pushing network bandwidth requirements to the limit. Despite the improvements of network technology, data centers cannot guarantee acceptable transfer rates and response times, which could be a critical requirement for many applications.

Devices at the edge constantly consume data coming from the cloud, forcing companies to build content delivery networks to decentralize data and service provisioning, to benefit from physical proximity to the end user.

### Goal

The aim of Edge Computing is to move the computation away from data centers towards the edge of the network, exploiting smart objects, mobile phones or network gateways to perform tasks and provide services on behalf of the cloud. By moving services to the edge, it is possible to provide content caching, service delivery, storage and IoT management resulting in better response times and transfer rates.

### Containers at the edge

Containers and Kubernetes are an excellent choice for deploying complex software to the edge. They are consistent, can work in standalone or cluster modes, easy to upgrade, provide support for different configs (storage, CPU intensive) and have a wide ecosystem that provides monitoring, logging, CI, etc.

However, there are many challenges facing running Kuberenets at the edge

- Most Kuberenetes distributions do not support ARM processors
- Kubernetes can easily consume up to 4 GB of RAM
- Kuberenetes was not built for offline management or embedded systems

## K3s

[K3s](https://k3s.io/) is a fully compliant Kubernetes distribution with some enhancements

### K3s Features

- Packaged as a single binary.
- Lightweight storage backend based on SQLite3 as the default storage mechanism. etcd3, MySQL, Postgres also still available.
-Simple launcher that handles a lot of the complexity of TLS and options.
- Secure by default with reasonable defaults for lightweight environments.
- Operation of all Kubernetes control plane components is encapsulated in a single binary and process. This allows K3s to automate and manage complex cluster operations like distributing certificates.
- Minimized external dependencies (just a modern kernel and cgroup mounts needed)
- Removes legacy and non default features, as well as alpha features.
- Removes In-tree cloud providers support, a cloud native Kuberenetes distribution will be more suitable and integrated with a cloud platform.
- Removes and In-tree storage drivers as they are available as add-ons.
- Removes the dependency on Docker and uses containerd instead.
- Simple but powerful “batteries-included” features have been added, such as:
  - Local storage provider
  - Service load balancer
  - Helm package manager controller
  - Traefik ingress controller

### K3s use cases

1. Edge computing and embedded systems
2. IOT Gateway
3. CI Environments
4. Single-App clusters

### K3s Architecture

A server node is defined as a machine (bare-metal or virtual) running the `k3s server` command. A worker node is defined as a machine running the `k3s agent` command.

![How K3s works](img/how-it-works-k3s.png)

- Single-server setup with an embedded database

  A server node is defined as a machine (bare-metal or virtual) running the k3s server command. A worker node is defined as a machine running the k3s agent command.

  ![Single server architecture](img/k3s-architecture-single-server.png)

- High-Availability K3s Server with a database

  Single server clusters can meet a variety of use cases, but for environments where uptime of the Kubernetes control plane is critical, K3s can be run in an HA configuration. HA K3s cluster is comprised of:
  - Two or more server nodes that will serve the Kubernetes API and run other control plane services.
  - A datastore (that can be external or the experimental DQlite embedded database).

  ![High-availability server architecture](img/k3s-architecture-ha-server.png)

- Agent node registration

  Agent nodes are registered with a web socket connection initiated by the k3s `agent` process, and the connection is maintained by a client-side load balancer running as part of the agent process.

  Agents will register with the server using the node cluster secret along with a randomly generated password for the node. The server will store the passwords for individual nodes, and any subsequent attempts must use the same password.

  If the stored password of an agent is removed from the agent, the password file should be recreated for the agent, or the entry removed from the server.

  A unique node ID can be appended to the hostname by launching K3s servers or agents using the `--with-node-id` flag.

### K3s Demo

- Single node

  ``` Powershell
  multipass launch -n k3s
  multipass exec k3s -- bash -c "curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE='644' sh -"
  multipass exec k3s -- sudo kubectl get nodes
  docker pull nginxdemos/hello
  docker tag nginxdemos/hello:latest localhost:5000/k3s-demo
  docker push localhost:5000/k3s-demo
  # docker image remove nginxdemos/hello:latest localhost:5000/k3s-demo
  # docker pull localhost:5000/k3s-demo
  # add Host IP to /etc/hosts
  sudo sh -c "echo '192.168.1.6 localhost' >> /etc/hosts"
  # create config.yaml
  nano ~/config.yaml
  # apply config
  sudo kubectl apply -f config.yaml
  # get ip
  sudo kubectl get ingress,svc,pods -n k3s-demo
  curl -k -X GET https://<IP>
  ```

- Cluster with highly available embedded database DQlite

  ``` Powershell
  multipass launch -n k3s-cluster
  multipass launch -n k3s-cluster-node-1
  multipass launch -n k3s-cluster-node-2
  multipass exec k3s-cluster -- bash -c "curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC='server --cluster-init' sh -s -"
  $TOKEN=$(multipass exec k3s-cluster sudo cat /var/lib/rancher/k3s/server/node-token)
  $IP = multipass info k3s-cluster | Select-String IP | %{($_ -split ':')[1].trim()}
  multipass exec k3s-cluster-node-1 -- bash -c "curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC='server --server https://$($IP):6443' K3S_URL=https://$($IP):6443 K3S_TOKEN=$($TOKEN) sh -s -"
  # modify start script @ /etc/systemd/system/k3s.service to use sudo
  multipass exec k3s-cluster-node-2 -- bash -c "curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC='server --server https://$($IP):6443' K3S_URL=https://$($IP):6443 K3S_TOKEN=$($TOKEN) sh -s -"
  # modify start script @ /etc/systemd/system/k3s.service to use sudo
  
  ```

- K3s and External database  
  - Notice the need for an external L4 load balancer in front of the master nodes
  - Unlike embedded HA, this will avoid the cluster going down if the main node is down

    ``` Powershell
    multipass launch -n postgres-db
    multipass exec postgres-db sudo apt update
    multipass exec postgres-db sudo apt install postgresql
    multipass exec sudo nano /etc/postgresql/12/main/postgresql.conf
    # change listen_addresses = '*'
    multipass exec sudo nano /etc/postgres/12/main/pg_hba.conf
    # add host all all 192.168.72.0/24 trust to allow all connections for multipass range
    multipass exec sudo systemctl restart postgresql
    # optionally create database .. k3s creates default if none is defined
    multipass launch -n k3s-lb -m 512M
    multipass launch -n k3s-server-1 -m 512M
    multipass launch -n k3s-server-2 -m 512M
    multipass exec k3s-lb -- bash -c "sudo snap install --edge gobetween"
    multipass exec k3s-lb -- bash -c "sudo nano /var/snap/gobetween/# common/gobetween.toml"
    # # change bind to servers.sample to "0.0.0.0:6443"
    # # add server IPs to static_list "IP:6443 weight=100"
    multipass exec k3s-lb sudo snap restart gobetween
    $DB_IP = multipass info postgres-db | Select-String IP | %{($_ -split ':')[1].trim()}
    multipass exec k3s-server-1 -- bash -c "curl -sfL https://get.k3s.io | K3S_DATASTORE_ENDPOINT='postgres://postgres@$($DB_IP):5432/kube' INSTALL_K3S_EXEC='--write-kubeconfig-mode 644 -t orPLcIQSeOzOUOpTZsqALIYU1mJ9rQVo --tls-san k3s.example.com --node-taint k3s-controlplane=true:NoExecute' sh -s - server"
    multipass exec k3s-server-2 -- bash -c "curl -sfL https://get.k3s.io | K3S_DATASTORE_ENDPOINT='postgres://postgres@$($DB_IP):5432/kube' INSTALL_K3S_EXEC='--write-kubeconfig-mode 644 -t orPLcIQSeOzOUOpTZsqALIYU1mJ9rQVo --tls-san k3s.example.com --node-taint k3s-controlplane=true:NoExecute' sh -s - server"
    multipass exec k3s-server-1 sudo nano /etc/rancher/k3s/k3s.yaml
    # modify server to gobetween ip
    multipass exec k3s-server-2 sudo nano /etc/rancher/k3s/k3s.yaml
    # modify server to gobetween ip
    multipass launch -n k3s-agent-1
    multipass launch -n k3s-agent-2
    $IP = multipass info k3s-lb | Select-String IP | %{($_ -split ':')[1].trim()}
    $TOKEN=$(multipass exec k3s-master-1 sudo cat /var/lib/rancher/k3s/server/node-token)
    multipass exec k3s-agent-1 -- bash -c "curl -sfL https://get.k3s.io | sh -s - agent --server https://$($IP):6443 -t $($TOKEN)  --node-label node-role.kubernetes.io/worker=worker"
    multipass exec k3s-agent-2 -- bash -c "curl -sfL https://get.k3s.io | sh -s - agent --server https://$($IP):6443 -t $($TOKEN)  --node-label node-role.kubernetes.io/worker=worker"
    multipass exec k3s-master-1 nano ~/config.yaml
    # paste configuration
    multipass exec k3s-master-1 -- bash -c "sudo kubectl create namespace k3s-demo"
    multipass exec k3s-master-1 -- bash -c "sudo kubectl appy -f ~/config.yaml"
    multipass exec k3s-master-1 -- bash -c "sudo kubectl get pods,services,ingress -n k3s-demo"
    # change config and notice change
    multipass exec k3s-master-1 nano ~/config.yaml
    multipass exec k3s-master-1 -- bash -c "sudo kubectl appy -f ~/config.yaml"
    multipass exec k3s-master-1 -- bash -c "sudo kubectl get pods,services,ingress -n k3s-demo"
    ```

- Add private registry
  - Modify /etc/rancher/k3s/registries.yaml
  - Add private mirror and update /etc/hosts if domain is private

    ``` YAML
    mirrors:
      customreg.com:
        endpoint:
          - "http://customreg.com:5000"
    ```
  
  - Add configuration to connect to the registry

    ``` YAML
      # With TLS + Auth
      configs:
        "customreg:5000":
          auth:
            username: xxxxxx # this is the registry username
            password: xxxxxx # this is the registry password
          tls:
            cert_file: # path to the cert file used in the registry
            key_file:  # path to the key file used in the registry
            ca_file:   # path to the ca file used in the registry
      # Without TLS + Auth
      configs:
      "customreg:5000":
        auth:
          username: xxxxxx # this is the registry username
          password: xxxxxx # this is the registry password
    ```

- Add Kubernetes dashboard
  - Download dashboard

    ``` Bash
    GITHUB_URL=https://github.com/kubernetes/dashboard/releases
    VERSION_KUBE_DASHBOARD=$(curl -w '%{url_effective}' -I -L -s -S ${GITHUB_URL}/latest -o /dev/null | sed -e 's|.*/||')
    sudo k3s kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/${VERSION_KUBE_DASHBOARD}/aio/deploy/recommended.yaml
    ```
  
  - Add admin user

    ``` YAML
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: admin-user
      namespace: kubernetes-dashboard
    ```

  - Add admin role

    ``` YAML
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      name: admin-user
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: ClusterRole
      name: cluster-admin
    subjects:
    - kind: ServiceAccount
      name: admin-user
      namespace: kubernetes-dashboard
    ```

  - Deploy role and user

    ``` Bash
    sudo k3s kubectl create -f dashboard.admin-user.yaml -f dashboard.admin-user-role.yaml
    ```

  - Get token

    ``` Bash
    sudo k3s kubectl -n kubernetes-dashboard describe secret admin-user-token | grep ^token
    ```

  - Access the dashboard at <https://$IP:6443/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/overview?namespace=default>
  
    ``` Bash
    # kubectl get pods -n kubernetes-dashboard
    # kubectl port-forward pods/kubernetes-dashboard-7d8574ffd9-mfxlk 8001 -n kubernetes-dashboard
    # sudo k3s kubectl proxy

    ```
  
  - Longhorn storage

    ``` YAML
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: longhorn-volv-pvc
    spec:
      accessModes:
        - ReadWriteOnce
      storageClassName: longhorn
      resources:
        requests:
          storage: 2Gi
    ```

    ``` YAML
    apiVersion: v1
    kind: Pod
    metadata:
      name: volume-test
      namespace: default
    spec:
      containers:
      - name: volume-test
        image: nginx:stable-alpine
        imagePullPolicy: IfNotPresent
        volumeMounts:
        - name: volv
          mountPath: /data
        ports:
        - containerPort: 80
      volumes:
      - name: volv
        persistentVolumeClaim:
          claimName: longhorn-volv-pvc
    ```

    ``` Bash
    kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/master/deploy/longhorn.yaml
    kubectl apply -f pvc.yaml -f pod.yaml
    ```

  To access the UI, create an Ingress to allow external traffic
  - Create a basic auth file named auth. It’s important the file generated is named auth (actually - that the secret has a key data.auth), otherwise the Ingress returns a 503.

    ``` Bash
    USER=<USERNAME_HERE>
    PASSWORD=<PASSWORD_HERE>
    echo "${USER}:$(openssl passwd -stdin -apr1 <<< ${PASSWORD})" >> auth
    ```

  - Create a secret

    ``` Bash
    kubectl -n longhorn-system create secret generic basic-auth --from-file=auth
    ```

  - Create an Ingress manifest longhorn-ingress

    ``` YAML
    apiVersion: networking.k8s.io/v1beta1
    kind: Ingress
    metadata:
      name: longhorn-ingress
      namespace: longhorn-system
      annotations:
        nginx.ingress.kubernetes.io/auth-type: basic
        nginx.ingress.kubernetes.io/ssl-redirect: 'false'
        nginx.ingress.kubernetes.io/auth-secret: basic-auth
        nginx.ingress.kubernetes.io/auth-realm: 'Authentication Required '
    spec:
      rules:
      - http:
          paths:
          - path: /
            backend:
              serviceName: longhorn-frontend
              servicePort: 80
    ```

  - Create the Ingress

    ``` Bash
    kubectl -n longhorn-system apply -f longhorn-ingress.yml
    ```

## K3D

[K3d](https://k3d.io/) is a lightweight wrapper to run k3s in docker. K3d makes it very easy to create single-node and multi-node k3s clusters in docker, e.g. for local development on Kubernetes.

### Shortcomings

- External datastores are not yet available in k3d

### Usage

``` Powershell
k3d cluster create k3d-cluster --image rancher/k3s:v1.18.8-k3s1  --servers 1 --agents 3
# HA cluster
k3d cluster create k3d-cluster --image rancher/k3s:v1.18.8-k3s1 --servers 3 --agents 3
```

## Jenkins X

Jenkins X provides pipeline automation, built-in GitOps, and preview environments to help teams collaborate and accelerate their software delivery at any scale.

### Setup

- Trial 1 on windows machine has failed.
- Trial 2 on Ubuntu multipass instance

  ``` Powershell
  multipass launch -n jx
  multipass shell jx
  sudo apt update
  # install docker
  sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
  sudo apt update
  sudo apt install docker-ce docker-ce-cli containerd.io
  # install k3d
  curl -s https://raw.githubusercontent.com/rancher/k3d/main/install.sh | bash
  # install jx
  curl -L "https://github.com/jenkins-x/jx/releases/download/$(curl --silent "https://github.com/jenkins-x/jx/releases/latest" | sed 's#.*tag/\(.*\)\".*#\1#')/jx-linux-amd64.tar.gz" | tar xzv "jx"
  sudo mv jx /usr/local/bin
  # install kubectl
  # can be skipped since it will be installed with jx bot
  curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
  chmod +x ./kubectl
  sudo mv ./kubectl /usr/local/bin/kubectl
  # create cluster
  sudo su
  k3d cluster create jx-cluster --image rancher/k3s:v1.18.8-k3s1 --timeout 300s --servers 1 --agents 1 -p 8081:80@loadbalancer --api-port 5678 --update-default-kubeconfig
  # get ingress external IP
  kubectl get services -n kube-system
  # boot jx
  jx boot # accept repo download > fails
  # modify jx-requirements
  # replace gke with kubernetes
  # modify ingress domain to $IP.nip.io and add ignoreLoadBalancer: true
  # save
  cd jenkins-x-boot-config/
  nano jx-requirements.yml
  # run boot jx again and answer questions to setup
  jx boot
  # add nginx service
  ##kubectl create deployment nginx --image=nginx -n kube-system
  ##kubectl create service clusterip nginx --tcp=80:80 -n kube-system
  ##kubectl apply -f <nginx.yaml>
  ##jx install --provider=kubernetes --skip-ingress --external-ip=10.43.223.87 --ingress-service=service/nginx --ingress-deployment=deployment.apps/nginx --ingress-namespace=kube-system
  ```
