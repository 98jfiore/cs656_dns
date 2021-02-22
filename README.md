# cs656_dns

### DNS Request Packet Format

- QNAME A domain name represented as a sequence of labels, where each label consists of a length
octet followed by that number of octets. The domain name terminates with the zero length
octet for the null label of the root. See the DNS Example query below.
3
- QTYPE A two octet code which specifies the type of the query. You should use 0x0001 for this project,
representing A records (host addresses). If you are completing the graduate version of this project,
you will also need to use 0x000f for mail server (MX) records and 0x0002 for name servers (NS)
records.
- QCLASS A two octet code that specifies the class of the query. You should always use 0x0001 for this
project, representing Internet addresses



### DNS Response Packet Format
 - NAME The domain name that was queried, in the same format as the QNAME in the questions.
- TYPE Two octets containing one of th type codes. This field specifies the meaning of the data in
the RDATA field. You should be prepared to interpret type 0x0001 (A record) and type 0x0005
(CNAME). If you are completing the graduate version of this project, you should also be prepared to
accept type 0x0002 (name servers) and 0x000f (mail servers).
- CLASS Two octets which specify the class of the data in the RDATA field. You should expect 0x0001
for this project, representing Internet addresses.
- TTL The number of seconds the results can be cached.
- RDLENGTH The length of the RDATA field.
- RDATA The data of the response. The format is dependent on the TYPE field: if the TYPE is 0x0001
for A records, then this is the IP address (4 octets). If the type is 0x0005 for CNAMEs, then this
is the name of the alias. If the type is 0x0002 for name servers, then this is the name of the
server. Finally if the type is 0x000f for mail servers, the format is
