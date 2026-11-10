
pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Source code checked out successfully!'
            }
        }

        stage('Verify Environment') {
            steps {
                echo 'Jenkins pipeline is executing successfully!'
                sh 'git --version'
                sh 'python3 --version'
                sh 'pwd'
                sh 'ls -la'
            }
        }

        stage('Install Dependencies'){
            steps{
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Run Pytest'){
            steps{
                sh '''
                    .venv/bin/python -m pytest -v
                '''
            }
        }

        stage('Verify Kubernetes Access') {
            steps {
                withCredentials([file(
                    credentialsId: 'kubeconfig-credentials',
                    variable: 'KUBECONFIG'
                )]) {
                    sh '''
                        echo "Checking Kubernetes cluster access..."
                        kubectl get nodes
                        echo "Checking application pods..."
                        kubectl get pods -n default
                    '''
                }
            }
        }

        stage('Build Docker Image'){
            steps{
                sh 'docker build -t employee-api:jenkins .'
            }
        }

        stage('Publish to GHCR') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'ghcr-credentials',
                    usernameVariable: 'GHCR_USER',
                    passwordVariable: 'GHCR_TOKEN'
                )]) {
                    sh '''
                        echo "$GHCR_TOKEN" | docker login ghcr.io \
                            -u "$GHCR_USER" --password-stdin

                        docker tag employee-api:jenkins \
                            ghcr.io/rk-swetha/employee-api-devops:jenkins

                        docker push ghcr.io/rk-swetha/employee-api-devops:jenkins

                        docker logout ghcr.io
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(
                    credentialsId: 'kubeconfig-credentials',
                    variable: 'KUBECONFIG'
                )]) {
                    sh '''
                        kubectl set image deployment/employee-api \
                            employee-api=ghcr.io/rk-swetha/employee-api-devops:jenkins \
                            -n default

                        kubectl rollout status deployment/employee-api \
                            -n default --timeout=120s

                        kubectl get pods -n default
                    '''
                }
            }
        }

        stage('Pipeline Complete') {
            steps {
                echo 'First Jenkins pipeline completed!'
            }
        }
    }

    post {
        success {
            echo 'All stages passed!'
        }

        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}
