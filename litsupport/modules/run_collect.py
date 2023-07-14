"""Test Module to perform an extra execution of the benchmark in the linux
perf tool."""
from litsupport import shellcommand
from litsupport import testplan
from litsupport.modules import run_under


def _mutateCommandLine(context, commandline):
    # Storing profile file in context allows other modules to be aware of it.
    cmd = shellcommand.parse(commandline)
    cmd.wrap(
        "/home/huawei/ml-in-comp/llvm-test-suite/collect-scripts/collect.sh",
        [],
    )
    
    #cmd.stdout = context.tmpBase + ".stdout"
    #cmd.stderr = context.tmpBase + ".stderr"
    
    return cmd.toCommandline()


def mutatePlan(context, plan):
    script = context.parsed_runscript
    if context.config.run_under:
        script = testplan.mutateScript(context, script, run_under.mutateCommandLine)
    script = testplan.mutateScript(context, script, _mutateCommandLine)
    plan.profilescript += script
