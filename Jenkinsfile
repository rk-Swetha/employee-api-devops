
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
                sh 'pwd'
                sh 'ls -la'
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
            echo 'Pipeline finished successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}
