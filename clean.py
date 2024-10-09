import os, sys, logging, argparse
from subprocess import check_output
from subprocess import CalledProcessError

def clean():
    ret = True

    # 1. Kill dnsmasq
    try:
        cmd = "killall dnsmasq"
        out = check_output(cmd, shell=True, encoding="ascii")
        logging.debug("cmd: {}".format(cmd))
        logging.info("{}".format(out))
    except CalledProcessError as e:
        logging.error("error: {}".format(e))

    # 2. Remove the internet interface
    cmd = "ip link del internet"
    out = check_output(cmd, shell=True, encoding="ascii")
    logging.debug("cmd: {}".format(cmd))
    logging.info("{}".format(out))

    # 3. Find the main interface toward the Internet
    cmd = "which route"
    out = check_output(cmd, shell=True, encoding="ascii")
    logging.debug("cmd: {}".format(cmd))
    logging.info("{}".format(out))

    if len(out) == 0:
        logging.debug("The iproute2 package is not installed")
        cmd = "apt-get install iproute2"
        out = check_output(cmd, shell=True, encoding="ascii")
        logging.debug("cmd: {}".format(cmd))
        logging.info("{}".format(out))

    cmd = "route -n"
    out = check_output(cmd, shell=True, encoding="ascii")
    logging.debug("cmd: {}".format(cmd))
    logging.info("{}".format(out))

    output = out.split("\n")
    minterface = None
    for line in output:
        tokens = line.strip().split(" ")
        if tokens[0] == "0.0.0.0":
            minterface = tokens[-1]
            break
    logging.info("Name of the main interface: {}".format(minterface))

    # 4. Remove the iptable rule set for the internet interface and the main interface
    cmd = "iptables -t nat -D POSTROUTING -o {} -j MASQUERADE".format(minterface)
    out = check_output(cmd, shell=True, encoding="ascii")
    logging.debug("cmd: {}".format(cmd))
    logging.info("{}".format(out))

    cmd = "iptables -D FORWARD -i {} -o internet -m state --state RELATED,ESTABLISHED -j ACCEPT".format(minterface)
    out = check_output(cmd, shell=True, encoding="ascii")
    logging.debug("cmd: {}".format(cmd))
    logging.info("{}".format(out))
   
    cmd = "iptables -D FORWARD -i internet -o {} -j ACCEPT".format(minterface)
    out = check_output(cmd, shell=True, encoding="ascii")
    logging.debug("cmd: {}".format(cmd))
    logging.info("{}".format(out))

    # 5. Remove all links of the pattern foo-tapX
    cmd = "ip link show | egrep -o [-_.[:alnum:]]+-tap[[:digit:]]+"
    out = check_output(cmd, shell=True, encoding="ascii")
    logging.debug("cmd: {}".format(cmd))
    logging.info("{}".format(out))

    taps = out.strip().split("\n")
    for tap in taps:
        if len(tap.strip()) == 0:
            continue
        cmd = "ip link del {}".format(tap)
        out = check_output(cmd, shell=True, encoding="ascii")
        logging.debug("cmd: {}".format(cmd))
        logging.info("{}".format(out))

        cmd = "iptables -t filter -D FORWARD -i {} -o {} -j ACCEPT".format(tap, tap)
        out = check_output(cmd, shell=True, encoding="ascii")
        logging.debug("cmd: {}".format(cmd))
        logging.info("{}".format(out))

    return ret

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    if os.geteuid() != 0:
        logging.error("Please run this script with the root privilege")
        sys.exit(1)

    clean()

if __name__ == "__main__":
    main()
