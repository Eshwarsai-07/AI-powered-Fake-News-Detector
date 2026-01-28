# 1. VPC: The main network container
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "ai-fake-news-detector-vpc"
  }
}

# 2. Internet Gateway: Allows access to the internet
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "ai-fake-news-detector-igw"
  }
}

# 3. Get available AZs dynamically
data "aws_availability_zones" "available" {
  state = "available"
}

# 4. Subnet: A specific section of the VPC for our instance
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "ai-fake-news-detector-subnet"
  }
}

# 4. Route Table: Traffic rules (Send internet traffic to Gateway)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "ai-fake-news-detector-rt"
  }
}

# 5. Association: Apply the Route Table to our Subnet
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
