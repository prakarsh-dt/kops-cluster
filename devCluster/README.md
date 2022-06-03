# Steps to create DevCluster

**Step-1:** Download the script
```bash
wget https://raw.githubusercontent.com/prakarsh-dt/kops-cluster/main/devCluster/cluster-create.py
```

**Step-2:** Execute the script
```bash
python3 cluster-create.py --cluster <clusterName.devtron.info> --region <us-east-1a> --bucket <kops-devcluster-singlenode> --devtron 
```
[Note: If you don't want to install Devtron using the script, remove --devtron/-d argument from the above command]

**Step-3:** Now copy & paste the command given after the script is executed
### Arguments

```bash
usage: python3 cluster-create.py [options]

A Script Written in Python to Create Single Node Kops Cluster & install Devtron

optional arguments:
  -h, --help      show this help message and exit
  -c, --cluster   name of your cluster i.e, xyz.devtron.info
  -r, --region    region to create your cluster i.e, us-east-1a
  -b, --bucket    bucket name to store kops configs i.e, kops-devcluster-singlenode
  -d, --devtron   to install Devtron after creating cluster
```
### Apply devtron-ucid
If Devtron is installed for testing/POC, please apply the below command.
```bash
kubectl -ndevtroncd apply -f https://raw.githubusercontent.com/prakarsh-dt/kops-cluster/main/devCluster/devtron-ucid.yaml 
```

### To Delete the Cluster
Execute the following command to delete the cluster
```bash
kops delete cluster <clusterName> --yes
```
