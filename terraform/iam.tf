resource "aws_iam_role" "ecs_execution_role" {
  name               = "EcsExecutionRole"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ecs-tasks.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      },
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "events.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "ecr_access_policy" {
  name        = "EcrAccessPolicy"
  description = "Allows ECS task execution role to pull images from ECR"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer"
      ],
      "Resource": "*"
    }]
  })
}

resource "aws_iam_policy" "ecs_exec_policy" {
  name        = "EcsExecPolicy"
  description = "Allows ECS Exec"
  
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "ecs:ExecuteCommand",
        "ecs:GetCommand",
        "ecs:ListCommands",
        "ecs:ListClusters",
        "ecs:ListContainerInstances",
        "ecs:RegisterTaskDefinition",
        "ecs:RunTask",
        "ssmmessages:StartSession",
        "ssmmessages:CreateControlChannel",
        "ssmmessages:CreateDataChannel",
        "ssmmessages:OpenControlChannel",
        "ssmmessages:OpenDataChannel",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "iam:PassRole",
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "attach_ecr_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_policy.ecr_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_ecs_exec_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_policy.ecs_exec_policy.arn
}