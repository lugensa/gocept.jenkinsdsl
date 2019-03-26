
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
    def slack_projectchannel

    def cloc_filename

    // Create configuration for ShiningPanda, set ENV and bootstrap project.
    private void create_config(job, config, commands) {
        def cmds = this.base_commands + '\\n' + commands // \\n escaped for python

        job.with {
            steps{
                virtualenv {
                        pythonName this.python_name
                        nature 'shell'
                        clear false
                        systemSitePackages false
                        ignoreExitCode false
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

            publishers{
                if (this.builds_to_trigger){
                    downstream(this.builds_to_trigger.tokenize(','))
                }
                if (this.slack_projectchannel) {
                    slackNotifier {
                        teamDomain('')
                        authToken('')
                        room('#' + this.slack_projectchannel)
                        startNotification(false)
                        notifyNotBuilt(true)
                        notifyAborted(true)
                        notifyFailure(true)
                        notifySuccess(false)
                        notifyUnstable(true)
                        notifyBackToNormal(true)
                        notifyRepeatedFailure(true)
                        includeTestSummary(false)
                        includeCustomMessage(false)
                        customMessage('Hello!')
                        buildServerUrl(null)
                        sendAs(null)
                        commitInfoChoice('NONE')
                    }
                }
                if (this.cloc_filename) {
                    slocCount {
                        pattern(this.cloc_filename)
                        encoding('UTF-8')
                    }
                }
            }
        }
    }
}
