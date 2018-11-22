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
 1) Queries all files beneath given S3 prefix
 2) The whole process is multi-threaded and fast. A scan of 1.1TB of data in stored in 20,000 files takes 5 minutes). Threads don't slow down client much as heavy lifting is done on AWS.
 3) The compression of the file is automatically inferred for you by picking GZIP or plain text depending on file extension. 
 4) Real-time execution progress display.
 5) The exact cost of the query returned for each run.
 6) Ability to only count records matching the filter in a  fast and efficient manner.
 7) You can easily limit the number of results returned while still keeping multi-threaded execution.
 8) Failed requests are properly handled and repeated if they are retriable (e.g. throttled calls). 

### Installation
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
usage: s3select [-h] [-p PREFIX] [-w WHERE] [-d DELIM] [-l LIMIT] [-v] [-D]
                [-c] [-o OUTPUT_FIELDS] [-t THREAD_COUNT]

s3select makes s3 select querying API much easier and faster

optional arguments:
  -h, --help            show this help message and exit
  -p PREFIX, --prefix PREFIX
                        S3 prefix beneath which all files are queried
  -w WHERE, --where WHERE
                        WHERE part of the SQL query
  -d DELIM, --delim DELIM
                        Delimiter to be used for CSV files. If specified CSV
                        parsing will be used. By default we expect JSON input
  -l LIMIT, --limit LIMIT
                        Maximum number of results to return
  -v, --verbose         Be more verbose
  -D, --disable_progress
                        Turn off progress line
  -c, --count           Only count records without printing them to stdout
  -o OUTPUT_FIELDS, --output_fields OUTPUT_FIELDS
                        What fields or columns to output
  -t THREAD_COUNT, --thread_count THREAD_COUNT
                        How many threads to use when executing s3_select api
                        requests. Default of 200 seems to be max that doesn't
                        cause throttling on AWS side
</pre>

It's always useful to peek at first few lines of input files to figure out contents:
<pre>
$ s3select -p s3://testing.bucket/json_example/ -l 3
{"name":"Gilbert","wins":[["straight","7♣"],["one pair","10♥"]]}
{"name":"Alexa","wins":[["two pair","4♠"],["two pair","9♠"]]}
{"name":"May","wins":[]}
Files processed: 0/1  Records matched: 3  Failed requests: 0</pre>

It's JSON. Great - that's s3select default format. Let's get a subset of its data
<pre>
$ s3select -p s3://testing.bucket/json_example -l 3 -w "s.name LIKE '%Gil%'" -o "s.wins"
{"wins":[["straight","7♣"],["one pair","10♥"]]}
Files processed: 1/1  Records matched: 1  Failed requests: 0
</pre>

What if the input is not in JSON:
<pre>
$ s3select -p s3://testing.bucket/csv_example -l 3
Exception caught when querying csv_example/example.csv: An error occurred (JSONParsingError) when calling the SelectObjectContent operation: Error parsing JSON file. Please check the file and try again.
</pre>
Exception means input isn't parsable JSON. Let's switch to CSV file delimited with `,` but you can specify any other delimiter char. Often used is `TAB` specified with `\\t` 
<pre>
$ s3select -p s3://testing.bucket/csv_example -l 3 -d ,
Gilbert,straight,7♣,one pair,10♥
Alexa,two pair,4♠,two pair,9♠
May,,,,
Files processed: 0/1  Records matched: 3  Failed requests: 0
</pre>

Since utilising the first line of CSV as a header isn't yet supported we'll select a subset of data using column enumeration:   
<pre>
$ s3select -p s3://testing.bucket/csv_example -l 3 -d , -w "s._1 LIKE '%i%'" -o "s._2"
straight
three of a kind
Files processed: 0/1  Records matched: 2  Failed requests: 0
</pre>

If you are interested in pricing for your requests, add `-v` to increase verbosity which will include pricing information at the end:
<pre>
$ s3select -p s3://testing.bucket/10G_sample -v -c
Files processed: 77/77  Records matched: 5696395  Failed requests: 0
Cost for data scanned: $0.02
Cost for data returned: $0.00
Cost for SELECT requests: $0.00
Total cost: $0.02
</pre>

### License

Distributed under the MIT license. See `LICENSE` for more information.
