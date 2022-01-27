# Download Config file
# Take user inputs
# Generate random cluster name and attach with Domain name
# Apply config file
# Execute the kops commands
import yaml
import random
import string
import subprocess as sp
import os

chars = string.ascii_lowercase
definedText =  'test.' + ''.join(random.choice(chars) for i in range(5)) + '.'

domianName  = input("Enter Your Cluster Domain : ")
clusterName = definedText + domianName

region = input("Enter the Region for Cluster : ")

# Cluster Config
with open('cluster.yaml', 'r') as f:
    dataCluster = yaml.safe_load(f)

dataCluster['metadata']['name']= clusterName
dataCluster['spec']['etcdClusters'][0]['etcdMembers'][0]['instanceGroup'] = "master-" + region
dataCluster['spec']['etcdClusters'][1]['etcdMembers'][0]['instanceGroup'] = "master-" + region
dataCluster['spec']['subnets'][0]['name'] = region
dataCluster['spec']['subnets'][0]['zone'] = region

with open('cluster.yaml', 'w') as f:
    yaml.dump(dataCluster, f)

# Master Node
with open('master.yaml', 'r') as f:
    dataMaster = yaml.safe_load(f)

dataMaster['metadata']['labels']['kops.k8s.io/cluster']= clusterName
dataMaster['metadata']['name'] = "master-" + region
dataMaster['spec']['nodeLabels']['kops.k8s.io/instancegroup'] = "master-" + region
dataMaster['spec']['subnets'][0] = region

with open('master.yaml', 'w') as f:
    yaml.dump(dataMaster, f)

# Worker Node
with open('worker.yaml', 'r') as f:
    dataWorker = yaml.safe_load(f)

dataWorker['metadata']['labels']['kops.k8s.io/cluster']= clusterName
dataWorker['spec']['subnets'][0] = region
with open('worker.yaml', 'w') as f:
    yaml.dump(dataWorker, f)

# Creating Cluster Config File 
sp.getoutput('echo "\n---" >> cluster.yaml')
sp.getoutput('echo "\n---" >> master.yaml')


# files = sp.getoutput("ls -1 *.yaml | awk '{print $1}'")
# files = list(files)

op = sp.Popen(["/bin/bash", "-c", "ls -q *.yaml"], stdout=sp.PIPE)
op = op.stdout.readlines()

# print(len(op))
# print(op)

for i in op:
    # i = i.decode("utf-8")
    # print(i)
    if i == "cluster-config.yaml\n".encode("utf-8"):
        # print("found the file")
        sp.getoutput('rm cluster-config.yaml')
        sp.getoutput('cat cluster.yaml master.yaml worker.yaml >> cluster-config.yaml')
        break
    else:
        print("Not Found")

# print("cluster-config.yaml\n".encode("utf-8"))

print("Creating Cluster Now")

os.system("kops create cluster -f cluster-config.yaml")
os.system("kops update cluster {} --yes".format(clusterName))

# sp.getoutput()
# os.system("echo {} is my cluster name".format(clusterName))