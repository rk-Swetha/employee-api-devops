
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
