"""Test module that runs llvm-profdata merge after executing the benchmark."""
from litsupport import shellcommand
from litsupport import testplan


def _mutateCommandline(context, commandline):
    cmd = shellcommand.parse(commandline)
    return cmd.toCommandline()


def _mutateScript(context, script):
    return testplan.mutateScript(context, script, _mutateCommandline)


def mutatePlan(context, plan):
    # run exec
    script = context.parsed_runscript
    plan.profilescript += _mutateScript(context, script)
    
    # move gmon.out
    profilefile = context.tmpBase + ".gmon.out"
    args = ["gmon.out", profilefile]
    echocmd = shellcommand.ShellCommand("mv", args)
    plan.profilescript += [echocmd.toCommandline()]

    # parse fcount
    parser = "/home/huawei/ml-in-comp/llvm-test-suite/ml-data/parse-fcount.sh"
    args = [context.executable, profilefile]
    parsecmd = shellcommand.ShellCommand(parser, args)
    parsecmd.stdout = context.tmpBase +  ".funcount"
    plan.profilescript += [parsecmd.toCommandline()]

