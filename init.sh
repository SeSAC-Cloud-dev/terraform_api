#!/bin/bash
apt update

apt install -y curl unzip gpg wget lsb-release python3-pip python3-venv

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
	    unzip awscliv2.zip && \
	        ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update

wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
	    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list && \
	        apt update && apt install -y terraform


python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt 

uvicorn main:app --host 0.0.0.0