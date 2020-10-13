# Custom resources and meta controller

## Custom resources

Custom resources are extensions of the Kubernetes API. Custom resources enable introducing new objects into the Kubernetes cluster to fulfill requirements. Once a custom resource is created in Kubernetes, it can be used like any other native Kubernetes object thus leveraging all the features of Kubernetes like its CLI, security, API services, RBAC etc.

### Types of custom resources

New resources are referred to as Custom Resources to distinguish them from built-in Kubernetes resources (like pods). Kubernetes provides two ways to add custom resources to a cluster:

- CustomResourceDefinitions (CRDs)
  - The CustomResourceDefinition API resource allows defining custom resources. Defining a CRD object creates a new custom resource with a name and schema that must be specified by the creator. The Kubernetes API serves and handles the storage of custom resource. The name of a CRD object must be a valid DNS subdomain name.

  - CRDs simplifies things by removing the need to create a new API server to handle the custom resource, but the generic nature of the implementation means you have less flexibility than with API server aggregation.

- API server aggregation (AA)
  - API Aggregation requires programming, but allows more control over API behaviors like how data is stored and conversion between API versions. Aggregated APIs are subordinate API servers that sit behind the primary API server, which acts as a proxy. To users, it simply appears that the Kubernetes API is extended.

### When to use CRDs or AAs

| CRDs | Aggregated API |
|------|----------------|
| Do not require programming. Users can choose any language for a CRD controller. | Requires programming in Go and building binary and image.|
| No additional service to run; CRDs are handled by API server. | An additional service to create and that could fail.|
| No ongoing support once the CRD is created. Any bug fixes are picked up as part of normal Kubernetes Master upgrades. | May need to periodically pickup bug fixes from upstream and rebuild and update the Aggregated API server.|
| No need to handle multiple versions of your API; for example, when you control the client for this resource, you can upgrade it in sync with the API. | You need to handle multiple versions of your API; for example, when developing an extension to share with the world. |

### ConfigMaps vs CRDs

| ConfigMaps | Custom resources |
|------------|------------------|
| There is an existing, well-documented config file format, such as a mysql.cnf or pom.xml | You want to use Kubernetes client libraries and CLIs to create and update the new resource |
|You want to put the entire config file into one key of a configMap | You want top-level support from kubectl |
|The main use of the config file is for a program running in a Pod on your cluster to consume the file to configure itself | You want to build new automation that watches for updates on the new object, and then CRUD other objects, or vice versa |
|Consumers of the file prefer to consume via file in a Pod or environment variable in a pod, rather than the Kubernetes API | You want to write automation that handles updates to the object |
|You want to perform rolling updates via Deployment, etc., when the file is updated | You want the object to be an abstraction over a collection of controlled resources, or a summarization of other resources |

---

## Metacontrollers

- Kubernetes Controller

  Distributed components in the Kubernetes control plane communicate with each other by posting records in a shared datastore (like a public message board).

  All participants can see what everyone is saying to everyone else, so each participant can easily access whatever information it needs to make the best decision, even as those needs change. The lack of silos also means extensions have the same power as built-in features.

  A Kubernetes controller is a long-running, automated, autonomous agent that participates in the control plane via this shared datastore (the Kubernetes API server). In the message board analogy, you can think of controllers like bots.

  A given controller might participate by doing any of the following:

  - Observing objects in the API server as inputs and creating or updating other objects in the API server as outputs (e.g. creating Pods for a ReplicaSet)
  - Observing objects in the API server as inputs and taking action in some other domain (e.g. spawning containers for a Pod)
  - Creating or updating objects in the API server to report observations from some other domain (e.g. “the container is running”)

- Custom Controller

  A custom controller is any controller that can be installed, upgraded, and removed in a running cluster, independently of the cluster’s own lifecycle. While custom resources provide storage for new types of objects, custom controllers define the behavior of a new extension to the Kubernetes API.

### Metacontroller

Metacontroller is a server that extends Kubernetes with APIs that encapsulate the common parts of writing custom controllers. It makes it easy to write and deploy custom controllers.

