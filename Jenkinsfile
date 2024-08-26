pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-registry-credential')
        DOCKER_IMAGE_NAME = "highfreshness/terraform-api"
        DOCKER_IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-registry-credential') {
                        docker.image("${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}").push()
                        docker.image("${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}").push("latest")
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout'
        }
    }
}