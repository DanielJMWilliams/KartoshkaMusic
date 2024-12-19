resource "aws_db_subnet_group" "db_subnet_group"{
    name = "kmusic-db-subnet-group"
    subnet_ids = [aws_subnet.private1.id, aws_subnet.private2.id]
}

resource "aws_db_instance" "kmusic-db" {
    engine                    = var.rds_engine
    instance_class            = var.db_class
    allocated_storage         = var.rds_allocated_storage
    identifier                = var.rds_identifier
    db_name                   = var.rds_db_name
    username                  = var.rds_username
    password                  = var.rds_password
    port                      = var.rds_port
    skip_final_snapshot       = true 
    vpc_security_group_ids    = [aws_security_group.rds_sg.id]
    db_subnet_group_name      = aws_db_subnet_group.db_subnet_group.name
    publicly_accessible       = false
}