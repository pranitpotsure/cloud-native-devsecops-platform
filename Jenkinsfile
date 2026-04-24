pipeline {
    agent any

    environment {
        AWS_REGION   = "ap-south-1"
        PROJECT_NAME = "boutique"
        IMAGE_TAG    = "${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

       stage('Set AWS Env') {
    steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-creds']]) {
            script {
                env.AWS_ACCOUNT_ID = sh(
                    script: "aws sts get-caller-identity --query Account --output text",
                    returnStdout: true
                ).trim()

                env.ECR_REGISTRY = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com"
            }
        }
    }
}

        stage('ECR Login') {
    steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-creds']]) {
            sh '''
                aws ecr get-login-password --region ${AWS_REGION} | \
                docker login --username AWS --password-stdin ${ECR_REGISTRY}
            '''
        }
    }
}

        stage('Build & Push') {
            steps {
                sh '''
                    cd src
                    SERVICES="adservice cartservice checkoutservice currencyservice emailservice frontend paymentservice productcatalogservice recommendationservice shippingservice shoppingassistantservice"

                    for SERVICE in $SERVICES; do
                        IMAGE="${ECR_REGISTRY}/${PROJECT_NAME}-${SERVICE}"

                        echo "Building $SERVICE..."
                        docker build -t $IMAGE:${IMAGE_TAG} -t $IMAGE:latest ./$SERVICE

                        echo "Pushing $SERVICE..."
                        docker push $IMAGE:${IMAGE_TAG}
                        docker push $IMAGE:latest
                    done
                '''
            }
        }

        stage('Deploy to K8s') {
            steps {
                sh '''
                    kubectl apply -f k8s/
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline Success"
        }
        failure {
            echo "❌ Pipeline Failed"
        }
    }
}