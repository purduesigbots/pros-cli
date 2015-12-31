package edu.purdue.sigbots.ros.cli.commands;

import edu.purdue.sigbots.ros.cli.updater.PROSActions;
import net.sourceforge.argparse4j.inf.Namespace;

public abstract class Command {
    public abstract void handleArguments(Namespace arguments, PROSActions actions);
}