This server hosts multiple controllers. However, the set of hosted controllers changes dynamically in response to updates in objects of the Metacontroller API types. Metacontroller is thus itself a controller that watches the Metacontroller API objects and launches hosted controllers in response. In other words, it’s a controller-controller – hence the name.

- Lambda Controller

  When a controller is created with one of the Metacontroller APIs, only the business logic function specific to that controller is provided. Since these functions are called via webhooks, they can be written in any language that can understand HTTP and JSON, and optionally host them with a Functions-as-a-Service provider.

  The Metacontroller server then executes a control loop, calling the function whenever necessary to decide what to do.

  These callback-based controllers are called lambda controllers. To keep the interface as simple as possible, each lambda controller API targets a specific controller pattern, such as:

  - CompositeController: objects composed of other objects
  - DecoratorController: attach new behavior to existing objects

  Each lambda controller API defines a set of hooks, which it calls to let the programmer implement his business logic. Currently, these lambda hooks must be implemented as webhooks.

### Metacontroller Features

- Declarative Watches

  Rather than writing boilerplate code for each type of resource, Metacontroller can set up watch streams that are shared across all controllers that use Metacontroller. Metacontroller acts like a demultiplexer, determining which controllers will care about a given event in the stream and triggering their hooks only as needed and the API server will only need to send one Pod watch stream (to Metacontroller itself).

- Declarative Declarative Rolling Update

  Kubernetes APIs offers the ability to declaratively specify gradual state transitions. When an app’s container image or configuration is updated, for example, these controllers will slowly roll out Pods with the new template and automatically pause if things don’t look right.Implementing gradual state transitions involves careful bookkeeping with auxiliary records, which is why StatefulSet originally launched without rolling updates.

  Metacontroller simplifies the build of APIs that offer declarative rolling updates without all this additional bookkeeping. In fact, Metacontroller provides a declarative interface for configuring how to implement declarative rolling updates in the controller (declarative declarative rolling update), without the need to write any code to take advantage of this feature.

---

## Kubernetes Operators

Kubernetes can manage and scale stateless applications, such as web apps, mobile backends, and API services, without requiring any additional knowledge about how these applications operate. The built-in features of Kubernetes are designed to easily handle these tasks.

However, stateful applications, like databases and monitoring systems, require additional domain-specific knowledge that Kubernetes doesn’t have. It needs this knowledge in order to scale, upgrade, and reconfigure these applications.

The Kubernetes Operator concept was developed by engineers at CoreOS in 2016 as an advanced and native way of building and driving every application on the Kubernetes cluster, which needs domain-specific knowledge. It provides a consistent approach to handle all application operational processes automatically, without any human reaction via close cooperation with the Kubernetes API. In other words, an operator is a way of packaging, running, and managing Kubernetes applications.

The Operator simulates human operator behaviors in three steps: Observe, Analyze, and Act. First, it observes the current cluster state by using the Kubernetes API. Second, it finds the differences between the desired state and current state. Last, it fixes the difference through one or both of the cluster management API or the Kubernetes API.

Kubernetes operators encode this specific domain knowledge into Kubernetes extensions so that it can manage and automate an application’s life cycle. By removing difficult manual application management tasks, Kubernetes operators make these processes scalable, repeatable, and standardized.

### Prometheus Operator

If we examine Prometheus Operator, one of the first and most popular operators, we will find that it simplifies the deployment and configuration of Prometheus, Alertmanager, and related monitoring components.

The core feature of the Prometheus Operator is to monitor the Kubernetes API server for changes to specific objects and ensure that the current Prometheus deployments match these objects. The Operator acts on the following Custom Resource Definitions (CRDs):

- Prometheus, which defines a desired Prometheus deployment.
- Alertmanager, which defines a desired Alertmanager deployment.
- ServiceMonitor, which specifies how groups of Kubernetes services should be monitored. The Operator automatically generates Prometheus scrape configuration based on the current state of the objects in the API server.
- PodMonitor, which specifies how a group of pods should be monitored. The Operator automatically generates Prometheus scrape configuration based on the current state of the objects in the API server.
- PrometheusRule, which defines a desired set of Prometheus alerting and/or recording rules. The Operator generates a rule file, which can be used by Prometheus instances.