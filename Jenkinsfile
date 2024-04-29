#!/usr/bin/env groovy
pipeline {
  agent {
      label 'commonagent'
  }

  stages {
    stage('Build docker container') {
      steps {
        ansiColor('xterm') {
        	sh('docker build -t cip-insights-reputation/address-lookup-welsh-country-names-lambda .')
        }
      }
    }
    stage('Push to ecr') {
      steps {
        sh("""
          aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 727065427295.dkr.ecr.eu-west-2.amazonaws.com
          docker tag cip-insights-reputation/address-lookup-welsh-country-names-lambda:latest 727065427295.dkr.ecr.eu-west-2.amazonaws.com/cip-insights-reputation/address-lookup-welsh-country-names-lambda:latest
          docker push 727065427295.dkr.ecr.eu-west-2.amazonaws.com/cip-insights-reputation/address-lookup-welsh-country-names-lambda:latest
        """)
      }
    }
  }
}
