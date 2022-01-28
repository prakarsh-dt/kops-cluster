# Download Config file
# Take user inputs
# Generate random cluster name and attach with Domain name
# Apply config file
# Execute the kops commands
from time import sleep
import yaml
import random
import string
import subprocess as sp
import os

def banner(heading):
    print("-"*25)
    print(heading)
    print("-"*25)


banner("Downloading files..")
os.system("sleep 2")
sp.getoutput("wget https://raw.githubusercontent.com/Abhinav-26/kops-cluster/dev-cluster-config/devCluster/cluster.yaml")
sp.getoutput("wget https://raw.githubusercontent.com/Abhinav-26/kops-cluster/dev-cluster-config/devCluster/master.yaml")
sp.getoutput("wget https://raw.githubusercontent.com/Abhinav-26/kops-cluster/dev-cluster-config/devCluster/worker.yaml")
print("\nDownloading Completed!\n")
os.system("sleep 2")

chars = string.ascii_lowercase
definedText =  'test.' + ''.join(random.choice(chars) for i in range(5)) + '.'

banner("Give Your Desired Values")

domianName  = input("Enter Your Cluster Domain : ")
clusterName = definedText + domianName

region = input("Enter the Region for Cluster : ")

stateStore = input("Enter the bucket name to store Cluster Configs :")
stateStore = "s3://{}".format(stateStore)

print("Your Entered bucket is :", stateStore)
os.system("sleep 1")
os.environ['KOPS_STATE_STORE'] = stateStore

os.system("cp cluster.yaml cluster.yaml.tmp && sed 's/---//g' cluster.yaml.tmp > cluster.yaml && rm cluster.yaml.tmp")
os.system("cp master.yaml master.yaml.tmp && sed 's/---//g' master.yaml.tmp > master.yaml && rm master.yaml.tmp")

# # # Cluster Config
with open('cluster.yaml', 'r') as f:
    dataCluster = yaml.safe_load(f)

dataCluster['metadata']['name']= clusterName
dataCluster['spec']['etcdClusters'][0]['etcdMembers'][0]['instanceGroup'] = "master-" + region
dataCluster['spec']['etcdClusters'][1]['etcdMembers'][0]['instanceGroup'] = "master-" + region
dataCluster['spec']['subnets'][0]['name'] = region
dataCluster['spec']['subnets'][0]['zone'] = region

with open('cluster.yaml', 'w') as f:
    yaml.dump(dataCluster, f)

# # # Master Node
with open('master.yaml', 'r') as f:
    dataMaster = yaml.safe_load(f)

dataMaster['metadata']['labels']['kops.k8s.io/cluster']= clusterName
dataMaster['metadata']['name'] = "master-" + region
dataMaster['spec']['nodeLabels']['kops.k8s.io/instancegroup'] = "master-" + region
dataMaster['spec']['subnets'][0] = region

with open('master.yaml', 'w') as f:
    yaml.dump(dataMaster, f)

# # # Worker Node
with open('worker.yaml', 'r') as f:
    dataWorker = yaml.safe_load(f)

dataWorker['metadata']['labels']['kops.k8s.io/cluster']= clusterName
dataWorker['spec']['subnets'][0] = region
with open('worker.yaml', 'w') as f:
    yaml.dump(dataWorker, f)

banner("Generating Cluster-Config File")

# Creating Cluster Config File 
if sp.getoutput("cat cluster.yaml | tail -n 1") == "---":
    print("cluster.yaml file configured for merging")
else:
    sp.getoutput('echo "\n---" >> cluster.yaml')

if sp.getoutput("cat master.yaml | tail -n 1") == "---":
    print("master.yaml file configured for merging")
else:
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
        # print("Found the file")
        os.system("rm cluster-config.yaml")
        print("\nCreating Config File\n")
        os.system("sleep 2")
        os.system("cat cluster.yaml master.yaml worker.yaml >> cluster-config.yaml")
        break
    elif i != "cluster-config.yaml\n".encode("utf-8"):
        # print("File Not Found")
        print("\nCreating new Config File\n")
        os.system("sleep 2")
        os.system("cat cluster.yaml master.yaml worker.yaml >> cluster-config.yaml")
        break

# print("cluster-config.yaml\n".encode("utf-8"))

banner("Creating Cluster...")
os.system("sleep 2")

os.system("kops create -f cluster-config.yaml")
print("{} has been Registered".format(clusterName))
os.system("sleep 2")

os.system("kops export kubeconfig --admin=18000h --name {}".format(clusterName))

print("Applying the cluster changes")
os.system("sleep 2")
os.system("kops update cluster {} --yes".format(clusterName))

