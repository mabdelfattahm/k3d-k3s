# Buildpacks and kpack

## Buildpacks

### What is a buildpack

A buildpack’s job is to gather everything an app needs to build and run, and it often does this job quickly and quietly. They are at the heart of transforming source code into a runnable app image.

Buildpacks are a good separation of concerns. It allow groups of equally enthusiastic teams to work together, each excelling in their own job. The developer's job is to focus on writing a good application, while someone is writing a buildpack for the framework/language and testing it against many other applications.

Using auto-detection, groups of buildpacks are sequentially tested against app’s source code and the first group that deems fit for source code will become the selected set of buildpacks for an app. Detection criteria is specific to each buildpack – for instance, an NPM buildpack might look for a package.json, and a Go buildpack might look for Go source files.

A builder is an image that bundles all the bits and information on how to build your apps, such as buildpacks and build-time image, as well as executes the buildpacks against your app source code.

### How to use buildpacks

- Select a builder  
  - To build an app, first decide which builder to use. A builder includes the buildpacks that will be used as well as the environment for building your app.
  - When using pack, run `pack suggest-builders` for a list of suggested builders. Many builder are available for the well-known languages like Java(Maven/Gradle), Go, PHP, Ruby, Python, etc.
- Build app
  After deciding on what builder to use, build the app using `pack build` command. To avoid specifying a builder each time set default builder using `pack set-default-builder <Builder>`
  
  ``` Bash
  pack build sample-app \
  --path samples/apps/java-maven \
  --builder cnbs/sample-builder:bionic
  ```

- Run app
  Run application using `docker run --rm -p 8080:8080 sample-app`

## kpack

  We have seen how `pack` works and how it builds a docker image from an application with ease, but where will one run `pack build` for a production applications, and what will trigger `pack build` to run when new Git commits are pushed?

  One solution is to setup a CI system to watch the Git repos, watch for updates to buildpacks, and run `pack build` automatically. Another solution is to use kpack.

  kpack uses the same system as the `pack` CLI, combined with the ability to watch for changes in both the source Git repository, and the upstream buildpacks using web hooks. If anything changes then the application is re-built and a new Docker image is created.

### How to use kpack

``` Powershell
sudo su
apt update
apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt update
apt install docker-ce docker-ce-cli containerd.io
# install k3d
curl -s https://raw.githubusercontent.com/rancher/k3d/main/install.sh |bash
k3d cluster create kpack-cluster --image rancher/k3s:v1.18.8-k3s1 --timeout 300s --servers 1 --agents 2 -p 8081:80@loadbalancer --api-port 5678 --update-default-kubeconfig
snap install kubectl --classic
mkdir kpack
cd kpack
curl -L https://github.com/pivotal/kpack/releases/download/v0.1.2/release-0.1.2.yaml -o kpack.yaml
kubectl apply -f kpack.yaml
kubectl create secret docker-registry registry-secret --docker-username=$username --docker-password=$password --docker-server=https://mofattah.jfrog.io
nano service-account.yaml
# apiVersion: v1
# kind: ServiceAccount
# metadata:
#  name: service-account
# secrets:
#  - name: registry-secret
kubectl apply -f service-account.yaml
nano cluster-store.yaml
# apiVersion: kpack.io/v1alpha1
# kind: ClusterStore
# metadata:
#   name: default
# spec:
#   sources:
#   - image: gcr.io/paketo-buildpacks/java
#   - image: gcr.io/paketo-buildpacks/nodejs
kubectl apply -f cluster-store.yaml
nano cluster-stack.yaml
# apiVersion: kpack.io/v1alpha1
# kind: ClusterStack
# metadata:
#   name: base
# spec:
#   id: "io.buildpacks.stacks.bionic"
#   buildImage:
#     image: "paketobuildpacks/build:base-cnb"
#   runImage:
#     image: "paketobuildpacks/run:base-cnb"
kubectl apply -f cluster-stack.yaml
nano builder.yaml
# apiVersion: kpack.io/v1alpha1
# kind: Builder
# metadata:
#   name: my-builder
#   namespace: default
# spec:
#   serviceAccount: service-account
#   tag: mofattah.jfrog.io/docker-quickstart/sample-builder
#   stack:
#     name: base
#     kind: ClusterStack
#   store:
#     name: default
#     kind: ClusterStore
#   order:
#   - group:
#     - id: paketo-buildpacks/java
#   - group:
#     - id: paketo-buildpacks/nodejs
kubectl apply -f builder.yaml
nano image.yaml
# apiVersion: kpack.io/v1alpha1
# kind: Image
# metadata:
#   name: sample-image
# spec:
#   tag: mofattah.jfrog.io/docker-quickstart/sample-image
#   serviceAccount: service-account
#   builder:
#     name: my-builder
#     kind: Builder
#   source:
#     git:
#       url: https://github.com/spring-projects/spring-petclinic
#       revision: master
kubectl apply -f image.yaml
nano image-jar.yaml
# apiVersion: kpack.io/v1alpha1
# kind: Image
# metadata:
#   name: some-image-from-jar
# spec:
#   tag: mofattah.jfrog.io/docker-quickstart/some-image-from-jar
#   serviceAccount: service-account
#   builder:
#     name: my-builder
#     kind: Builder
#   source:
#     blob:
#       url: https://storage.googleapis.com/build-service/sample-apps/spring-petclinic-2.1.0.BUILD-SNAPSHOT.jar
kubect; apply -f image-jar.yaml
curl -L https://github.com/pivotal/kpack/releases/download/v0.1.2/logs-v0.1.2-linux.tgz -o logs.tgz
tar -xzvf logs.tgz
chomd +x logs
rm logs.tgz
apt install jq
kubectl logs -n kpack $(kubectl get pod -n kpack | grep Running | head -n1 | awk '{print $1}') -f | jq -R fromjson?
```

#### kpack Problems

- All images are failing at the time of the trial due to the error
  > "error": "Operation cannot be fulfilled on builds.kpack.io 'IMAGE': the object has been modified; please apply your changes to the latest version and try again
- Documentation is straight forward, but there is no good support section
- Cannot seem to get the log utility to work
