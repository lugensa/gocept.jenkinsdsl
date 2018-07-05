
class IntegrationBuilder extends AbstractBuilder {

    def junit_filename
    def coverage_filename
    def htmlcov_path
    def pep8_filename
    def python_name

    def throttle_category

    def shell_co_solr
    def shell_clean_env
    def shell_prepare_bo
    def shell_shutdown

    def virtualenv_solr
    def virtualenv_instance

    def log_days
    def log_builds

    def trigger_cron = 'H 6-18/4 * * 1-5'
    def trigger_scm = 'H/5 * * * *'

    // Run tests using py.test and publish coverage results.
    public void create_config(job, config) {

        job.with {

            triggers {
                cron(this.trigger_cron)
                scm(this.trigger_scm)
            }
            steps {
                shell(shell_co_solr)
                shell(shell_clean_env)
                shell(shell_prepare_bo)
                virtualenv {
                    pythonName this.python_name
                    nature 'shell'
                    clear false
                    systemSitePackages false
                    ignoreExitCode false
                    command(virtualenv_solr)
                }
                virtualenv {
                    pythonName this.python_name
                    nature 'shell'
                    clear false
                    systemSitePackages false
                    ignoreExitCode true
                    command(virtualenv_instance)
                }
                shell(shell_shutdown)
            }

            publishers {
                archiveJunit(this.junit_filename) {
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
                    maxTotal 0
                    categories([this.throttle_category])
                }

            logRotator(this.log_days as int, this.log_builds as int)
            checkoutRetryCount()

        }
    }
}
