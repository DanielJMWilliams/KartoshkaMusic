resource "aws_lb" "web_lb" {
  name               = "web-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.external_lb_sg.id]
  subnets            = [aws_subnet.public1.id, aws_subnet.public2.id]
}


resource "aws_lb_target_group" "web_tg" {
  name        = "web-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
}


resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.web_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_tg.arn
  }
}

resource "aws_lb_listener" "https_listener" {
  load_balancer_arn = aws_lb.web_lb.arn
  port              = 443
  protocol          = "HTTPS"

  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = data.aws_acm_certificate.example.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_tg.arn
  }
}

data "aws_route53_zone" "web_zone" {
  name         = "danielspyros.com"
  private_zone = false
}

/*

resource "aws_route53_zone" "web_zone" {
  name = "danielspyros.com"
}

*/
resource "aws_route53_record" "web_dns" {
  zone_id = data.aws_route53_zone.web_zone.zone_id
  name    = "www"
  type    = "A"

  alias {
    name                   = aws_lb.web_lb.dns_name
    zone_id                = aws_lb.web_lb.zone_id
    evaluate_target_health = true
  }
}

data "aws_acm_certificate" "example" {
  domain   = "www.danielspyros.com"
  statuses = ["ISSUED"]
}
