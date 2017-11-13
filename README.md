# GetAltNames
Get Subject Alt Names for SSL Certificates which can provide you with URI's, Emails, DNS names and IP Addresses.

It's useful in a discovery phase of a pentesting assesment, just a little tool to provide you with more information about your target and scope.

This is alpha, it doesn't do as much as it should. lots of things and features are missing, but it delivers, treat it as a quick-dirty-code.

# Usage:
```
Usage:  getaltname.rb [OPTIONS]

Specific Options:
    -h, --host host                  Host to extract alternative names.
Common Options:
    -p, --port port                  Port to connect to (default 443)
        --help                       Show this message
```

# Example
In this case the tool give you subdomains that you probably didn't find with a subdomain brute force.

```
λ linuxbox getaltname → λ git release/0.1.0* → ./getaltname.rb -h examplewebsite.com
100 Subject Alternative Names found:

adquisiciones.examplewebsite.com
bib.examplewebsite.com
ccpe.examplewebsite.com
cedocfec.examplewebsite.com
compufec.examplewebsite.com
control-co.examplewebsite.com
dbe.examplewebsite.com
dde-e.examplewebsite.com
dde.examplewebsite.com
di.examplewebsite.com
diex.examplewebsite.com
docentes.examplewebsite.com
dtic.examplewebsite.com
extension.examplewebsite.com
fcys.examplewebsite.com
--- SNIP ---
```
