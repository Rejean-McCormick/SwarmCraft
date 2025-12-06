# Terraform configuration for imaginary catalog deployment

terraform {
  required_version = ">= 1.4"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0.0"
    }
  }
  backend "s3" {
    bucket = "imaginary-catalog-terraform-state"
    key    = "global/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

# IAM roles for ECS task execution

resource "aws_iam_role" "ecs_task_execution" {
  name = "ecs-task-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = { Service = "ecs-tasks.amazonaws.com" },
        Effect = "Allow",
        Sid = ""
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy_attach" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.ecs_task_execution.arn
}

resource "aws_iam_policy" "ecs_task_execution" {
  name        = "ecs-task-execution-policy"
  description = "Policy for ECS task execution"
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = ["ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage", "ecr:BatchCheckLayerAvailability", "logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Resource = "*",
        Effect   = "Allow"
      }
    ]
  })
}

# Networking (placeholders; replace with real VPC/Subnet IDs in your environment or import existing resources)

resource "aws_vpc" "catalog_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "imaginary-catalog-vpc"
  }
}

resource "aws_subnet" "catalog_subnet" {
  vpc_id            = aws_vpc.catalog_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  tags = {
    Name = "imaginary-catalog-subnet"
  }
}

resource "aws_security_group" "catalog_sg" {
  name        = "imaginary-catalog-sg"
  description = "SG for imaginary catalog"
  vpc_id      = aws_vpc.catalog_vpc.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ECS Cluster

resource "aws_ecs_cluster" "catalog" {
  name = "imaginary-catalog-cluster"
}

# Image variables (or use default placeholders)
variable "backend_image" {
  type    = string
  default = "nginx:alpine"
}

variable "frontend_image" {
  type    = string
  default = "nginx:alpine"
}

locals {
  backend_image  = var.backend_image
  frontend_image = var.frontend_image
  container_definitions = jsonencode([
    {
      name           = "catalog-backend"
      image          = local.backend_image
      essential      = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
    },
    {
      name           = "catalog-frontend"
      image          = local.frontend_image
      essential      = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]
    }
  ])
}

# Task Definition includes both containers so a single Fargate task can run backend + frontend

resource "aws_ecs_task_definition" "catalog" {
  family                   = "imaginary-catalog"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  container_definitions    = local.container_definitions
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task_execution.arn
}

# ECS Service

resource "aws_ecs_service" "catalog" {
  name            = "imaginary-catalog-svc"
  cluster         = aws_ecs_cluster.catalog.id
  task_definition = aws_ecs_task_definition.catalog.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = [aws_subnet.catalog_subnet.id]
    security_groups  = [aws_security_group.catalog_sg.id]
    assign_public_ip = true
  }
}
