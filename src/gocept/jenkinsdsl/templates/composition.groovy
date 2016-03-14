
// The final composition of the jobs in done in the following part.
out.println('COPY NEXT LINE MANUALLY TO POST-BUILD-ACTIONS')

for (config in configs) {
    out.print(config.name + ',')

    job = freeStyleJob(config.name)
    job.with {
        description(config.description)
    }

    config.vcs.create_config(job, config)
    config.builder.create_config(job, config)
    config.redmine.create_config(job, config)
}
out.println()