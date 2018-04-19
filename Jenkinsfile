stage('Build') {
  parallel (
    "linux64": {
      node("lin64") {
        checkout scm
        sh './scripts/install_build_dependencies.sh'
        sh 'vex --python python3.6 -mr jenkins ./scripts/build.sh'
        archiveArtifacts artifacts: 'out/*', onlyIfSuccessful: true
        archiveArtifacts artifacts: '*version', onlyIfSuccessful: true
      }
    },
    "linux86": {
      node("lin86") {
        checkout scm
        sh './scripts/install_build_dependencies.sh'
        sh 'vex --python python3.6 -mr jenkins ./scripts/build.sh'
        archiveArtifacts artifacts: 'out/*', onlyIfSuccessful: true
        archiveArtifacts artifacts: '*version', onlyIfSuccessful: true
      }
    },
    "windows64": {
      node("win64") {
        checkout scm
        powershell '.\\scripts\\install_build_dependencies.ps1'
        powershell '.\\scripts\\build.ps1'
        archiveArtifacts artifacts: 'out/*', onlyIfSuccessful: true
        archiveArtifacts artifacts: '*version', onlyIfSuccessful: true
      }
    },
    "windows86": {
      node("win86") {
        checkout scm
        powershell '.\\scripts\\install_build_dependencies.ps1'
        powershell '.\\scripts\\build.ps1'
        archiveArtifacts artifacts: 'out/*', onlyIfSuccessful: true
        archiveArtifacts artifacts: '*version', onlyIfSuccessful: true
      }
    }
  )
}
