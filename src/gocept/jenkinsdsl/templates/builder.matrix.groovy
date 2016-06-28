
class MatrixBuilder extends AbstractBuilder{

    def python_names
    def buildout_configs

    def type = 'matrixJob'

    def junit_filename
    def coverage_filename
    def htmlcov_path
    def pep8_filename

    def virtualenv_commands
    def run_sequentially

    def log_days
    def log_builds

    def trigger_cron = '@daily'
    def trigger_scm = 'H/5 * * * *'

    def throttle_category


    public void create_config(job, config) {
        job.with {
            axes {
                python(this.python_names.tokenize(','))
                runSequentially(this.run_sequentially as boolean)
                if (this.buildout_configs) {
                    text('buildout_config', this.buildout_configs.tokenize(''))
                }
            }

            triggers {
                cron(this.trigger_cron)
                scm(this.trigger_scm)
            }
            steps {
                virtualenv {
                    nature 'shell'
                    clear false
                    systemSitePackages false
                    ignoreExitCode false
                    command(virtualenv_commands)
                }
            }
            publishers {
                archiveJunit(this.junit_filename) {
                    retainLongStdout()
                    testDataPublishers {
                        publishTestAttachments()
                    }
                }

                if (this.coverage_filename) {
                    cobertura(this.coverage_filename) {
                        onlyStable true
                        sourceEncoding 'UTF_8'
                    }
                }
            }

            if (this.htmlcov_path) {
                configure {
                    project -> project / 'publishers' / 'jenkins.plugins.shiningpanda.publishers.CoveragePublisher' {
                        htmlDir this.htmlcov_path
                    }
                }
            }

            if (this.pep8_filename) {
                publishers {
                    violations(100) {
                        pep8(10, 100, 9999, this.pep8_filename)
                    }
                }
            }

            if (this.throttle_category)
                throttleConcurrentBuilds {
                    maxPerNode 0
                    maxTotal 1
                    categories([this.throttle_category])
                    throttleMatrixBuilds(false)
                    throttleMatrixConfigurations(true)
                }

            wrappers {
                timeout {
                    absolute(this.timeout as int)
                    abortBuild()
                }
            }

            logRotator(this.log_days as int, this.log_builds as int)
            checkoutRetryCount()
        }
    }
}
