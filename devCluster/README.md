# Steps to create DevCluster

**Step-1:** Download the script
```bash
wget https://raw.githubusercontent.com/prakarsh-dt/kops-cluster/main/devCluster/cluster-create.py
```

**Step-2:** Execute the script
```bash
python3 cluster-create.py
```

**Step-3:** Now copy the command given after the script is executed

### To Delete a Cluster
Execute the following command to delete the cluster
```bash
kops delete cluster Cluster_Name --yes
```
