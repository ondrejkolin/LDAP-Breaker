# LDAP-Breaker
Small Python utility used for migrating old LDAP instance. Beware Spaghetti code ahead! 

## Description
This codes was written in order to simplify the migration of old LDAP data. Check -h for notice. 
Distributed with no warranty and under GNU GPL v3

## Usage
`./main.py -i /home/user/ldap-data/database.ldif -r ',ou=aclroles,dc=ldap,dc=example,dc=com'`
<br> -i input file
<br> -r restrict search domain, using a comma makes sure you don't get the main ou (ou=people,dc=ldap,dc=example,dc=com)

`./main.py -i /home/user/ldap-data/database.ldif -r ,ou=people,dc=ldap,dc=example,dc=com -f gosaAccount gosaUserTemplate samba.* -a samba.*  gosaSpam.* -v 1`
<br> -f remove objectClass based on regexp
<br> -a removes attributes based on regexp

`./main.py -i /home/user/ldap-data/database.ldif -r ou=systems,dc=ldap,dc=example,dc=com -w "^objectClass:organizationalUnit" -ww True`
<br> -w Select all elements matching the search rule. Using dash "^" negates the search (for example plaintext passwords)
<br> -ww True/False, Makes the -w matched records to be matched (who ldap record, not only the attribute)

`./main.py -i /home/user/ldap-data/database.ldif -r ,ou=servers,ou=systems,dc=ldap,dc=example,dc=com -a gotoMode goMailServerStatus -s "objectClass:goMailServer|fdPostfixServer" "structuralObjectClass:GOhard|fdServer" "objectClass:GOhard|fdServer" -f "goServer" -n "objectClass:ipHost" "objectClass:ieee802Device" -v 6`
<br> -v set the verbosity level between 0 and 10, default is 1. 
<br> -s replace attribute value to new value. Works on arrays. Syntax is: attrribute:old_value|new_value
<br> -n create new attributes on all records. Syntax is: attribute:value

`./main.py -i /home/user/ldap-data/database.ldif -r ou=group,ou=systems,dc=ldap,dc=example,dc=com -l memberUid -z
<br> -l limit attributes only to `memberUid`
<br> -z if any records has no attributes before printing out (after filtering) it won't be stated. 
## `./main.py --help`
```
usage: usage: main.py [-h] -i input [-o output] [-r restrict]
               [-s substitute [substitute ...]] [-f filter [filter ...]]
               [-a attributes [attributes ...]] [-n new [new ...]]
               [-v verbosity] [-w watch [watch ...]] [-ww watchdog_strict]
               [-l list [list ...]] [-z zero]

LDIF Parser

optional arguments:
  -h, --help            show this help message and exit
  -i input, --input input
                        Ldif file to be proceed
  -o output, --output output
                        Ldif file to be outputed
  -r restrict, --restrict restrict
                        Restrict the output only to CN ending with this
                        string. If you wan't the object itself to be immitted
                        prepend with ","
  -s substitute [substitute ...], --substitute substitute [substitute ...]
                        Substitutes matched attribute:key values for desired
                        value. Syntax "attribute:old_value|new_value"
  -f filter [filter ...], --filter filter [filter ...]
                        ObjectClass filter which will be removed from the user
  -a attributes [attributes ...], --attributes attributes [attributes ...]
                        Attributes filter which will be removed from the user
  -n new [new ...], --new new [new ...]
                        Attributes which needs to be added, appends to
                        existings lists. Syntax "attribute:value"
  -v verbosity, --verbosity verbosity
                        Configure the verbosity level, 0 is nothing, 10 is a
                        lot
  -w watch [watch ...], --watch watch [watch ...]
                        Watch attributes with values matching regexp.
                        Prepending the expression with '^' checks if the
                        string does not match. Usage: userClass:[Tt]roll
                        ^userPassword:{CRYPT}
  -ww watchdog_strict   Delete after watchdog match? True/False
  -l list [list ...], --list list [list ...]
                        List of allowed attributes. Other attributes will be
                        therefore removed
  -z zero, --zero zero  Remove object with zero attributes?

```
