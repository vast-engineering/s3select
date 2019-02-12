## S3 select

![alt text](https://github.com/marko-bast/s3select/raw/master/s3select_example_run.gif "Example run")
Example query run on 10GB of GZIP compressed JSON data (>60GB uncompressed)

### Motivation
[Amazon S3 select](https://docs.aws.amazon.com/AmazonS3/latest/dev/s3-glacier-select-sql-reference-select.html) is one of the coolest features AWS released in 2018. It's benefits are:
1) Very fast and low on network utilization as it allows you to return only a subset of the file contents from S3 using limited SQL select query. Since filtering of the data takes place on AWS machine where S3 file resides, network data transfer can be significantly limited depending on query issued.
2) Is lightweight on the client side because all filtering is done on a machine where the S3 data is located 
4) It's [cheap](https://aws.amazon.com/s3/pricing/#Request_pricing_.28varies_by_region.29) at $0.002 per GB scanned and $0.0007 per GB returned<br>
For more details about S3 select see this [presentation](https://www.youtube.com/watch?v=uxcyoc6uaLM).<p>

Unfortunately, S3 select API query call is limited to only one file on S3 and syntax is quite cumbersome, making it very impractical for daily usage. These are and more flaws are intended to be fixed with this s3select command.    

### Features at a glance
Most important features:
 1) Queries all files beneath given S3 prefix(es)
 2) The whole process is multi-threaded and fast. A scan of 1.1TB of data in stored in 20,000 files takes 5 minutes). Threads don't slow down client much as heavy lifting is done on AWS.
 3) The compression of the file is automatically inferred for you by picking GZIP or plain text depending on file extension. 
 4) Real-time execution progress display.
 5) The exact cost of the query returned for each run.
 6) Ability to only count records matching the filter in a  fast and efficient manner.
 7) You can easily limit the number of results returned while still keeping multi-threaded execution.
 8) Failed requests are properly handled and repeated if they are retriable (e.g. throttled calls). 

### Installation and Upgrade
s3select is developed in Python and uses [pip](http://www.pip-installer.org/en/latest/).<p>

The easiest way to install/upgrade s3select is to use `pip` in a `virtualenv`:

<pre>$ pip install -U s3select</pre>

or, if you are not installing in a `virtualenv`, to install/upgrade globally:

<pre>$ sudo pip install -U s3select</pre>

or for your user:

<pre>$ pip install --user -U s3select</pre>

### Authentication

s3select uses the same authentication and endpoint configuration as [aws-cli](https://github.com/aws/aws-cli#getting-started). If aws command is working on your machine, there is no need for any additional configuration.

### Example usage
First get some help:
<pre>
$ s3select -h
usage: s3select [-h] [-w WHERE] [-d FIELD_DELIMITER] [-D RECORD_DELIMITER]
                [-l LIMIT] [-v] [-c] [-H] [-o OUTPUT_FIELDS] [-t THREAD_COUNT]
                [--profile PROFILE] [-M MAX_RETRIES]
                prefixes [prefixes ...]

s3select makes s3 select querying API much easier and faster

positional arguments:
  prefixes              S3 prefix (or more) beneath which all files are
                        queried

optional arguments:
  -h, --help            show this help message and exit
  -w WHERE, --where WHERE
                        WHERE part of the SQL query
  -d FIELD_DELIMITER, --field_delimiter FIELD_DELIMITER
                        Field delimiter to be used for CSV files. If specified
                        CSV parsing will be used. By default we expect JSON
                        input
  -D RECORD_DELIMITER, --record_delimiter RECORD_DELIMITER
                        Record delimiter to be used for CSV files. If
                        specified CSV parsing will be used. By default we
                        expect JSON input
  -l LIMIT, --limit LIMIT
                        Maximum number of results to return
  -v, --verbose         Be more verbose
  -c, --count           Only count records without printing them to stdout
  -H, --with_filename   Output s3 path of a filename that contained the match
  -o OUTPUT_FIELDS, --output_fields OUTPUT_FIELDS
                        What fields or columns to output
  -t THREAD_COUNT, --thread_count THREAD_COUNT
                        How many threads to use when executing s3_select api
                        requests. Default of 150 seems to be on safe side. If
                        you increase this there is a chance you'll need also
                        to increase nr of open files on your OS
  --profile PROFILE     Use a specific AWS profile from your credential file.
  -M MAX_RETRIES, --max_retries MAX_RETRIES
                        Maximum number of retries per queried S3 object in
                        case API request fails
</pre>

It's always useful to peek at first few lines of input files to figure out contents:
<pre>
$ s3select -l 3 s3://testing.bucket/json_example/
{"name":"Gilbert","wins":[["straight","7♣"],["one pair","10♥"]]}
{"name":"Alexa","wins":[["two pair","4♠"],["two pair","9♠"]]}
{"name":"May","wins":[]}</pre>

It's JSON. Great - that's s3select default format. Let's get a subset of its data
<pre>
$ s3select -l 3 -w "s.name LIKE '%Gil%'" -o "s.wins" s3://testing.bucket/json_example
{"wins":[["straight","7♣"],["one pair","10♥"]]}
</pre>

What if the input is not in JSON:
<pre>
$ s3select -l 3 s3://testing.bucket/csv_example
Exception caught when querying csv_example/example.csv: An error occurred (JSONParsingError) when calling the SelectObjectContent operation: Error parsing JSON file. Please check the file and try again.
</pre>
Exception means input isn't parsable JSON. Let's switch to CSV file delimited with `,` but you can specify any other delimiter char. Often used is `TAB` specified with `\\t` 
<pre>
$ s3select -l 3 -d , s3://testing.bucket/csv_example
Gilbert,straight,7♣,one pair,10♥
Alexa,two pair,4♠,two pair,9♠
May,,,,
</pre>

Since utilising the first line of CSV as a header isn't yet supported we'll select a subset of data using column enumeration:   
<pre>
$ s3select -l 3 -d , -w "s._1 LIKE '%i%'" -o "s._2" s3://testing.bucket/csv_example
straight
three of a kind
</pre>

If you are interested in pricing for your requests, add `-v` to increase verbosity which will include pricing information at the end:
<pre>
$ s3select -v -c s3://testing.bucket/10G_sample
Files processed: 77/77  Records matched: 5696395  Bytes scanned: 21 GB
Cost for data scanned: $0.02
Cost for data returned: $0.00
Cost for SELECT requests: $0.00
Total cost: $0.02
</pre>

### License

Distributed under the MIT license. See `LICENSE` for more information.
