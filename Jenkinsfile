
pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment{
        ECR_REPO = "214346124741.dkr.ecr.ap-northeast-2.amazonaws.com/cloudnexus/daas_backend"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/SeSAC-Cloud-dev/terraform_api.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 214346124741.dkr.ecr.ap-northeast-2.amazonaws.com'
                sh 'docker build -t cloudnexus/daas_backend:${BUILD_NUMBER} .'
            }
        }
        
        stage('Tag Docker Image') {
            steps {
                sh 'docker tag cloudnexus/daas_backend:${BUILD_NUMBER} ${ECR_REPO}:${BUILD_NUMBER}'
                sh 'docker tag cloudnexus/daas_backend:${BUILD_NUMBER} ${ECR_REPO}:latest'
            }
        }
        
        stage('Publish Docker Image') {
            steps {
                sh 'docker push ${ECR_REPO}:${BUILD_NUMBER}'
                sh 'docker push ${ECR_REPO}:latest'
            }
        }
    }

    post {
        always {
            script {
                //sh 'docker system prune -f'
                //sh 'docker rmi $(docker images -q --filter "dangling=true")
                  sh 'docker rmi ${ECR_REPO}:${BUILD_NUMBER}'
                  sh 'docker rmi cloudnexus/daas_backend:latest'
            }
        }
    }

}

