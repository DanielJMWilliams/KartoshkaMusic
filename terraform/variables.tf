variable "aws_region" {
  description = "AWS region"
  default     = "eu-west-2"
}

variable "app_image_url"{
  description= "The application image url for ecs."
}

variable "app_container_name"{
  description= "The application container name."
}