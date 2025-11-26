terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "indostar-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "indostar-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "IndoStar Naturals"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"
  
  environment         = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
}

# RDS PostgreSQL
module "rds" {
  source = "./modules/rds"
  
  environment           = var.environment
  vpc_id               = module.vpc.vpc_id
  private_subnet_ids   = module.vpc.private_subnet_ids
  db_instance_class    = var.db_instance_class
  db_name              = var.db_name
  db_username          = var.db_username
  db_password          = var.db_password
  multi_az             = var.db_multi_az
  backup_retention     = var.db_backup_retention
}

# ElastiCache Redis
module "redis" {
  source = "./modules/redis"
  
  environment         = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  node_type          = var.redis_node_type
  num_cache_nodes    = var.redis_num_nodes
}

# S3 and CloudFront
module "cdn" {
  source = "./modules/cdn"
  
  environment    = var.environment
  domain_name    = var.domain_name
  bucket_name    = var.s3_bucket_name
  certificate_arn = var.acm_certificate_arn
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"
  
  environment        = var.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  certificate_arn   = var.acm_certificate_arn
}

# ECS Cluster (Alternative to Kubernetes)
module "ecs" {
  source = "./modules/ecs"
  
  environment         = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  alb_target_group_arn = module.alb.backend_target_group_arn
  
  backend_image      = var.backend_image
  frontend_image     = var.frontend_image
  
  database_url       = module.rds.connection_string
  redis_url          = module.redis.connection_string
  
  environment_variables = var.environment_variables
  secrets              = var.secrets
}

# Route 53 DNS
module "dns" {
  source = "./modules/dns"
  
  domain_name         = var.domain_name
  alb_dns_name        = module.alb.dns_name
  alb_zone_id         = module.alb.zone_id
  cloudfront_dns_name = module.cdn.cloudfront_dns_name
  cloudfront_zone_id  = module.cdn.cloudfront_zone_id
}

# Auto Scaling
module "autoscaling" {
  source = "./modules/autoscaling"
  
  environment     = var.environment
  ecs_cluster_name = module.ecs.cluster_name
  ecs_service_name = module.ecs.backend_service_name
  
  min_capacity = var.autoscaling_min_capacity
  max_capacity = var.autoscaling_max_capacity
}
