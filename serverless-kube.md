# Serverless computing

## What is serverless computing

Serverless computing is a cloud computing model in which the cloud provider runs the server, and dynamically manages the allocation of machine resources. Pricing is based on the actual amount of resources consumed by an application, rather than on pre-purchased units of capacity.

Serverless computing simplifies the process of deploying code into production. Scaling, capacity planning and maintenance operations may be hidden from the developer.

Serverless code can be used in conjunction with code deployed in traditional styles, such as microservices. Alternatively, applications can be written to be purely serverless and use no provisioned servers at all.

Serverless computing should have:

- No management of servers or hosts
- Self auto-scale and provisison based on load
- Costs should be based on usage
- Performance is defined in terms other than host count or size

### Function as a service (FaaS)

> FaaS is about running backend code without managing your own server systems or your own long-lived server applications. - Martin Fowler

## Serverless Providers

- From cloud providers
  - Proprietary/Closed source
    - AWS Lambda was (First FaaS offering by a large public cloud vendor)
    - Google Cloud Functions
    - Microsoft Azure Functions
  - Open source  
    - IBM/Apache's OpenWhisk
    - Oracle Cloud Fn

- Based on Kubernetes
  - OpenFaas
  - Kubeless
  - Fission
  - Knative
  - TrigerMesh

## Knative

Knative extends Kubernetes to provide a set of middleware components that are essential to build container-based applications that can run anywhere.

Each of the components under the Knative project attempt to identify common patterns and codify the best practices that are shared by successful, real-world, Kubernetes-based frameworks and applications.

Developing in Knative requires almost exactly the same set of steps any other k8s application would take. It requires the developer to manage a Dockerfile, an image repository, a local copy of Docker to build against, and reference base images.

## OpenFaaS

OpenFaaS makes it easy for developers to deploy event-driven functions and microservices to Kubernetes without repetitive, boiler-plate coding. Package your code or an existing binary in a Docker image to get a highly scalable endpoint with auto-scaling and metrics.

OpenFaaS uses a templating system that hides the existence of a Dockerfile from the developer. However, it’s easy to find should someone want to make lower level changes. OpenFaaS CLI takes care of build, push to repo, and deployment steps and the base framework includes an API gateway that immediately makes functions callable from tools like curl.

## Oracle's Fn project

The Fn Project has been started and is currently funded by Oracle, who uses a fork to power its own Oracle Functions product.

With Fn, the Dockerfile is obscured from the developer. The CLI helps manage build, push, and deploy steps, but a power user can still bring their own Dockerfile and the CLI will build that as the function. 

Fn project has its own FDK, which is rolling out on a variety of languages to help accelerate function development and provide access to HTTP primitive objects to make building REST API’s with Fn far more flexible.

## Platform 9's Fission

Fission is Kubernetes native-framework which uses a base image called an “environment” that functions get injected into which removes the need of having a local Docker instance to build custom images against or having to manage any kind of container images repository, but it still gives the developer the flexibility of providing a custom runtime environment if needed.

Unlike most of the projects mentioned before, which instantiate function-specific containers that always stay resident in memory, Fission maintains a pool of containers that contain language runtimes, but only get the function code loaded into them upon function invocation, a model much closer to how the public cloud services like Lambda do it.  

Fission also has a very flexible API gateway that enables developers to build routes independent of function names and paths.

## Bitnami's Kubeless

Kubeless is also a Kubernetes-native serverless framework that eases the developer experience considerably with it's comprehensive set of examples making it easy to learn.

Kubeless offers the best developer experience with a command line tool that's similar to Amazon Lambda CLI.  It also provides Prometheus monitoring of functions calls and latency.

## Demos

### Knative Demo

``` Powershell
multipass launch -n knative-k3s
# transfer files
multipass exec mkdir knative
multipass transfer kourier-nodeport.yaml knative-k3s:knative/kourier-nodepack.yaml
multipass transfer kn-linux-amd64 knative-k3s:knative/kn
multipass transfer .\Desktop\whitepaper\codes\load-tests\normal-hello.py knative-k3s:knative/normal-hello.py
# access k3s shell
multipass shell knative-k3s
# Install k3s
curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE='644' sh -s - --disable traefik
# Install knative serving custom resources
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.17.0/serving-crds.yaml
# Install knative serving core
kubectl apply --filename https://github.com/knative/serving/releases/download/v0.17.0/serving-core.yaml
# Install kourier ingress as a lightweight replacement for Istio
# kubectl apply --filename https://github.com/knative/net-kourier/releases/download/v0.17.0/kourier.yaml
kubectl apply -f knative/kourier-nodeport.yaml
# Make kourier the default Ingress
kubectl patch configmap/config-network --namespace knative-serving --type merge --patch '{"data":{"ingress.class":"kourier.ingress.networking.knative.dev"}}'
# # Apply http://xip.io/ DNS
# kubectl apply --filename https://github.com/knative/serving/releases/download/v0.17.0/serving-default-domain.yaml
# Download knative CLI
# curl https://storage.googleapis.com/knative-nightly/client/latest/kn-linux-amd64 -O
# chmod +x kn-linux-amd64
# sudo mv kn-linux-amd64 /usr/bin/kn
sudo mv knative/kn-linux-amd64 /usr/bin/kn
# Export Kubeconfig
cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
# create registry container secret
export username=''
export password=''
kubectl create secret docker-registry registry-secret --docker-username=$username --docker-password=$password --docker-server=https://mofattah.jfrog.io
# append new line to curl output
echo '-w "\n"' >> ~/.curlrc
# create service
kn service create hello-world --pull-secret registry-secret --image mofattah.jfrog.io/docker-quickstart/hello-nodejs --env TARGET="World"
# test endpoint
curl http://hello-world.default.127.0.0.1.nip.io:31080
# load tests requirements
sudo apt update
sudo apt install python3-pip
pip3 install locust
# update concurrency
kn service update hello-world --concurrency-limit=1
# load and see how scaling happens
locust -f knative/normal-hello.py --host http://hello-world.default.127.0.0.1.nip.io:31080 --headless -u 100 -r 10 -t 1m
# update with max scale
kn service update hello-world --max-scale=5
# load and see how scaling is limited now
locust -f knative/normal-hello.py --host http://hello-world.default.127.0.0.1.nip.io:31080 --headless -u 100 -r 10 -t 1m
# update concurrecny
kn service update hello-world --revision-name hello-world-1 --concurrency-limit=0
# load and see no almost scaling even though max-scale is still 5
locust -f knative/normal-hello.py --host http://hello-world.default.127.0.0.1.nip.io:31080 --headless -u 100 -r 10 -t 1m
# update message
kn service update hello-world --revision-name hello-world-2 --env TARGET="Ergonomics"
# test new output
curl http://hello-world.default.127.0.0.1.nip.io:31080
# update traffic
kn service update hello-world --traffic hello-world-1=20,hello-world-2=80
# load and see output come from 2 revisions
locust -f knative/normal-hello.py --host http://hello-world.default.127.0.0.1.nip.io:31080 --headless -u 100 -r 10 -t 1m
# update new revision with tag
kn service update hello-world --revision-name hello-world-3 --tag hello-world-3=hw3 --env TARGET="all of you"
# load and see that with no traffic update last revision is not used
locust -f knative/normal-hello.py --host http://hello-world.default.127.0.0.1.nip.io:31080 --headless -u 100 -r 10 -t 1m
# curl from special url using the tag
curl http://hw3-hello-world.default.127.0.0.1.nip.io:31080

```
