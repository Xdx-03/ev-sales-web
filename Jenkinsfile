pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 40, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '10'))
    }

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['test', 'staging'],
            description: '选择 Jenkins 中已经维护好的隔离测试环境'
        )
        choice(
            name: 'TEST_SUITE',
            choices: ['smoke', 'critical', 'mobile-h5', 'all-ui'],
            description: '选择要执行的测试范围'
        )
        choice(
            name: 'BROWSER_SOURCE',
            choices: ['playwright-chromium', 'system-chrome'],
            description: 'CI 推荐 Playwright Chromium；已有 Chrome 的自托管节点可选 system-chrome'
        )
        booleanParam(
            name: 'RUN_LIVE_TESTS',
            defaultValue: false,
            description: '显式开启真实 UI 回归；关闭时只做静态检查和场景收集'
        )
    }

    environment {
        PYTHONUNBUFFERED = '1'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv .venv
                            .venv/bin/python -m pip install -r requirements-dev.txt
                        '''
                    } else {
                        bat '''
                            @echo off
                            python -m venv .venv
                            .venv/Scripts/python.exe -m pip install -r requirements-dev.txt
                        '''
                    }
                }
            }
        }

        stage('Static validation') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            .venv/bin/python -m ruff check .
                            .venv/bin/python -m ruff format --check .
                            .venv/bin/python -m mypy
                            .venv/bin/python -m compileall -q ev_web tests run_web_tests.py
                            .venv/bin/python -m pytest --collect-only -q
                        '''
                    } else {
                        bat '''
                            @echo off
                            .venv/Scripts/python.exe -m ruff check .
                            .venv/Scripts/python.exe -m ruff format --check .
                            .venv/Scripts/python.exe -m mypy
                            .venv/Scripts/python.exe -m compileall -q ev_web tests run_web_tests.py
                            .venv/Scripts/python.exe -m pytest --collect-only -q
                        '''
                    }
                }
            }
        }

        stage('Install browser') {
            when {
                expression {
                    params.RUN_LIVE_TESTS && params.BROWSER_SOURCE == 'playwright-chromium'
                }
            }
            steps {
                script {
                    if (isUnix()) {
                        sh '.venv/bin/python -m playwright install chromium'
                    } else {
                        bat '@.venv/Scripts/python.exe -m playwright install chromium'
                    }
                }
            }
        }

        stage('Live UI regression') {
            when {
                expression { params.RUN_LIVE_TESTS }
            }
            steps {
                script {
                    def configCredentialIds = [
                        test: 'ev-sales-web-test-config',
                        staging: 'ev-sales-web-staging-config'
                    ]
                    def suiteMarkers = [
                        smoke: 'smoke',
                        critical: 'critical',
                        'mobile-h5': 'mobile and h5',
                        'all-ui': 'ui and live'
                    ]
                    def credentialId = configCredentialIds[params.TEST_ENV]
                    def marker = suiteMarkers[params.TEST_SUITE]
                    def browserArgs = params.BROWSER_SOURCE == 'system-chrome'
                        ? '--browser chromium --browser-channel chrome'
                        : '--browser chromium'

                    if (!credentialId || !marker) {
                        error('未知的环境或测试范围参数')
                    }

                    withCredentials([
                        file(credentialsId: credentialId, variable: 'EV_WEB_CONFIG_FILE')
                    ]) {
                        if (isUnix()) {
                            sh(
                                label: "Run ${params.TEST_SUITE} on ${params.TEST_ENV}",
                                script: """
                                    set +x
                                    .venv/bin/python run_web_tests.py \\
                                      --config \"\$EV_WEB_CONFIG_FILE\" \\
                                      --env \"${params.TEST_ENV}\" \\
                                      -m \"${marker}\" \\
                                      ${browserArgs}
                                """
                            )
                        } else {
                            bat(
                                label: "Run ${params.TEST_SUITE} on ${params.TEST_ENV}",
                                script: """
                                    @echo off
                                    .venv/Scripts/python.exe run_web_tests.py ^
                                      --config \"%EV_WEB_CONFIG_FILE%\" ^
                                      --env \"${params.TEST_ENV}\" ^
                                      -m \"${marker}\" ^
                                      ${browserArgs}
                                """
                            )
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('reports/junit.xml')) {
                    junit testResults: 'reports/junit.xml', keepLongStdio: true
                }
                archiveArtifacts(
                    artifacts: 'allure-results/**,artifacts/**',
                    allowEmptyArchive: true,
                    fingerprint: false
                )
            }
        }
    }
}
