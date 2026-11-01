
pipeline {
    agent any

    environment {
        AI_IMAGE = "iris-ai-model:ci-${BUILD_NUMBER}"
        FRONTEND_IMAGE = "iris-frontend:ci-${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub'
            }
        }

        stage('Validate Python Application') {
            steps {
                sh '''
                    python3 -m py_compile ai-model/app.py
                    echo "Python syntax validation successful"
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    docker build -t "$AI_IMAGE" ./ai-model
                    docker build -t "$FRONTEND_IMAGE" ./frontend
                '''
            }
        }

        stage('Load Images into Minikube') {
            steps {
                sh '''
                    minikube image load "$AI_IMAGE"
                    minikube image load "$FRONTEND_IMAGE"
                '''
            }
        }

        stage('Deploy MongoDB') {
            steps {
                sh '''
                    kubectl apply -f kubernetes/mongodb.yaml

                    kubectl rollout status deployment/mongodb \
                        --timeout=180s
                '''
            }
        }

        stage('Deploy AI Application') {
            steps {
                sh '''
                    kubectl apply -f kubernetes/ai-deployment.yaml
                    kubectl apply -f kubernetes/ai-service.yaml

                    kubectl set image deployment/iris-ai-deployment \
                        iris-ai-container="$AI_IMAGE"

                    kubectl rollout status deployment/iris-ai-deployment \
                        --timeout=180s
                '''
            }
        }

        stage('Deploy Frontend') {
            steps {
                sh '''
                    kubectl apply -f kubernetes/frontend-deployment.yaml
                    kubectl apply -f kubernetes/frontend-service.yaml

                    kubectl set image deployment/iris-frontend-deployment \
                        iris-frontend-container="$FRONTEND_IMAGE"

                    kubectl rollout status deployment/iris-frontend-deployment \
                        --timeout=180s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "Checking Kubernetes Pods..."
                    kubectl get pods

                    echo "Checking Kubernetes Services..."
                    kubectl get services

                    echo "Checking Deployments..."
                    kubectl get deployments
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD Pipeline failed. Check the Jenkins console output.'
        }
    }
}
