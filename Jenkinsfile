pipeline {
    agent {
        docker {
            image 'python:3.12'
        }
    }
    
    triggers {
        githubPush()
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/your-repo/your-project.git'
            }
        }
        
        stage('Update Dockerfile') {
            agent {
                label 'controller'
            }
            steps {
                sh 'docker build -t terraform-api:${BUILD_NUMBER} .'
            }
        }
        
        stage('Build Docker Image') {
            agent {
                label 'controller'
            }
            steps {
                sh 'docker build -t terraform-api:${BUILD_NUMBER} .'
            }
        }
        
        stage('Tag Docker Image') {
            agent {
                label 'controller'
            }
            steps {
                sh 'docker tag terraform-api:${BUILD_NUMBER} highfreshness/terraform-api:${BUILD_NUMBER}'
                sh 'docker tag terraform-api:${BUILD_NUMBER} highfreshness/terraform-api:latest'
            }
        }
        
        stage('Publish Docker Image') {
            agent {
                label 'controller'
            }
            steps {
                withDockerRegistry(credentialsId: 'docker-registry-credentials', url: 'https://index.docker.io/v1/') {
                    sh 'docker push highfreshness/terraform-api:${BUILD_NUMBER}'
                    sh 'docker push highfreshness/terraform-api:latest'
                }
            }
        }
    }
}