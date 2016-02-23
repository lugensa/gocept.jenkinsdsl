
class AbstractBuilder implements Builder {

    def base_commands
    def timeout
    def python_name

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
                cron('@daily')
                scm('H/5 * * * *')
            }

            // logRotator(daysToKeepInt=100, numToKeepInt=100) did not work in 1.43
            logRotator(100, 100)
            checkoutRetryCount()
        }
    }
}
