#!/usr/bin/env python3
'''
This codes was written in order to simplify the migration of old LDAP data. Check -h for notice.
Distributed with no warranty and under GNU GPL v3
'''



def main():

    def pretty_print(data):
        """
        This function prints the output
        :param data:
        :return:
        """
        object_count: int = 0
        def log(text:str, level=1):
            if (level <= VERBOSITY):
                sys.stderr.write(str(text) + "\n")

        def central_print(text, level=1, space="-", size=max(20, int(os.popen('stty size', 'r').read().split()[1]))):
            log(space * ((size - len(text) - 2) // 2) + " " + text + " " + space * ((size - len(text) - 2) // 2), level)

        def run_watchdog(reverse, regexp, value, attribute):
            log("watchdog debug: Reverse: {}, Regexp: {}, Value: {}, Attribute: {}".format(reverse, regexp, value, attribute), 9)
            result = True
            try:
                if type(value).__name__ == 'list':
                    for item in value:
                        result = result and run_watchdog(reverse, regexp, item, attribute)
                else:
                    if regexp.match(value.decode()):
                        log("Matched the regexp '{}' in attribute {}!".format(regexp.pattern, value), 7)
                        if (reverse):
                            log("WATCHDOG SPOTTED: {}".format(value))
                            return False
                    else:
                        if (not(reverse)):
                                log("WATCHDOG NOT MATCHING: {} on {}".format(value, regexp), 3)
                                return False
            except TypeError:
                log("Unsupported watched object type on attribute {}, got {}".format(attribute, type(value).__name__))
            return result


        def output (cn, content, object_type="Object"):
            central_print("Object " + " '" + cn.split(",")[0].split("=")[1] + "'", 3)
            to_be_removed = []
            for banned in FILTERED_CLASSES:
                pattern = re.compile("^" + str(banned) + "$")
                for value in content["objectClass"]:
                    if pattern.match(str(value)) is not None:
                        to_be_removed.append(value)
                    else:
                        log("{} not matched for removal with {}".format(value, pattern.pattern), 9)

            for remove in to_be_removed:
                content["objectClass"].remove(remove)
                log("Removing objectClass: {}".format(remove), 4)

            to_be_removed = []
            watchdog_result = True
            for key in content.keys():
                if len(ATTRIBUTES_LIST) and key not in ATTRIBUTES_LIST:
                    log ("Based on attributes list removing attribute {} ".format(key),3)
                    to_be_removed.append(key)


                for banned in FILTERED_ATTRIBUTES:
                    pattern = re.compile("^" + str(banned) + "$")
                    if pattern.match(key) is not None:
                        to_be_removed.append(key)


                for (attribute, old_value, new_value) in SUBSTITUTE:
                    if (key == attribute):
                        log("Found matching attribute {} for substitution".format(key), 9)
                        if type(content[key]).__name__ == 'list':
                            _to_be_removed = []
                            _to_be_added = []
                            for item in content[key]:
                                if item.decode() == old_value:
                                    _to_be_removed.append(item)
                                    _to_be_added.append(new_value.encode())
                                    log("Replacing on key {} value {} for {} ".format(key, old_value, new_value), 5)
                                else:
                                    log("Array replace: {} is not {}".format(item, old_value), 9)
                            for remove in _to_be_removed:
                                content[key].remove(remove)
                            for append in _to_be_added:
                                content[key].append(append)
                        elif content[key] == old_value:
                            content[key] = new_value
                            log("Replacing on key {} value {} for {} ".format(key, old_value, new_value), 5)

                    else:
                        log("Replace condition {}:{}  not met key {}".format(attribute, old_value, key), 9)

                for (reverse, attribute, regexp) in WATCHER:
                    if key != attribute:
                        continue
                    else:
                        watchdog_result = run_watchdog(reverse, regexp, content[key], attribute)
                        if watchdog_result:
                            log("Removing {} due to watchdog results".format(cn), 1)

            for remove in to_be_removed:
                try:
                    content.pop(remove)
                    log("Removing attribute: {}".format(remove), 4)
                except KeyError:
                    log("Failed to remove {}, already removed?".format(remove), 9)

            if watchdog_result and WATCHDOG_STRICT:
                log("Watchdog blocked")
                return

            for (attribute, value) in NEW_ATTRIBUTES:
                value = value.encode()
                log("Adding attribute {} with value {}".format(attribute, value), 4)
                try:
                    content.get(attribute)
                    if (type(content[attribute]).__name__ == 'list'):
                        content[attribute].append(value)
                    else:
                        content[attribute] = value
                except KeyError:
                        raise Exception("Attribute {} is already present! For rewriting attributes use another function.".format(attribute))

            if not len(content.key()):
                if REMOVE_WHEN_ZERO_ATTRS:
                    log('Removing {} because it has no attribute left. Rest in piece(s)'.format(cn), 6)
                    return
                log('Please notice, that {} has no attributes!'.format(cn), 2)




            log(content, 9)
            OUTPUT_FILE.unparse(cn, content)
            log("Written the object {}".format(cn), 6)


        for (cn, content) in data:
            if cn.endswith(RESTRICT):
                object_count+=1
                output(cn, content)
            else:
                log("{} restricted from output".format(cn), 10)

        log("", 2)
        central_print("FINISHED", 2)
        log("Object count: {}".format(object_count), 2)



    from ldif import LDIFRecordList, LDIFWriter
    import argparse
    import re
    import sys
    import os

    parser = argparse.ArgumentParser(description='LDIF Parser')
    parser.add_argument('-i', '--input', metavar='input', type=str, required=True,
                        help='Ldif file to be proceed')
    parser.add_argument('-o', '--output', metavar='output', type=str, required=False, default=None,
                        help='Ldif file to be outputed')
    parser.add_argument('-r', '--restrict', metavar='restrict', type=str, default = "",
                        help='Restrict the output only to CN ending with this string. \nIf you wan\'t the object itself to be immitted prepend with ","')
    parser.add_argument('-s', '--substitute', metavar='substitute', type=str, nargs="+", required=False, default = [],
                        help='Substitutes matched attribute:key values for desired value. Syntax "attribute:old_value|new_value"')
    parser.add_argument('-f', '--filter', metavar='filter', type=str, nargs="+", required=False, default = [],
                        help='ObjectClass filter which will be removed from the user')
    parser.add_argument('-a', '--attributes', metavar='attributes', type=str, nargs="+", required=False, default = [],
                        help='Attributes filter which will be removed from the user')
    parser.add_argument('-n', '--new', metavar='new', type=str, nargs="+", required=False, default = [],
                    help='Attributes which needs to be added, appends to existings lists. Syntax "attribute:value"')
    parser.add_argument('-v', '--verbosity', metavar='verbosity', type=int, required=False, default=1,
                        help='Configure the verbosity level, 0 is nothing, 10 is a lot')
    parser.add_argument('-w', '--watch', metavar='watch', type=str, nargs="+", required=False, default = [],
                        help='Watch attributes with values matching regexp. Prepending the expression with \'^\' checks if the string does not match.\nUsage: \nuserClass:[Tt]roll\n^userPassword:{CRYPT}')
    parser.add_argument('-ww', metavar="watchdog_strict", type=bool, required=False, default=None,
                        help="Delete after watchdog match? True/False")
    parser.add_argument('-l', '--list', metavar='list', type=str, nargs="+", required=False, default = [],
                        help='List of allowed attributes. Other attributes will be therefore removed')
    parser.add_argument('-z', '--zero', metavar='zero', type=bool, required=False, default = False,
                        help='Remove object with zero attributes?')


    args = parser.parse_args()
    input_file = open(args.input, "r")
    if args.output is not None:
        OUTPUT_FILE = LDIFWriter(open(args.output, "w"))
    else:
        OUTPUT_FILE = LDIFWriter(sys.stdout)
    VERBOSITY = args.verbosity
    RESTRICT = args.restrict
    FILTERED_CLASSES = [x.encode() for x in args.filter]
    FILTERED_ATTRIBUTES = args.attributes
    WATCHER = []
    WATCHDOG_STRICT = args.ww
    for watcher in args.watch:
        try:
            if watcher.startswith("^"):
                reverse = True
                watcher = watcher[1:]
            else:
                reverse = False
            attribute = watcher.split(":")[0]
            regexp = ":".join(watcher.split(":")[1:])
            WATCHER.append((reverse, attribute, re.compile("^" + regexp + "$")))
        except KeyError:
            log("Watcher string not matching our expectations! Check the help -h!", 0)
    SUBSTITUTE = []
    for substitute in args.substitute:
        try:
            attribute = substitute.split(":")[0]
            old_value, new_value = ":".join(substitute.split(":")[1:]).split("|")
            SUBSTITUTE.append((attribute, old_value, new_value))
        except KeyError:
            log("Substitute string not matching expectations! Check the help -h", 0)
    NEW_ATTRIBUTES = []
    try:
        NEW_ATTRIBUTES =  [item.split(":", 1) for item in args.new]
    except KeyError:
        log("Attribute creation error! Check the help -h", 0)
    try:
        ATTRIBUTES_LIST = args.list
    except KeyError:
       log("Error when parsing allowed attributes list, check your syntax")

    REMOVE_WHEN_ZERO_ATTRS = True




    record_list = LDIFRecordList(input_file, max_entries=0)
    record_list.parse()
    pretty_print(record_list.all_records)


if __name__ == "__main__":
    main()
