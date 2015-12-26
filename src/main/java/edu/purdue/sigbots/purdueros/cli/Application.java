package edu.purdue.sigbots.purdueros.cli;

import edu.purdue.sigbots.purdueros.cli.commands.Command;
import edu.purdue.sigbots.purdueros.cli.commands.CreateCommand;
import edu.purdue.sigbots.purdueros.cli.commands.FetchCommand;
import edu.purdue.sigbots.purdueros.cli.commands.UpgradeCommand;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.impl.action.StoreTrueArgumentAction;
import net.sourceforge.argparse4j.impl.action.VersionArgumentAction;
import net.sourceforge.argparse4j.inf.*;

import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;

public class Application {
    public static void main(String[] args) {
        ArgumentParser parser = createArgumentParser();

        Namespace namespace = parser.parseArgsOrFail(args);

        if (namespace == null) {
            System.err.println("Error parsing arguments");
            return;
        }

        Object handler = namespace.get("handler");

        if ((handler != null) && handler instanceof Class<?>) {
            try {
                Command command = (Command) ((Class<?>) handler)
                        .getConstructor(Namespace.class)
                        .newInstance(namespace);
                command.handleArgs();
            } catch (InstantiationException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            } catch (InvocationTargetException e) {
                e.printStackTrace();
            } catch (NoSuchMethodException e) {
                e.printStackTrace();
            }
        }
    }

    private static ArgumentParser createArgumentParser() {
        ArgumentParser parser = ArgumentParsers.newArgumentParser("pros");
        parser.description("Create and upgrade PROS projects.");
        parser.version("0.1.5");
        parser.defaultHelp(true);
        parser.addArgument("--version").action(new VersionArgumentAction());

        Subparsers subparsers = parser.addSubparsers().title("command").dest("command");


        ArrayList<String> defaultEnvironments = new ArrayList<String>();
        defaultEnvironments.add("none");

        // <editor-fold desc="Create subparser">
        Subparser createSubparser = subparsers.addParser("create").defaultHelp(true)
                .setDefault("handler", CreateCommand.class);
        createSubparser.addArgument("directory")
                .help("PROS project directory to create.");
        createSubparser.addArgument("--kernel").nargs("?").metavar("KERNEL").setDefault("latest")
                .help("Specify kernel version to create to. " +
                        "Latest defaults to highest locally available repository. " +
                        "Use 'pros fetch latest' to download latest repository from online site.");
        createSubparser.addArgument("--environments").nargs("+").setDefault(defaultEnvironments)
                .help("Define environments to target. " +
                        "Available environments are determined by the kernel kernels and " +
                        "can be found by using 'pros fetch KERNEL -e'");
        createSubparser.addArgument("-f", "--force").action(new StoreTrueArgumentAction())
                .help("Don't prompt to overwrite existing directory.");
        createSubparser.addArgument("-v", "--verbose").action(new StoreTrueArgumentAction())
                .help("Use this flag to enable verbose output.");
        // </editor-fold>

        // <editor-fold desc="Upgrade subparser">
        Subparser upgradeSubparser = subparsers.addParser("upgrade").defaultHelp(true)
                .setDefault("handler", UpgradeCommand.class);
        upgradeSubparser.addArgument("directory")
                .help("PROS project directory to upgrade.");
        upgradeSubparser.addArgument("--kernel").nargs("?").metavar("KERNEL").setDefault("latest")
                .help("Specify kernel version to upgrade to.");
        upgradeSubparser.addArgument("--environments").nargs("+").setDefault(defaultEnvironments)
                .help("Define environments to target. " +
                        "Available environments are determined by the kernel kernels and " +
                        "can be found by using 'pros fetch KERNEL -e'");
        upgradeSubparser.addArgument("-f", "--force").action(new StoreTrueArgumentAction())
                .help("Create/update files regardless if project is considered to be a PROS project.");
        upgradeSubparser.addArgument("-v", "--verbose").action(new StoreTrueArgumentAction())
                .help("Use this flag to enable verbose output.");
        // </editor-fold>

        // <editor-fold desc="Fetch subparser">
        Subparser fetchSubparser = subparsers.addParser("fetch").defaultHelp(true)
                .setDefault("handler", FetchCommand.class);
        fetchSubparser.addArgument("kernel")
                .help("Kernel to fetch. " +
                        "May be 'latest' to fetch latest from online site or locally available (whichever is higher). " +
                        "'all' specifies all kernels if applicable.");
        fetchSubparser.addArgument("--site").nargs("?").metavar("SITE")
                .setDefault("https://raw.githubusercontent.com/edjubuh/purdueros-kernels/master")
                .help("Specify site to do online operations with.");
        MutuallyExclusiveGroup mutuallyExclusiveGroup = fetchSubparser.addMutuallyExclusiveGroup();
        mutuallyExclusiveGroup.addArgument("-e", "--environments").action(new StoreTrueArgumentAction())
                .help("List all environments that can be used with this kernel");
        mutuallyExclusiveGroup.addArgument("-d", "--download").action(new StoreTrueArgumentAction())
                .help("Downloads kernel(s) from online site. Will delete kernel template if it exists locally.");
        mutuallyExclusiveGroup.addArgument("-c", "--clean").action(new StoreTrueArgumentAction())
                .help("Deletes kernel template(s) from local repository.");
        fetchSubparser.addArgument("-v", "--verbose").action(new StoreTrueArgumentAction())
                .help("Use this flag to enable verbose output.");
        fetchSubparser.epilog("Without -e, -d, or -c, will list if the specified kernel is available locally and/or online.");
        // </editor-fold>
        return parser;
    }
}
