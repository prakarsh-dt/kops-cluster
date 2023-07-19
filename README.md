# Commands to create a Test KOPs Cluster

## Prerequisites
1. Ensure that the machine you are running the kops commands on has proper AWS access to be able to create the cluster.
2. Ensure that the machine you are running has kops installed

### STEPS

1. Download the kops configuration file
```shell
wget https://raw.githubusercontent.com/prakarsh-dt/kops-cluster/main/test/kops-spots-use1-cluster-config.yaml
```

2. Set the KOPS_STATE_STORE environment variable with the statestore bucket
```shell
export KOPS_STATE_STORE="s3://statestore-bucket-name"
```

3. Create the cluster with the configs from the downloaded file (Please change the cluster name/other configs if you have to before issuing the **kops create** command)
To change the cluster name please replace cluster name mentioned in the nodegroup labels as well.
```shell
kops create -f kops-spots-use1-cluster-config.yaml
kops update cluster test.devtron.k8s.local --yes
```

4. Create Secret
```shell
kops create secret --name test.devtron.k8s.local sshpublickey admin -i ~/.ssh/id_rsa.pub
kops update cluster test.devtron.k8s.local --yes
```

5. Update kubeconfig file to communicate with cluster
```shell
kops export kubeconfig --admin=18000h --name test.devtron.k8s.local
```

6. To delete the cluster please use the following command (make sure the KOPS_STATE_STORE environment variable is set)
```shell
kops delete cluster test.devtron.k8s.local --yes
```
