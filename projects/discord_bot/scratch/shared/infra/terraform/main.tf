provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "discord-bot-artifacts" {
  bucket = "discord-bot-artifacts"
  acl    = "private"
}
