resource "aws_ecs_cluster" "ecs"{
    name = "kmusic-cluster"
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/kmusic/app"
  retention_in_days = 7
}
resource "aws_ecs_task_definition" "app" {
  family                   = "app"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_execution_role.arn
  container_definitions    = jsonencode([{
    name      = "kmusicApp"
    image     = var.app_image_url
    cpu       = 256
    memory    = 512
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.app.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }
    }
    portMappings = [
      {
        containerPort = 80
        hostPort      = 80 //we talk to the pod on this port
      }
    ]
    environment = [
      {
        name  = "DEBUG"
        value = "true"
      },
      {
        name  = "SPOTIFY_REDIRECT_URI"
        value = "https://kmusic.danielspyros.com/callback"
      },
      {
        name  = "SPOTIFY_LOGIN_SCOPE"
        value = "user-modify-playback-state user-read-playback-state user-read-recently-played user-read-currently-playing user-library-read user-library-modify"
      },
      {
        name="ALLOWED_HOSTS"
        value = "kmusic.danielspyros.com,danielspyros.com,web-lb-847508913.eu-west-2.elb.amazonaws.com,${aws_lb.web_lb.dns_name},10.0.0.*"
      }
    ]
    secrets = [
      {
        name      = "SPOTIFY_CLIENT_ID"
        valueFrom = "${data.aws_secretsmanager_secret.spotify_client.arn}:SPOTIFY_CLIENT_ID::"
      },
      {
        name      = "SPOTIFY_CLIENT_SECRET"
        valueFrom = "${data.aws_secretsmanager_secret.spotify_client.arn}:SPOTIFY_CLIENT_SECRET::"
      },
      {
        name      = "DJANGO_SECRET"
        valueFrom = "${data.aws_secretsmanager_secret.django.arn}:DJANGO_SECRET::"
      }
    ]
    command = ["python", "manage.py", "runserver", "0.0.0.0:80"]
  }])
}

data "aws_secretsmanager_secret" "spotify_client" {
  name = "kmusic/spotify_client"
}

data "aws_secretsmanager_secret" "django" {
  name = "kmusic/django"
}

resource "aws_ecs_service" "app" {
  name                    = "kmusic-app-service"
  cluster                 = aws_ecs_cluster.ecs.arn
  task_definition         = aws_ecs_task_definition.app.arn
  desired_count           = 1
  launch_type             = "FARGATE"
  enable_execute_command  = true


  load_balancer {
    target_group_arn = aws_lb_target_group.web_tg.arn
    container_name = var.app_container_name
    container_port = 80
  }
  

  network_configuration {
    subnets           = [aws_subnet.public1.id]
    security_groups   = [aws_security_group.ecs.id]
    assign_public_ip  = true
  }
}