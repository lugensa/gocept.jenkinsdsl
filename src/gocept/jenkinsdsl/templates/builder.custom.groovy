
class CustomBuilder extends AbstractBuilder {
    def additional_commands

    public void create_config(job, config) {
        super.create_config(job, config, this.additional_commands)
    }
}
