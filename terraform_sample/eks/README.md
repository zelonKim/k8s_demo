## Provision EKS using Terraform
```
https://developer.hashicorp.com/terraform/tutorials/kubernetes/eks

https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_cluster
```

### main.tf
```
provider "aws" {
  region = var.region
}

# Fetches the list of available availability zones (AZs).
# filter: Only get AZs that are already available
data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

# cluster_name: Cluster name is generated dynamically, using a random string for uniqueness.
locals {
  cluster_name = "education-eks-${random_string.suffix.result}"
}

# random_string "suffix": Generates a random 8-character alphanumeric string (no special chars).
resource "random_string" "suffix" {
  length  = 8
  special = false
}

# Use the public Terraform VPC module (version 5.8.1).
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"

  name = "education-vpc"

  cidr = "10.0.0.0/16"
  azs  = slice(data.aws_availability_zones.available.names, 0, 3)

  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]

  # Use a NAT Gateway for private subnets’ internet access.
  enable_nat_gateway   = true
  # Use a single NAT gateway (cost-saving).
  single_nat_gateway   = true
  # Enable DNS hostnames inside the VPC.
  enable_dns_hostnames = true

  # Tagging subnets so that EKS knows which ones can host load balancers:
  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.8.5"

  cluster_name    = local.cluster_name
  cluster_version = "1.29"

  cluster_endpoint_public_access           = true
  enable_cluster_creator_admin_permissions = true

  # Install AWS EBS CSI driver addon.
  # The addon uses an IAM role (created separately using IRSA).
  cluster_addons = {
    aws-ebs-csi-driver = {
      service_account_role_arn = module.irsa-ebs-csi.iam_role_arn
    }
  }

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Default settings for node groups: Amazon Linux 2 AMI.
  eks_managed_node_group_defaults = {
    ami_type = "AL2_x86_64"

  }

  eks_managed_node_groups = {
    one = {
      name = "node-group-1"

      instance_types = ["t3.small"]

      min_size     = 1
      max_size     = 3
      desired_size = 2
    }

    two = {
      name = "node-group-2"

      instance_types = ["t3.small"]

      min_size     = 1
      max_size     = 2
      desired_size = 1
    }
  }
}


# https://aws.amazon.com/blogs/containers/amazon-ebs-csi-driver-is-now-generally-available-in-amazon-eks-add-ons/ 
data "aws_iam_policy" "ebs_csi_policy" {
  arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}

# Use a Terraform module to create an IAM role that Kubernetes pods can assume via IRSA (IAM Roles for Service Accounts).
module "irsa-ebs-csi" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role-with-oidc"
  version = "5.39.0"

  create_role                   = true
  role_name                     = "AmazonEKSTFEBSCSIRole-${module.eks.cluster_name}"
  provider_url                  = module.eks.oidc_provider
  role_policy_arns              = [data.aws_iam_policy.ebs_csi_policy.arn]
  oidc_fully_qualified_subjects = ["system:serviceaccount:kube-system:ebs-csi-controller-sa"]
}

```