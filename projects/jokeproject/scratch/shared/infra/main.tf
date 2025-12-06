##############################
# Shared Infra for Staging
##############################

module "eks_cluster" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 23.0"

  cluster_name    = "jokegen-staging-cluster"
  cluster_version = "1.27"
  subnets         = ["subnet-12345678", "subnet-23456789"]
  vpc_id          = "vpc-12345678"

  worker_groups = [
    {
      name                 = "worker-group-1"
      instance_type        = "t3.medium"
      asg_desired_capacity = 2
    }
  ]
}

resource "kubernetes_namespace" "jokegen" {
  metadata {
    name = "jokegen"
  }
}

resource "null_resource" "placeholder" {
  provisioner "local-exec" {
    command = "echo 'Infrastructure placeholder for staging'"
  }
}
