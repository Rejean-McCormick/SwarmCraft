variable "aws_region" {
  description = "AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "k8s_host" {
  description = "Kubernetes cluster API server endpoint"
  type        = string
  default     = "https://kubernetes.example.com"
}

variable "k8s_client_certificate" {
  description = "Base64-encoded client certificate for Kubernetes authentication"
  type        = string
  default     = ""
}

variable "k8s_client_key" {
  description = "Base64-encoded client key for Kubernetes authentication"
  type        = string
  default     = ""
}

variable "k8s_cluster_ca_certificate" {
  description = "Base64-encoded cluster CA certificate"
  type        = string
  default     = ""
}
