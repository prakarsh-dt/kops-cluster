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
import argparse

def banner(heading):
    print("-"*25)
    print(heading)
    print("-"*25)

parser = argparse.ArgumentParser(prog='python3 cluster-create.py', usage='%(prog)s [options]', 
                                description="A Script Written in Python to Create Single Node Kops Cluster")

parser.add_argument("-c", "--cluster", required=True, help="name of your cluster i.e, xyz.devtron.info", metavar="")
parser.add_argument("-r", "--region", required=True, help="region to create your cluster i.e, us-east-1a", metavar="")
parser.add_argument("-b", "--bucket", required=True, help="bucket name to store kops configs i.e, kops-devcluster-singlenode", metavar="")
parser.add_argument("-d", "--devtron", action="store_true", help="to install Devtron after creating cluster")

args = parser.parse_args()

banner("Downloading Config Files..")
os.system("sleep 2")
sp.getoutput("wget https://raw.githubusercontent.com/prakarsh-dt/kops-cluster/main/devCluster/cluster.yaml")
sp.getoutput("wget https://raw.githubusercontent.com/prakarsh-dt/kops-cluster/main/devCluster/master.yaml")
sp.getoutput("wget https://raw.githubusercontent.com/prakarsh-dt/kops-cluster/main/devCluster/worker.yaml")
print("\nFiles has been Downloaded!\n")
os.system("sleep 2")

# installDevtron = args.devtron

chars = string.ascii_lowercase
global definedText
definedText =  'test.' + ''.join(random.choice(chars) for i in range(5)) + '.'

global clusterName
clusterName = definedText + args.cluster
# print(clusterName)

global region
region = args.region
# print(region)

global stateStore
stateStore = args.bucket
stateStore = "s3://{}".format(stateStore)
# print(stateStore)
print("Received values are - \nCluster Name - {}\nRegion - {}\nBucket Name - {}\n".format(clusterName, region, stateStore))

os.system("sleep 1")
os.environ['KOPS_STATE_STORE'] = stateStore

os.system("cp cluster.yaml cluster.yaml.tmp && sed 's/---//g' cluster.yaml.tmp > cluster.yaml && rm cluster.yaml.tmp")
os.system("cp master.yaml master.yaml.tmp && sed 's/---//g' master.yaml.tmp > master.yaml && rm master.yaml.tmp")

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

banner("Generating Cluster-Config File..")

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

banner("Creating Cluster..")
os.system("sleep 2")

os.system("kops create -f cluster-config.yaml")
# print("{} has been Registered".format(clusterName))
os.system("sleep 2")


banner("Applying the Cluster Changes..")
os.system("sleep 2")
os.system("kops update cluster {} --yes".format(clusterName))

os.system("kops export kubeconfig --admin=18000h --name {}".format(clusterName))

banner("Validating Cluster..")
os.system("sleep 2")
os.system("touch temp.txt")

while sp.getoutput("cat temp.txt") == "":
    value = sp.getoutput("kops validate cluster | grep ip | awk '{print $1}' > temp.txt")
    # print("\nThe Node is Not Ready Yet...\n")
    os.system("kops validate cluster")
    os.system("sleep 20")
    if sp.getoutput("cat temp.txt") != "":
        print("\n\nFound the Node Name : ", end="")
        os.system("cat temp.txt")
    else:
        continue

banner("Extracting the Node Name")
os.system("sleep 2")
nodeName = sp.getoutput("cat temp.txt")

banner("Checking Taints..")
os.system("sleep 2")
os.system("kubectl describe node {} | grep Taints".format(nodeName))

banner("Removing Taints")
os.system("sleep 2")
os.system("kubectl taint node {} node-role.kubernetes.io/master:NoSchedule-".format(nodeName))

# Removing Downloaded Resources
os.system("rm cluster-config.yaml cluster.yaml master.yaml worker.yaml temp.txt")


if args.devtron != False:
    banner("Installing Devtron")
    sp.getoutput("wget https://raw.githubusercontent.com/prakarsh-dt/kops-cluster/main/devCluster/devtron-ucid.yaml")
    os.system("helm repo add devtron https://helm.devtron.ai && helm repo update")
    sp.getoutput("helm install devtron devtron/devtron-operator --create-namespace --namespace devtroncd --set installer.modules={cicd}")
    banner("Validating Installation")
    os.system("sleep 2")
    os.system("touch status.txt")

    while sp.getoutput("cat status.txt") != "Applied":
        sp.getoutput("kubectl -n devtroncd get installers installer-devtron -o jsonpath='{.status.sync.status}' > status.txt")
        os.system("sleep 30")
        if sp.getoutput("cat status.txt") == "Downloaded":
            print("\nStill Downloading Microservices : ", end="")
            os.system("cat status.txt")
            print("\n")
            os.system("kubectl get pods -ndevtroncd")
        else:
            continue

    print("\nCongratulations! Devtron has been installed Successfully.\n")
    os.system("helm status devtron -ndevtroncd")
    os.system("rm status.txt && sleep 2")
    banner("Changing LB to NodePort")
    os.system("kubectl patch -n devtroncd svc devtron-service -p \'{\"spec\": {\"ports\": [{\"port\": 80,\"targetPort\": \"devtron\",\"protocol\": \"TCP\",\"name\": \"devtron\",\"nodePort\": 32080}],\"type\": \"NodePort\",\"selector\": {\"app\": \"devtron\"}}}\'")
    banner("Applying ucid")
    os.system("kubectl apply -f devtron-ucid.yaml -ndevtroncd")
    os.system("rm devtron-ucid.yaml")


banner("Please Execute the Following Command")
os.system("sleep 3")
print("\n* export KOPS_STATE_STORE={}".format(stateStore))