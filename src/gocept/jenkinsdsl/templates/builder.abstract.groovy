
class AbstractBuilder implements Builder {

    def base_commands
    def timeout
    def python_name

    def log_days
    def log_builds

    def trigger_cron = '@daily'
    def trigger_scm = 'H/5 * * * *'

    def type = 'freeStyleJob'

    def builds_to_trigger


    // Create configuration for ShiningPanda, set ENV and bootstrap project.
    private void create_config(job, config, commands) {
        def cmds = this.base_commands + '\\n' + commands // \\n escaped for python

        job.with {
            configure {
                project -> project / builders / 'jenkins.plugins.shiningpanda.builders.VirtualenvBuilder' {
                    pythonName python_name
                    nature 'shell'
                    clear 'false'
                    systemSitePackages 'false'
                    ignoreExitCode 'false'
                    command(cmds)
                }
            }

            wrappers {
                timeout {
                    absolute(this.timeout as int)
                    abortBuild()
                }
            }

            triggers {
                cron(this.trigger_cron)
                scm(this.trigger_scm)
            }

            // logRotator(daysToKeepInt=100, numToKeepInt=100) did not work in 1.43
            logRotator(this.log_days as int, this.log_builds as int)
            checkoutRetryCount()

            if (this.builds_to_trigger){
                postBuildSteps{
                    downstreamParameterized {
                        trigger(this.builds_to_trigger) {
                        }

                    }
                }
            }
        }
    }
}
