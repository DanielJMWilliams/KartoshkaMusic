variable "aws_region" {
  description = "AWS region"
  default     = "eu-west-2"
}

variable "rds_engine" {
  description = "Database engine for RDS"
}

variable "db_class" {
  description = "Instance class for RDS"
}

variable "rds_allocated_storage" {
  description = "Allocated storage for RDS"
}

variable "rds_identifier" {
  description = "Identifier for RDS instance"
}

variable "rds_db_name" {
  description = "Database name for RDS instance"
}

variable "rds_username" {
  description = "Username for RDS database"
}

variable "rds_password" {
  description = "Password for RDS database"
}

variable "rds_port" {
  description = "Password for RDS database"
}

variable "app_image_url"{
  description= "The application image url for ecs."
}

variable "app_container_name"{
  description= "The application container name."
}