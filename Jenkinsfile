#!/usr/bin/groovy

// App configuration.
def appName = "cura-print-time-estimator"
def imageTag = "${appName}:${env.BRANCH_NAME}.${env.BUILD_NUMBER}"

node(defaultNode)
{
    stage("Checkout")
    {
        checkout scm
    }

    // Build the Docker image for this service
    stage("Build")
    {
        sh "docker build --file Dockerfile.tests --tag ${imageTag} ."
        sh "docker rmi ${imageTag}"
        currentBuild.result = "SUCCESS"
        return
    }
}
