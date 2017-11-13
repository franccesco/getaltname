# GetAltNames
Get Subject Alt Names for SSL Certificates which can provide you with DNS names or virtual servers.

It's useful in a discovery phase of a pentesting assesment, just a little tool to provide you with more information about your target and scope.

This is alpha, it doesn't do as much as it should. lots of things and features are missing, but it delivers, treat it as a quick-dirty-code.

# Usage:
```
Usage:  getaltname.rb -h HOST [-p port]

Specific Options:
    -h, --host host                  Host to extract alternative names.
Common Options:
    -p, --port port                  Port to connect to (default 443)
        --help                       Show this message
```

# Example
In this case the tool give you subdomains that you probably didn't find with a subdomain brute force.

```
/getaltname.rb -h microsoft.com
140 Subject Alternative Names found:
==================================
msdn.com
xbox.com
*.live.com
*.msdn.com
gigjam.com
windows.nl
winhec.com
winhec.net
*.azure.biz
*.azure.net
*.getie.com
*.msdn2.com
*.netfx.com
*.vssdk.com
surface.com
windows.com
*.gigjam.com
*.msdntv.com
*.windows.nl
*.winhec.com
*.winhec.net
--- SNIP ---
```

# TO-DO
[ ] File output
[ ] Input to scan
[ ] Remove duplicates