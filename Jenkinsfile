pipeline {
    agent any

    triggers {
        githubPush()
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/SeSAC-Cloud-dev/terraform_api_v2.git'
            }
        }
        
        stage('Update Dockerfile') {
            steps {
                sh 'docker build -t terraform-api:${BUILD_NUMBER} .'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t terraform-api:${BUILD_NUMBER} .'
            }
        }
        
        stage('Tag Docker Image') {
            steps {
                sh 'docker tag terraform-api:${BUILD_NUMBER} highfreshness/terraform-api:${BUILD_NUMBER}'
                sh 'docker tag terraform-api:${BUILD_NUMBER} highfreshness/terraform-api:latest'
            }
        }
        
        stage('Publish Docker Image') {
            steps {
                withDockerRegistry(credentialsId: 'docker-registry-credential', url: 'https://index.docker.io/v1/') {
                    sh 'docker push highfreshness/terraform-api:${BUILD_NUMBER}'
                    sh 'docker push highfreshness/terraform-api:latest'
                }
            }
        }
    }
}