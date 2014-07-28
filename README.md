Invoke the Core
===============

![](http://i.imgur.com/6V8XFRp.png?1)

Provision a CoreOS cluster with an invoke script. Lets you use Rackspace's OnMetal or performance machines.

Steal freely from this for your own OpenStack setup.

## Requirements

* invoke
* rackspace-novaclient

Just `pip install invoke rackspace-novaclient` in your favorite way.

## Usage

Assuming you have the typical OpenStack environment variables set up (and are
using Rackspace flavors):

```
invoke cluster
```

This by default boots a cluster using the SSH key named "main" from nova. You
can also change this key at runtime:

```
invoke cluster --key-name=rgbkrk
```

## Playing around

Once your cluster is up, ssh into any of the nodes and run `fleetctl list-machines`

```
$ ssh -A core@162.209.124.8
CoreOS (stable)
core@n00 ~ $ fleetctl list-machines
MACHINE		IP		METADATA
06cf1e22...	162.209.124.8	provider=rackspace,region=IAD
21c8d9ac...	162.209.125.24	provider=rackspace,region=IAD
dad793a2...	162.209.125.29	provider=rackspace,region=IAD
```

You can now [submit containers to be shuffled around by fleet](https://coreos.com/docs/launching-containers/launching/launching-containers-fleet/)
and generally have a go at [all the stuff you should get ready to cram in your
head](https://coreos.com/docs/) for CoreOS.
